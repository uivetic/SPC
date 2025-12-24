#!/usr/bin/env python3
"""
Konvertuje Service Account JSON fajl u string za environment variable.
Koristi se za Render/produkciju deployment.
"""
import json
import sys
import os

def convert_credentials_to_string(file_path: str) -> str:
    """Konvertuje JSON fajl u string za environment variable"""
    if not os.path.exists(file_path):
        print(f"❌ Fajl ne postoji: {file_path}")
        sys.exit(1)
    
    try:
        with open(file_path, 'r') as f:
            credentials = json.load(f)
        
        # Konvertuj u kompaktan JSON string
        credentials_string = json.dumps(credentials, separators=(',', ':'))
        
        return credentials_string
    except json.JSONDecodeError as e:
        print(f"❌ Greška pri čitanju JSON fajla: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Greška: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Default putanja
    default_path = "service-account-key.json"
    
    # Proveri argumente
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = default_path
    
    # Konvertuj
    credentials_string = convert_credentials_to_string(file_path)
    
    print("✅ Service Account JSON konvertovan u string:")
    print("")
    print("=" * 80)
    print("Kopiraj sledeći tekst i postavi kao GOOGLE_SHEETS_CREDENTIALS na Render:")
    print("=" * 80)
    print(credentials_string)
    print("=" * 80)
    print("")
    print("💡 Napomena: Ovo je osetljiv podatak. Ne deli ga javno!")

