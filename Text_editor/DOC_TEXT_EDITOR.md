# Text Editor — Tamagotchi Paradise

## What does it do?

The text editor lets you rename all text in the firmware:
- Characters (MAMETCHI → GAETAN, etc.)
- Objects (HAT IRUKATCHI → CUSTOM HAT, etc.)
- Localizations (the script supports all 6 in-game languages)

What it does automatically:
1. Locates the text archive in the firmware (it's relocated in different versions, the script finds it)
2. Handles the custom charset (the game doesn't use ASCII: characters have their own codes)
3. Recalculates checksums (two archives need verification sums)
4. Produces a firmware ready to flash

The HTML interface shows available space (max 15c = 15 characters max) and prevents you from typing too much. Compared to just using Python CLI, this is helpful.

## How we found it

The firmware contains a standard archive (Sonix ARC2 format: signature 0x32435241). We located it at 0x111000 first (known address).

This main archive contains 9 files (the 9 game translations: EN, FR, DE, PT, ES, IT, plus variants). Each is itself an ARC2 archive.

The game doesn't use ASCII. Codes are 16-bit (2 bytes) and map to:
- 0x00FD + ASCII for A–Z, digits, punctuation
- 0x131 for space
- 0x132 + n for digits 0–9
- 0x197, 0x196, 0x199, 0x1AA, 0x178 for É, Ç, Ê, Ñ, '

Each text is 16-bit codes terminated by 0 (null terminator). Texts are stored sequentially in a binary block.

Two levels of checksums:
- Each ARC2 archive has a checksum: sum of content bytes (4 bytes)
- We must recalculate after modification

We changed a text in the text archive, recalculated checksums, flashed, and verified on console.

## How to use it

### Option 1: HTML Editor in Browser

File: `text-editor.html`

1. Open `text-editor.html` in a browser
2. Drag your .bin dump, or click to choose
3. Choose language (default = French, your console)
4. Text list displays with:
   - Current text
   - max 15c = 15 chars max to replace it
5. Click a text to edit it
6. Editor prevents you from typing too long (shows counter)
7. Download and flash with Asprogrammer

Allowed characters:
- Letters A–Z (uppercase mandatory, script forces them)
- Digits 0–9
- Space
- Accents: É, Ç, Ê, Ñ
- Apostrophe '

The buttons "É Ç Ê Ñ '" let you insert accents without a special keyboard.

### Option 2: Python Command-Line

File: `text-editor.py`

View all names:
```bash
python text-editor.py mydump.bin --list
```

Output:
```
Names (language 2) :

  max 15c : MAMETCHI
  max 18c : HAT IRUKATCHI
  max 12c : ROCKY YOUNG
  ...
```

View only names containing a word:
```bash
python text-editor.py mydump.bin --list --filter HAT
```

Rename one or more names:
```bash
python text-editor.py mydump.bin "MAMETCHI" "GAETAN"
```

Output:
```
  ✓ "MAMETCHI" → "GAETAN"
Done! File ready to flash: mydump-RENAMED.bin
```

Multiple renames at once:
```bash
python text-editor.py mydump.bin \
  "MAMETCHI" "GAETAN" \
  "HAT IRUKATCHI" "MY CUSTOM HAT" \
  "ROCKY YOUNG" "CHOCOBO"
```

Change language:
```bash
python text-editor.py mydump.bin --language 1 "MAMETCHI" "GAETAN"
```

Languages: 1=EN, 2=FR (default), 3=DE, 4=PT, 5=ES, 6=IT

Custom output file:
```bash
python text-editor.py mydump.bin "MAMETCHI" "GAETAN" -o result.bin
```

## Practical examples

Scenario 1: You want to rename your main character.

With HTML:
1. Open `text-editor.html`
2. Drag your dump
3. Search "MAMETCHI" or filter by that word
4. Click the text and type your new name (max 15c)
5. Download and flash

With Python:
```bash
python text-editor.py mydump.bin "MAMETCHI" "GAETAN"
```

Scenario 2: You want to translate from English to French.

First, view names in English:
```bash
python text-editor.py mydump.bin --language 1 --list
```

Then rename in French (and translate in your language):
```bash
python text-editor.py mydump.bin "ROCKY YOUNG" "JEUNE ROCKY"
```

Scenario 3: You want to rename 10 characters plus 5 objects.

With Python, in one command:
```bash
python text-editor.py mydump.bin \
  "MAMETCHI" "GAETAN" \
  "KUCHIPATCHI" "MARCO" \
  "YOUNG TAMAGOTCHI" "TINY TAM" \
  "HAT IRUKATCHI" "MY HAT" \
  ...
```

With HTML, you modify them one by one, but it's more visual.

## Common problems

Don't save a backup first: always keep one.

Exceeded character limit: HTML editor tells you, but in CLI you need to check with --list.

Unsupported characters (Eastern European accents): script refuses with a clear error.

Checksum forgotten: if you use a third-party tool that doesn't recalculate, firmware won't boot. Script and HTML do it automatically.

Confused about old/new: the order is python text-editor.py dump.bin "OLD" "NEW". Order matters.

## Associated files

| File | Role |
|------|------|
| text-editor.html | Browser interface (archive location, custom charset, checksum recalc) |
| text-editor.py | Python CLI (same functionality as HTML, but command-line) |

Technical notes:

Archive structure:
- Main archive: 0x111000 (ARC2 signature 0x32435241)
- Text archive: found dynamically in main (9 files = 9 languages)
- Each language: binary block with 16-bit null-terminated texts

Charset mapping:
```
0x00FD–0x017A → ASCII (A–Z, 0–9, punctuation)
0x131         → SPACE
0x132–0x13B   → Digits 0–9
0x197, 0x196, 0x199, 0x1AA, 0x178 → É, Ç, Ê, Ñ, '
```

Checksums:
- Sum of content bytes (4 bytes, little-endian)
- Two checksums to recalculate: text archive plus main archive
- The script does this automatically

Language IDs: 1=EN, 2=FR, 3=DE, 4=PT, 5=ES, 6=IT

---

# Editeur de textes — Tamagotchi Paradise

## A quoi ca sert ?

L'editeur de textes te permet de renommer tous les textes du firmware :
- Personnages (MAMETCHI → GAETAN, etc.)
- Objets (CHAPEAU IRUKATCHI → CHAPEAU CUSTOM, etc.)
- Localisations (le script supporte les 6 langues du jeu)

Ce qu'il fait automatiquement :
1. Localise l'archive de textes dans le firmware (elle est relogee selon les versions, le script la cherche)
2. Gere le charset custom (le jeu n'utilise pas l'ASCII : les caracteres ont leurs propres codes)
3. Recalcule les checksums (deux archives ont besoin d'une somme de controle)
4. Produit un firmware pret a flasher

L'interface HTML te montre l'espace disponible (max 15c = 15 caracteres max) et t'empeche de taper trop long. Compared to just using Python CLI, c'est utile.

## Comment on a trouve ?

Le firmware contient une archive standard (format Sonix ARC2 : signature 0x32435241). On l'a localisee a 0x111000 d'abord (adresse connue).

Cette archive principale contient 9 fichiers (les 9 traductions du jeu : EN, FR, DE, PT, ES, IT, plus variantes). Chacune est elle-meme une archive ARC2.

Le jeu n'utilise pas l'ASCII. Les codes sont sur 16 bits (2 octets) et mappent a :
- 0x00FD + ASCII pour A–Z, chiffres, ponctuation
- 0x131 pour l'espace
- 0x132 + n pour les chiffres 0–9
- 0x197, 0x196, 0x199, 0x1AA, 0x178 pour É, Ç, Ê, Ñ, '

Chaque texte = codes 16-bit termines par 0 (null terminator). Les textes sont stockes sequentiellement dans un bloc binaire.

Deux niveaux de checksums :
- Chaque archive ARC2 a un checksum : somme des octets du contenu (4 octets)
- On doit recalculer apres modification

On a change un texte dans l'archive texte, recalcule les checksums, flashe, et verifie sur console.

## Comment s'en servir ?

### Option 1 : Editeur HTML dans le navigateur

Fichier : `text-editor.html`

1. Ouvre `text-editor.html` dans un navigateur
2. Glisse ton dump .bin dessus, ou clique pour choisir
3. Choisis la langue (defaut = Francais, ta console)
4. Liste des textes s'affiche avec :
   - Le texte actuel
   - max 15c = 15 caracteres max pour le remplacer
5. Clique un texte pour le modifier
6. L'editeur t'empeche de taper trop long (affiche le compteur)
7. Telecharge et flashe avec Asprogrammer

Caracteres autorises :
- Lettres A–Z (majuscules obligatoires, le script les force)
- Chiffres 0–9
- Espace
- Accents : É, Ç, Ê, Ñ
- Apostrophe '

Les boutons "É Ç Ê Ñ '" te permettent d'inserer les accents sans clavier special.

### Option 2 : Script Python en ligne de commande

Fichier : `text-editor.py`

Voir tous les noms :
```bash
python text-editor.py mondump.bin --liste
```

Affiche :
```
Noms (langue 2) :

  max 15c : MAMETCHI
  max 18c : CHAPEAU IRUKATCHI
  max 12c : ROCKY YOUNG
  ...
```

Voir seulement les noms contenant un mot :
```bash
python text-editor.py mondump.bin --liste --filtre CHAPEAU
```

Renommer un ou plusieurs noms :
```bash
python text-editor.py mondump.bin "MAMETCHI" "GAETAN"
```

Affiche :
```
  ✓ "MAMETCHI" → "GAETAN"
Termine ! Fichier pret a flasher : mondump-RENOMME.bin
```

Plusieurs renommages d'un coup :
```bash
python text-editor.py mondump.bin \
  "MAMETCHI" "GAETAN" \
  "CHAPEAU IRUKATCHI" "MON CHAPEAU PERSO" \
  "ROCKY YOUNG" "CHOCOBO"
```

Changer de langue :
```bash
python text-editor.py mondump.bin --langue 1 "MAMETCHI" "GAETAN"
```

Langues : 1=EN, 2=FR (defaut), 3=DE, 4=PT, 5=ES, 6=IT

Fichier de sortie personnalise :
```bash
python text-editor.py mondump.bin "MAMETCHI" "GAETAN" -o resultat.bin
```

## Exemples pratiques

Scenario 1 : Tu veux renommer ton personnage principal.

Avec l'HTML :
1. Ouvre `text-editor.html`
2. Glisse ton dump
3. Cherche "MAMETCHI" ou filtre par ce mot
4. Clique le texte et tape ton nouveau nom (max 15c)
5. Telecharge et flashe

Avec Python :
```bash
python text-editor.py mondump.bin "MAMETCHI" "GAETAN"
```

Scenario 2 : Tu veux traduire de l'anglais vers le francais.

D'abord, vois les noms en anglais :
```bash
python text-editor.py mondump.bin --langue 1 --liste
```

Puis renomme en francais (et traduis dans ta langue) :
```bash
python text-editor.py mondump.bin "ROCKY YOUNG" "JEUNE ROCKY"
```

Scenario 3 : Tu veux renommer 10 personnages plus 5 objets.

Avec Python, en une commande :
```bash
python text-editor.py mondump.bin \
  "MAMETCHI" "GAETAN" \
  "KUCHIPATCHI" "MARCO" \
  "YOUNG TAMAGOTCHI" "PETIT TAM" \
  "CHAPEAU IRUKATCHI" "MON CHAPEAU" \
  ...
```

Avec l'HTML, tu les modifies un par un, mais c'est plus visuel.

## Pieges courants

N'oublie pas de faire une sauvegarde avant de tester. Garde toujours une copie.

Depasse le max de caracteres : l'editeur HTML te le dit, mais en CLI tu dois verifier avec --liste.

Caracteres non geres (accents de l'est europeen) : le script refuse avec un message d'erreur clair.

Checksum oublie : si tu utilises un outil tiers qui ne recalcule pas, le firmware ne bootara pas. Le script et l'HTML le font automatiquement.

Confusion ancien/nouveau : l'ordre est python text-editor.py dump.bin "ANCIEN" "NOUVEAU". L'ordre compte.

## Fichiers associes

| Fichier | Role |
|---------|------|
| text-editor.html | Interface navigateur (localisation d'archive, charset custom, recalc checksums) |
| text-editor.py | CLI Python (meme fonctionnalite que HTML, mais ligne de commande) |

Notes techniques :

Structure d'archive :
- Archive principale : 0x111000 (signature ARC2 0x32435241)
- Archive textes : trouvee dynamiquement dans la principale (9 fichiers = 9 langues)
- Chaque langue : bloc binaire avec textes 16-bit null-terminated

Charset mapping :
```
0x00FD–0x017A → ASCII (A–Z, 0–9, ponctuation)
0x131         → SPACE
0x132–0x13B   → Chiffres 0–9
0x197, 0x196, 0x199, 0x1AA, 0x178 → É, Ç, Ê, Ñ, '
```

Checksums :
- Somme des octets du contenu (4 octets, little-endian)
- Deux checksums a recalculer : archive textes plus archive principale
- Le script le fait automatiquement

Language IDs : 1=EN, 2=FR, 3=DE, 4=PT, 5=ES, 6=IT
