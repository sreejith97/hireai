from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import os
from datetime import datetime
from contextlib import asynccontextmanager

from database import init_db
from models import PDFSource, Clause, Contract, EquityGrant, Employee
from services.pdf_service import extract_text_from_pdf
from services.llm_service import assemble_contract_from_clauses
from services.parsing_service import heuristic_extract_clauses

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    yield

app = FastAPI(
    title="Auto-HR Backend",
    description="Backend for PDF-based contract generation (MongoDB)",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Requirements models
class ContractLegalRequest(BaseModel):
    company_id: str
    country: str

class ContractEmploymentRequest(BaseModel):
    legal_contract_id: str
    candidate: Dict[str, Any]

class PDFExtractRequest(BaseModel):
    pdf_id: str

class EquityGrantRequest(BaseModel):
    employee_id: str
    vesting_start_date: str # YYYY-MM-DD
    number_of_options: int
    vesting_schedule: Dict[str, Any] # e.g. {"details": "4 year vesting, 1 year cliff"}

# --- API Endpoints ---

@app.post("/legal/pdf/upload", tags=["PDF Ingestion"])
async def upload_legal_pdf(
    file: UploadFile = File(...),
    country: str = "Unknown"
):
    """Upload a legal PDF (e.g., Labor Law)"""
    content = await file.read()
    
    # Save file to disk
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create PDF Source record
    pdf_source = PDFSource(
        filename=file.filename,
        category="law",
        country=country,
        file_path=file_path
    )
    await pdf_source.create()
    
    # Trigger extraction
    text = extract_text_from_pdf(content)
    
    # Save extracted clauses
    # Use heuristic parsing to avoid LLM rate limits/token costs at ingestion
    extracted_data = heuristic_extract_clauses(text, f"Legal Document: {file.filename}")
    clauses_list = extracted_data.get("clauses", [])
    
    for c_data in clauses_list:
        clause = Clause(
            text=c_data["text"],
            clause_type=c_data["clause_type"],
            country=c_data.get("country") or country,
            variables=json.dumps(c_data.get("variables", {})),
            source_id=str(pdf_source.id)
        )
        await clause.create()
    
    return {"message": "PDF uploaded and processed", "pdf_id": str(pdf_source.id), "file_path": file_path, "clauses_count": len(clauses_list)}

@app.post("/policies/pdf/upload", tags=["PDF Ingestion"])
async def upload_policy_pdf(
    file: UploadFile = File(...),
    company_id: str = "Unknown"
):
    """Upload a Company Policy PDF"""
    content = await file.read()
    
    # Save file to disk
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    pdf_source = PDFSource(
        filename=file.filename,
        category="policy",
        company_id=company_id,
        file_path=file_path
    )
    await pdf_source.create()
    
    text = extract_text_from_pdf(content)
    
    extracted_data = heuristic_extract_clauses(text, f"Company Policy: {file.filename}")
    clauses_list = extracted_data.get("clauses", [])
    
    for c_data in clauses_list:
        clause = Clause(
            text=c_data["text"],
            clause_type=c_data["clause_type"],
            country=c_data.get("country"),
            variables=json.dumps(c_data.get("variables", {})),
            source_id=str(pdf_source.id)
        )
        await clause.create()
        
    return {"message": "Policy uploaded and processed", "pdf_id": str(pdf_source.id), "file_path": file_path, "clauses_count": len(clauses_list)}

@app.post("/clauses/extract", tags=["Clause Management"])
async def extract_clauses_from_existing_pdf(
    request: PDFExtractRequest
):
    """Re-run extraction for a stored PDF (Not fully implemented)"""
    return {"message": "Extraction currently happens at upload time."}

@app.get("/clauses", tags=["Clause Management"])
async def list_clauses(
    country: str = None,
    clause_type: str = None
):
    """List extracted clauses with optional filtering"""
    try:
        query = Clause.find_all()
        if country:
            query = query.find(Clause.country == country)
        if clause_type:
            query = query.find(Clause.clause_type == clause_type)
            
        clauses = await query.to_list()
        
        # Serialize to ensure frontend compatibility
        results = []
        for c in clauses:
            c_dict = c.model_dump()
            c_dict["id"] = str(c.id) # Convert ObjectId to string
            
            # Parse variables string to JSON object if needed
            if "variables" in c_dict and isinstance(c_dict["variables"], str):
                try:
                    c_dict["variables"] = json.loads(c_dict["variables"])
                except:
                    c_dict["variables"] = {}
            
            # Explicitly remove _id if present to avoid duplicate id fields or serialization errors
            if "_id" in c_dict:
                del c_dict["_id"]
                
            results.append(c_dict)
            
        return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/employees/upload_excel", tags=["Employee Management"])
async def upload_employees_excel(
    file: UploadFile = File(...)
):
    """Upload Excel/CSV file with employee details"""
    from services.excel_service import parse_employee_excel, parse_employee_csv
    from models import Employee
    
    content = await file.read()
    filename = file.filename.lower()
    
    employee_list = []
    errors = []
    
    # Parse Logic
    try:
        if filename.endswith(".csv"):
             employee_list = parse_employee_csv(content)
        else:
             # Default try excel, if fails maybe try csv?
             try:
                 employee_list = parse_employee_excel(content)
             except Exception as e:
                 # Fallback to CSV text parsing
                 try:
                     employee_list = parse_employee_csv(content)
                 except:
                     raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file: {str(e)}")
    
    saved_count = 0
    
    for emp_data in employee_list:
        try:
            # Check if exists (simple UPSERT based on ID)
            if emp_data.get("employee_id"):
                existing = await Employee.find_one(Employee.employee_id == emp_data["employee_id"])
                if existing:
                    # Update fields
                    existing.name = emp_data["name"]
                    existing.role = emp_data.get("role")
                    existing.email = emp_data.get("email")
                    await existing.save()
                    saved_count += 1
                    continue
            
            # Create new
            employee = Employee(**emp_data)
            await employee.create()
            saved_count += 1
        except Exception as e:
            errors.append(f"Error saving {emp_data.get('name')}: {str(e)}")
            
    return {
        "message": "Employees processed", 
        "saved_count": saved_count, 
        "total_parsed": len(employee_list),
        "errors": errors
    }

@app.get("/employees", tags=["Employee Management"])
async def list_employees():
    """List all employees"""
    from models import Employee
    return await Employee.find_all().to_list()

@app.post("/contracts/generate/legal", tags=["Contract Generation"])
async def generate_legal_contract(
    request: ContractLegalRequest
):
    """Generate a legal contract structure (no candidate data)"""
    # Fetch relevant clauses
    law_clauses = await Clause.find(Clause.country == request.country).to_list()
    
    # Fetch policy clauses
    policy_sources = await PDFSource.find(PDFSource.category == "policy").to_list()
    policy_ids = [str(p.id) for p in policy_sources]
    
    policy_clauses = await Clause.find({"source_id": {"$in": policy_ids}}).to_list()
    
    all_clauses = []
    for c in law_clauses + policy_clauses:
        c_dict = c.model_dump()
        c_dict["id"] = str(c_dict["id"]) if c_dict.get("id") else None
        c_dict["source_id"] = str(c_dict["source_id"]) if c_dict.get("source_id") else None
        all_clauses.append(c_dict)
    
    if not all_clauses:
        raise HTTPException(status_code=404, detail="No relevant clauses found")

    # LLM Assembly
    requirements = {
        "country": request.country,
        "company_id": request.company_id
    }
    
    assembly_result = assemble_contract_from_clauses(all_clauses, requirements)
    assembled_contract_data = assembly_result.get("assembled_contract", [])
    
    # Store draft contract
    contract = Contract(
        contract_type="legal",
        company_id=request.company_id,
        content=json.dumps(assembled_contract_data)
    )
    await contract.create()
    
    return {"legal_contract_id": str(contract.id), "clauses": assembled_contract_data}

@app.post("/contracts/generate/employment", tags=["Contract Generation"])
async def generate_employment_contract(
    request: ContractEmploymentRequest
):
    """Inject candidate data into a legal contract"""
    contract = await Contract.get(request.legal_contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    contract_content = json.loads(contract.content)
    
    final_clauses = []
    candidate_data = request.candidate
    
    for item in contract_content:
        # Pre-process: If item is a dict with just "text" (LLM artifact), convert to string
        if isinstance(item, dict) and "text" in item and not item.get("clause_id") and not item.get("id"):
            item = item["text"]

        # CASE A: Item is a direct text string (from LLM rewriting)
        if isinstance(item, str):
            text = item
            # Perform variable replacement on the text directly
            # 1. Define Defaults (UAE Labor Law / Best Practice)
            defaults = {
                "probation_period": "6", # Months
                "notice_period": "30",   # Days
                "annual_leave": "30",    # Days
                "working_hours": "8",
                "rest_days": "1",
                "currency": "AED",
                "term": "2",             # Years standard
                "company_address": "Dubai, United Arab Emirates",
                "company_name": contract.company_id or "Employer"
            }
            
            # 2. Merge candidate data (Candidate overrides defaults)
            final_vars = {**defaults, **candidate_data}
            
            # 3. Add Computed Values
            if "start_date" in final_vars:
                try:
                    # Calculate end_date based on term
                    start_dt = datetime.strptime(str(final_vars["start_date"]), "%Y-%m-%d")
                    term_years = int(float(final_vars.get("term", 2)))
                    
                    # Simple calculation: same day, + term years
                    end_dt = start_dt.replace(year=start_dt.year + term_years)
                    # Adjust for leap year if needed (Feb 29 -> Feb 28 or Mar 1) - .replace handles errors? No, separate logic.
                    # But for now, let's keep it simple or use relativedelta if available (not standard).
                    # Actually standard way:
                    try:
                        end_dt = start_dt.replace(year=start_dt.year + term_years)
                    except ValueError: # Leap day case
                        end_dt = start_dt.replace(year=start_dt.year + term_years, day=28)
                        
                    final_vars["end_date"] = end_dt.strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Error computing end_date: {e}")
                    # Fallback to empty if calculation fails
                    final_vars["end_date"] = "________________"

            # Add company_id as company_name if missing (covered by defaults but ensuring precedence)
            if contract.company_id and "company_name" not in final_vars:
                final_vars["company_name"] = contract.company_id
                
            for k, v in final_vars.items():
                val_str = str(v)
                # Replace {key}
                text = text.replace(f"{{{k}}}", val_str)
                # Replace [Insert Key] or [Insert Key Name] loose matching attempt
                text = text.replace(f"[Insert {k}]", val_str)
                text = text.replace(f"[Insert {k.replace('_', ' ').title()}]", val_str)
            
            # Clean up leftover placeholders if any (simple heuristic)
            import re
            text = re.sub(r'\[Insert .*?\]', '_______________', text)
            
            final_clauses.append(text)
            
        # CASE B: Item is a clause object with an ID
        elif isinstance(item, dict):
            clause_id = item.get("clause_id") or item.get("id")
            
            if clause_id:
                # Try to get clause from DB to ensure text integrity
                db_clause = await Clause.get(clause_id)
                if db_clause:
                    text = db_clause.text
                    
                    # 1. Start with default variables extracted from the clause source
                    final_vars = {}
                    try:
                        if db_clause.variables:
                            final_vars = json.loads(db_clause.variables)
                    except:
                        pass
                    
                    # 2. Update with variables resolved during assembly (context-specific)
                    assembly_vars = item.get("variables", {})
                    if assembly_vars:
                        final_vars.update(assembly_vars)
                    
                    # 3. Update with candidate specific data (highest priority)
                    final_vars.update(candidate_data)
                    
                    # Perform replacement
                    for k, v in final_vars.items():
                         # Handle potential case mismatch or cleanup
                         val_str = str(v)
                         text = text.replace(f"{{{k}}}", val_str)
                    
                    final_clauses.append(text)
                else:
                    # Fallback if clause not found (shouldn't happen)
                    final_clauses.append(f"[Clause {clause_id} missing]")
            # Fallback if clause deleted but ID exists in contract draft?
            pass
    
    # Save final employment contract
    employment_contract = Contract(
        contract_type="employment",
        company_id=contract.company_id,
        candidate_name=candidate_data.get("name"),
        content=json.dumps(final_clauses),
        status="generated"
    )
    await employment_contract.create()
    
    return {"employment_contract_id": str(employment_contract.id), "final_text": "\n\n".join(final_clauses)}

@app.get("/contracts", tags=["Contract Generation"])
async def list_contracts(contract_type: Optional[str] = None):
    """List all contracts, optionally filtered by type"""
    query = Contract.find_all()
    if contract_type:
        query = query.find(Contract.contract_type == contract_type)
    return await query.to_list()

@app.get("/contracts/{contract_id}/pdf", tags=["Contract Generation"])
async def download_contract_pdf(contract_id: str):
    """Generate and download PDF for a contract"""
    from services.pdf_gen_service import generate_contract_pdf
    from fastapi.responses import StreamingResponse
    
    contract = await Contract.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    if contract.contract_type != "employment":
         raise HTTPException(status_code=400, detail="Can only generate PDF for final employment contracts")
         
    # content is stored as a JSON list of strings, join them
    try:
        clauses = json.loads(contract.content)
        full_text = "\n\n".join(clauses)
    except:
        full_text = contract.content
        
    pdf_buffer = generate_contract_pdf(full_text)
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Contract_{contract.candidate_name or 'Draft'}.pdf"}
    )

@app.post("/contracts/{contract_id}/amend", tags=["Contract Versioning"])
async def amend_contract(contract_id: str, amendments: Dict[str, Any]):
    """Create a new version of a contract with amendments"""
    original = await Contract.get(contract_id)
    if not original:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    # Archive original
    original.is_active = False
    await original.save()
    
    # Create new version
    new_content = original.content
    # Simple replace for amendment demo
    for k, v in amendments.items():
        new_content = new_content.replace(str(k), str(v))
        
    new_contract = Contract(
        contract_type=original.contract_type,
        status="amended",
        company_id=original.company_id,
        candidate_name=original.candidate_name,
        content=new_content,
        version=original.version + 1,
        parent_contract_id=str(original.id),
        is_active=True
    )
    await new_contract.create()
    return {"message": "Contract amended", "new_contract_id": str(new_contract.id), "version": new_contract.version}

@app.post("/contracts/{contract_id}/renew", tags=["Contract Versioning"])
async def renew_contract(contract_id: str, new_end_date: str):
    """Renew a contract"""
    original = await Contract.get(contract_id)
    if not original:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Logic similar to amend but focused on dates
    new_contract = Contract(
        contract_type=original.contract_type,
        status="renewed",
        company_id=original.company_id,
        candidate_name=original.candidate_name,
        content=original.content, # In real app, would update date clauses
        version=original.version + 1,
        parent_contract_id=str(original.id)
    )
    await new_contract.create()
    return {"message": "Contract renewed", "new_contract_id": str(new_contract.id)}

@app.post("/equity/generate", tags=["Equity Documentation"])
async def generate_equity_grant(request: EquityGrantRequest):
    """Generate an Equity Grant Letter"""
    return {"message": "Equity grant generation not implemented yet."}

# --- Chatbot Endpoint ---
# --- Chatbot Endpoint ---
class ChatRequest(BaseModel):
    message: str
    employee_id: Optional[str] = None # Optional now, generic check first
    history: List[Dict[str, str]] = []

@app.post("/chat", tags=["Conversational HR"])
async def chat_endpoint(request: ChatRequest):
    """
    Conversational HR Assistant.
    Handles:
    1. Identity Verification
    2. Policy QA (RAG)
    3. HR Actions (Tools)
    """
    from services.rag_service import search_knowledge_base
    from services.chat_tools import get_leave_balance, submit_expense, update_address, verify_identity
    from services.llm_service import client  # Re-use the Groq client
    
    user_msg = request.message
    emp_id = request.employee_id
    
    # Context Builder
    user_context_str = "Status: UNVERIFIED - UNKNOWN USER"
    
    if emp_id:
        from models import Employee
        # Fetch details to inject into context
        emp_record = await Employee.find_one(Employee.employee_id == emp_id)
        if emp_record:
            user_context_str = f"""
            Status: VERIFIED
            Employee ID: {emp_id}
            Name: {emp_record.name}
            Role: {emp_record.role}
            Department: {emp_record.additional_data_dict.get('Department', 'Unknown')}
            """
    
    # SYSTEM PROMPT: Define tools and behavior
    system_prompt = f"""
    You are an intelligent, friendly, and concise HR Assistant. 
    Your goal is to help employees with questions and tasks quickly and efficiently.
    
    USER CONTEXT:
    {user_context_str}
    
    TONE & STYLE:
    - distinct, modern, and professional but approachable.
    - NO "Dear User" or "Best Regards". Do NOT write like an email.
    - Be concise. Get straight to the answer.
    
    TOOLS:
    1. VERIFY_IDENTITY(employee_id): **CRITICAL**: Use this if the user is UNVERIFIED and provides an ID.
    2. SEARCH_POLICY(query): Answer questions about rules, leave policy, etc.
    3. GET_LEAVE_BALANCE(employee_id): Check leave days.
    4. SUBMIT_EXPENSE(amount, description): Claim expense.
    5. UPDATE_ADDRESS(new_address): Change address.
    
    PROTOCOL:
    - **IF USER IS UNVERIFIED**:
      - You MUST ask for their Employee ID if they haven't provided it.
      - If they provide something looking like an ID (e.g., "EMP001"), use TOOL:VERIFY_IDENTITY|ID
      - Do NOT answer policy/personal questions until verified.
    
    - **IF USER IS VERIFIED**:
      - If question -> TOOL:SEARCH_POLICY|query
      - If personal data -> TOOL:GET_LEAVE_BALANCE
      - If action -> TOOL:SUBMIT_EXPENSE or TOOL:UPDATE_ADDRESS
      - If small talk -> Reply normally.
    
    Output ONLY the tool command if a tool is needed.
    """
    
    # 1. Intent Classification
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User: {user_msg}"}
            ],
            temperature=0,
            max_tokens=100
        )
        response_text = completion.choices[0].message.content.strip()
        
    except Exception as e:
        return {"response": "I'm having trouble connecting to my brain right now. Please try again."}
        
    # 2. Execute Tool
    tool_response = None
    final_response = response_text
    verified_id_flag = None
    
    # Robust Parsing: Check for "TOOL:" prefix OR Regex for function call style
    import re
    
    command = None
    args = []
    
    if response_text.startswith("TOOL:"):
        parts = response_text.split("|")
        command = parts[0].replace("TOOL:", "").strip()
        args = parts[1:]
    elif "(" in response_text and ")" in response_text:
        # Fallback: Generic Function Call Parser
        # Matches: COMMAND(arg1, "arg2")
        try:
            # 1. Extract Command Name
            cmd_match = re.match(r'([A-Z_]+)\s*\(', response_text)
            if cmd_match:
                command = cmd_match.group(1)
                
                # 2. Extract Content inside parens
                # Find content between first ( and last )
                start_idx = response_text.find("(")
                end_idx = response_text.rfind(")")
                if start_idx != -1 and end_idx != -1:
                    params_str = response_text[start_idx+1:end_idx]
                    
                    # 3. Simple Argument Splitter (handling quotes is hard with simple split, but let's try)
                    # For now, simplistic splitting by comma if not in quotes
                    # Or just regex extract args? 
                    # Let's try a regex that grabs non-comma stuff or quoted stuff
                    raw_args = re.findall(r'(?:[^,"]|"(?:\\.|[^"])*")+', params_str)
                    args = []
                    for arg in raw_args:
                        clean_arg = arg.strip()
                        # Remove key= if present (kwarg to positional)
                        if "=" in clean_arg:
                            clean_arg = clean_arg.split("=", 1)[1].strip()
                        # Remove quotes
                        clean_arg = clean_arg.strip('"').strip("'")
                        if clean_arg:
                            args.append(clean_arg)
        except Exception as e:
            print(f"Parsing Error: {e}")
    
    if command:
        if command == "VERIFY_IDENTITY":
             eid = args[0] if args else user_msg
             # Extra cleanup just in case
             eid = eid.strip().strip('"').strip("'")
             
             res = await verify_identity(eid)
             if res["valid"]:
                 tool_response = f"IDENTITY VERIFIED: Name={res['name']}, Role={res['role']}. WELCOME THEM."
                 verified_id_flag = eid
             else:
                 tool_response = f"ERROR: Employee ID {eid} not found. Ask them to check and try again."
        
        elif command == "SEARCH_POLICY":
            query = args[0] if args else user_msg
            tool_data = await search_knowledge_base(query)
            tool_response = f"POLICY CONTEXT:\n{tool_data}"
            
        elif command == "GET_LEAVE_BALANCE":
            target_id = emp_id or "unknown"
            balance = await get_leave_balance(target_id)
            tool_response = f"LEAVE BALANCE: {balance}"
            
        elif command == "SUBMIT_EXPENSE":
            if not emp_id:
                tool_response = "ERROR: User must verify identity first."
            else:
                try:
                    amount = args[0]
                    desc = args[1] if len(args) > 1 else "Expense"
                    res = await submit_expense(emp_id, float(amount), desc)
                    tool_response = f"ACTION RESULT: {res}"
                except:
                   tool_response = "Error: Invalid format."
                
        elif command == "UPDATE_ADDRESS":
             if not emp_id:
                  tool_response = "ERROR: User must verify identity first."
             else:
                  addr = args[0] if args else ""
                  res = await update_address(emp_id, addr)
                  tool_response = f"ACTION RESULT: {res}"

        elif command == "ADD_DEPENDENT":
             if not emp_id:
                  tool_response = "ERROR: User must verify identity first."
             else:
                  name = args[0] if args else "Unknown"
                  relation = args[1] if len(args) > 1 else "Dependent"
                  from services.chat_tools import add_dependent
                  res = await add_dependent(emp_id, name, relation)
                  tool_response = f"ACTION RESULT: {res}"
            
        # 3. Final Synthesis
        if tool_response:
            synthesis_prompt = f"""
            User Input: {user_msg}
            Tool Result: {tool_response}
            
            Task: Respond to the user based on the Tool Result.
            
            GUIDELINES:
            - **Natural Language ONLY**: Never output raw JSON, dictionaries, or lists (e.g., do NOT say "annual: 0").
            - **Friendly & Professional**: Use the user's name if known.
            - **Context**:
                - If checking leave: Say "You have X days of annual leave and Y days of sick leave."
                - If verified: "Welcome back, [Name]. I've verified your identity."
                - If verification failed: "I couldn't verify that ID. Please check it and try again."
            - **Be Concise**: One or two sentences is usually enough.
            """
            
            synth_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful HR Assistant."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.3
            )
            final_response = synth_completion.choices[0].message.content.strip()

    return {
        "response": final_response, 
        "intent_debug": response_text,
        "verified_employee_id": verified_id_flag
    }
    # Create Equity Record
    grant = EquityGrant(
        employee_id=request.employee_id,
        vesting_start_date=datetime.strptime(request.vesting_start_date, "%Y-%m-%d"),
        number_of_options=request.number_of_options,
        vesting_schedule=json.dumps(request.vesting_schedule),
        status="granted"
    )
    await grant.create()
    
    # Generate PDF (Simplistic text generation for now)
    from services.pdf_gen_service import generate_contract_pdf
    
    text = f"""
    EQUITY OPTION GRANT LETTER
    
    Date: {datetime.utcnow().strftime('%Y-%m-%d')}
    To Employee ID: {request.employee_id}
    
    We are pleased to grant you {request.number_of_options} stock options.
    
    Vesting Start Date: {request.vesting_start_date}
    Vesting Schedule: {request.vesting_schedule.get('details', 'Standard Standard')}
    
    This grant is subject to the terms of the Company Stock Option Plan.
    """
    
    pdf_buffer = generate_contract_pdf(text)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Grant_{request.employee_id}.pdf"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
