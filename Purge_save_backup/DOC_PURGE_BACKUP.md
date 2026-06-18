# Purge Save Backup — Tamagotchi Paradise

## What does it do?

The purge backup tool clears the save backup region in your firmware.

On a real console, when you save your game, Tamagotchi Paradise stores:
- Main save at 0xEFE000 (4 KB)
- Backup save at 0xEFF000 (4 KB) — in case the main save gets corrupted

This tool fills the backup region with 0xFF bytes (the "erased" state in flash memory), effectively clearing any old save data from that backup slot.

Why use it?
- You dumped a console with an old save and want a fresh backup slot
- You're preparing a clean firmware for someone else
- You want to ensure the backup doesn't interfere with your testing

## How we found it

By analyzing Tamagotchi Paradise save structures (CRC validation, decryption), we identified that saves are stored at fixed addresses in the XIP region: 0xEFE000 and 0xEFF000.

In flash memory, "blank" regions are filled with 0xFF bytes. When you erase a sector, all bytes become 0xFF. The firmware treats this as an empty/invalid save.

Unlike renaming (which requires checksum recalculation), simply filling with 0xFF doesn't corrupt anything. The firmware just sees an invalid save and ignores it.

We filled 0xEFF000–0xF00000 with 0xFF, flashed, and confirmed on console that the backup save slot was recognized as empty.

The result: simple, safe, and bulletproof.

## How to use it

File: `purge_backup.py`

Basic usage:
```bash
python purge_backup.py mydump.bin
```

Output:
```
File: mydump.bin (16.0 Mo)
Backup BEFORE: ff000000000000000000000000000000...
Backup AFTER:  ff000000000000000000000000000000...
Backup purged and file saved!

Ready to flash!
```

That's it. The tool:
1. Validates the file is 16 MB
2. Fills 0xEFF000–0xF00000 with 0xFF
3. Saves it in place (overwrites the original file)
4. Shows before/after hex dump so you can verify

On Windows: you can also drag-drop a .bin file onto the script if you have Python installed with file associations set up.

Output location:
- The modified file is saved in the same place as the input file
- No -o option needed. The tool modifies it directly.

## Practical examples

Scenario 1: You just dumped an old console with an old save.

```bash
python purge_backup.py old_console.bin
```

This clears the backup slot so it's clean for your next test.

Scenario 2: You're preparing a firmware dump for a colleague.

```bash
python purge_backup.py clean_firmware.bin
```

Ensures the backup save region doesn't have stale data from your testing.

Scenario 3: You want to keep your main save but clear the backup.

```bash
python purge_backup.py mydump.bin
```

Only the backup at 0xEFF000 is cleared. Your main save at 0xEFE000 is left alone.

## Common problems

Confusing main save and backup save: this tool only clears the backup at 0xEFF000. Your main save at 0xEFE000 is left untouched.

Forgetting to re-flash: after running the tool, you still need to flash the modified firmware to your console with Asprogrammer.

File must be exactly 16 MB: if your dump is incomplete or corrupted, the tool will reject it with a clear error message.

## Associated files

| File | Role |
|------|------|
| purge_backup.py | Python script (validation, fill with 0xFF, save) |

Technical notes:
- Address range: 0xEFF000 to 0xF00000 (4 KB = 0x1000 bytes)
- Fill value: 0xFF (standard flash "erased" state)
- Backup save structure: same as main save (encrypted PRAM, CRC-protected)
- Effect on console: firmware sees the backup slot as empty/invalid and ignores it

---

# Purger le backup — Tamagotchi Paradise

## A quoi ca sert ?

L'outil purge backup efface la region de sauvegarde de secours dans ton firmware.

Sur une vraie console, quand tu sauvegardes ton jeu, Tamagotchi Paradise stocke :
- Save principal a 0xEFE000 (4 Ko)
- Save de secours a 0xEFF000 (4 Ko) — en cas de corruption du save principal

Cet outil remplit la region de secours avec des octets 0xFF (l'etat "efface" en memoire flash), ce qui efface effectivement toutes les anciennes donnees de sauvegarde du slot de secours.

Pourquoi l'utiliser ?
- Tu as dumpe une console avec une vieille save et tu veux un slot de secours vierge
- Tu prepares un firmware propre pour quelqu'un d'autre
- Tu veux t'assurer que le backup n'interfere pas avec tes tests

## Comment on a trouve ?

En analysant les structures de save de Tamagotchi Paradise (validation CRC, dechiffrement), on a identifie que les saves sont stockees a des adresses fixes dans la region XIP : 0xEFE000 et 0xEFF000.

En memoire flash, les regions "vierges" sont remplies d'octets 0xFF. Quand tu effaces un secteur, tous les octets deviennent 0xFF. Le firmware traite ca comme une save vide/invalide.

Contrairement au renommage (qui necessite un recalcul de checksum), remplir avec 0xFF ne corrompt rien. Le firmware voit juste une save invalide et l'ignore.

On a rempli 0xEFF000–0xF00000 avec 0xFF, flashe, et verifie sur console que le slot de save de secours etait reconnu comme vierge.

Le resultat : simple, sur, et infaillible.

## Comment s'en servir ?

Fichier : `purge_backup.py`

Utilisation basique :
```bash
python purge_backup.py mondump.bin
```

Affiche :
```
File: mondump.bin (16.0 Mo)
Backup BEFORE: ff000000000000000000000000000000...
Backup AFTER:  ff000000000000000000000000000000...
Backup purged and file saved!

Ready to flash!
```

C'est tout. L'outil :
1. Valide que le fichier fait 16 Mo
2. Remplit 0xEFF000–0xF00000 avec 0xFF
3. Sauvegarde en place (ecrase le fichier original)
4. Affiche un dump hex avant/apres pour que tu verifies

Sous Windows : tu peux aussi faire un drag-drop d'un fichier .bin sur le script si tu as Python installe avec les associations de fichiers configurees.

Lieu de sortie :
- Le fichier modifie est sauvegarde au meme endroit que le fichier d'entree
- Pas d'option -o necessaire. L'outil le modifie directement.

## Exemples pratiques

Scenario 1 : Tu viens de dumper une vieille console avec une vieille save.

```bash
python purge_backup.py vieille_console.bin
```

Ca efface le slot de secours pour qu'il soit propre pour ton prochain test.

Scenario 2 : Tu prepares un dump de firmware pour un collegue.

```bash
python purge_backup.py firmware_propre.bin
```

Ca s'assure que la region de save de secours n'a pas de donnees perimees de tes tests.

Scenario 3 : Tu veux garder ta save principale mais effacer le backup.

```bash
python purge_backup.py mondump.bin
```

Seul le backup a 0xEFF000 est efface. Ta save principale a 0xEFE000 est laissee seule.

## Pieges courants

Confondre save principale et save de secours : cet outil n'efface que le backup a 0xEFF000. Ta save principale a 0xEFE000 est laissee seule.

Oublier de reflusher : apres avoir lance l'outil, tu dois toujours flasher le firmware modifie sur ta console avec Asprogrammer.

Le fichier doit faire exactement 16 Mo : si ton dump est incomplet ou corrompu, l'outil le rejettera avec un message d'erreur clair.

## Fichiers associes

| Fichier | Role |
|---------|------|
| purge_backup.py | Script Python (validation, remplissage avec 0xFF, sauvegarde) |

Notes techniques :
- Plage d'adresse : 0xEFF000 a 0xF00000 (4 Ko = 0x1000 octets)
- Valeur de remplissage : 0xFF (etat "efface" standard en flash)
- Structure de save de secours : identique a celle de la save principale (PRAM chiffre, protege par CRC)
- Effet sur la console : le firmware voit le slot de secours comme vierge/invalide et l'ignore
