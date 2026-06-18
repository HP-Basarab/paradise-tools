#!/usr/bin/env python3
"""
purge_backup.py — Tamagotchi Paradise Firmware
Remplace 0xEFF000–0xF00000 (4 Ko) par 0xFF et sauvegarde en place.
Usage: drag-drop un fichier .bin sur ce script (Windows) ou passe-le en argument (cli).
"""

import sys
import os
import struct
from pathlib import Path

def purge_backup(firmware_path):
    """Purifie le backup de save et remplace le fichier en place."""
    
    # Validation fichier
    if not os.path.exists(firmware_path):
        print(f"Fichier introuvable: {firmware_path}")
        return False
    
    if not firmware_path.lower().endswith('.bin'):
        print(f"Le fichier doit être un .bin (reçu: {os.path.basename(firmware_path)})")
        return False
    
    file_size = os.path.getsize(firmware_path)
    if file_size != 0x1000000:  # 16 Mo
        print(f"Taille incorrecte: {file_size} octets (attendu: {0x1000000})")
        return False
    
    print(f"File: {os.path.basename(firmware_path)} ({file_size / (1024*1024):.1f} Mo)")
    
    # Charger le firmware
    with open(firmware_path, 'rb') as f:
        data = bytearray(f.read())
    
    # Vérifier l'état avant
    backup_start = 0xEFF000
    backup_end = 0xF00000
    current_state = data[backup_start:backup_start+16]
    print(f"Backup BEFORE: {current_state.hex()[:32]}...")
    
    # Purifier (remplir avec 0xFF)
    data[backup_start:backup_end] = b'\xFF' * (backup_end - backup_start)
    
    # Vérifier l'état après
    new_state = data[backup_start:backup_start+16]
    print(f"Backup AFTER:  {new_state.hex()[:32]}...")
    
    # Sauvegarder en place
    with open(firmware_path, 'wb') as f:
        f.write(data)
    
    print(f"Backup purged and file saved!")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python purge_backup.py <fichier.bin>")
        print("Or: drag-drop a .bin onto this script (Windows)")
        sys.exit(1)
    
    firmware_file = sys.argv[1]
    success = purge_backup(firmware_file)
    
    if not success:
        sys.exit(1)
    
    print("\nReady to flash!")
