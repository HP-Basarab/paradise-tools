#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ghosts.py - Changer l'identite des ghosts d'un Tamagotchi Paradise.

Un "ghost" = un tama present dans tes biomes (ou archive dans les etoiles).
Chaque ghost est un paquet independant qu'on peut editer (checksum recalcule tout seul).

CE QUE CA CHANGE : l'identite stockee (nom + famille + genes).
CE QUE CA NE CHANGE (peut-etre) PAS : l'image (les sprites sont embarques dans le ghost ;
   il faudra peut-etre les remplacer a part). A confirmer en flashant.
CE QU'ON NE PEUT PAS FAIRE : reassigner un ghost a un autre biome (c'est dans la save, bloquee).

UTILISATION
-----------
  Voir tes ghosts :              python ghosts.py mondump.bin --liste
  Voir les persos possibles :    python ghosts.py mondump.bin --persos
                                 python ghosts.py mondump.bin --persos TCHI
  Remplacer (ghost actuel -> nouveau perso) :
       python ghosts.py mondump.bin "CHODRACOTCHI" "MAMETCHI"
       python ghosts.py mondump.bin "BATCHI" "KUCHIPATCHI" "MENDAKOTCHI" "MEOWTCHI"
  Sortie (defaut <nom>-GHOSTS.bin) :  ... -o resultat.bin

Le perso cible se donne par son nom (ex. MAMETCHI) ou son numero (ex. 4022).
Le nom doit faire 12 caracteres maximum (place reservee dans le ghost).
"""

import struct, sys, argparse, os

GHOST_DEBUT = 0xDEE000
GHOST_FIN   = 0xE45FFF
GHOST_PAS   = 0x2000

NOMS = {
    1001: 'BABYMARUTCHI',
    2002: 'LAND KID',
    2003: 'WATER KID',
    2004: 'SKY KID',
    2069: 'FOREST KID',
    3005: 'ROAR YOUNG',
    3006: 'TODDLE YOUNG',
    3007: 'LICK YOUNG',
    3008: 'SPROUT YOUNG',
    3009: 'GLIDE YOUNG',
    3010: 'LEAP YOUNG',
    3011: 'PADDLE YOUNG',
    3012: 'FLOAT YOUNG',
    3013: 'FLAP YOUNG',
    3014: 'CHIRP  YOUNG',
    3015: 'BUMBLE YOUNG',
    3016: 'ROCKY YOUNG',
    3070: 'FOREST ROAR YOUNG',
    3071: 'FOREST TODDLE YOUNG',
    3072: 'FOREST CHIRP YOUNG',
    3073: 'FOREST SPROUT YOUNG',
    4017: 'BBMARUTCHI',
    4018: 'MEOWTCHI',
    4019: 'POCHITCHI',
    4020: 'GUMAX',
    4021: 'RATCHI',
    4022: 'MAMETCHI',
    4023: 'MIMITCHI',
    4024: 'MOLMOTCHI',
    4025: 'SHEEPTCHI',
    4026: 'SEBIRETCHI',
    4027: 'LEOPATCHI',
    4028: 'ELIZARDOTCHI',
    4029: 'HEAVYTCHI',
    4030: 'FURAWATCHI',
    4031: 'TUSTUSTCHI',
    4032: 'POTSUNENTCHI',
    4033: 'SHIGEMI-SAN',
    4034: 'IRUKATCHI',
    4035: 'KAMETCHI',
    4036: 'BEAVERTCHI',
    4037: 'KUJIRATCHI',
    4038: 'AXOLOPATCHI',
    4039: 'IMORITCHI',
    4040: 'KAWAZUTCHI',
    4041: 'URUOTCHI',
    4042: 'TACHUTCHI',
    4043: 'SHARKTCHI',
    4044: 'ANKOTCHI',
    4045: 'OTOTOTCHI',
    4046: 'KURARATCHI',
    4047: 'MENDAKOTCHI',
    4048: 'AMEFURATCHI',
    4049: 'GUSOKUTCHI',
    4050: 'HORHOTCHI',
    4051: 'MONGATCHI',
    4052: 'EAGLETCHI',
    4053: 'BATCHI',
    4054: 'PAPILLOTCHI',
    4055: 'KABUTOTCHI',
    4056: 'TENTOTCHI',
    4057: 'HATCHITCHI',
    4058: 'KUCHIPATCHI',
    4059: 'BATATCHI',
    4060: 'PEACOTCHI',
    4061: 'KIWITCHI',
    4062: 'GEMTCHI',
    4063: 'ORETATCHI',
    4064: 'ISHIKOROTCHI',
    4065: 'MAGMATCHI',
    4066: 'CHODRACOTCHI',
    4067: 'MERMARINTCHI',
    4068: 'YAYACORNTCHI',
    4074: 'FOREST HORHOTCHI',
    4075: 'KONKOTCHI',
    4076: 'TIGAOTCHI',
    4077: 'TANOONTCHI',
    4078: 'LESSAPANTCHI',
    4079: 'KANOKOTCHI',
    4080: 'SUIGYUTCHI',
    4081: 'PANBOOTCHI',
    4082: 'KACHITCHI',
    4083: 'TOKIPATCHI',
    4084: 'KUCHIPATCHI (Forest)',
    4085: 'SPARROTCHI',
    4086: 'SHIITAKETCHI',
    4087: 'PEATCHI',
    4088: 'NAPPATCHI',
    4089: 'RUSHRADITCHI',
    4090: 'TATSUTCHI',
    4800: 'OMARUTCHI',
    4801: 'POOPTCHI',
    4802: 'MEERTCHI',
    4803: 'SHYONTCHI',
}

# ---- correspondance code du jeu <-> caractere (meme charset que les textes) ----
ACC_VERS_TXT = {0x197:'E', 0x196:'C', 0x199:'E', 0x1AA:'N', 0x178:"'"}  # affichage simplifie
def code_vers_car(code):
    if code in ACC_VERS_TXT: return ACC_VERS_TXT[code]
    if code == 0x131: return ' '
    if 0x132 <= code <= 0x13B: return chr(ord('0')+(code-0x132))
    if 0x00FD <= code <= 0x017A:
        c = code-0x00FD
        if 0x20 <= c <= 0x7E: return chr(c)
    return None
def car_vers_code(c):
    if c == ' ': return 0x131
    if c.isdigit(): return 0x132+(ord(c)-ord('0'))
    o = ord(c)
    if 0x20 <= o <= 0x7E: return 0x00FD+o
    raise ValueError('caractere non gere : "%s"' % c)

NOM_ADR1, NOM_ADR2, NOM_MAX = 0x2C, 0x46, 12   # deux champs de nom, 12 car. max

def lire(buf, off): return struct.unpack_from("<I", buf, off)[0]
def lire16(buf, off): return struct.unpack_from("<H", buf, off)[0]

def lire_nom(buf, base, champ):
    s=[]; p=base+champ
    for _ in range(NOM_MAX+2):
        ci=lire16(buf,p); c=code_vers_car(ci)
        if ci==0 or c is None: break
        s.append(c); p+=2
    return "".join(s)

def trouver_ghosts(buf):
    """Liste les slots de ghosts valides : [(slot, adresse, char_id, eye_id, nom), ...]."""
    res=[]; slot=0
    while True:
        base=GHOST_DEBUT+slot*GHOST_PAS
        if base+0x120>len(buf) or base>GHOST_FIN: break
        cid=lire16(buf,base+0x0C); eye=lire16(buf,base+0x0E)
        tlen=lire(buf,base+0x10C)
        if cid in NOMS and 0x1000<=tlen<=0x8000:
            res.append((slot,base,cid,eye,lire_nom(buf,base,NOM_ADR1)))
        slot+=1
    return res

def recalc_checksum(buf, base):
    """w0 = somme des mots de 32 bits de +8 a la fin ; w4 = -w0."""
    tlen=lire(buf,base+0x10C); fin=base+((tlen+3)&~3)
    s=0
    for o in range(base+8, fin, 4): s=(s+lire(buf,o))&0xFFFFFFFF
    struct.pack_into("<I", buf, base+0x00, s)
    struct.pack_into("<I", buf, base+0x04, (-s)&0xFFFFFFFF)

def ecrire_nom(buf, base, champ, nom):
    p=base+champ
    for c in nom:
        struct.pack_into("<H", buf, p, car_vers_code(c)); p+=2
    # terminateur + remplissage du champ (NOM_MAX+1 mots) avec des zeros
    for q in range(p, base+champ+(NOM_MAX+1)*2): buf[q]=0

def remplacer(buf, base, cible_id):
    nom=NOMS[cible_id].strip()
    if len(nom) > NOM_MAX:
        raise ValueError('"%s" fait %d caracteres (max %d).' % (nom, len(nom), NOM_MAX))
    struct.pack_into("<H", buf, base+0x0C, cible_id)   # identite
    struct.pack_into("<H", buf, base+0x0E, cible_id)   # genes (= meme perso)
    ecrire_nom(buf, base, NOM_ADR1, nom)               # nom (copie 1)
    ecrire_nom(buf, base, NOM_ADR2, nom)               # nom (copie 2)
    recalc_checksum(buf, base)

def resoudre_cible(txt):
    if txt.isdigit():
        i=int(txt)
        if i in NOMS: return i
        raise SystemExit('  ! numero de perso inconnu : %s' % txt)
    cible=txt.strip().upper()
    for i,n in NOMS.items():
        if n.strip().upper()==cible: return i
    raise SystemExit('  ! perso introuvable : "%s" (essaie --persos)' % txt)

def main():
    p=argparse.ArgumentParser(description="Changer l'identite des ghosts d'un Tamagotchi Paradise.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Exemples :\n  python ghosts.py mondump.bin --liste\n'
               '  python ghosts.py mondump.bin "BATCHI" "MAMETCHI"\n')
    p.add_argument("fichier")
    p.add_argument("paires", nargs="*", help='"GHOST ACTUEL" "NOUVEAU PERSO" (par paires)')
    p.add_argument("-l","--liste", action="store_true", help="lister tes ghosts")
    p.add_argument("--persos", nargs="?", const="", help="lister les persos possibles (filtre optionnel)")
    p.add_argument("-o","--sortie")
    a=p.parse_args()
    if not os.path.exists(a.fichier): p.error("fichier introuvable : %s" % a.fichier)
    buf=bytearray(open(a.fichier,"rb").read())

    if a.persos is not None:
        f=a.persos.upper()
        for i,n in sorted(NOMS.items()):
            if not f or f in n.upper(): print("  %5d : %s" % (i, n))
        return

    ghosts=trouver_ghosts(buf)
    if a.liste:
        print("Ghosts trouves :\n")
        for slot,base,cid,eye,nom in ghosts:
            g=" (genes: %s)" % NOMS.get(eye, eye) if eye!=cid else ""
            print("  slot %-2d @0x%X : %s%s" % (slot, base, nom, g))
        return

    if not a.paires or len(a.paires)%2!=0:
        p.error('donne des paires : "GHOST ACTUEL" "NOUVEAU PERSO". (Ou --liste / --persos.)')

    par_nom={nom.upper():(slot,base) for slot,base,cid,eye,nom in ghosts}
    par_slot={str(slot):(slot,base) for slot,base,cid,eye,nom in ghosts}
    paires=list(zip(a.paires[0::2], a.paires[1::2]))
    for actuel, nouveau in paires:
        cle=actuel.strip().upper()
        if cle in par_nom: slot,base=par_nom[cle]
        elif actuel in par_slot: slot,base=par_slot[actuel]
        else:
            print('  ! ghost "%s" introuvable (essaie --liste)' % actuel); sys.exit(1)
        cible=resoudre_cible(nouveau)
        try: remplacer(buf, base, cible)
        except ValueError as e: print("  ! %s" % e); sys.exit(1)
        print('  OK  slot %d : -> %s' % (slot, NOMS[cible].strip()))

    sortie=a.sortie or (os.path.splitext(a.fichier)[0]+"-GHOSTS.bin")
    open(sortie,"wb").write(buf)
    print("\nTermine ! Fichier pret a flasher : %s" % sortie)

if __name__=="__main__":
    try: main()
    except BrokenPipeError: pass
    except KeyboardInterrupt: print("\nInterrompu.")
