import re

def heuristic_extract_clauses(text: str, source_name: str):
    """
    Extracts clauses from text using regex and heuristics instead of an LLM.
    This saves tokens and avoids rate limits.
    """
    clauses = []
    
    # 1. Try to split by common legal headers (Article X, Section Y)
    # Regex for "Article 1", "Article I", "Section 1", "1. Title"
    # Removed (?m) from start and handling it via re.MULTILINE where needed or just relying on line-by-line which we do below anyway.
    # Actually, the split logic below uses capturing group which caused the error when (?m) was inside ().
    header_pattern = r"^(?:Article|Section|Rule|Clause)\s+(?:\d+|[IVX]+)\.?"
    
    # Split text by these headers, but keep the headers
    # verify if we have headers
    if re.search(header_pattern, text, re.MULTILINE):
        parts = re.split(f"({header_pattern}.*)", text, flags=re.MULTILINE)
        # parts[0] is pre-text, then specific parts
        # re.split with capturing group returns [pre, delimiter, content, delimiter, content...]
        # wait, if I put the whole line in capturing group, it returns [pre, line, post...]
        # Let's use a simpler approach: iterate line by line and group
        
        current_clause_text = []
        current_header = "Preamble"
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if re.match(header_pattern, line):
                # Save previous clause if substantial
                if current_clause_text:
                    full_text = "\n".join(current_clause_text)
                    if len(full_text) > 50: # Ignore tiny snippets
                        clauses.append({
                            "text": full_text,
                            "clause_type": infer_clause_type(full_text, current_header),
                            "variables": {},
                            "country": None
                        })
                
                # Start new clause
                current_header = line
                current_clause_text = [line]
            else:
                current_clause_text.append(line)
        
        # Add last clause
        if current_clause_text:
            full_text = "\n".join(current_clause_text)
            if len(full_text) > 50:
                clauses.append({
                    "text": full_text,
                    "clause_type": infer_clause_type(full_text, current_header),
                    "variables": {},
                    "country": None
                })
                
    else:
        # 2. Fallback: Split by double newlines (Paragraphs)
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if len(para) > 100: # Only substantial paragraphs
                clauses.append({
                    "text": para,
                    "clause_type": infer_clause_type(para),
                    "variables": {},
                    "country": None
                })
                
    return {"clauses": clauses}

def infer_clause_type(text: str, header: str = "") -> str:
    """Guess clause type based on keywords"""
    text_lower = text.lower()
    header_lower = header.lower()
    combined = f"{header_lower} {text_lower}"
    
    if "probation" in combined:
        return "probation"
    elif "termination" in combined or "notice period" in combined or "resign" in combined:
        return "termination"
    elif "salary" in combined or "remuneration" in combined or "pay" in combined:
        return "compensation"
    elif "leave" in combined or "vacation" in combined or "holiday" in combined:
        return "leave"
    elif "confidential" in combined or "secrecy" in combined:
        return "confidentiality"
    elif "non-compete" in combined or "competition" in combined:
        return "non_compete"
    elif "working hour" in combined or "schedule" in combined:
        return "working_hours"
    elif "duty" in combined or "responsibility" in combined or "role" in combined:
        return "duties"
    else:
        return "general"
