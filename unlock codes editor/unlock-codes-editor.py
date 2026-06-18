#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codes.py - Changer les codes d'unlock (mots de passe numeriques) d'un Tamagotchi Paradise.

Les codes sont stockes en clair (ASCII, 8 chiffres) dans le firmware. Les changer
= reecrire 8 octets, sans aucun checksum a recalculer.

UTILISATION
-----------
  Voir tous les codes :       python codes.py mondump.bin --liste
  Changer un code :           python codes.py mondump.bin 46746507 11112222
  Plusieurs d'un coup :       python codes.py mondump.bin 46746507 11112222 17556258 33334444
  Sortie (defaut <nom>-CODES.bin) :  ... -o resultat.bin

Le nouveau code doit faire 8 chiffres.
"""
import sys, argparse, os

def is_entry(buf,o):
    return o+9<=len(buf) and all(48<=buf[o+k]<=57 for k in range(8)) and buf[o+8]==0

def trouver_table(buf):
    """Repere le plus long tableau de codes (entrees de 9 octets : 8 chiffres + nul)."""
    best=(0,0)  # (debut, nombre)
    o=0x11000; fin=min(0x110000,len(buf))
    while o<fin:
        if is_entry(buf,o):
            start=o; n=0
            while is_entry(buf,o): o+=9; n+=1
            if n>best[1]: best=(start,n)
        else:
            o+=1
    if best[1]<20: raise RuntimeError("table de codes introuvable")
    return best

def lire_codes(buf):
    start,n=trouver_table(buf)
    return start,n,[buf[start+i*9:start+i*9+8].decode() for i in range(n)]

def main():
    p=argparse.ArgumentParser(description="Changer les codes d'unlock d'un Tamagotchi Paradise.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Exemples :\n  python codes.py mondump.bin --liste\n'
               '  python codes.py mondump.bin 46746507 11112222\n')
    p.add_argument("fichier")
    p.add_argument("paires", nargs="*", help="paires : ANCIEN_CODE NOUVEAU_CODE")
    p.add_argument("-l","--liste", action="store_true", help="afficher tous les codes (index + code)")
    p.add_argument("-o","--sortie")
    a=p.parse_args()
    if not os.path.exists(a.fichier): p.error("fichier introuvable : %s" % a.fichier)
    buf=bytearray(open(a.fichier,"rb").read())
    start,n,codes=lire_codes(buf)

    if a.liste:
        print("%d codes (index : code) :\n" % n)
        for i,c in enumerate(codes): print("  %3d : %s" % (i,c))
        return

    if not a.paires or len(a.paires)%2!=0:
        p.error("donne des paires : ANCIEN_CODE NOUVEAU_CODE. (Ou --liste.)")

    pos={c:start+i*9 for i,c in enumerate(codes)}  # code -> adresse
    for ancien, nouveau in zip(a.paires[0::2], a.paires[1::2]):
        if not (len(nouveau)==8 and nouveau.isdigit()):
            print("  ! nouveau code invalide (8 chiffres requis) : %s" % nouveau); sys.exit(1)
        if ancien not in pos:
            print('  ! code "%s" introuvable dans la table (essaie --liste)' % ancien); sys.exit(1)
        adr=pos[ancien]
        buf[adr:adr+8]=nouveau.encode()
        print("  OK  %s -> %s  (@0x%X)" % (ancien, nouveau, adr))

    sortie=a.sortie or (os.path.splitext(a.fichier)[0]+"-CODES.bin")
    open(sortie,"wb").write(buf)
    print("\nTermine ! Fichier pret a flasher : %s" % sortie)

if __name__=="__main__":
    try: main()
    except BrokenPipeError: pass
