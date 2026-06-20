# Ghosts Editor — Tamagotchi Paradise

## What does it do?

The ghosts editor lets you change the identity of the "ghosts" stored in your firmware.

A ghost = a tama present in your biomes (or archived in the stars). Each ghost is an independent packet you can edit, with its own checksum (recalculated automatically). This editor lets you:
- View all the ghosts found in your dump (real name, slot, address)
- Turn any ghost into any other character (name + id rewritten)
- Download the modified firmware ready to flash

It is compatible with both **Sky** and **Jade Forest** firmwares.

What it changes: the stored identity (name + family/character id + genes).

What it might NOT change: the image. Sprites are embedded in the ghost; on Jade the structure differs, so the name change is reliable but the sprite must be confirmed by flashing a test on a single ghost first.

What you cannot do: reassign a ghost to a different biome (that's stored in the save, which is locked).

## How we found it

Ghosts live high in the flash, well above the rest of the data. The Python script walks fixed slots from 0xDEE000 to 0xE45FFF with a stride of 0x2000 (8 KB per slot).

To stay compatible across versions (Sky and Jade), the HTML editor scans **dynamically by signature** instead of using a fixed address: starting at 0xC00000 it looks for packets where the two header words satisfy `w0 + w4 == 0` (with `w0 != 0`), where the length field at +0x10C is sane (between 0x1000 and 0x8000), and where the checksum verifies (sum of 32-bit words from +8 to the end equals `w0`). That signature is what uniquely identifies a ghost packet.

Inside each ghost:
- The character id is at +0x0C (Sky) or +0x10A (Jade); the genes/eye id is at +0x0E
- The name is stored twice (+0x2C and +0x46), 12 characters max each
- The charset is the same custom 16-bit charset as the text editor (not ASCII)

Each ghost has its own checksum: word at +0x00 is the sum of 32-bit words from +8 to the end (4-byte aligned), and the word at +0x04 is its two's complement (so the two add up to 0). We change the identity, recalculate this checksum, flash, and verify on console.

## How to use it

### Option 1: HTML Editor in Browser

File: `ghost_editor.html`

1. Open `ghost_editor.html` in any browser (Chrome, Firefox, Safari)
2. Drag your .bin dump onto it, or click to choose
3. The editor finds the ghosts automatically and shows each one's real identity (name, slot, address)
4. Use the dropdown next to a ghost to pick a new character (grouped: Adults, Young, Kids, Baby, Forest, Other)
5. The name + id are rewritten and the checksum is recalculated instantly
6. Download the modified file and flash it with Asprogrammer

No files are sent anywhere — everything happens in your browser.

### Option 2: Python Command-Line

File: `ghosts_editor.py`

View your ghosts:
```bash
python ghosts_editor.py mydump.bin --liste
```

This shows:
```
Ghosts trouves :

  slot 0  @0xDEE000 : CHODRACOTCHI
  slot 1  @0xDF0000 : BATCHI (genes: MAMETCHI)
  ...
```

View the characters you can use (optional filter):
```bash
python ghosts_editor.py mydump.bin --persos
python ghosts_editor.py mydump.bin --persos TCHI
```

Replace one or more ghosts (current ghost, new character — by pairs):
```bash
python ghosts_editor.py mydump.bin "CHODRACOTCHI" "MAMETCHI"
python ghosts_editor.py mydump.bin "BATCHI" "KUCHIPATCHI" "MENDAKOTCHI" "MEOWTCHI"
```

The target character can be given by name (MAMETCHI) or by number (4022). The name must fit in 12 characters (reserved space in the ghost).

Output:
```
  OK  slot 0 : -> MAMETCHI
Termine ! Fichier pret a flasher : mydump-GHOSTS.bin
```

Choose output file:
```bash
python ghosts_editor.py mydump.bin "BATCHI" "MAMETCHI" -o result.bin
```

## Practical examples

Scenario 1: You want to see your ghosts and which characters are available.

With HTML: open `ghost_editor.html`, drag your dump — the list and the dropdowns show everything.

With Python:
```bash
python ghosts_editor.py mydump.bin --liste
python ghosts_editor.py mydump.bin --persos
```

Scenario 2: You want to turn one of your ghosts into MAMETCHI.

With HTML: find the ghost in the list, pick MAMETCHI in its dropdown, download, flash.

With Python:
```bash
python ghosts_editor.py mydump.bin "BATCHI" "MAMETCHI"
```

Scenario 3: You want to replace several ghosts at once.

With HTML: change each dropdown one by one, then download.

With Python, in one command:
```bash
python ghosts_editor.py mydump.bin \
  "BATCHI" "MAMETCHI" \
  "CHODRACOTCHI" "KUCHIPATCHI" \
  "MENDAKOTCHI" "MEOWTCHI"
```

## Common problems

Don't forget to save a backup before testing. Always keep one.

Name too long: a target character whose name exceeds 12 characters is rejected with a clear error.

Sprite not changing (Jade Forest): the name/id change is reliable, but the image may stay the same. Confirm by flashing a test on a single ghost before doing them all.

Trying to move a biome: you cannot reassign a ghost to another biome — that information lives in the save, which is locked.

Ghost not found: the "current ghost" name must match a ghost actually present in your dump. Use `--liste` to see the exact names.

Confused about old/new in the CLI: the order is `python ghosts_editor.py dump.bin "CURRENT GHOST" "NEW CHARACTER"`. Order matters.

## Associated files

| File | Role |
|------|------|
| ghost_editor.html | Browser interface (dynamic scan, dropdown per ghost, Sky + Jade, checksum recalc) |
| ghosts_editor.py | Python CLI (list ghosts, list characters, replace by pairs) |

Technical notes:
- Ghost slots: 0xDEE000 to 0xE45FFF, stride 0x2000 (8 KB per slot)
- HTML dynamic scan: from 0xC00000, signature `w0 + w4 == 0`, sane length, verified checksum
- Identity id: +0x0C (Sky) / +0x10A (Jade); genes/eye id: +0x0E
- Name: stored twice at +0x2C and +0x46, 12 characters max, custom 16-bit charset
- Length field: +0x10C (sane range 0x1000–0x8000)
- Checksum: +0x00 = sum of 32-bit words from +8 to end; +0x04 = -sum (the script does it automatically)

---

# Editeur de ghosts — Tamagotchi Paradise

## A quoi ca sert ?

L'editeur de ghosts te permet de changer l'identite des "ghosts" stockes dans ton firmware.

Un ghost = un tama present dans tes biomes (ou archive dans les etoiles). Chaque ghost est un paquet independant qu'on peut editer, avec son propre checksum (recalcule automatiquement). Cet editeur te permet de :
- Voir tous les ghosts trouves dans ton dump (vrai nom, slot, adresse)
- Transformer n'importe quel ghost en n'importe quel autre perso (nom + id reecrits)
- Telecharger le firmware modifie pret a flasher

Il est compatible avec les firmwares **Sky** ET **Jade Forest**.

Ce que ca change : l'identite stockee (nom + famille/id du perso + genes).

Ce que ca ne change (peut-etre) PAS : l'image. Les sprites sont embarques dans le ghost ; sur Jade la structure differe, donc le changement de nom est fiable mais le sprite doit etre confirme en flashant un test sur un seul ghost d'abord.

Ce qu'on ne peut pas faire : reassigner un ghost a un autre biome (c'est dans la save, qui est bloquee).

## Comment on a trouve ?

Les ghosts se trouvent haut dans la flash, bien au-dessus du reste des donnees. Le script Python parcourt des slots fixes de 0xDEE000 a 0xE45FFF, avec un pas de 0x2000 (8 Ko par slot).

Pour rester compatible entre les versions (Sky et Jade), l'editeur HTML scanne **dynamiquement par signature** au lieu d'utiliser une adresse fixe : a partir de 0xC00000, il cherche les paquets ou les deux mots d'en-tete verifient `w0 + w4 == 0` (avec `w0 != 0`), ou le champ de longueur a +0x10C est sain (entre 0x1000 et 0x8000), et ou le checksum se verifie (somme des mots de 32 bits de +8 jusqu'a la fin = `w0`). Cette signature identifie un paquet ghost de maniere unique.

A l'interieur de chaque ghost :
- L'id du perso est a +0x0C (Sky) ou +0x10A (Jade) ; l'id des genes/eye est a +0x0E
- Le nom est stocke deux fois (+0x2C et +0x46), 12 caracteres max chacun
- Le charset est le meme charset custom 16-bit que l'editeur de textes (pas de l'ASCII)

Chaque ghost a son propre checksum : le mot a +0x00 est la somme des mots de 32 bits de +8 jusqu'a la fin (aligne sur 4 octets), et le mot a +0x04 est son complement a deux (les deux s'additionnent a 0). On change l'identite, on recalcule ce checksum, on flashe, et on verifie sur console.

## Comment s'en servir ?

### Option 1 : Editeur HTML dans le navigateur

Fichier : `ghost_editor.html`

1. Ouvre `ghost_editor.html` dans n'importe quel navigateur (Chrome, Firefox, Safari)
2. Glisse ton dump .bin dessus, ou clique pour choisir
3. L'editeur trouve les ghosts automatiquement et affiche la vraie identite de chacun (nom, slot, adresse)
4. Utilise le menu deroulant a cote d'un ghost pour choisir un nouveau perso (regroupes : Adultes, Jeunes, Enfants, Bebe, Forest, Autres)
5. Le nom + l'id sont reecrits et le checksum est recalcule instantanement
6. Telecharge le fichier modifie et flashe-le avec Asprogrammer

Aucun fichier n'est envoye nulle part — tout se fait dans ton navigateur.

### Option 2 : Script Python en ligne de commande

Fichier : `ghosts_editor.py`

Voir tes ghosts :
```bash
python ghosts_editor.py mondump.bin --liste
```

Affiche :
```
Ghosts trouves :

  slot 0  @0xDEE000 : CHODRACOTCHI
  slot 1  @0xDF0000 : BATCHI (genes: MAMETCHI)
  ...
```

Voir les persos possibles (filtre optionnel) :
```bash
python ghosts_editor.py mondump.bin --persos
python ghosts_editor.py mondump.bin --persos TCHI
```

Remplacer un ou plusieurs ghosts (ghost actuel, nouveau perso — par paires) :
```bash
python ghosts_editor.py mondump.bin "CHODRACOTCHI" "MAMETCHI"
python ghosts_editor.py mondump.bin "BATCHI" "KUCHIPATCHI" "MENDAKOTCHI" "MEOWTCHI"
```

Le perso cible se donne par son nom (MAMETCHI) ou son numero (4022). Le nom doit tenir en 12 caracteres (place reservee dans le ghost).

Affiche :
```
  OK  slot 0 : -> MAMETCHI
Termine ! Fichier pret a flasher : mondump-GHOSTS.bin
```

Choisir le fichier de sortie :
```bash
python ghosts_editor.py mondump.bin "BATCHI" "MAMETCHI" -o resultat.bin
```

## Exemples pratiques

Scenario 1 : Tu veux voir tes ghosts et les persos disponibles.

Avec l'HTML : ouvre `ghost_editor.html`, glisse ton dump — la liste et les menus deroulants montrent tout.

Avec Python :
```bash
python ghosts_editor.py mondump.bin --liste
python ghosts_editor.py mondump.bin --persos
```

Scenario 2 : Tu veux transformer un de tes ghosts en MAMETCHI.

Avec l'HTML : trouve le ghost dans la liste, choisis MAMETCHI dans son menu deroulant, telecharge, flashe.

Avec Python :
```bash
python ghosts_editor.py mondump.bin "BATCHI" "MAMETCHI"
```

Scenario 3 : Tu veux remplacer plusieurs ghosts d'un coup.

Avec l'HTML : change chaque menu deroulant un par un, puis telecharge.

Avec Python, en une commande :
```bash
python ghosts_editor.py mondump.bin \
  "BATCHI" "MAMETCHI" \
  "CHODRACOTCHI" "KUCHIPATCHI" \
  "MENDAKOTCHI" "MEOWTCHI"
```

## Pieges courants

N'oublie pas de faire une sauvegarde avant de tester. Garde toujours une copie.

Nom trop long : un perso cible dont le nom depasse 12 caracteres est refuse avec un message d'erreur clair.

Sprite qui ne change pas (Jade Forest) : le changement de nom/id est fiable, mais l'image peut rester la meme. Confirme en flashant un test sur un seul ghost avant de tous les faire.

Essayer de changer de biome : tu ne peux pas reassigner un ghost a un autre biome — cette info est dans la save, qui est bloquee.

Ghost introuvable : le nom du "ghost actuel" doit correspondre a un ghost reellement present dans ton dump. Utilise `--liste` pour voir les noms exacts.

Confusion ancien/nouveau dans la CLI : l'ordre est `python ghosts_editor.py dump.bin "GHOST ACTUEL" "NOUVEAU PERSO"`. L'ordre compte.

## Fichiers associes

| Fichier | Role |
|---------|------|
| ghost_editor.html | Interface navigateur (scan dynamique, menu deroulant par ghost, Sky + Jade, recalc checksum) |
| ghosts_editor.py | CLI Python (liste des ghosts, liste des persos, remplacement par paires) |

Notes techniques :
- Slots de ghosts : 0xDEE000 a 0xE45FFF, pas de 0x2000 (8 Ko par slot)
- Scan dynamique HTML : depuis 0xC00000, signature `w0 + w4 == 0`, longueur saine, checksum verifie
- Id d'identite : +0x0C (Sky) / +0x10A (Jade) ; id des genes/eye : +0x0E
- Nom : stocke deux fois a +0x2C et +0x46, 12 caracteres max, charset custom 16-bit
- Champ de longueur : +0x10C (plage saine 0x1000–0x8000)
- Checksum : +0x00 = somme des mots de 32 bits de +8 jusqu'a la fin ; +0x04 = -somme (le script le fait automatiquement)
