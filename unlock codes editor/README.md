# Unlock Codes Editor — Tamagotchi Paradise

## What does it do?

The unlock codes editor lets you change the numeric passwords (8-digit codes) that unlock items in Tamagotchi Paradise.

On your console, you enter a code and you unlock a hat, a crown, an accessory, etc. This editor lets you:
- View all codes stored in your firmware
- Change any code without any math
- Download the modified firmware ready to flash

Why it's simple: codes are stored in plain text (ASCII, 8 digits) in the firmware, with no checksum to recalculate. You modify 8 bytes, that's it.

## How we found it

We scanned the XIP range (0x11000–0x110000) looking for patterns of "8 ASCII digits followed by a null byte" (C structure `char[8] + \0`).

A real code table should contain at least 20 consecutive codes. We used this as a criterion to avoid false positives from random "0-9 + null" sequences.

We took a code visible on the console, found it in the dump at the calculated address, modified it, flashed it, and validated on hardware.

Unlike the save which has a CRC, codes have no verification mechanism. You can modify them directly.

The code table ended up at 0x167C70 in all tested dumps, though the script searches automatically just in case.

## How to use it

### Option 1: HTML Editor in Browser

File: `editeur_codes.html`

1. Open `editeur_codes.html` in any browser (Chrome, Firefox, Safari)
2. Drag your .bin dump onto it, or click to choose
3. The editor displays all codes with their indexes (#0, #1, etc.)
4. Click a code to edit it (8 digits only)
5. Download the modified file and flash it with Asprogrammer

No files are sent anywhere — everything happens in your browser.

### Option 2: Python Command-Line

File: `codes.py`

View all codes:
```bash
python codes.py mydump.bin --list
```

This shows:
```
103 codes found (index : code) :

    0 : 12345678
    1 : 23456789
   ...
   70 : 46746507
   85 : 17556258
```

Change one or more codes:
```bash
python codes.py mydump.bin 46746507 11112222 17556258 33334444
```

The format is: old code, new code (pairs). Multiple pairs work fine.

Output:
```
  OK  46746507 -> 11112222  (@0x16xxxx)
  OK  17556258 -> 33334444  (@0x16xxxx)
Done! File ready to flash: mydump-CODES.bin
```

Choose output file:
```bash
python codes.py mydump.bin 46746507 11112222 -o result.bin
```

## Practical examples

Scenario 1: You want to see all codes.

With HTML: open `editeur_codes.html`, drag your dump, done.

With Python:
```bash
python codes.py mydump.bin --list | grep -E "^  (70|85)"
```

Scenario 2: You want to unlock the hat at index 70.

Change the code to something simple like 00000000.

With HTML: click index 70, type 00000000, OK, download, flash.

With Python:
```bash
python codes.py mydump.bin 46746507 00000000
```

Scenario 3: You want to create 5 new codes.

With HTML: modify the 5 codes you want, one by one.

With Python:
```bash
python codes.py mydump.bin \
  10101010 11111111 \
  20202020 22222222 \
  30303030 33333333 \
  40404040 44444444 \
  50505050 55555555
```

## Common problems

Don't forget to save a backup before testing. Always keep one.

Code entered incorrectly (less than 8 digits): the HTML editor will flag it in red.

Confused about old/new in the CLI: the order is `python codes.py dump.bin OLD NEW`. Order matters.

## Associated files

| File | Role |
|------|------|
| editeur_codes.html | Browser interface (drag-drop, visual editing) |
| codes.py | Python CLI (scan, list, modify, validate) |

Technical notes:
- Scan range: 0x11000 to 0x110000 (XIP zone)
- Entry size: 9 bytes (8 ASCII digits + 1 null terminator)
- Minimum validated: 20 consecutive codes (avoids false positives)
- Checksum: none (direct modification)

---

# Editeur de codes — Tamagotchi Paradise

## A quoi ca sert ?

L'editeur de codes te permet de changer les mots de passe numeriques (codes a 8 chiffres) qui deverrouillent des objets dans Tamagotchi Paradise.

Sur ta console, tu entres un code et tu deverrouilles un chapeau, une couronne, un accessoire, etc. Cet editeur te permet de :
- Voir tous les codes stockes dans ton firmware
- Changer n'importe quel code sans calcul mathematique
- Telecharger le firmware modifie pret a flasher

Pourquoi c'est simple : les codes sont stockes en clair (ASCII, 8 chiffres) dans le firmware, sans checksum a recalculer. Tu modifies 8 octets, c'est tout.

## Comment on a trouve ?

On a scanne la plage XIP (0x11000–0x110000) en cherchant des patterns de "8 chiffres ASCII suivi d'un octet nul" (structure C `char[8] + \0`).

Une vraie table de codes doit contenir au minimum 20 codes d'affiilee. On a utilise ce critere pour eviter les faux positifs (des sequences "0-9 + nul" aleatoires).

On a pris un code affiche sur la console, on l'a cherche dans le dump, trouve a l'adresse calculee, et modifie. Puis on a flashe et valide sur materiel.

Contrairement a la save (qui a un CRC), les codes n'ont aucun mecanisme de verification. On peut les modifier directement.

La table de codes s'est trouvee systematiquement a 0x167C70 dans tous les dumps testes, mais le script cherche automatiquement au cas ou.

## Comment s'en servir ?

### Option 1 : Editeur HTML dans le navigateur

Fichier : `editeur_codes.html`

1. Ouvre `editeur_codes.html` dans n'importe quel navigateur (Chrome, Firefox, Safari)
2. Glisse ton dump .bin dessus, ou clique pour choisir
3. L'editeur affiche tous les codes avec leurs index (#0, #1, etc.)
4. Clique un code pour le modifier (8 chiffres uniquement)
5. Telecharge le fichier modifie et flashe-le avec Asprogrammer

Aucun fichier n'est envoye nulle part — tout se fait dans ton navigateur.

### Option 2 : Script Python en ligne de commande

Fichier : `codes.py`

Voir tous les codes :
```bash
python codes.py mondump.bin --liste
```

Affiche :
```
103 codes trouves (index : code) :

    0 : 12345678
    1 : 23456789
   ...
   70 : 46746507
   85 : 17556258
```

Changer un ou plusieurs codes :
```bash
python codes.py mondump.bin 46746507 11112222 17556258 33334444
```

Le format est : ancien code, nouveau code (paires). Plusieurs paires, pas de souci.

Affiche :
```
  OK  46746507 -> 11112222  (@0x16xxxx)
  OK  17556258 -> 33334444  (@0x16xxxx)
Termine ! Fichier pret a flasher : mondump-CODES.bin
```

Choisir le fichier de sortie :
```bash
python codes.py mondump.bin 46746507 11112222 -o resultat.bin
```

## Exemples pratiques

Scenario 1 : Tu veux voir tous les codes.

Avec l'HTML : ouvre `editeur_codes.html`, glisse ton dump, done.

Avec Python :
```bash
python codes.py mondump.bin --liste | grep -E "^  (70|85)"
```

Scenario 2 : Tu veux deverrouiller le chapeau a l'index 70.

Change le code en quelque chose de simple comme 00000000.

Avec l'HTML : clique l'index 70, tape 00000000, OK, telecharge, flashe.

Avec Python :
```bash
python codes.py mondump.bin 46746507 00000000
```

Scenario 3 : Tu veux creer 5 nouveaux codes.

Avec l'HTML : modifie les 5 codes que tu veux, un par un.

Avec Python :
```bash
python codes.py mondump.bin \
  10101010 11111111 \
  20202020 22222222 \
  30303030 33333333 \
  40404040 44444444 \
  50505050 55555555
```

## Pieges courants

N'oublie pas de faire une sauvegarde avant de tester. Garde toujours une copie.

Code entre incorrectement (moins de 8 chiffres) : l'editeur HTML va le signaler en rouge.

Confusion ancien/nouveau dans la CLI : l'ordre est `python codes.py dump.bin ANCIEN NOUVEAU`. L'ordre compte.

## Fichiers associes

| Fichier | Role |
|---------|------|
| editeur_codes.html | Interface navigateur (drag-drop, edition visuelle) |
| codes.py | CLI Python (scan, liste, modification, validation) |

Notes techniques :
- Plage de scan : 0x11000 a 0x110000 (zone XIP)
- Taille d'entree : 9 octets (8 chiffres ASCII + 1 null terminator)
- Minimum valide : 20 codes d'affiilee (evite les faux positifs)
- Checksum : aucun (modification directe)