from typing import Optional, List, Dict, Any
from beanie import Document, Link
from pydantic import Field
from datetime import datetime
import json

class PDFSource(Document):
    filename: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    category: str  # "law", "policy", etc.
    country: Optional[str] = None
    company_id: Optional[str] = None
    file_path: Optional[str] = None # Added field for file path
    
    class Settings:
        name = "pdf_sources"

class EquityGrant(Document):
    employee_id: str
    grant_date: datetime = Field(default_factory=datetime.utcnow)
    vesting_start_date: datetime
    number_of_options: int
    vesting_schedule: str # JSON string describing the schedule
    status: str = "draft" # draft, granted, exercised, cancelled
    
    class Settings:
        name = "equity_grants"

class Clause(Document):
    text: str
    clause_type: str
    country: Optional[str] = None
    variables: str = Field(default="{}")
    page_number: Optional[int] = None
    
    source_id: Optional[str] = None
    
    class Settings:
        name = "clauses"

    @property
    def variables_dict(self) -> Dict[str, Any]:
        return json.loads(self.variables)

    @variables_dict.setter
    def variables_dict(self, value: Dict[str, Any]):
        self.variables = json.dumps(value)

class Contract(Document):
    contract_type: str
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    company_id: Optional[str] = None
    candidate_name: Optional[str] = None
    content: str
    
    # Versioning
    version: int = 1
    parent_contract_id: Optional[str] = None
    is_active: bool = True
    
    class Settings:
        name = "contracts"

class Employee(Document):
    employee_id: Optional[str] = None # Internal ID or Employee Number from Excel
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    salary: Optional[str] = None # Storing as string to keep currency symbol if needed, or parse later
    start_date: Optional[str] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    additional_data: str = Field(default="{}") # JSON string for any other columns
    
    class Settings:
        name = "employees"

    @property
    def additional_data_dict(self) -> Dict[str, Any]:
        try:
             return json.loads(self.additional_data)
        except:
             return {}
