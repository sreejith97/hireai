import asyncio
from database import init_db
from models import Employee

async def main():
    await init_db()
    
    employees = await Employee.find_all().to_list()
    print(f"Total Employees in DB: {len(employees)}")
    for emp in employees:
        print(f"ID: {emp.employee_id}, Name: {emp.name}, Role: {emp.role}")

    # Test query
    test_id = "EMP001"
    found = await Employee.find_one(Employee.employee_id == test_id)
    if found:
        print(f"\nSUCCESS: Found {test_id}")
    else:
        print(f"\nFAILURE: Could not find {test_id}")

if __name__ == "__main__":
    asyncio.run(main())
