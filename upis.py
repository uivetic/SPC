from sheetConnection import workbook, worksheet_list, normalize_name


def upisi(items):
    for item in items:
        if len(item):
            if item[0] == 'p':
                resultP = find_and_write(item, workbook.worksheet("Projekti"))
                print(resultP)
            if item[0] == 'h':
                resultH = find_and_write(item, workbook.worksheet("2025 HR"))
            if item[0] == 'o':
                resultO = find_and_write(item, workbook.worksheet("2025 Opšte"))

def find_and_write(item, sheet):
    # Upis i trazenje prvog dropdowna
    all_values = sheet.get_all_values()
    result = []
    for i in range(1, 4):
        found = False
        search_words = set(normalize_name(item[i].lower()).split())  # Split search_value into words

        for row_idx, row in enumerate(all_values, start=1):  # Start from 1 (Google Sheets index)
            if found:
                break
            for col_idx, cell in enumerate(row, start=1):  # Start from 1
                cell_words = set(normalize_name(str(cell).lower()).split())

                if search_words.issubset(cell_words):
                    result.append((row_idx, col_idx))
                    found = True
                    break
            
               
    if len(result):
        return result
    else:
        return None
    