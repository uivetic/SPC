# Google Groups Setup - Automatski pristup za članove grupe

## Pregled

Aplikacija automatski proverava da li je korisnik član Google Groups mailing liste `opsta@best.rs` i daje mu pristup za pregled bodova.

## Setup koraci

### 1. Omogući Google Admin SDK API

1. Idite na [Google Cloud Console](https://console.cloud.google.com/)
2. Odaberite vaš projekat
3. Idite na "APIs & Services" → "Library"
4. Pretražite "Admin SDK API"
5. Kliknite "Enable"

### 2. Omogući Domain-Wide Delegation

1. Idite na [Google Cloud Console](https://console.cloud.google.com/)
2. Odaberite vaš projekat
3. Idite na "APIs & Services" → "Credentials"
4. Pronađite vaš Service Account (onaj koji koristite za Google Sheets)
5. Kliknite na Service Account email
6. Idite na "Advanced settings" → "Domain-wide delegation"
7. Kliknite "Add new" i dodajte:
   - **Client ID**: (ID vašeg Service Account-a)
   - **OAuth scopes**: `https://www.googleapis.com/auth/admin.directory.group.readonly`
8. Sačuvajte

### 3. Dodaj Service Account u Google Workspace Admin

1. Idite na [Google Admin Console](https://admin.google.com/)
2. Idite na "Security" → "API Controls" → "Domain-wide Delegation"
3. Kliknite "Add new"
4. Unesite:
   - **Client ID**: (ID vašeg Service Account-a iz Google Cloud Console)
   - **OAuth Scopes**: `https://www.googleapis.com/auth/admin.directory.group.readonly`
5. Kliknite "Authorize"

### 4. Dodaj GOOGLE_ADMIN_EMAIL u environment variables

**VAŽNO:** Za domain-wide delegation, potrebno je da dodate admin email u environment variables.

1. **Idite na Render Dashboard** → Vaš backend servis → Environment
2. **Dodajte novu varijablu:**
   ```bash
   Key: GOOGLE_ADMIN_EMAIL
   Value: hr@best.rs  # ili bilo koji super admin email
   ```

**Lokalno:**
Dodajte u `backend/.env`:
```bash
GOOGLE_ADMIN_EMAIL=hr@best.rs
```

### 5. Proveri da li je grupa javna ili dozvoljava pristup

1. Idite na [Google Groups](https://groups.google.com/)
2. Pronađite grupu `opsta@best.rs`
3. Proverite da li Service Account email može da vidi članove grupe

## Alternativno rešenje (ako Domain-Wide Delegation ne radi)

Ako setup Domain-Wide Delegation nije moguć, možete ručno dodati Gmail emailove u `ALLOWED_VIEW_EMAILS` listu u `backend/app/config.py`:

```python
ALLOWED_VIEW_EMAILS: list[str] = [
    "uros.ivetic@gmail.com",
    "drugi.email@gmail.com",
    # ... dodajte ostale emailove
]
```

## Testiranje

Nakon setup-a, testirajte:

1. Prijavite se sa Gmail emailom koji je član `opsta@best.rs` grupe
2. Trebalo bi da imate pristup za pregled bodova
3. Ne biste trebalo da imate pristup za unos bodova (osim ako niste u `ALLOWED_WRITE_EMAILS`)

## Troubleshooting

### Greška: "403 Forbidden" ili "Insufficient Permission"

**Rešenje:**
- Proverite da li je Admin SDK API omogućen
- Proverite da li je Domain-Wide Delegation pravilno podešen
- Proverite da li su OAuth scopes tačno dodati

### Greška: "404 Not Found" za grupu

**Rešenje:**
- Proverite da li je `GOOGLE_GROUP_EMAIL` tačno postavljen na `opsta@best.rs`
- Proverite da li grupa postoji u Google Workspace

### API ne vraća rezultate

**Rešenje:**
- Proverite da li je Service Account email dodat u Google Workspace Admin Console
- Proverite da li su OAuth scopes tačno dodati
- Proverite logove za detaljne greške

## Napomena

- Provera članstva u grupi se cache-uje na 1 sat da bi se smanjio broj API poziva
- Ako Google Groups API ne radi, aplikacija automatski dozvoljava sve `@best.rs` emailove kao fallback
- Za production, preporučeno je da se koristi Redis cache za bolje performanse

