# Tamagotchi Paradise Reverse Engineering

Tools and documentation for modifying Tamagotchi Paradise firmware (Sonix SNC7330).

**Note:** The Python scripts and internal comments are currently in French. I'll get around to translating them one day(tm). The documentation is available in both English and French.

---

Edit unlock codes, rename characters, manage saves, and change the system language—all while automatically handling checksums and encryption.

Everything runs in your browser or via Python CLI. No server, no complicated setup.

## Tools

**Unlock Codes Editor** — Change the 8-digit unlock codes that grant items on the console.
- Browser: `unlock-codes-editor.html` | CLI: `unlock-codes-editor.py` | Docs: [Unlock_codes_editor](Unlock_codes_editor/)

**Text Editor** — Rename characters and objects across all 6 languages. Handles custom charset and checksums automatically.
- Browser: `text-editor.html` | CLI: `text-editor.py` | Docs: [Text_editor](Text_editor/)

**Purge Save Backup** — Clear the backup save slot by filling it with 0xFF bytes.
- CLI: `purge_backup.py` | Docs: [Purge_save_backup](Purge_save_backup/)

**Language Patcher** — Change your save's language setting. English and French confirmed; others pending regional dump comparisons.
- Browser: `language-patcher.html` | Docs: [Language_patcher](Language_patcher/)

**Ghosts Editor** — Manage the 16 ghost save slots.
- Browser: `ghosts-editor.html` | Docs: `DOC_GHOSTS.md` (coming soon)

(Sprite Offset Editor coming soon)

## Getting started

### Browser tools

Open any `.html` file in Chrome, Firefox, or Safari. Drag your firmware dump onto the interface. No installation needed.

### Python tools

Requires Python 3.6+. No external dependencies.

```bash
python unlock-codes-editor.py mydump.bin --list
python text-editor.py mydump.bin "MAMETCHI" "GAETAN"
python purge_backup.py mydump.bin
```

## Hardware

You'll need:
- Asprogrammer or compatible programmer
- MX25L12835F flash chip (16 MB)
- Pogo pins for connecting (soldering optional)

## Current state

Solidly mapped:
- Unlock codes (no checksum, direct modification)
- Character and object names (16-bit charset, CRC-16)
- Save checksum algorithms
- Language field in save (English, French confirmed)

In progress:
- Language codes for German, Spanish, Italian (need regional dumps)
- Sprite composite definition format (needs SWD debugging)
- Additional unlock item names

## Documentation

- [Unlock_codes_editor](Unlock_codes_editor/) — Unlock codes
- [Text_editor](Text_editor/) — Renaming
- [Purge_save_backup](Purge_save_backup/) — Backup cleanup
- [Language_patcher](Language_patcher/) — Language switching
- `DOC_GHOSTS.md` — Ghost management (coming soon)

For reverse engineering details:
- `GUIDE_GHIDRA_Tamagotchi_Paradise.md` — Ghidra workflow with SWD debugging
- `tama_paradise.h` — C structures with validated offsets
- `tama_label_known.py` — Ghidra script for labeling addresses

## Contributing

Have regional firmware dumps? Knowledge about sprites or unlock items? Share it. Dump comparisons are the fastest way to fill in the gaps.

## Disclaimer

These tools modify your console's firmware. Keep backups of your original dumps before trying anything new. Use at your own risk.

---

# Tamagotchi Paradise — Reverse Engineering

Outils et documentation pour modifier le firmware de Tamagotchi Paradise (Sonix SNC7330).

**Note:** Les scripts Python et les commentaires internes sont actuellement en francais. Je prendrai le temps de les traduire un jour(tm). La documentation est disponible en anglais et en francais.

---

Edite les codes de deverrouillage, renomme les personnages, gere les sauvegardes, et change la langue du systeme—tout en gerant automatiquement les checksums et le chiffrement.

Tout fonctionne dans ton navigateur ou via CLI Python. Pas de serveur, pas de configuration compliquee.

## Outils

**Editeur de Codes** — Change les codes de deverrouillage a 8 chiffres qui accordent des objets.
- Navigateur: `unlock-codes-editor.html` | CLI: `unlock-codes-editor.py` | Docs: [Unlock_codes_editor](Unlock_codes_editor/)

**Editeur de Textes** — Renomme les personnages et les objets a travers les 6 langues. Gere le charset custom et les checksums automatiquement.
- Navigateur: `text-editor.html` | CLI: `text-editor.py` | Docs: [Text_editor](Text_editor/)

**Purger le Backup** — Efface le slot de save de backup en le remplissant avec des octets 0xFF.
- CLI: `purge_backup.py` | Docs: [Purge_save_backup](Purge_save_backup/)

**Patcheur de Langue** — Change la langue de ta save. Anglais et francais confirmes ; les autres en attente de comparaisons de dumps regionaux.
- Navigateur: `language-patcher.html` | Docs: [Language_patcher](Language_patcher/)

**Editeur de Ghosts** — Gere les 16 slots de save de fantomes.
- Navigateur: `ghosts-editor.html` | Docs: `DOC_GHOSTS.md` (a venir)

## Bien commencer

### Outils navigateur

Ouvre n'importe quel fichier `.html` dans Chrome, Firefox, ou Safari. Glisse ton dump de firmware sur l'interface. Aucune installation necessaire.

### Outils Python

Necessite Python 3.6+. Aucune dependance externe.

```bash
python unlock-codes-editor.py mondump.bin --liste
python text-editor.py mondump.bin "MAMETCHI" "GAETAN"
python purge_backup.py mondump.bin
```

## Materiel

Tu auras besoin de:
- Asprogrammer ou programmateur compatible
- Puce flash MX25L12835F (16 Mo)
- Pogo pins pour la connexion (soudure optionnelle)

## Etat actuel

Solidement cartographie:
- Codes de deverrouillage (pas de checksum, modification directe)
- Noms de personnages et d'objets (charset 16-bit, CRC-16)
- Algorithmes de checksum de save
- Champ de langue dans la save (anglais, francais confirmes)

En cours:
- Codes de langue pour l'allemand, l'espagnol, l'italien (besoin de dumps regionaux)
- Format des definitions composites de sprites (besoin du debug SWD)
- Noms d'objets de deverrouillage supplementaires

## Documentation

- [Unlock_codes_editor](Unlock_codes_editor/) — Codes de deverrouillage
- [Text_editor](Text_editor/) — Renommage
- [Purge_save_backup](Purge_save_backup/) — Nettoyage du backup
- [Language_patcher](Language_patcher/) — Changement de langue
- `DOC_GHOSTS.md` — Gestion des ghosts (a venir)

Pour les details de reverse engineering:
- `GUIDE_GHIDRA_Tamagotchi_Paradise.md` — Workflow Ghidra avec debug SWD
- `tama_paradise.h` — Structures C avec offsets valides
- `tama_label_known.py` — Script Ghidra pour labelliser les adresses

## Contribuer

Tu as des dumps de firmware regionaux? Des connaissances sur les sprites ou les objets de deverrouillage? Partage-les. Les comparaisons de dumps sont le moyen le plus rapide de combler les lacunes.

## Disclaimer

Ces outils modifient le firmware de ta console. Garde des sauvegardes de tes dumps originaux avant d'essayer quelque chose de nouveau. A utiliser a tes propres risques.
