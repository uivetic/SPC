from sheetConnection import workbook, worksheet_list, normalize_name
import gspread
import re

def upisi(items, pairs):
    print(pairs)
    print('opet parovi = ', items, pairs)

    sheets = {
        'o': workbook.worksheet("2025 Opšte"),
        'h': workbook.worksheet("2025 HR"),
        'p': workbook.worksheet("Projekti"),
    }

    all_values_cache = {
        key: sheet.get_all_values()
        for key, sheet in sheets.items()
    }

    for name, points in pairs:
        for item in items:
            if not item:
                continue
            key = item[0]
            if key in sheets:
                sheet = sheets[key]
                all_values = all_values_cache[key]
                result = find_and_write(item, sheet, all_values, name)
                if result is None:
                    print(f"Greska prilikom pronalaska pozicije za osobu {name}!")
                    continue
                try:
                    update(result[0], result[1], float(points), sheet)
                except Exception as e:
                    print(f"Greska prilikom upisivanja bodova za osobu {name}: {e}")

def find_and_write(item, sheet, all_values, name):
    result = []

    if item[1] == 'Aktivacija u godišnjim timovima' or 'Radne grupe':
        limit = 31  # koliko polja na desno maksimalno moze da se trazi neka vrednost
        dokle = 4   # koliko itema se uzima
    else:
        limit = 11
        dokle = 3
    for i in range(1, dokle):
        found = False
        search_words = set(re.split(r"[ /]+", normalize_name(item[i])))
        if item[0] == 'p':
            start_value = 1 if i == 1 else 3
        else:
            start_value = 2 if i == 1 else 3 if i == 2 else 4

        for row_idx, row in enumerate(all_values[start_value:], start=start_value):
            if found:
                break
            if item[0] == 'o':
                if result:
                    if i in [2, 3]:
                        valid_cols = [col for _, col in reversed(result) if col is not None]
                        start_col = valid_cols[0] if valid_cols else 0 #uzima poslednju ne null vrednost iz resulta, npr [(2,55), (Null, Null)] -> 55
                    else:
                        start_col = 0
                else:
                    start_col = 0
            else:
                start_col = result[0][1] if result and result[0][1] is not None else 0
            
            if item[1] == 'Radne grupe' and i == 2:
                search_words = set(re.split(r"[ /]+", normalize_name(item[3])))
                #ovih specijalnih slucajeva ima pun kurac
            for col_idx, cell in enumerate(row[start_col:], start=start_col):
                if start_col and col_idx > start_col + limit:
                    break
                cell_words = set(re.split(r"[ /]+", normalize_name(cell)))
                if search_words.issubset(cell_words):
                    result.append((row_idx, col_idx))
                    found = True
                    break

        if not found:
            result.append((None, None))
    try:
        cell = sheet.find(name)
        valid_results = [res for res in result if res[1] is not None]
        print("rezultat = ", result)
        if not valid_results:
            print(f"Pozicija nije pronađena za osobu {name}")
            return None
        return (cell.row, valid_results[-1][1])
    except:
        print(f"Osoba {name} nije pronađena u sheetu.")
        return None

def update(row, col, points, sheet):
    print('red, kolona = ', row, col)
    try:
        cell_val = float(sheet.cell(row, col + 1).value)
    except:
        cell_val = None

    value_to_update = str(cell_val + points) if cell_val else str(points)
    sheet.update_cell(row, col + 1, value_to_update)
