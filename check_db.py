
import asyncio
from database import init_db
from models import Clause, Contract
import json

async def check_clauses():
    await init_db()
    
    # Check Clauses
    count = await Clause.count()
    print(f"Total Clauses: {count}")
    
    # Check Contracts
    contracts = await Contract.find_all().to_list()
    print(f"Total Contracts: {len(contracts)}")
    print(f"Total Contracts: {len(contracts)}")
    for i, c in enumerate(contracts):
        content_len = len(c.content)
        try:
             json_len = len(json.loads(c.content))
        except:
             json_len = "Invalid JSON"
        print(f"[{i}] ID: {c.id} | Type: {c.contract_type} | Content Len: {content_len} chars | JSON Items: {json_len}")
        if json_len != "Invalid JSON" and json_len > 0:
             content_json = json.loads(c.content)
             print(f"    First Item Type: {type(content_json[0])}")
             if isinstance(content_json[0], dict):
                 print(f"    First Item Keys: {content_json[0].keys()}")
                 print(f"    First Item Content: {content_json[0]}")

if __name__ == "__main__":
    asyncio.run(check_clauses())
