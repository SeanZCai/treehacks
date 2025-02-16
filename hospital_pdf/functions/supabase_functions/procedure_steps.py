from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict
from supabase import create_client, Client
from pathlib import Path
from functions.supabase.supabaseFunctions import upload_requirements, get_requirements_by_phase, get_all_requirements
import base64
from PIL import Image
import io
from io import BytesIO

# Get the project root directory (3 levels up from this file since we're in supabase folder)
ROOT_DIR = Path(__file__).parent.parent.parent.parent
ENV_PATH = ROOT_DIR / '.env'

print(f"Looking for .env at: {ENV_PATH}")  # Debug print
print(f"File exists: {ENV_PATH.exists()}")  # Debug print

# Load environment variables
load_dotenv(ENV_PATH)

# Debug prints for environment variables
print("\nEnvironment Variables Debug:")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')[:30]}..." if os.getenv('SUPABASE_URL') else "SUPABASE_URL not set")
print(f"SUPABASE_SERVICE_KEY length: {len(os.getenv('SUPABASE_SERVICE_KEY'))} chars" if os.getenv('SUPABASE_SERVICE_KEY') else "SUPABASE_SERVICE_KEY not set")
print(f"First 10 chars of key: {os.getenv('SUPABASE_SERVICE_KEY')[:10]}..." if os.getenv('SUPABASE_SERVICE_KEY') else "")

# Initialize OpenAI
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# System role for procedure step extraction
SYSTEM_ROLE = """You are an AI assistant specialized in analyzing surgical procedures and extracting ordered steps.
Your primary responsibilities are:
1. Extract clear, sequential steps from surgical procedure descriptions
2. Maintain the exact order of steps as they must be performed
3. Ensure each step is clear, concise, and actionable
4. Include critical safety checks and verifications
5. Format each step with its numerical order

Output format should be a numbered list where each step follows this pattern:
1. [Step description]
2. [Step description]
etc.

Remember:
- Order is critically important
- Each step must be clear and specific
- Include safety checks where appropriate
- Maintain medical terminology accuracy"""

def initialize_supabase() -> Client:
    """Initialize Supabase client"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    print("\nInitializing Supabase:")
    print(f"URL valid: {'Yes' if supabase_url and supabase_url.startswith('https://') else 'No'}")
    print(f"Key valid format: {'Yes' if supabase_key and len(supabase_key) > 20 else 'No'}")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials")
        
    return create_client(supabase_url, supabase_key)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extract_procedure_steps(image_path: str = None) -> List[Dict[str, str]]:
    """Extract ordered steps by phase from a surgical checklist using GPT-4 Vision."""
    try:
        # Use the ROOT_DIR to find the image
        image_path = ROOT_DIR / 'hospital_pdf' / 'data' / 'surgicalchecklist.jpeg'
            
        print(f"Looking for image at: {image_path}")
        print(f"File exists: {image_path.exists()}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found at {image_path}")
            
        print(f"Reading image...")
        base64_image = encode_image(str(image_path))
        
        print("Making GPT-4 Vision API call...")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_ROLE
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the ordered steps by phase from this surgical checklist."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=4096
        )
        
        print("Received GPT response, parsing steps...")
        response_text = completion.choices[0].message.content
        print(f"Raw response:\n{response_text[:200]}...")  # Print first 200 chars
        
        # Parse the response into ordered steps by phase
        steps = []
        current_phase = None
        current_order = 0
        
        for line in response_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Reset order counter for new phase
            if line.startswith('##') or line.endswith(':'):
                current_phase = line.replace('#', '').replace(':', '').strip().lower()
                current_order = 0
                continue
                
            if line[0].isdigit():
                current_order += 1
                number, description = line.split('.', 1)
                steps.append({
                    'requirement': description.strip(),
                    'phase': current_phase,
                    'order': current_order,
                    'completion_status': False  # Default to not completed
                })
        
        print(f"Parsed {len(steps)} steps")
        print("Sample step:", steps[0] if steps else "No steps found")
        return steps
        
    except Exception as e:
        print(f"Error extracting procedure steps: {str(e)}")
        return None

def store_procedure_steps(steps: List[Dict[str, str]]) -> bool:
    """
    Store procedure steps in treehacks_reqs table.
    
    Args:
        steps (List[Dict]): List of steps with 'requirement', 'phase', and 'order' fields
        
    Returns:
        bool: Success status
    """
    try:
        # Filter to only include the required fields
        formatted_steps = [
            {
                'requirement': step['requirement'],
                'phase': step['phase'],
                'order': step['order']
            }
            for step in steps
        ]
        
        return bool(upload_requirements(formatted_steps))
        
    except Exception as e:
        print(f"Error storing procedure steps: {str(e)}")
        return False

def get_procedure_steps(procedure_name: str) -> List[Dict[str, str]]:
    """
    Retrieve ordered procedure steps from Supabase.
    
    Args:
        procedure_name (str): Name of the surgical procedure
        
    Returns:
        List[Dict[str, str]]: Ordered list of procedure steps
    """
    try:
        supabase = initialize_supabase()
        
        # Get steps ordered by step_order
        response = supabase.table('surgical_steps')\
            .select('*')\
            .eq('procedure_name', procedure_name)\
            .order('step_order')\
            .execute()
            
        return response.data
        
    except Exception as e:
        print(f"Error retrieving procedure steps: {str(e)}")
        return None

def test_procedure_processing():
    """Test function for procedure step processing"""
    # Debug prints for environment variables
    print("Starting test procedure processing...")
    
    # Test data with explicit ordering
    test_requirements = [
        {
            "requirement": "Verify patient identity and confirm surgical site",
            "phase": "pre-op",
            "order": 1
        },
        {
            "requirement": "Confirm all necessary equipment is present and sterile",
            "phase": "pre-op",
            "order": 2
        },
        {
            "requirement": "Perform initial incision",
            "phase": "intra-op",
            "order": 1
        },
        {
            "requirement": "Monitor vital signs throughout procedure",
            "phase": "intra-op",
            "order": 2
        },
        {
            "requirement": "Verify instrument and sponge count",
            "phase": "post-op",
            "order": 1
        },
        {
            "requirement": "Document all post-operative instructions",
            "phase": "post-op",
            "order": 2
        }
    ]
    
    print("\nUploading test requirements...")
    success = upload_requirements(test_requirements)
    print(f"Upload success: {success}")
    
    if success:
        print("\nRetrieving requirements by phase:")
        for phase in ['pre-op', 'intra-op', 'post-op']:
            print(f"\n{phase.upper()} Requirements:")
            phase_reqs = get_requirements_by_phase(phase)
            if phase_reqs:
                for req in phase_reqs:
                    print(f"{req['order']}. {req['requirement']}")

if __name__ == "__main__":
    # Provide the full path to your PDF if it's in a different location
    pdf_path = ROOT_DIR / 'hospital_pdf' / 'data' / 'surgicalchecklist.pdf'
    extract_procedure_steps(str(pdf_path))