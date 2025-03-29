import os
import sys
import gspread 
import unicodedata
from google.oauth2.service_account import Credentials

# resava qt.qpa.wayland: Wayland does not support QWindow::requestActivate()
if sys.platform.startswith("linux"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"


#Normalize name comparison, uroš -> uros
def normalize_name(input_str):

    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join([c for c in normalized_str if unicodedata.category(c) != 'Mn'])

# Google cloud API
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

# Connection with spreadsheet using email in credentials json and authorization
creds = Credentials.from_service_account_file("../credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# Opening sheet by Sheet ID
sheet_id = "1UMMIeubY1-v5AKrXXiCf9TOQjBgNjOfzeqvelGMEPbA"
workbook = client.open_by_key(sheet_id)

worksheet_list = map(lambda x: x.title, workbook.worksheets())
#print(list(worksheet_list))

sheet = workbook.worksheet("ZBIR")
all_values = sheet.get_all_values()

# Extracting all names in ZBIR sub-sheet
names_list = [row[1] for row in all_values[6:] if isinstance(row[1], str)]
