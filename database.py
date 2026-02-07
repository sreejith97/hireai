from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv
import os
import certifi

# Import models (will be defined in models.py)
# We need to import them inside the init function or after definition to avoid circular imports if any,
# but typically we import them at top level if models.py doesn't import database.py immediately.
# For now, let's assume models.py will be updated and we can import them here.
# However, to avoid ImportErrors before models.py is updated, I'll do a local import in init_db.

load_dotenv()

async def init_db():
    database_url = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auto_hr_db")
    
    # Create Motor client
    if "mongodb+srv" in database_url:
         client = AsyncIOMotorClient(database_url, tlsCAFile=certifi.where())
    else:
        client = AsyncIOMotorClient(database_url) 
    
    # Initialize Beanie with the specific database
    from models import PDFSource, Clause, Contract, Employee, EquityGrant
    await init_beanie(database=client[db_name], document_models=[PDFSource, Clause, Contract, Employee, EquityGrant])
