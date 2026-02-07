import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def extract_clauses_from_text(text: str, source_name: str):
    # Chunking logic to avoid Rate Limits (TPM)
    # 6000 TPM limit on free tier. We'll stick to safer chunk sizes.
    chunk_size = 12000 # ~3000 tokens
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    all_clauses = []
    
    import time
    
    for i, chunk in enumerate(chunks):
        prompt = f"""
        You are a legal document parser.
        Input: Part {i+1}/{len(chunks)} of Legal text from {source_name}.
        Task:
        - Split into atomic clauses
        - Assign a clause type
        - Detect applicability (country or company specific)
        - Extract variables

        Return a JSON object with a key "clauses" containing a list of objects.
        Each object should have:
        - clause_type (string, e.g., "probation", "termination", "salary")
        - text (string, the clause text with placeholders like {{variable_name}} if applicable)
        - variables (dictionary of extracted variables and their default values)
        - country (string, inferred from text or null)

        Input Text:
        {chunk}
        """
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful legal assistant that outputs only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            data = json.loads(completion.choices[0].message.content)
            all_clauses.extend(data.get("clauses", []))
            
            # Simple rate limit backoff if needed (though 6000 TPM might still be hit if we go fast)
            # A small sleep might help refill the bucket slightly? 
            # Actually, with 9706 tokens total, splitting into 3 chunks of 3k tokens...
            # We arguably need to wait 1 minute between chunks if the limit is strictly 6000/min.
            # But let's try with just splitting first.
            if len(chunks) > 1:
                time.sleep(2) 
                
        except Exception as e:
            print(f"Error extracting from chunk {i}: {e}")
            # Continue to next chunk instead of crashing
            pass

    return {"clauses": all_clauses}

def assemble_contract_from_clauses(clauses_list: list, requirements: dict):
    clauses_json = json.dumps(clauses_list)
    requirements_json = json.dumps(requirements)
    
    prompt = f"""
    You are assembling a legal contract.
    
    Available Clauses:
    {clauses_json}
    
    Requirements:
    {requirements_json}
    
    Task:
    - Select compatible clauses based on requirements.
    - Resolve conflicts (Law overrides Policy).
    - Organize into a professional UAE/Dubai Employment Contract structure:
      1. Terms of Employment (Fixed-term 1-3 years)
      2. Parties (Employer & Employee Name/Address)
      3. Job Details (Title, Duties, Workplace)
      4. Remuneration (Basic Salary >=50%, Allowances breakdown)
      5. Probation Period (Max 6 months)
      6. Working Conditions (Hours, Rest Days, 30 Days Annual Leave)
      7. Termination (Min 30 days notice)
      8. End of Service Gratuity
      9. Non-Compete (Max 2 years, if applicable)
    - Language: English (Standard). 
    - Format: Use Markdown for headers (## Section Name) and bold text (**bold**).
    - Use EXACT placeholders for variable data:
      - Candidate Name: {{name}}
      - Position/Role: {{role}}
      - Basic Salary: {{salary}}
      - Allowances: {{allowances}}
      - Start Date: {{start_date}}
      - Company Name: {{company_name}}
      - Company Address: {{company_address}}
    - Return a JSON object with "assembled_contract" containing a list of text blocks.
    - You MUST rewrite clauses to form a cohesive, professional document. Do not just list disjointed text.
    - If you rewrite, return the full text strings in the list.
    """
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful legal assistant that outputs only JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    return json.loads(completion.choices[0].message.content)
