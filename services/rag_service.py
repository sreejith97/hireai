
from models import Clause, PDFSource
from typing import List, Dict, Any

async def search_knowledge_base(query: str, country: str = None) -> str:
    """
    Searches the Clause database for relevant policies.
    For now, uses a simple regex search. In production, use embeddings.
    """
    # Simple keyword extraction (very naive)
    keywords = [w for w in query.split() if len(w) > 3]
    
    if not keywords:
        return ""
        
    # Construct regex query for ANY keyword
    # regex pattern: (keyword1|keyword2|...)
    pattern = "|".join(keywords)
    
    db_query = {"text": {"$regex": pattern, "$options": "i"}}
    
    if country:
        db_query["country"] = country
        
    # Fetch top 5 matches
    clauses = await Clause.find(db_query).limit(5).to_list()
    
    if not clauses:
        return "No specific policies found for this query."
        
    results = []
    for c in clauses:
        source_name = "Unknown Policy"
        if c.source_id:
             # Ideally we fetch source name, but let's skip for speed or cache it
             pass
        results.append(f"- [{c.clause_type.upper()}]: {c.text}")
        
    return "\n\n".join(results)
