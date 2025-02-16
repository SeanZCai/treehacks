import os
from pathlib import Path
import json
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(
    filename='uploader.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_supabase() -> Client:
    """Initialize and return the Supabase client."""
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials in .env file")

    return create_client(supabase_url, supabase_key)

def get_existing_files(supabase: Client, bucket_name: str = 'maps') -> set:
    """Retrieve a set of existing file names from Supabase storage."""
    try:
        files = supabase.storage.from_(bucket_name).list()
        existing_files = {file['name'] for file in files}
        logging.info(f"Retrieved {len(existing_files)} existing files from Supabase storage.")
        return existing_files
    except Exception as e:
        logging.error(f"Failed to retrieve existing files from Supabase: {e}")
        return set()

def upload_requirement(requirement: str, phase: str, order: int) -> Dict:
    """
    Upload a single requirement to the treehacks_reqs table.
    
    Args:
        requirement (str): The requirement text to upload
        phase (str): The phase of the requirement
        order (int): The order within the phase
        
    Returns:
        Dict: The created requirement record
    """
    try:
        supabase = initialize_supabase()
        
        response = supabase.table('treehacks_reqs').insert({
            'requirement': requirement,
            'phase': phase,
            'order': order
        }).execute()
        
        return response.data[0]
        
    except Exception as e:
        print(f"Error uploading requirement: {str(e)}")
        return None

def upload_requirements(requirements: List[Dict[str, str]]) -> List[Dict]:
    """
    Upload multiple requirements to the treehacks_reqs table.
    
    Args:
        requirements (List[Dict]): List of dicts with 'requirement', 'phase', and 'order' keys
        
    Returns:
        List[Dict]: List of created requirement records
    """
    try:
        supabase = initialize_supabase()
        
        # Prepare records for batch insert
        records = [
            {
                'requirement': req['requirement'],
                'phase': req['phase'],
                'order': req['order']
            } 
            for req in requirements
        ]
        
        response = supabase.table('treehacks_reqs').insert(records).execute()
        return response.data
        
    except Exception as e:
        print(f"Error uploading requirements: {str(e)}")
        return None

def get_all_requirements() -> List[Dict]:
    """Retrieve all requirements from the treehacks_reqs table."""
    try:
        supabase = initialize_supabase()
        
        response = supabase.table('treehacks_reqs')\
            .select('*')\
            .order('phase,order')\
            .execute()
            
        return response.data
        
    except Exception as e:
        print(f"Error retrieving requirements: {str(e)}")
        return None

def get_requirements_by_phase(phase: str) -> List[Dict]:
    """
    Retrieve requirements for a specific phase.
    
    Args:
        phase (str): The phase to filter by
        
    Returns:
        List[Dict]: List of requirement records for the specified phase
    """
    try:
        supabase = initialize_supabase()
        
        response = supabase.table('treehacks_reqs')\
            .select('*')\
            .eq('phase', phase)\
            .order('order')\
            .execute()
            
        return response.data
        
    except Exception as e:
        print(f"Error retrieving requirements for phase: {str(e)}")
        return None