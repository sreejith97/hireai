
from typing import Dict, Any

# Mock Database for HRIS Data
MOCK_LEAVE_BALANCES = {
    "emp_001": {"annual": 25, "sick": 10},
    "emp_002": {"annual": 5, "sick": 2}
}

MOCK_EXPENSES = []

async def get_leave_balance(employee_id: str) -> Dict[str, int]:
    """Returns the leave balance for an employee"""
    # Normalize ID to match mock keys
    key = employee_id.strip().lower()
    return MOCK_LEAVE_BALANCES.get(key, {"annual": 0, "sick": 0})

async def submit_expense(employee_id: str, amount: float, description: str) -> str:
    """Submits an expense claim"""
    MOCK_EXPENSES.append({
        "employee_id": employee_id,
        "amount": amount,
        "description": description,
        "status": "Pending Approval"
    })
    return f"Expense claim for AED {amount} received. Status: Pending Approval."

async def update_address(employee_id: str, new_address: str) -> str:
    """Updates the employee's address"""
    # In a real app, update Employee model
    return f"Address updated to: {new_address}"

async def verify_identity(employee_id: str) -> Dict[str, Any]:
    """Verifies if an employee ID exists in the database"""
    from models import Employee
    import re
    
    # 1. Clean the input ID
    # Remove quotes, spaces, invisible chars
    clean_id = employee_id.strip().strip('"').strip("'")
    
    print(f"DEBUG: verify_identity called. Original: '{employee_id}', Cleaned: '{clean_id}'")
    
    # 2. Try Exact Match
    employee = await Employee.find_one(Employee.employee_id == clean_id)
    
    # 3. Try Case-Insensitive Match if not found
    if not employee:
        print(f"DEBUG: Exact match failed for '{clean_id}'. Trying case-insensitive.")
        # Beanie/MongoDB regex for case insensitive
        employee = await Employee.find_one({"employee_id": {"$regex":f"^{re.escape(clean_id)}$", "$options": "i"}})
        
    if employee:
        print(f"DEBUG: Found employee: {employee.name}")
        return {
            "valid": True,
            "name": employee.name,
            "role": employee.role,
            "department": "Unknown" 
        }
        
    print(f"DEBUG: Verification FAILED for '{clean_id}'")
    return {"valid": False, "error": f"Employee ID {clean_id} not found"}

async def add_dependent(employee_id: str, name: str, relation: str) -> str:
    """
    Mock workflow: Adds a dependent and routes to benefits provider.
    """
    # In real app: Update DB, Email Benefits Provider, etc.
    return f"Request to add {name} ({relation}) has been initiated. I've sent the details to our insurance provider. You will receive a confirmation email shortly."
