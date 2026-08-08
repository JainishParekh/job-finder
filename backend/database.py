from supabase import create_client, Client
from dotenv import load_dotenv
from backend.settings import settings

load_dotenv()

# Initialize the Supabase client
db: Client = create_client(settings.supabase_url, settings.supabase_key)


def get_db():
    return db
