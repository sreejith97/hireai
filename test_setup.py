import requests
import json
import io
import time
from pypdf import PdfWriter

BASE_URL = "http://localhost:8000"

def create_dummy_pdf(content="This is a dummy legal document for testing purposes."):
    writer = PdfWriter()
    page = writer.add_blank_page(width=72, height=72)
    # We can't easily add text to a blank page with just pypdf without other libs, 
    # but for extraction testing, we might need a real PDF or just accept empty text if pypdf extracts nothing from blank.
    # To make pypdf extract something, we'd need a real PDF. 
    # For now, let's just create a valid PDF structure. The extraction might yield empty string, which is fine for flow testing.
    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    return output_stream

def print_response(response):
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_full_flow():
    print("🚀 Starting Full API Test Flow...")
    
    # 1. Upload Legal PDF
    print("\n--- 1. Uploading Legal PDF ---")
    pdf_file = create_dummy_pdf()
    files = {'file': ('uae_labor_law.pdf', pdf_file, 'application/pdf')}
    params = {"country": "UAE"}
    
    response = requests.post(f"{BASE_URL}/legal/pdf/upload", files=files, params=params)
    if response.status_code != 200:
        print(f"❌ Legal Upload Failed: {response.status_code}")
        print_response(response)
        return
    
    legal_data = response.json()
    print("✅ Legal PDF Uploaded")
    print_response(response)
    
    # 2. Upload Policy PDF
    print("\n--- 2. Uploading Policy PDF ---")
    pdf_file = create_dummy_pdf()
    files = {'file': ('company_policy.pdf', pdf_file, 'application/pdf')}
    params = {"company_id": "TechCorp"}
    
    response = requests.post(f"{BASE_URL}/policies/pdf/upload", files=files, params=params)
    if response.status_code != 200:
        print(f"❌ Policy Upload Failed: {response.status_code}")
        print_response(response)
        return

    print("✅ Policy PDF Uploaded")
    print_response(response)
    
    # 3. List Clauses
    print("\n--- 3. Listing Clauses ---")
    response = requests.get(f"{BASE_URL}/clauses", params={"country": "UAE"})
    if response.status_code != 200:
        print(f"❌ List Clauses Failed: {response.status_code}")
        return
    
    clauses = response.json()
    print(f"✅ Retrieved {len(clauses)} clauses for UAE")
    if len(clauses) > 0:
        print("Sample Clause:", clauses[0])
    
    # 4. Generate Legal Contract
    print("\n--- 4. Generating Legal Contract (Draft) ---")
    payload = {
        "company_id": "TechCorp",
        "country": "UAE"
    }
    response = requests.post(f"{BASE_URL}/contracts/generate/legal", json=payload)
    if response.status_code != 200:
        print(f"❌ Generate Legal Contract Failed: {response.status_code}")
        print_response(response)
        # Verify if 404 is due to empty clauses (expected with dummy PDF that has no text)
        if response.status_code == 404:
             print("⚠️ 404 Expected if dummy PDF has no text for LLM to extract.")
        return

    legal_contract_data = response.json()
    print("✅ Legal Contract Generated")
    print_response(response)
    legal_contract_id = legal_contract_data.get("legal_contract_id")

    # 5. Generate Employment Contract
    print("\n--- 5. Generating Employment Contract (Final) ---")
    payload = {
        "legal_contract_id": legal_contract_id,
        "candidate": {
            "name": "John Doe",
            "role": "Senior Engineer",
            "salary": "25000",
            "currency": "AED",
            "start_date": "2026-05-01"
        }
    }
    response = requests.post(f"{BASE_URL}/contracts/generate/employment", json=payload)
    if response.status_code != 200:
        print(f"❌ Generate Employment Contract Failed: {response.status_code}")
        print_response(response)
        return

    employment_data = response.json()
    print("✅ Employment Contract Generated")
    print("--- Final Contract Text ---")
    print(employment_data.get("final_text"))

if __name__ == "__main__":
    test_full_flow()
