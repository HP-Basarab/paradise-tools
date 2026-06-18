# Language Patcher — Tamagotchi Paradise

## What does it do?

The language patcher changes the language of your save on the console.

When you save a game in Tamagotchi Paradise, the firmware stores your language preference in the encrypted save region. If you dump a console that was set to English and want to change it to French, this tool rewrites that language byte and recalculates the CRC checksum so the console accepts the modified save.

What it does:
1. Reads your firmware dump
2. Detects the current language of your save
3. Lets you pick a new language
4. Recalculates the CRC-16 checksum (required for the save to be valid)
5. Outputs a modified firmware ready to flash

Why this matters: the console validates every save with a CRC. If you just change the language byte, the checksum becomes invalid and the console rejects the save. This tool handles that automatically.

## Current state

For now, we've only mapped English and French with certainty. The other languages (German, Spanish, Italian) are shown in the interface as available, but we haven't confirmed their codes yet by comparing actual dumps.

The plan is to gather more dumps from different regional consoles and compare them to identify the exact codes for each language. If you have dumps from other regions, comparing them will help complete the map.

## How we found it

The save is stored encrypted in PRAM at 0x1000–0x10FFF (64 KB). We decrypted it using AES-256 CBC with the device key 0x5aaf34fb.

The language field is stored as a single byte somewhere in the decrypted save. By comparing dumps from English and French consoles, we found the offset and confirmed: English = 0x04, French = 0x06.

To verify the checksum, we calculated CRC-16 (Rocksoft polynomial) over the entire decrypted save. When the checksum matches, the console accepts the save. We confirmed this on hardware.

The remaining languages (German, Spanish, Italian, and the mystery "Index" slots) haven't been verified yet. We know they exist in the UI because the game supports 9 language tables in the text archive, but without dumps from those regional variants, we can't confirm their codes.

## How to use it

File: `language-patcher.html`

1. Open `patcheur_langue.html` in a browser
2. Drag your .bin firmware onto it, or click to choose
3. The tool detects your current language and validates the save checksum
4. Select a new language from the dropdown (EN and FR are confirmed; others are experimental)
5. Click "Generate patched firmware"
6. Download the result and flash it with Asprogrammer

The tool shows status badges:
- Green "OK" means the checksum is valid
- Orange "WARN" means the language is untested
- Red "ERR" means something went wrong

Example output log:
```
Loading firmware...
Found save at 0xEFE000
Decrypting save (AES-256 CBC)...
Current language: EN (0x04)
CRC-16 valid
Patching to FR (0x06)...
Recalculating CRC-16...
Done! Download ready.
```

## Common scenarios

Scenario 1: You dumped a console in English and want to change it to French.

Load the dump, select French from the dropdown, generate, flash.

Scenario 2: You want to test what happens with an unknown language code.

You can try any of the "Index" slots (0x00–0x03), but be aware the console might not recognize them or might crash. Good for experimentation on a console you don't mind testing.

Scenario 3: You have a dump from a German console and want to help identify the language code.

Compare your German dump with a known English dump. Look for where they differ in the decrypted save. The byte that differs from English is probably the language field. Report it and we can add it to the map.

## Common problems

Language shows as untested: the tool will still patch it, but the console might not recognize it. Only EN and FR are confirmed to work.

Checksum shows invalid: your dump might be corrupted, or the save was never valid on the console. Try a fresh dump if possible.

Console rejects the patched save: make sure you flashed with the correct programmer settings and that the flash chip is properly connected.

## Associated files

| File | Role |
|------|------|
| patcheur_langue.html | Browser interface (decrypt, detect language, recalc CRC, output) |

Technical notes:

Save structure:
- Encrypted at 0xEFE000 (4 KB = main save, 0xEFF000 = backup)
- AES-256 CBC encryption with device key 0x5aaf34fb
- CRC-16 Rocksoft polynomial over entire decrypted save

Language field:
- Confirmed: EN = 0x04, FR = 0x06
- Untested: DE (0x05?), ES (0x07?), IT (0x08?), and Index 0–3

Next steps for other languages:
- Need to compare dumps from German, Spanish, Italian regional consoles
- Extract decrypted saves and identify the language byte
- Confirm CRC calculation still works

---

# Patcheur de Langue — Tamagotchi Paradise

## A quoi ca sert ?

Le patcheur de langue change la langue de ta save sur la console.

Quand tu sauvegardes un jeu dans Tamagotchi Paradise, le firmware stocke ta preference de langue dans la region de save chiffree. Si tu as dumpe une console qui etait reglée en anglais et que tu veux la changer en francais, cet outil reedrit ce byte de langue et recalcule le checksum CRC pour que la console accepte la save modifiee.

Ce qu'il fait :
1. Lit ton dump de firmware
2. Detecte la langue actuelle de ta save
3. Te laisse choisir une nouvelle langue
4. Recalcule le checksum CRC-16 (necessaire pour que la save soit valide)
5. Produit un firmware modifie pret a flasher

Pourquoi ca compte : la console valide chaque save avec un CRC. Si tu changes juste le byte de langue, le checksum devient invalide et la console rejette la save. Cet outil gere ca automatiquement.

## Etat actuel

Pour l'instant, on a seulement cartographie l'anglais et le francais avec certitude. Les autres langues (allemand, espagnol, italien) sont affichees dans l'interface comme disponibles, mais on n'a pas confirme leurs codes en comparant des dumps reels.

Le plan est de rassembler plus de dumps de consoles differentes par region et de les comparer pour identifier les codes exacts de chaque langue. Si tu as des dumps d'autres regions, les comparer aidera a completer la carte.

## Comment on a trouve ?

La save est stockee chiffree dans la PRAM a 0x1000–0x10FFF (64 Ko). On l'a dechiffre en utilisant AES-256 CBC avec la cle du dispositif 0x5aaf34fb.

Le byte de langue est stocke quelque part dans la save dechiffree. En comparant des dumps de consoles en anglais et en francais, on a trouve l'offset et confirme : Anglais = 0x04, Francais = 0x06.

Pour verifier le checksum, on a calcule CRC-16 (polynome Rocksoft) sur toute la save dechiffree. Quand le checksum correspond, la console accepte la save. On a confirme ca sur materiel.

Les langues restantes (allemand, espagnol, italien, et les slots "Index" mysterieux) n'ont pas ete verifiees. On sait qu'elles existent dans l'UI parce que le jeu supporte 9 tables de texte, mais sans dumps des variantes regionales, on ne peut pas confirmer leurs codes.

## Comment s'en servir ?

Fichier : `language-patcher.html`

1. Ouvre `patcheur_langue.html` dans un navigateur
2. Glisse ton firmware .bin dessus, ou clique pour choisir
3. L'outil detecte ta langue actuelle et valide le checksum de la save
4. Selectionne une nouvelle langue dans le menu deroulant (EN et FR sont confirmes ; les autres sont experimentales)
5. Clique "Generer le firmware patche"
6. Telecharge le resultat et flashe-le avec Asprogrammer

L'outil affiche des badges de statut :
- Vert "OK" signifie que le checksum est valide
- Orange "WARN" signifie que la langue n'a pas ete testee
- Rouge "ERR" signifie que quelque chose s'est mal passe

Exemple de log de sortie :
```
Loading firmware...
Found save at 0xEFE000
Decrypting save (AES-256 CBC)...
Current language: EN (0x04)
CRC-16 valid
Patching to FR (0x06)...
Recalculating CRC-16...
Done! Download ready.
```

## Scenarios courants

Scenario 1 : Tu as dumpe une console en anglais et tu veux la changer en francais.

Charge le dump, selectionne le francais dans le menu, genere, flashe.

Scenario 2 : Tu veux tester ce qui se passe avec un code de langue inconnu.

Tu peux essayer n'importe quel slot "Index" (0x00–0x03), mais sache que la console pourrait ne pas le reconnaitre ou pourrait planter. Bon pour l'experimentation sur une console que tu ne crains pas de tester.

Scenario 3 : Tu as un dump d'une console allemande et tu veux aider a identifier le code de langue.

Compare ton dump allemand avec un dump anglais connu. Cherche ou ils different dans la save dechiffree. Le byte qui differe de l'anglais est probablement le byte de langue. Signale-le et on peut l'ajouter a la carte.

## Pieges courants

La langue s'affiche comme non-testee : l'outil va quand meme la patcher, mais la console pourrait ne pas la reconnaitre. Seuls EN et FR sont confirmes comme fonctionnant.

Le checksum s'affiche comme invalide : ton dump pourrait etre corrompu, ou la save n'a jamais ete valide sur la console. Essaie un dump recent si possible.

La console rejette la save patchee : assure-toi que tu as flashe avec les parametres corrects du programmateur et que la puce flash est bien connectee.

## Fichiers associes

| Fichier | Role |
|---------|------|
| patcheur_langue.html | Interface navigateur (dechiffrement, detection de langue, recalc CRC, sortie) |

Notes techniques :

Structure de la save :
- Chiffree a 0xEFE000 (4 Ko = save principale, 0xEFF000 = backup)
- Chiffrement AES-256 CBC avec la cle du dispositif 0x5aaf34fb
- CRC-16 polynome Rocksoft sur toute la save dechiffree

Byte de langue :
- Confirme : EN = 0x04, FR = 0x06
- Non-teste : DE (0x05?), ES (0x07?), IT (0x08?), et Index 0–3

Prochaines etapes pour les autres langues :
- Besoin de comparer des dumps de consoles regionales allemande, espagnole, italienne
- Extraire les saves dechiffrees et identifier le byte de langue
- Confirmer que le calcul CRC fonctionne toujours
