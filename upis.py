from sheetConnection import workbook, worksheet_list, normalize_name
import re

def upisi(items):
    for item in items:
        if len(item):
            if item[0] == 'o':
                resultO = find_and_write_opste(item, workbook.worksheet("2025 Opšte"))
                print(resultO)
            if item[0] == 'h':
                resultH = find_and_write_hr(item, workbook.worksheet("2025 HR"))
                print(resultH)
            if item[0] == 'p':
                resultP = find_and_write_projekti(item, workbook.worksheet("Projekti"))
                print(resultP)


def find_and_write_projekti(item, sheet):

    # Get all values from the sheet
    all_values = sheet.get_all_values()
    result = []

    for i in range(1, 3):
        found = False

        # Normalize the name and split it into words
        # Use regex to split by spaces or slashes
        # eg. items = ['p', 'BEST design WEEK', 'SR', '4']
        # search_words = {'BEST', 'design', 'WEEK'}
        search_words = set(re.split(r"[ /]+", normalize_name(item[i])))
        if search_words.__contains__('p'):
            if search_words.__contains__('pr') and search_words.__contains__('tim'):
                word = 'pr'
                search_words = {word}
            if search_words.__contains__('fr') and search_words.__contains__('tim'):
                word = 'fr'
                search_words = {word}
            if search_words.__contains__('it') and search_words.__contains__('asistent'):
                word = 'it'
                search_words = {word}
            if search_words.__contains__('pub') and search_words.__contains__('asistent'):
                word = 'pub'
                search_words = {word}

        # print('search words = ', search_words)
        start_value = 1 if i == 1 else 3  

        for row_idx, row in enumerate(all_values[start_value:], start=start_value):
            if found:
                break
                
            # print(row_idx, row)
            # If there is a previous result, start from that column; otherwise, start from the first column
            # print(result)
            start_col = result[0][1] if result else 0  

            for col_idx, cell in enumerate(row[start_col:], start=start_col): 
                # 11 je najduzi broj kolona za neki projekat
                if start_col and col_idx > start_col+11:
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
            
    return result if result else None


def find_and_write_hr(item, sheet):

    # Get all values from the sheet
    all_values = sheet.get_all_values()
    result = []

    for i in range(1, 3):
        found = False

        # Normalize the name and split it into words
        # Use regex to split by spaces or slashes
        # eg. items = ['p', 'BEST design WEEK', 'SR', '4']
        # search_words = {'BEST', 'design', 'WEEK'}
        search_words = set(re.split(r"[ /-]+", normalize_name(item[i])))
        if search_words.__contains__('diskusiona') and search_words.__contains__('grupa'):
            word = 'diskusiona'
            search_words = {word}

        # print('search words = ', search_words)
        start_value = 2 if i == 1 else 3

        for row_idx, row in enumerate(all_values[start_value:], start=start_value):
            if found:
                break
                
            # print(row_idx, row)
            # If there is a previous result, start from that column; otherwise, start from the first column
            # print(result)
            start_col = result[0][1] if result else 0  

            for col_idx, cell in enumerate(row[start_col:], start=start_col): 
                # 11 je najduzi broj kolona za neki projekat
                if start_col and col_idx > start_col+11:
                    break 
                cell_words = set(re.split(r"[ /-]+", normalize_name(cell)))
                # if row_idx <=6:
                    # print(search_words, col_idx, row_idx, cell_words)
                if search_words.issubset(cell_words):
                    result.append((row_idx, col_idx))
                    found = True
                    # print('Pronađeno:', search_words, cell_words, col_idx, row_idx)
                    break
            if not found:
                result.append("None")
            
    return result if result else None


def find_and_write_opste(item, sheet):

    # Get all values from the sheet
    all_values = sheet.get_all_values()
    result = []
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

        # print('search words = ', search_words)
        start_value = 2 if i == 1 else 3 

        for row_idx, row in enumerate(all_values[start_value:], start=start_value):
            if found:
                break
                
            # print(row_idx, row)
            # If there is a previous result, start from that column; otherwise, start from the first column
            # print(result)
            if result:
                if i == 2:
                    start_col = result[0][1]
                elif i == 3:
                    start_col = result[1][1]
                else:
                    start_col = 0
            else:
                start_col = 0
            #start_col = result[0][1] if result else 0  

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
            
    return result if result else None