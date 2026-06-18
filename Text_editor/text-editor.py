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
    return '·'                           # caractère spécial non géré (affichage seulement)


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
#  Modification
# ----------------------------------------------------------------------------
def ecrire_nom(buf, adresse, place, nouveau_texte):
    """Écrit un nouveau texte à la place de l'ancien (et complète avec des zéros)."""
    codes = [caractere_vers_code(c) for c in nouveau_texte]
    octets_necessaires = len(codes) * 2 + 2            # texte + terminateur
    if octets_necessaires > place:
        maxi = place // 2 - 1
        raise ValueError(f'"{nouveau_texte}" est trop long : {len(codes)} caractères (maximum {maxi}).')
    p = adresse
    for code in codes:
        struct.pack_into("<H", buf, p, code)
        p += 2
    for q in range(p, adresse + place):                # remplir le reste de zéros
        buf[q] = 0


def recalculer_checksums(buf):
    """Recalcule les deux checksums (somme des octets). Ordre important : textes d'abord."""
    archive_textes = trouver_archive_textes(buf)
    for archive in (archive_textes, ADRESSE_ARCHIVE_PRINCIPALE):
        somme = sum(buf[archive + 8: archive + fin_du_contenu(buf, archive)]) & 0xFFFFFFFF
        struct.pack_into("<I", buf, archive + 4, somme)


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
                   help="table de langue (défaut 2 = français ; 1=EN 3=DE 4=PT 5=ES 6=IT)")
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

    table = {texte: (adresse, place) for adresse, place, texte in lister_noms(buf, args.langue)}
    paires = list(zip(args.noms[0::2], args.noms[1::2]))

    for ancien, nouveau in paires:
        if ancien not in table:
            print(f'  ✗ "{ancien}" introuvable. (Vérifie l\'orthographe, ou lance --liste.)')
            sys.exit(1)
        adresse, place = table[ancien]
        try:
            ecrire_nom(buf, adresse, place, nouveau.upper())
        except ValueError as e:
            print(f"  ✗ {e}")
            sys.exit(1)
        print(f'  ✓ "{ancien}" → "{nouveau.upper()}"')

    recalculer_checksums(buf)

    sortie = args.sortie or (os.path.splitext(args.fichier)[0] + "-RENOMME.bin")
    open(sortie, "wb").write(buf)
    print(f"\nTerminé ! Fichier prêt à flasher : {sortie}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        print("\nInterrompu.")
