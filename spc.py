import gspread 
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file("credentials.json", scopes = scopes)

client = gspread.authorize(creds)

# Sheet sa prostorima Shared/Bord/XXIII/HR
sheet_id = "1WR7s3ydHrpIIjmLdkuQEeqUxeW6cMXr_NEiLUVluFOY"

workbook = client.open_by_key(sheet_id)

worksheet_list = map(lambda x: x.title, workbook.worksheets())

print(list(worksheet_list))

sheet = workbook.worksheet("Sheet1")
cell = sheet.find("neka")

# Vraca redni broj reda i kolone
print(cell.row, cell.col)
