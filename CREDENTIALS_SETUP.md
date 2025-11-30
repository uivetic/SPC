# Google Sheets Credentials Setup

## Problem
Aplikacija ne može da se poveže sa Google Sheets jer nedostaje `credentials.json` fajl.

## Rešenje

### Opcija 1: Koristite postojeći credentials.json (ako postoji)

Ako imate `credentials.json` fajl negde na računaru:

1. Kopirajte ga u root folder projekta:
   ```bash
   cp /putanja/do/credentials.json /Users/uros/Desktop/SPC/credentials.json
   ```

2. Proverite da li backend može da ga pronađe:
   ```bash
   cd backend
   ls -la ../credentials.json
   ```

### Opcija 2: Kreirajte novi Service Account (preporučeno)

1. **Idite na Google Cloud Console**
   - https://console.cloud.google.com/
   - Izaberite isti projekat koji koristite za OAuth

2. **Kreirajte Service Account**
   - Idite na "IAM & Admin" > "Service Accounts"
   - Kliknite "+ CREATE SERVICE ACCOUNT"
   - Unesite:
     - Service account name: "spc-sheets-service"
     - Service account ID: automatski se generiše
   - Kliknite "CREATE AND CONTINUE"
   - Preskočite "Grant this service account access to project" (kliknite "CONTINUE")
   - Kliknite "DONE"

3. **Kreirajte JSON Key**
   - Kliknite na kreirani Service Account
   - Idite na tab "KEYS"
   - Kliknite "ADD KEY" > "Create new key"
   - Izaberite "JSON"
   - Kliknite "CREATE"
   - JSON fajl će se automatski downloadovati

4. **Postavite credentials.json**
   - Preimenujte downloadovani fajl u `credentials.json`
   - Premestite ga u `/Users/uros/Desktop/SPC/credentials.json`
   - **VAŽNO:** Ne commit-ujte ovaj fajl u git! (već je u .gitignore)

5. **Dajte pristup Google Sheets dokumentu**
   - Otvorite Google Sheets dokument (ID: `17yR3BJzslf4HLMGTDc0OvzRaY3t7VAZ1-CGx5GxQM_Q`)
   - Kliknite "Share" (gore desno)
   - Dodajte email adresu Service Account-a (nalazi se u `credentials.json` kao `client_email`)
   - Dajte mu "Editor" pristup
   - Kliknite "Send"

### Opcija 3: Koristite postojeći credentials.json iz desktop aplikacije

Ako ste već koristili desktop aplikaciju, možda već imate `credentials.json`:

1. Pronađite gde se nalazi:
   ```bash
   find ~ -name "credentials.json" 2>/dev/null
   ```

2. Kopirajte ga u projekat:
   ```bash
   cp /putanja/do/credentials.json /Users/uros/Desktop/SPC/credentials.json
   ```

## Provera

Nakon postavljanja `credentials.json`:

1. Restartujte backend server
2. Proverite da li API radi:
   - Otvorite http://localhost:8000/docs
   - Testirajte `/api/v1/users` endpoint (zahteva autentifikaciju)
   - Ili testirajte direktno u frontend aplikaciji

## Troubleshooting

### "FileNotFoundError: credentials.json"
- Proverite da li fajl postoji na putanji: `../credentials.json` (relativno od backend foldera)
- Ili promenite putanju u `.env`: `GOOGLE_SHEETS_CREDENTIALS_PATH=/Users/uros/Desktop/SPC/credentials.json`

### "Permission denied" ili "The caller does not have permission"
- Proverite da li je Service Account email dodat u Google Sheets dokument kao Editor
- Proverite da li je Service Account email tačan (iz `credentials.json`)

### "Invalid credentials"
- Proverite da li je `credentials.json` validan JSON fajl
- Proverite da li su svi potrebni polja prisutna (`type`, `project_id`, `private_key_id`, `private_key`, `client_email`, itd.)

