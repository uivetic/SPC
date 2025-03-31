from sheetConnection import workbook, worksheet_list, normalize_name
import re

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
    all_values = sheet.get_all_values()
    result = []

    for i in range(1, 3):
        found = False
        search_words = set(re.split(r"[ /]+", normalize_name(item[i])))

        # Start from row 1 if i == 1, otherwise start from row 3
        start_value = 1 if i == 1 else 4  

        for row_idx, row in enumerate(all_values[start_value - 1:], start=start_value):
            if found:
                break

            # If there is a previous result, start from that column; otherwise, start from the first column
            start_col = result[0][1] if result else 0  

            for col_idx, cell in enumerate(row[start_col:], start=start_col):  
                cell_words = set(re.split(r"[ /]+", normalize_name(cell)))

                if search_words.issubset(cell_words):
                    result.append((row_idx, col_idx))
                    found = True
                    break
            if not found:
                result.append("None")
            
    return result if result else None

    