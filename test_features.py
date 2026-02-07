import requests
import json
import io
import openpyxl
from datetime import datetime

BASE_URL = "http://localhost:8000"

def create_dummy_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Name", "Role", "Email", "Salary", "Start Date", "Nationality", "Passport Number"])
    ws.append(["Alice Smith", "Designer", "alice@example.com", "20000", "2024-06-01", "UK", "P123456"])
    ws.append(["Bob Jones", "Manager", "bob@example.com", "35000", "2024-07-01", "USA", "A987654"])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def test_new_features():
    print("🚀 Starting Excel & PDF Test Flow...")
    
    # 1. Upload Employee Excel
    print("\n--- 1. Uploading Employee Excel ---")
    excel_file = create_dummy_excel()
    files = {'file': ('employees.xlsx', excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    
    response = requests.post(f"{BASE_URL}/employees/upload_excel", files=files)
    if response.status_code != 200:
        print(f"❌ Excel Upload Failed: {response.status_code}")
        print(response.text)
        return
        
    print("✅ Excel Uploaded")
    print(json.dumps(response.json(), indent=2))
    
    # 2. List Employees
    print("\n--- 2. Listing Employees ---")
    response = requests.get(f"{BASE_URL}/employees")
    employees = response.json()
    print(f"✅ Retrieved {len(employees)} employees")
    if len(employees) > 0:
        print("Sample Employee:", employees[0])

    # 3. Generate Employment Contract (using existing method for setup)
    # We need a legal contract ID first. 
    # Assumption: A legal contract draft exists from previous tests or we create one.
    # Let's try to create one quick if we can, or reuse if we stored it (we didn't store it persistently in this script).
    # So we'll try to generate a new legal contract draft first.
    print("\n--- 3. Preparing Contract for PDF Generation ---")
    
    # Needs valid clauses in DB. Assuming DB state is preserved from previous run.
    # If not, this might fail, but let's try.
    payload = {"company_id": "TechCorp", "country": "UAE"}
    response = requests.post(f"{BASE_URL}/contracts/generate/legal", json=payload)
    
    if response.status_code == 200:
        legal_contract_id = response.json().get("legal_contract_id")
        
        # Generate final
        payload_final = {
            "legal_contract_id": legal_contract_id,
            "candidate": {
                "name": "Alice Smith",
                "role": "Designer",
                "salary": "20000",
                "start_date": "2024-06-01"
            }
        }
        resp_final = requests.post(f"{BASE_URL}/contracts/generate/employment", json=payload_final)
        if resp_final.status_code == 200:
            employment_contract_id = resp_final.json().get("employment_contract_id")
            
            # 4. Download PDF
            print("\n--- 4. Downloading Contract PDF ---")
            pdf_response = requests.get(f"{BASE_URL}/contracts/{employment_contract_id}/pdf")
            
            if pdf_response.status_code == 200:
                with open("test_contract.pdf", "wb") as f:
                    f.write(pdf_response.content)
                print(f"✅ PDF Downloaded: test_contract.pdf ({len(pdf_response.content)} bytes)")
            else:
                print(f"❌ PDF Download Failed: {pdf_response.status_code}")
                print(pdf_response.text)
        else:
             print("⚠️ Could not generate employment contract (maybe missing clauses). Skipping PDF test.")
    else:
        print("⚠️ Could not generate legal contract draft (maybe missing clauses). Skipping PDF test.")

if __name__ == "__main__":
    test_new_features()
