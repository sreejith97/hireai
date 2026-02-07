import openpyxl
from io import BytesIO
from typing import List, Dict, Any
import json

def parse_employee_excel(file_content: bytes) -> List[Dict[str, Any]]:
    """
    Parses an Excel file containing employee details.
    Expected columns: Name, Role, Email, Salary, Start Date, Nationality, Passport Number, Employee ID
    """
    workbook = openpyxl.load_workbook(filename=BytesIO(file_content), data_only=True)
    sheet = workbook.active
    
    employees = []
    headers = {}
    
    # Iterate through rows
    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        if i == 0:
            # Header row
            for col_idx, cell_value in enumerate(row):
                if cell_value:
                    headers[col_idx] = str(cell_value).strip().lower()
            continue
            
        # Data rows
        employee_map = {}
        additional_map = {}
        has_data = False
        
        # Temp storage for name parts
        first_name = ""
        last_name = ""
        
        for col_idx, cell_value in enumerate(row):
            if col_idx in headers:
                header = headers[col_idx]
                val = str(cell_value) if cell_value is not None else None
                
                if val:
                    has_data = True
                
                # Cleanup specific characters from money like '$' or ','
                if "salary" in header and val:
                     val = val.replace("$", "").replace(",", "")
                
                # Check known headers
                if header in ["employee id", "id", "emp_id"]:
                    employee_map["employee_id"] = val
                elif header in ["first name", "firstname"]:
                    first_name = val
                elif header in ["last name", "lastname"]:
                    last_name = val
                elif header in ["job title", "role", "position", "designation"]:
                    employee_map["role"] = val
                elif header in ["email", "email address"]:
                    employee_map["email"] = val
                elif header in ["salary (monthly)", "salary", "gross salary", "monthly salary"]:
                    employee_map["salary"] = val
                elif header in ["date of joining", "joining date", "start date"]:
                    # Ensure date format is string or ISO? openpyxl returns datetime objects often
                    if hasattr(cell_value, 'isoformat'):
                         employee_map["start_date"] = cell_value.strftime("%Y-%m-%d")
                    else:
                         employee_map["start_date"] = val
                elif header in ["country", "nationality"]:
                    employee_map["nationality"] = val
                elif header in ["passport number", "passport no"]:
                    employee_map["passport_number"] = val
                else:
                    # Store other columns
                    if val:
                         # Use original header string for key or capitalized? 
                         # Let's simple use Title Case for key display
                         key_display = header.replace("_", " ").title()
                         additional_map[key_display] = val

        # Construct full name
        if first_name or last_name:
             full_name = f"{first_name or ''} {last_name or ''}".strip()
             employee_map["name"] = full_name
        
        if has_data and employee_map.get("name"):
            employee_map["additional_data"] = json.dumps(additional_map)
            employees.append(employee_map)
            
    return employees

def parse_employee_csv(file_content: bytes) -> List[Dict[str, Any]]:
    """
    Parses a CSV file containing employee details.
    """
    import csv
    from io import StringIO
    
    content_str = file_content.decode("utf-8")
    f = StringIO(content_str)
    reader = csv.DictReader(f)
    
    employees = []
    
    for row in reader:
        # Normalize keys (strip, lower)
        clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        
        emp = {}
        additional = {}
        
        # Mapping
        # Note: CSV keys match exact header text usually
        
        # ID
        if "employee id" in clean_row: emp["employee_id"] = clean_row["employee id"]
        elif "id" in clean_row: emp["employee_id"] = clean_row["id"]
        
        # Name
        fname = clean_row.get("first name", "")
        lname = clean_row.get("last name", "")
        if fname or lname:
             emp["name"] = f"{fname} {lname}".strip()
        elif "name" in clean_row:
             emp["name"] = clean_row["name"]
             
        # Role
        if "job title" in clean_row: emp["role"] = clean_row["job title"]
        elif "role" in clean_row: emp["role"] = clean_row["role"]
        
        # Email
        if "email" in clean_row: emp["email"] = clean_row["email"]
        
        # Start Date
        if "date of joining" in clean_row: emp["start_date"] = clean_row["date of joining"]
        
        # Collect others
        
        if emp.get("name"):
             employees.append(emp)
             
    return employees
