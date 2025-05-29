from sheetConnection import workbook, normalize_name
import gspread
import re

class SheetCache:
    def __init__(self, sheet):
        self.sheet = sheet
        self.all_values = sheet.get_all_values()
        self.name_to_row = {}
        self.normalized_cells = []  # Cache of normalized words per cell for fast search
        
        # Build name->row index, assume names in column B (index 1)
        for idx, row in enumerate(self.all_values[1:], start=2):
            if len(row) > 1:
                self.name_to_row[row[1]] = idx

        # Pre-normalize all cells once for fast searching
        for row in self.all_values:
            norm_row = []
            for cell in row:
                norm_row.append(set(re.split(r"[ /]+", normalize_name(cell))))
            self.normalized_cells.append(norm_row)

    def find_name_row(self, name):
        return self.name_to_row.get(name)

    def get_cell_value(self, row, col):
        # row,col are 1-based; convert to 0-based for lists
        try:
            return int(self.all_values[row-1][col-1])
        except (IndexError, ValueError):
            return None

    def batch_update_cells(self, updates):
        # updates is list of gspread.Cell objects
        if not updates:
            return
        self.sheet.update_cells(updates)

def find_and_write_cached(item, sheet_cache, name):
    all_values = sheet_cache.all_values
    normalized_cells = sheet_cache.normalized_cells

    if item[1] == 'Aktivacija u godišnjim timovima':
        limit = 50
        dokle = 4
    else:
        limit = 11
        dokle = 3

    result = []

    for i in range(1, dokle):
        found = False
        search_words = set(re.split(r"[ /]+", normalize_name(item[i])))

        if item[0] == 'p':
            start_value = 1 if i == 1 else 3
        else:
            start_value = 2 if i == 1 else 3

        for row_idx in range(start_value, len(all_values)):
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

            row_cells_norm = normalized_cells[row_idx]

            for col_idx in range(start_col, min(start_col + limit + 1, len(row_cells_norm))):
                if search_words.issubset(row_cells_norm[col_idx]):
                    result.append((row_idx, col_idx))
                    found = True
                    break
            if not found:
                result.append("None")

    row = sheet_cache.find_name_row(name)
    if row is None or not result or result[-1] == "None":
        return None
    else:
        return (row, result[-1][1])

def upisi(items, pairs):
    print('opet parovi = ', items, pairs)

    # Preload caches for all relevant sheets ONCE per call
    sheet_names = {
        'o': "2025 Opšte",
        'h': "2025 HR",
        'p': "Projekti"
    }
    sheet_caches = {k: SheetCache(workbook.worksheet(v)) for k,v in sheet_names.items()}

    # Accumulate updates by sheet: {sheet_cache: [gspread.Cell, ...]}
    updates_by_sheet = {cache: [] for cache in sheet_caches.values()}

    for name, points in pairs:
        points_int = None
        try:
            points_int = int(points)
        except:
            print(f"Invalid points for {name}: {points}")
            continue
        for item in items:
            if len(item) == 0:
                continue
            key = item[0]
            if key not in sheet_caches:
                continue
            sheet_cache = sheet_caches[key]

            result = find_and_write_cached(item, sheet_cache, name)
            if result is None:
                print(f"Name {name} not found or item not matched in sheet {sheet_cache.sheet.title}")
                continue
            row, col = result
            current_val = sheet_cache.get_cell_value(row, col+1) or 0  # col+1 to get "next" column value

            new_val = current_val + points_int
            cell = gspread.Cell(row, col+1, value=new_val)
            updates_by_sheet[sheet_cache].append(cell)

    # Batch update all sheets
    for sheet_cache, cells in updates_by_sheet.items():
        if cells:
            try:
                sheet_cache.batch_update_cells(cells)
            except Exception as e:
                print(f"Batch update failed on sheet {sheet_cache.sheet.title}: {e}")
