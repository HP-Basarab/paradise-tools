# Biome Patcher — Tamagotchi Paradise

## What does it do?

The biome patcher sets the **starting biome** of a new game on the console.

Tamagotchi Paradise has four biomes: Land, Water, Sky, and Jade Forest. The biome your game starts in is stored as a flag in the firmware. This tool rewrites that flag, recalculates the firmware checksum so the console still boots, and (optionally) wipes the save to force a fresh new game in the chosen biome.

What it does:
1. Reads your firmware dump
2. Lets you pick a starting biome (Land, Water, Sky, Jade)
3. Writes the biome flag and its two associated fields
4. Recalculates the firmware checksum (required for the console to boot)
5. Optionally clears the save (forces a new game)
6. Outputs a modified firmware ready to flash

Why this matters: the firmware is protected by a global additive checksum. If you change the biome byte without fixing it, the console refuses the firmware. This tool handles that automatically.

## How we found it

The biome flag lives at 0xD49000, near the end of the firmware's main data block. By comparing dumps that started in different biomes, we found the byte that selects the biome (1 = Land, 2 = Water, 3 = Sky, 4 = Jade) plus two small fields right before the checksum, at +0xD49FF4 and +0xD49FF6.

Those two fields go together: Land, Water and Sky all use (0x0001, 0x0004), while Jade Forest uses (0x0002, 0x0000). They have to match the selected biome or the game gets confused.

The whole block up to 0xD49FF8 is protected by a checksum. It's a 32-bit value `V` stored at 0xD49FF8 such that `sum(bytes[0 : 0xD49FF8]) + V = 0xFFFFFC03` (a fixed magic constant), with the complement `~V` stored right after at 0xD49FFC. After changing the biome, we recompute `V` from the new byte sum, write both words, flash, and the console boots in the chosen biome.

To start completely fresh, the tool can also fill the save region (0xEFE000–0xF00000) with 0xFF, which the console treats as "no save" and starts a brand new game.

## How to use it

File: `flag_biome_editor.html`

1. Open `flag_biome_editor.html` in any browser (Chrome, Firefox, Safari)
2. Drag your .bin firmware onto it, or click to choose (must be exactly 16 MB)
3. Pick the starting biome: Land, Water, Sky, or Jade Forest
4. Leave "Effacer la sauvegarde" checked to force a fresh new game (recommended), or uncheck it to only change the flag
5. Click "Download the firmware"
6. Download the result and flash it with Asprogrammer

No files are sent anywhere — everything happens in your browser.

The output is named after your choice, e.g. `tamagotchi_biome_4_Jade.bin`.

## Common scenarios

Scenario 1: You want to start a new game directly in Jade Forest.

Load the dump, pick Jade, keep "clear save" checked, download, flash. The console boots into a brand new game in Jade Forest.

Scenario 2: You want to restart fresh in a specific biome.

Same as above with any biome. The "clear save" option wipes your current tamas and progress so the game starts over in the biome you picked.

Scenario 3: You want to change only the biome flag without wiping your save.

Uncheck "clear save". The tool rewrites the flag and fixes the checksum but leaves your save intact. Note this is experimental: a save made in one biome may not fully agree with a different starting flag.

## Common problems

File rejected (not 16 MB): a full Paradise firmware is exactly 16 MB (16,777,216 bytes). A partial dump won't work.

Don't forget to save a backup before testing. Always keep one.

Clear save wipes everything: when "clear save" is checked (the default), your current tamas and progress are erased on purpose to force a new game. Uncheck it if you only want to change the flag.

Save and flag disagree: if you change the biome flag but keep an existing save (clear save unchecked), the game might behave oddly. Clearing the save avoids this.

## Associated files

| File | Role |
|------|------|
| flag_biome_editor.html | Browser interface (set biome flag, recalc firmware checksum, optional save wipe) |

Technical notes:
- Requires a full 16 MB firmware (0x1000000 bytes)
- Biome byte: 0xD49000 (1 = Land, 2 = Water, 3 = Sky, 4 = Jade)
- Flag fields (little-endian u16): +0xD49FF4 and +0xD49FF6 — Land/Water/Sky = (0x0001, 0x0004), Jade = (0x0002, 0x0000)
- Firmware checksum: V at 0xD49FF8 = (0xFFFFFC03 − sum of bytes [0 : 0xD49FF8]) mod 2^32; complement ~V at 0xD49FFC
- Clear save (optional): fills 0xEFE000–0xF00000 with 0xFF

---

# Patcheur de Biome — Tamagotchi Paradise

## A quoi ca sert ?

Le patcheur de biome definit le **biome de depart** d'une nouvelle partie sur la console.

Tamagotchi Paradise a quatre biomes : Terre, Eau, Ciel et Jade Forest. Le biome dans lequel ta partie commence est stocke sous forme de flag dans le firmware. Cet outil reecrit ce flag, recalcule le checksum du firmware pour que la console boote toujours, et (en option) efface la save pour forcer une nouvelle partie dans le biome choisi.

Ce qu'il fait :
1. Lit ton dump de firmware
2. Te laisse choisir un biome de depart (Terre, Eau, Ciel, Jade)
3. Ecrit le flag de biome et ses deux champs associes
4. Recalcule le checksum du firmware (necessaire pour que la console boote)
5. Efface la save en option (force une nouvelle partie)
6. Produit un firmware modifie pret a flasher

Pourquoi ca compte : le firmware est protege par un checksum additif global. Si tu changes le byte de biome sans le corriger, la console refuse le firmware. Cet outil gere ca automatiquement.

## Comment on a trouve ?

Le flag de biome se trouve a 0xD49000, vers la fin du bloc de donnees principal du firmware. En comparant des dumps qui commencaient dans des biomes differents, on a trouve le byte qui selectionne le biome (1 = Terre, 2 = Eau, 3 = Ciel, 4 = Jade) plus deux petits champs juste avant le checksum, a +0xD49FF4 et +0xD49FF6.

Ces deux champs vont ensemble : Terre, Eau et Ciel utilisent tous (0x0001, 0x0004), tandis que Jade Forest utilise (0x0002, 0x0000). Ils doivent correspondre au biome selectionne sinon le jeu s'embrouille.

Tout le bloc jusqu'a 0xD49FF8 est protege par un checksum. C'est une valeur de 32 bits `V` stockee a 0xD49FF8 telle que `somme(octets[0 : 0xD49FF8]) + V = 0xFFFFFC03` (une constante magique fixe), avec le complement `~V` stocke juste apres a 0xD49FFC. Apres avoir change le biome, on recalcule `V` a partir de la nouvelle somme des octets, on ecrit les deux mots, on flashe, et la console boote dans le biome choisi.

Pour repartir completement a zero, l'outil peut aussi remplir la region de save (0xEFE000–0xF00000) avec 0xFF, ce que la console interprete comme "pas de save" et lance une toute nouvelle partie.

## Comment s'en servir ?

Fichier : `flag_biome_editor.html`

1. Ouvre `flag_biome_editor.html` dans n'importe quel navigateur (Chrome, Firefox, Safari)
2. Glisse ton firmware .bin dessus, ou clique pour choisir (doit faire exactement 16 Mo)
3. Choisis le biome de depart : Terre, Eau, Ciel ou Jade Forest
4. Laisse "Effacer la sauvegarde" coche pour forcer une nouvelle partie (recommande), ou decoche-le pour seulement changer le flag
5. Clique "Telecharger le firmware"
6. Telecharge le resultat et flashe-le avec Asprogrammer

Aucun fichier n'est envoye nulle part — tout se fait dans ton navigateur.

La sortie est nommee d'apres ton choix, ex. `tamagotchi_biome_4_Jade.bin`.

## Scenarios courants

Scenario 1 : Tu veux commencer une nouvelle partie directement dans Jade Forest.

Charge le dump, choisis Jade, laisse "effacer la save" coche, telecharge, flashe. La console boote sur une toute nouvelle partie dans Jade Forest.

Scenario 2 : Tu veux recommencer a zero dans un biome precis.

Comme ci-dessus avec n'importe quel biome. L'option "effacer la save" efface tes tamas et ta progression actuels pour que le jeu reparte dans le biome choisi.

Scenario 3 : Tu veux changer seulement le flag de biome sans effacer ta save.

Decoche "effacer la save". L'outil reecrit le flag et corrige le checksum mais laisse ta save intacte. Note que c'est experimental : une save faite dans un biome peut ne pas etre totalement coherente avec un flag de depart different.

## Pieges courants

Fichier refuse (pas 16 Mo) : un firmware Paradise complet fait exactement 16 Mo (16 777 216 octets). Un dump partiel ne marchera pas.

N'oublie pas de faire une sauvegarde avant de tester. Garde toujours une copie.

Effacer la save efface tout : quand "effacer la save" est coche (par defaut), tes tamas et ta progression actuels sont effaces volontairement pour forcer une nouvelle partie. Decoche-le si tu veux seulement changer le flag.

Save et flag incoherents : si tu changes le flag de biome mais gardes une save existante ("effacer la save" decoche), le jeu pourrait se comporter bizarrement. Effacer la save evite ce probleme.

## Fichiers associes

| Fichier | Role |
|---------|------|
| flag_biome_editor.html | Interface navigateur (ecriture du flag de biome, recalc checksum firmware, effacement save optionnel) |

Notes techniques :
- Necessite un firmware complet de 16 Mo (0x1000000 octets)
- Byte de biome : 0xD49000 (1 = Terre, 2 = Eau, 3 = Ciel, 4 = Jade)
- Champs de flag (u16 little-endian) : +0xD49FF4 et +0xD49FF6 — Terre/Eau/Ciel = (0x0001, 0x0004), Jade = (0x0002, 0x0000)
- Checksum firmware : V a 0xD49FF8 = (0xFFFFFC03 − somme des octets [0 : 0xD49FF8]) mod 2^32 ; complement ~V a 0xD49FFC
- Effacer la save (optionnel) : remplit 0xEFE000–0xF00000 avec 0xFF
