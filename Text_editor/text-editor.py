#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This script was cleaned up / documented with AI help for clarity and readability.
"""
text-editor.py — Renommer les personnages / objets d'un firmware Tamagotchi Paradise.

UTILISATION
-----------
  Voir tous les noms :
      python text-editor.py mondump.bin --liste
      python text-editor.py mondump.bin --liste --filtre CHAPEAU

  Renommer (ancien puis nouveau, entre guillemets si espaces) :
      python text-editor.py mondump.bin "MAMETCHI" "GAETAN"
      python text-editor.py mondump.bin "CHAPEAU IRUKATCHI" "CHAPEAU CUSTOM" "ROCKY YOUNG" "CHOCOBO"

  Choisir le fichier de sortie (sinon : <nom>-RENOMME.bin) :
      python text-editor.py mondump.bin "MAMETCHI" "GAETAN" -o resultat.bin

NOTES
-----
- Pars toujours d'un dump récent de TA console (pour garder ta progression).
- Le nouveau nom doit tenir dans la place de l'ancien (le script te dit le maximum).
- Caractères gérés : A–Z, chiffres, espace, accents É Ç Ê Ñ et l'apostrophe.
- Le script trouve l'archive tout seul (rien n'est codé en dur) et recalcule les checksums.
"""

import sys, struct, argparse, os

# --- Le firmware range les textes dans une "archive" qui commence à cette adresse ---
ADRESSE_ARCHIVE_PRINCIPALE = 0x111000
MAGIC_ARC2 = 0x32435241          # signature "ARC2" qui marque une archive
LANGUE_FRANCAIS = 2              # index de la table française (1=EN, 2=FR, 3=DE, 4=PT, 5=ES, 6=IT)

# --- Correspondance entre les codes du jeu et les caractères lisibles ---
# (le jeu n'utilise pas l'ASCII normal : chaque caractère a son propre code sur 16 bits)
ACCENTS_VERS_TEXTE = {0x197: 'É', 0x196: 'Ç', 0x199: 'Ê', 0x1AA: 'Ñ', 0x178: "'"}
TEXTE_VERS_ACCENTS = {v: k for k, v in ACCENTS_VERS_TEXTE.items()}


def code_vers_caractere(code):
    """Traduit un code du jeu en caractère lisible (ou None si c'est la fin du texte)."""
    if code == 0:
        return None                      # 0 = fin de chaîne
    if code in ACCENTS_VERS_TEXTE:
        return ACCENTS_VERS_TEXTE[code]
    if code == 0x131:
        return ' '
    if 0x132 <= code <= 0x13B:           # chiffres 0 à 9
        return chr(ord('0') + (code - 0x132))
    if 0x00FD <= code <= 0x017A:         # lettres et ponctuation (ASCII décalé de 0xFD)
        c = code - 0x00FD
        if 0x20 <= c <= 0x7E:
            return chr(c)
    if code == 0xF000:                   # saut de ligne
        return '⏎'
    return f'⟨{code:04X}⟩'      # glyphe non-latin : jeton ⟨XXXX⟩ (sans perte)


def caractere_vers_code(c):
    """Traduit un caractère tapé par l'utilisateur en code du jeu (ou lève une erreur)."""
    if c in TEXTE_VERS_ACCENTS:
        return TEXTE_VERS_ACCENTS[c]
    if c == ' ':
        return 0x131
    if c.isdigit():
        return 0x132 + (ord(c) - ord('0'))
    code = ord(c)
    if 0x20 <= code <= 0x7E:
        return 0x00FD + code
    raise ValueError(f'caractère non géré : "{c}"  (autorisés : A–Z, chiffres, espace, É Ç Ê Ñ, apostrophe)')


# ----------------------------------------------------------------------------
#  Lecture de la structure du fichier
# ----------------------------------------------------------------------------
def lire_mot(buf, position):
    """Lit un nombre de 32 bits (4 octets) à une position donnée."""
    return struct.unpack_from("<I", buf, position)[0]


def trouver_archive_textes(buf):
    """Cherche l'archive qui contient les 9 langues, où qu'elle soit dans le fichier."""
    if lire_mot(buf, ADRESSE_ARCHIVE_PRINCIPALE) != MAGIC_ARC2:
        raise RuntimeError("Ce fichier n'a pas l'air d'être un firmware Paradise (archive introuvable).")
    nb_fichiers = lire_mot(buf, ADRESSE_ARCHIVE_PRINCIPALE + 12)
    for i in range(nb_fichiers):
        entree = ADRESSE_ARCHIVE_PRINCIPALE + 16 + i * 16
        debut = ADRESSE_ARCHIVE_PRINCIPALE + lire_mot(buf, entree + 4)
        if 0 <= debut < len(buf) - 16 and lire_mot(buf, debut) == MAGIC_ARC2 and lire_mot(buf, debut + 12) == 9:
            return debut
    raise RuntimeError("Archive de textes (9 langues) introuvable.")


def fin_du_contenu(buf, debut_archive):
    """Renvoie l'octet où se termine le contenu d'une archive (pour le checksum)."""
    nb_fichiers = lire_mot(buf, debut_archive + 12)
    fin = 0
    for i in range(nb_fichiers):
        entree = debut_archive + 16 + i * 16
        fin = max(fin, lire_mot(buf, entree + 4) + lire_mot(buf, entree + 12))
    return fin


def lister_noms(buf, langue):
    """Renvoie la liste des textes d'une langue : [(adresse, place_en_octets, texte), ...]."""
    archive = trouver_archive_textes(buf)
    decalage = lire_mot(buf, archive + 16 + langue * 16 + 4)
    longueur = lire_mot(buf, archive + 16 + langue * 16 + 12)
    base = archive + decalage

    resultat, i, courant, debut = [], 0, [], None
    while i < longueur - 1:
        code = struct.unpack_from("<H", buf, base + i)[0]
        if code == 0:                                  # fin d'un texte
            if courant:
                texte = "".join(courant)
                if any(ch.isalpha() or ch.isdigit() for ch in texte):
                    place = (base + i - debut) + 2     # taille réservée, terminateur compris
                    resultat.append((debut, place, texte))
            courant, debut = [], None
        else:
            if debut is None:
                debut = base + i
            courant.append(code_vers_caractere(code) or '·')
        i += 2
    return resultat


# ----------------------------------------------------------------------------
#  Modification — ré-empaquetage (longueur illimitée)
# ----------------------------------------------------------------------------
#  On ne réécrit plus "sur place" (ce qui imposait que le nouveau nom tienne
#  dans l'ancien). On reconstruit entièrement l'archive de textes : un nom peut
#  donc être plus long ou plus court que l'original. L'archive Strings est le
#  dernier fichier de l'archive principale ; elle grandit dans la zone libre
#  qui suit (octets 0xFF), sans déplacer aucun autre fichier.

def indice_fichier_textes(buf):
    """Renvoie l'indice du fichier Strings dans l'archive principale."""
    nb = lire_mot(buf, ADRESSE_ARCHIVE_PRINCIPALE + 12)
    for i in range(nb):
        debut = ADRESSE_ARCHIVE_PRINCIPALE + lire_mot(buf, ADRESSE_ARCHIVE_PRINCIPALE + 16 + i * 16 + 4)
        if 0 <= debut < len(buf) - 16 and lire_mot(buf, debut) == MAGIC_ARC2 and lire_mot(buf, debut + 12) == 9:
            return i
    raise RuntimeError("Archive de textes introuvable.")


def parser_toutes_tables(buf):
    """Parse les 9 tables -> liste de 9 listes de chaînes ; chaque chaîne = liste de codes 16 bits."""
    archive = trouver_archive_textes(buf)
    tables = []
    for t in range(9):
        decalage = lire_mot(buf, archive + 16 + t * 16 + 4)
        longueur = lire_mot(buf, archive + 16 + t * 16 + 12)
        base = archive + decalage
        chaines, courant, i = [], [], 0
        while i < longueur - 1:
            code = struct.unpack_from("<H", buf, base + i)[0]
            if code == 0:
                chaines.append(courant); courant = []
            else:
                courant.append(code)
            i += 2
        tables.append(chaines)
    return tables


def construire_archive_textes(tables):
    """Reconstruit l'archive Strings (en-tête + 9 entrées + données) -> bytearray."""
    n = 9
    taille_entete = 16 + n * 16
    blobs = []
    for chaines in tables:
        ba = bytearray()
        for s in chaines:
            for code in s:
                ba += struct.pack("<H", code & 0xFFFF)
            ba += b"\x00\x00"
        blobs.append(bytes(ba))
    out = bytearray(taille_entete)
    struct.pack_into("<I", out, 0, MAGIC_ARC2)
    struct.pack_into("<I", out, 12, n)
    curseur = taille_entete
    for t in range(n):
        e = 16 + t * 16
        struct.pack_into("<I", out, e + 0, 0)               # flags
        struct.pack_into("<I", out, e + 4, curseur)         # offset (relatif à l'archive)
        struct.pack_into("<I", out, e + 8, len(blobs[t]))   # clen
        struct.pack_into("<I", out, e + 12, len(blobs[t]))  # ulen
        out += blobs[t]
        curseur += len(blobs[t])
    total = len(out)
    struct.pack_into("<I", out, 8, total - 16)              # champ length = total - 16
    somme = sum(out[8:total]) & 0xFFFFFFFF                  # checksum = somme [+8 : fin]
    struct.pack_into("<I", out, 4, somme)
    return bytes(out)


# L'archive Strings grandit DANS la zone libre (0xFF) qui la suit, SANS décaler
# les régions à adresses fixes au-delà (bloc Version 0xD49000, ghosts, save
# 0xEFE000, …). On écrit donc sur place dans la copie 16 Mo intacte.
LIMITE_ZONE_LIBRE = 0xD49000   # 1ère région fixe après les assets

def reempaqueter(buf, tables):
    """Reconstruit le firmware avec les tables modifiées. Renvoie un bytearray 16 Mo
    où SEULE la zone de l'archive Strings change (rien d'autre n'est déplacé)."""
    nouvelle = construire_archive_textes(tables)
    fk = indice_fichier_textes(buf)
    strOff = lire_mot(buf, ADRESSE_ARCHIVE_PRINCIPALE + 16 + fk * 16 + 4)
    strLen = lire_mot(buf, ADRESSE_ARCHIVE_PRINCIPALE + 16 + fk * 16 + 12)
    strAbs = ADRESSE_ARCHIVE_PRINCIPALE + strOff
    fin_main = fin_du_contenu(buf, ADRESSE_ARCHIVE_PRINCIPALE)
    if strOff + strLen != fin_main:
        raise RuntimeError("L'archive Strings n'est pas le dernier fichier de l'archive principale.")
    if strAbs + len(nouvelle) > LIMITE_ZONE_LIBRE:
        raise RuntimeError(f"Textes trop volumineux : dépasse la zone libre avant {LIMITE_ZONE_LIBRE:#x}. Raccourcis des noms.")
    out = bytearray(buf)                       # copie 16 Mo intacte
    out[strAbs:strAbs + len(nouvelle)] = nouvelle   # écrit sur place
    if len(nouvelle) < strLen:                 # reliquat -> zone libre (0xFF)
        for o in range(strAbs + len(nouvelle), strAbs + strLen):
            out[o] = 0xFF
    # maj entrée main file (clen/ulen)
    struct.pack_into("<I", out, ADRESSE_ARCHIVE_PRINCIPALE + 16 + fk * 16 + 8, len(nouvelle))
    struct.pack_into("<I", out, ADRESSE_ARCHIVE_PRINCIPALE + 16 + fk * 16 + 12, len(nouvelle))
    # maj champ length + checksum de l'archive principale
    new_fin_main = strOff + len(nouvelle)
    struct.pack_into("<I", out, ADRESSE_ARCHIVE_PRINCIPALE + 8, new_fin_main - 16)
    somme = sum(out[ADRESSE_ARCHIVE_PRINCIPALE + 8: ADRESSE_ARCHIVE_PRINCIPALE + new_fin_main]) & 0xFFFFFFFF
    struct.pack_into("<I", out, ADRESSE_ARCHIVE_PRINCIPALE + 4, somme)
    return out


def texte_vers_codes(texte):
    """Convertit un texte saisi en liste de codes. Gère les jetons ⟨XXXX⟩ (glyphes non-latins)."""
    codes, i = [], 0
    while i < len(texte):
        ch = texte[i]
        if ch == '⟨':
            fin = texte.find('⟩', i)
            if fin > i:
                hexa = texte[i + 1:fin]
                try:
                    codes.append(int(hexa, 16) & 0xFFFF); i = fin + 1; continue
                except ValueError:
                    pass
            raise ValueError("jeton ⟨…⟩ invalide (format attendu : ⟨ABCD⟩)")
        if ch == '⏎':
            codes.append(0xF000); i += 1; continue
        codes.append(caractere_vers_code(ch)); i += 1
    return codes


# ----------------------------------------------------------------------------
#  Programme principal
# ----------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description="Renommer des personnages / objets dans un firmware Tamagotchi Paradise.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Exemples :\n'
               '  python text-editor.py mondump.bin --liste\n'
               '  python text-editor.py mondump.bin "MAMETCHI" "GAETAN"\n'
               '  python text-editor.py mondump.bin "ROCKY YOUNG" "CHOCOBO" "MAMETCHI" "GAETAN"\n')
    p.add_argument("fichier", help="le dump .bin de ta console")
    p.add_argument("noms", nargs="*", help='paires : "ANCIEN" "NOUVEAU" (autant que tu veux)')
    p.add_argument("-l", "--liste", action="store_true", help="afficher tous les noms puis quitter")
    p.add_argument("--filtre", default="", help="avec --liste : ne montrer que les noms contenant ce mot")
    p.add_argument("--langue", type=int, default=LANGUE_FRANCAIS,
                   help="table de langue (défaut 2 = français ; 0=JP 1=EN 3=DE 4=PT 5=ES 6=IT 7=ZH 8=KO)")
    p.add_argument("-o", "--sortie", help="fichier de sortie (défaut : <nom>-RENOMME.bin)")
    args = p.parse_args()

    if not os.path.exists(args.fichier):
        p.error(f"fichier introuvable : {args.fichier}")
    buf = bytearray(open(args.fichier, "rb").read())

    # --- Mode liste : on affiche et on s'arrête ---
    if args.liste:
        filtre = args.filtre.upper()
        print(f"Noms (langue {args.langue}) :\n")
        for adresse, place, texte in lister_noms(buf, args.langue):
            if filtre and filtre not in texte.upper():
                continue
            print(f'  max {place // 2 - 1:>2}c : {texte}')
        return

    # --- Mode renommage : on attend des paires ancien/nouveau ---
    if not args.noms or len(args.noms) % 2 != 0:
        p.error('donne des paires : "ANCIEN" "NOUVEAU". (Ou utilise --liste pour voir les noms.)')

    # On repère chaque ancien nom par son indice dans la table de langue choisie,
    # puis on reconstruit l'archive (longueur du nouveau nom libre).
    tables = parser_toutes_tables(buf)
    chaines = tables[args.langue]
    # texte lisible -> indice (première occurrence)
    index_par_texte = {}
    for idx, s in enumerate(chaines):
        txt = "".join(code_vers_caractere(c) or '·' for c in s)
        index_par_texte.setdefault(txt, idx)

    paires = list(zip(args.noms[0::2], args.noms[1::2]))
    for ancien, nouveau in paires:
        if ancien not in index_par_texte:
            print(f'  ✗ "{ancien}" introuvable. (Vérifie l\'orthographe, ou lance --liste.)')
            sys.exit(1)
        idx = index_par_texte[ancien]
        try:
            chaines[idx] = texte_vers_codes(nouveau.upper())
        except ValueError as e:
            print(f"  ✗ {e}")
            sys.exit(1)
        print(f'  ✓ "{ancien}" → "{nouveau.upper()}"')

    out = reempaqueter(buf, tables)

    sortie = args.sortie or (os.path.splitext(args.fichier)[0] + "-RENOMME.bin")
    open(sortie, "wb").write(out)
    print(f"\nTerminé ! Fichier prêt à flasher : {sortie}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        print("\nInterrompu.")
