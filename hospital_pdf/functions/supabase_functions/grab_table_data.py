import os
from dotenv import load_dotenv
from supabase import create_client, Client

def initialize_supabase() -> Client:
    """Initialize and return the Supabase client."""
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials in .env file")
    return create_client(supabase_url, supabase_key)

def get_all_requirements():
    """
    Test function for the batch compliance checking system using real requirements from Supabase
    """
    supabase = initialize_supabase()
    result = supabase.table('treehacks_reqs') \
        .select('requirement') \
        .order('phase,order') \
        .execute()
        
    return result