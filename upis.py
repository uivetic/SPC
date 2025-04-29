from sheetConnection import workbook, worksheet_list, normalize_name
import gspread
import re

def upisi(items, names):
    for name in names:
        for item in items:
            if len(item):
                if item[0] == 'o':
                    sheet = workbook.worksheet("2025 Opšte")
                    resultO = find_and_write(item, sheet, name)
                    print(resultO)
                    update(resultO[0], resultO[1], resultO[-1], sheet)
                if item[0] == 'h':
                    sheet = workbook.worksheet("2025 HR")
                    resultH = find_and_write(item, sheet, name)
                    print(resultH)
                    update(resultH[0],resultH[1], resultH[-1], sheet)
                if item[0] == 'p':
                    sheet = workbook.worksheet("Projekti")
                    resultP = find_and_write(item, sheet, name)
                    print(resultP)
                    update(resultP[0], resultP[1], resultP[-1], sheet)
            
def find_and_write(item, sheet, name):
    # Get all values from the sheet
    all_values = sheet.get_all_values()
    result = []

    # limit - the longest number of positions for a certain activity
    # eg. JobFair -> 1. CT, 2. SR ..... 11. Logistics team
    if item[1] == 'Aktivacija u godišnjim timovima':
        limit = 50
        dokle = 4
    else:
        limit = 11
        dokle = 3
    
    for i in range(1, dokle):
        found = False

        # Normalize the name and split it into words
        # Use regex to split by spaces or slashes
        # eg. items = ['p', 'BEST design WEEK', 'SR', '4']
        # search_words = {'BEST', 'design', 'WEEK'}
        search_words = set(re.split(r"[ /]+", normalize_name(item[i])))

        if item[0] == 'p':
            start_value = 1 if i == 1 else 3
        else:
            start_value = 2 if i == 1 else 3
        
        for row_idx, row in enumerate(all_values[start_value:], start=start_value):
            if found:
                break
            
            if item[0] == 'o':
                if result:
                    if i == 2:
                        start_col = result[0][1]
                    elif i == 3:
                        start_col = result[1][1]
                    else:
                        start_col = 0
                else:
                    start_col = 0
            else:
                start_col = result[0][1] if result else 0
            for col_idx, cell in enumerate(row[start_col:], start=start_col): 
                # 11 je najduzi broj kolona za neki projekat
                if start_col and col_idx > start_col+limit:
                    break 
                cell_words = set(re.split(r"[ /]+", normalize_name(cell)))
                # if row_idx <=6:
                    # print(search_words, col_idx, row_idx, cell_words)
                if search_words.issubset(cell_words):
                    result.append((row_idx, col_idx))
                    found = True
                    # print('Pronađeno:', search_words, cell_words, col_idx, row_idx)
                    break
            if not found:
                result.append("None")

    try:
        cell = sheet.find(name)
        red = cell.row
        return (red, result[-1][1], int(item[-1]))
    except:
        print("nije nasao")
        return None
def update(row, col, points, sheet):
    print('red, kolona = ', row, col)
    try:
        cell_val = int(sheet.cell(row, col+1).value)
    except:
        cell_val = None
    if cell_val:
        value_to_update = str(cell_val+points)
        sheet.update_cell(row, col+1, value_to_update)
    else:
        print(points)
        value_to_update = str(points)
        print(value_to_update)
        sheet.update_cell(row, col+1, value_to_update)