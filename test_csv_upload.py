import requests

url = "http://localhost:8000/employees/upload_excel"
file_path = "uploads/sample_employees.csv"

with open(file_path, "rb") as f:
    files = {"file": ("sample_employees.csv", f, "text/csv")}
    response = requests.post(url, files=files)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
