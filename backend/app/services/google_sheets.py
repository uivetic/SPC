"""Google Sheets service for async operations"""
import gspread
import re
import unicodedata
import json
from typing import List, Dict, Optional, Tuple
from gspread.exceptions import WorksheetNotFound, APIError
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials
from app.config import settings
from app.services.cache_service import cache_service
import asyncio
from functools import lru_cache

# Import roles dictionaries
import sys
import os
# Add parent directory to path to import roles files
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)
try:
    from rolesOpste import rolesOpsteDict, kvartaliGodisnji
    from rolesHR import rolesHRDict
    from rolesProjekti import rolesProjektiDict
except ImportError:
    # Fallback if roles files are not available
    rolesOpsteDict = {}
    rolesHRDict = {}
    rolesProjektiDict = {}
    kvartaliGodisnji = []


def normalize_name(input_str: str) -> str:
    """Normalize name for comparison (uroš -> uros)"""
    if not isinstance(input_str, str):
        return ""
    normalized_str = unicodedata.normalize('NFD', input_str)
    cleaned_str = ''.join([c for c in normalized_str if unicodedata.category(c) != 'Mn'])
    return cleaned_str.lower()


class GoogleSheetsService:
    """Service for Google Sheets operations"""
    
    def __init__(self):
        self._workbook: Optional[gspread.Spreadsheet] = None
        self._client: Optional[gspread.Client] = None
        self._names_cache: Optional[List[str]] = None
        self._normalized_names_cache: Optional[List[str]] = None
    
    async def _get_workbook(self) -> gspread.Spreadsheet:
        """Get or initialize workbook connection"""
        if self._workbook is None:
            await self._initialize_connection()
        return self._workbook
    
    async def _initialize_connection(self):
        """Initialize Google Sheets connection"""
        loop = asyncio.get_event_loop()
        
        def load_credentials():
            # Try to load from environment variable first (for Render/cloud deployment)
            credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
            if credentials_json:
                try:
                    creds_dict = json.loads(credentials_json)
                    return Credentials.from_service_account_info(
                        creds_dict,
                        scopes=settings.GOOGLE_SHEETS_SCOPES
                    )
                except (json.JSONDecodeError, ValueError) as e:
                    raise ValueError(f"Invalid GOOGLE_SHEETS_CREDENTIALS JSON: {e}")
            
            # Fallback to file path (for local development)
            if not os.path.exists(settings.GOOGLE_SHEETS_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Credentials file not found: {settings.GOOGLE_SHEETS_CREDENTIALS_PATH}. "
                    "Either set GOOGLE_SHEETS_CREDENTIALS environment variable or provide a valid file path."
                )
            return Credentials.from_service_account_file(
                settings.GOOGLE_SHEETS_CREDENTIALS_PATH,
                scopes=settings.GOOGLE_SHEETS_SCOPES
            )
        
        creds = await loop.run_in_executor(None, load_credentials)
        client = await loop.run_in_executor(None, gspread.authorize, creds)
        self._client = client
        self._workbook = await loop.run_in_executor(
            None,
            client.open_by_key,
            settings.GOOGLE_SHEETS_ID
        )
    
    async def get_all_names(self) -> List[str]:
        """Get all names from ZBIR sheet"""
        # Check cache first
        cached_names = await cache_service.get("names_list")
        if cached_names:
            self._names_cache = cached_names
            self._normalized_names_cache = [normalize_name(name) for name in cached_names]
            return cached_names
        
        if self._names_cache is not None:
            return self._names_cache
        
        workbook = await self._get_workbook()
        loop = asyncio.get_event_loop()
        
        try:
            sheet = await loop.run_in_executor(None, workbook.worksheet, "ZBIR")
            all_values = await loop.run_in_executor(None, sheet.get_all_values)
            
            names = [row[1] for row in all_values[6:] if len(row) > 1 and isinstance(row[1], str) and row[1]]
            self._names_cache = names
            self._normalized_names_cache = [normalize_name(name) for name in names]
            
            # Cache the result
            await cache_service.set("names_list", names)
            
            return names
        except Exception as e:
            raise Exception(f"Greška pri učitavanju imena: {str(e)}")
    
    async def search_names(self, query: str, limit: int = 10) -> List[str]:
        """Search names with fuzzy matching"""
        names = await self.get_all_names()
        normalized_names = self._normalized_names_cache or [normalize_name(name) for name in names]
        normalized_query = normalize_name(query)
        
        # Substring matches
        substring_matches = [
            name for name, norm_name in zip(names, normalized_names)
            if normalized_query in norm_name
        ]
        
        # Fuzzy matches using simple similarity
        fuzzy_matches = []
        for name, norm_name in zip(names, normalized_names):
            if normalized_query in norm_name or norm_name in normalized_query:
                if name not in substring_matches:
                    fuzzy_matches.append(name)
        
        # Combine and deduplicate
        results = list(dict.fromkeys(substring_matches + fuzzy_matches))
        return results[:limit]
    
    async def write_points(
        self, 
        batch: List[List[str]], 
        pairs: List[List[str]]  # Changed from Tuple to List for JSON compatibility
    ) -> Dict[str, int]:
        """Write points to Google Sheets"""
        workbook = await self._get_workbook()
        loop = asyncio.get_event_loop()
        
        # Determine which sheets are needed
        sheet_names = {
            'o': "2025 Opšte",
            'h': "2025 HR",
            'p': "Projekti"
        }
        
        needed_keys = set()
        for item in batch:
            if item and len(item) > 0:
                key = item[0]
                if key in sheet_names:
                    needed_keys.add(key)
        
        if not needed_keys:
            raise ValueError("Nema podataka za upis")
        
        # Get worksheets
        sheets = {}
        for key in needed_keys:
            sheet_name = sheet_names[key]
            try:
                sheet = await loop.run_in_executor(None, workbook.worksheet, sheet_name)
                sheets[key] = sheet
            except WorksheetNotFound:
                available = await loop.run_in_executor(None, workbook.worksheets)
                available_names = [ws.title for ws in available]
                raise Exception(
                    f"Worksheet '{sheet_name}' ne postoji. "
                    f"Dostupni: {', '.join(available_names)}"
                )
        
        # Load all values
        all_values_cache = {}
        for key, sheet in sheets.items():
            all_values = await loop.run_in_executor(None, sheet.get_all_values)
            all_values_cache[key] = all_values
        
        # Prepare batch updates
        batch_updates = {key: [] for key in sheets.keys()}
        
        for pair in pairs:
            name, points = pair[0], pair[1]
            for item in batch:
                if not item:
                    continue
                
                key = item[0]
                if key not in sheets:
                    continue
                
                sheet = sheets[key]
                all_values = all_values_cache[key]
                
                result = await self._find_and_write(item, sheet, all_values, name, loop)
                if result is None:
                    continue
                
                row, col = result
                try:
                    # Get current cell value
                    cell_val = await loop.run_in_executor(
                        None,
                        lambda: float(sheet.cell(row, col + 1).value) if sheet.cell(row, col + 1).value else 0.0
                    )
                except (ValueError, TypeError):
                    cell_val = 0.0
                
                # Prepare update (as number, not string)
                value_to_update = cell_val + float(points)
                cell_range = rowcol_to_a1(row, col + 1)
                batch_updates[key].append({
                    'range': cell_range,
                    'values': [[value_to_update]]
                })
        
        # Execute batch updates
        for key, updates in batch_updates.items():
            if updates:
                try:
                    await loop.run_in_executor(
                        None,
                        sheets[key].batch_update,
                        updates
                    )
                except APIError as e:
                    raise Exception(f"Greška pri upisu u '{sheet_names[key]}': {str(e)}")
        
        # Invalidate cache
        self._names_cache = None
        await cache_service.delete("names_list")
        await cache_service.invalidate_pattern("points:*")
        
        return {"count": len(pairs)}
    
    async def _find_and_write(
        self, 
        item: List[str], 
        sheet: gspread.Worksheet, 
        all_values: List[List[str]], 
        name: str,
        loop: asyncio.AbstractEventLoop
    ) -> Optional[Tuple[int, int]]:
        """Find position and return (row, col) for writing points"""
        result = []
        
        if item[1] == 'Aktivacija u godišnjim timovima' or item[1] == 'Radne grupe':
            limit = 31
            dokle = 4
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
                            start_col = valid_cols[0] if valid_cols else 0
                        else:
                            start_col = 0
                    else:
                        start_col = 0
                else:
                    start_col = result[0][1] if result and result[0][1] is not None else 0
                
                if item[1] == 'Radne grupe' and i == 2:
                    search_words = set(re.split(r"[ /]+", normalize_name(item[3])))
                
                if result == []:
                    limit = 1000
                
                for col_idx, cell in enumerate(row[start_col:start_col + limit], start=start_col):
                    cell_words = set(re.split(r"[ /]+", normalize_name(cell)))
                    if search_words.issubset(cell_words):
                        result.append((row_idx, col_idx))
                        found = True
                        break
            
            if not found:
                result.append((None, None))
        
        # Find name row
        try:
            cell = await loop.run_in_executor(None, sheet.find, name)
            valid_results = [res for res in result if res[1] is not None]
            if not valid_results:
                return None
            return (cell.row, valid_results[-1][1])
        except Exception:
            return None
    
    async def get_points_for_person(self, name: str) -> Dict[str, str]:
        """Get points for a specific person"""
        # Check cache first
        cache_key = f"points:{name}"
        cached_points = await cache_service.get(cache_key)
        if cached_points:
            return cached_points
        
        workbook = await self._get_workbook()
        loop = asyncio.get_event_loop()
        
        try:
            sheet = await loop.run_in_executor(None, workbook.worksheet, 'ZBIR')
            all_values = await loop.run_in_executor(None, sheet.get_all_values)
            
            name_col_idx = 1
            row_idx = None
            
            # Normalize the search name for comparison
            normalized_search_name = normalize_name(name)
            
            # First, try to find exact match
            for i, row in enumerate(all_values[1:], start=2):
                if len(row) > name_col_idx and row[name_col_idx].strip() == name.strip():
                    row_idx = i
                    break
            
            # If not found, try normalized match
            if row_idx is None:
                for i, row in enumerate(all_values[1:], start=2):
                    if len(row) > name_col_idx:
                        normalized_row_name = normalize_name(row[name_col_idx])
                        if normalized_row_name == normalized_search_name:
                            row_idx = i
                            break
            
            # If still not found, try substring match (like search_names does)
            if row_idx is None:
                for i, row in enumerate(all_values[1:], start=2):
                    if len(row) > name_col_idx:
                        normalized_row_name = normalize_name(row[name_col_idx])
                        if normalized_search_name in normalized_row_name or normalized_row_name in normalized_search_name:
                            row_idx = i
                            break
            
            if row_idx is None:
                raise Exception(f"Osoba '{name}' nije pronađena u bazi")
            
            row_data = all_values[row_idx - 1]
            
            result = {
                'hr': row_data[2] if len(row_data) > 2 else "0",
                'opste': row_data[3] if len(row_data) > 3 else "0",
                'projekti': row_data[4] if len(row_data) > 4 else "0",
                'ukupno': row_data[5] if len(row_data) > 5 else "0",  # Column F: TOTAL (index 5)
                'status': row_data[6] if len(row_data) > 6 else ""    # Column G: STATUS (index 6)
            }
            
            # Cache the result
            await cache_service.set(cache_key, result)
            
            return result
        except Exception as e:
            raise Exception(f"Greška pri čitanju bodova: {str(e)}")
    
    async def get_all_people(self) -> List[Dict[str, str]]:
        """Get list of all people with their points summary"""
        names = await self.get_all_names()
        people = []
        
        for name in names:
            try:
                points = await self.get_points_for_person(name)
                people.append({
                    "name": name,
                    **points
                })
            except Exception:
                continue
        
        return people
    
    async def get_candidates(self, min_points: float, required_status: str = None) -> List[Dict[str, str]]:
        """Get candidates with points above minimum threshold and optional status filter"""
        workbook = await self._get_workbook()
        loop = asyncio.get_event_loop()
        
        try:
            sheet = await loop.run_in_executor(None, workbook.worksheet, 'ZBIR')
            all_values = await loop.run_in_executor(None, sheet.get_all_values)
            
            print(f"\n=== GET_CANDIDATES DEBUG ===")
            print(f"Min points: {min_points}")
            print(f"Required status: {required_status}")
            print(f"Total rows: {len(all_values)}")
            
            # Print first 3 data rows for debugging
            print("\nFirst 3 data rows:")
            for i in range(1, min(4, len(all_values))):
                row = all_values[i]
                print(f"Row {i}: len={len(row)}")
                if len(row) > 7:
                    print(f"  Name (idx 1): {row[1]}")
                    print(f"  Ukupno (idx 6): {row[6]}")
                    print(f"  Status (idx 7): {row[7]}")
            
            candidates = []
            checked_count = 0
            points_pass = 0
            status_pass = 0
            
            # Skip header row (index 0), start from row 1
            for row_data in all_values[1:]:
                if len(row_data) < 2:  # Skip empty rows
                    continue
                
                name = row_data[1].strip() if len(row_data) > 1 else ""
                if not name:  # Skip rows without name
                    continue
                
                checked_count += 1
                
                # Get ukupno points from column 5 (index 5, which is column F)
                try:
                    ukupno_str = row_data[5] if len(row_data) > 5 else "0"
                    # Remove any non-numeric characters except decimal point
                    ukupno_str = ukupno_str.replace(",", ".").strip()
                    ukupno_points = float(ukupno_str) if ukupno_str else 0.0
                except (ValueError, IndexError) as e:
                    print(f"Error parsing points for {name}: {e}")
                    ukupno_points = 0.0
                
                # Get status from column 6 (index 6, which is column G)
                status = row_data[6].strip() if len(row_data) > 6 else ""
                
                # Check if points are above threshold
                if ukupno_points > min_points:
                    points_pass += 1
                    
                    # If status filter is specified, check it (case-insensitive)
                    if required_status is not None:
                        # Handle "N/A" as empty string (since empty cells read as "")
                        status_matches = False
                        if required_status.upper() == "N/A":
                            # For N/A, accept empty string, "N/A", or whitespace
                            status_matches = (not status or status.upper() == "N/A")
                        else:
                            # For other statuses, do exact match
                            status_matches = (status.upper() == required_status.upper())
                        
                        if status_matches:
                            status_pass += 1
                            candidates.append({
                                "name": name,
                                "ukupno": str(ukupno_points),
                                "status": status if status else "N/A"
                            })
                        else:
                            if checked_count <= 5:  # Log first 5 failures
                                print(f"  Status mismatch: {name} has '{status}' (expected '{required_status}')")
                    else:
                        candidates.append({
                            "name": name,
                            "ukupno": str(ukupno_points),
                            "status": status
                        })
            
            print(f"\nStats:")
            print(f"  Checked: {checked_count}")
            print(f"  Points > {min_points}: {points_pass}")
            print(f"  Status match: {status_pass}")
            print(f"  Final candidates: {len(candidates)}")
            print("=========================\n")
            
            # Sort by points descending
            candidates.sort(key=lambda x: float(x["ukupno"]), reverse=True)
            
            return candidates
        except Exception as e:
            print(f"Exception in get_candidates: {e}")
            raise Exception(f"Greška pri čitanju kandidata: {str(e)}")
    
    async def get_activities(self) -> List[Dict]:
        """Get all activities organized by category"""
        categories = []
        
        # Opšte
        if rolesOpsteDict:
            # Remove empty string key if present
            filtered_opste = {k: v for k, v in rolesOpsteDict.items() if k}
            categories.append({
                "category": "o",
                "name": "Opšte",
                "activities": filtered_opste
            })
        
        # HR
        if rolesHRDict:
            filtered_hr = {k: v for k, v in rolesHRDict.items() if k}
            categories.append({
                "category": "h",
                "name": "HR",
                "activities": filtered_hr
            })
        
        # Projekti
        if rolesProjektiDict:
            filtered_projekti = {k: v for k, v in rolesProjektiDict.items() if k}
            categories.append({
                "category": "p",
                "name": "Projekti",
                "activities": filtered_projekti
            })
        
        return categories
    
    async def get_projects(self) -> List[str]:
        """Get list of projects"""
        if rolesProjektiDict:
            return list(rolesProjektiDict.keys())
        return []

