from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict
from .supabase_functions.supabaseFunctions import upload_requirements, get_requirements_by_phase, get_all_requirements
from pathlib import Path

# Get the project root directory (2 levels up from this file)
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_DIR / '.env'

# Load environment variables from the correct path
load_dotenv(ENV_PATH)

# Initialize OpenAI
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# System role for procedure step extraction
SYSTEM_ROLE = """You are an AI assistant specialized in analyzing surgical procedures and extracting ordered steps by phase.
Your primary responsibilities are:
1. Extract clear, sequential steps from surgical procedure descriptions
2. Categorize steps into appropriate phases: 'pre-op', 'intra-op', or 'post-op'
3. Maintain the exact order of steps within each phase
4. Ensure each step is clear, concise, and actionable
5. Include critical safety checks and verifications

Output format should be steps grouped by phase, where each step follows this pattern:
pre-op:
1. [Step description]
2. [Step description]

intra-op:
1. [Step description]
2. [Step description]

post-op:
1. [Step description]
2. [Step description]

Remember:
- Order within each phase is critically important
- Each step must be clear and specific
- Include safety checks where appropriate
- Maintain medical terminology accuracy"""

def extract_procedure_steps(procedure_text: str) -> List[Dict[str, str]]:
    """
    Extract ordered steps by phase from a surgical procedure description using GPT-4.
    
    Args:
        procedure_text (str): The surgical procedure description
        
    Returns:
        List[Dict[str, str]]: List of steps with their descriptions and phases
    """
    try:
        print("Extracting procedure steps...")
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,  # Low temperature for consistent, precise responses
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_ROLE
                },
                {
                    "role": "user",
                    "content": f"Extract the ordered steps by phase from this surgical procedure:\n\n{procedure_text}"
                }
            ]
        )
        
        # Parse the response into ordered steps by phase
        response_text = completion.choices[0].message.content
        steps = []
        current_phase = None
        
        for line in response_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for phase headers
            if line.lower().endswith(':'):
                current_phase = line.lower().rstrip(':')
                continue
                
            if current_phase and line[0].isdigit():
                # Split at first period after number
                number, description = line.split('.', 1)
                steps.append({
                    'requirement': description.strip(),
                    'phase': current_phase
                })
        
        return steps
        
    except Exception as e:
        print(f"Error extracting procedure steps: {str(e)}")
        return None

def store_procedure_steps(steps: List[Dict[str, str]]) -> bool:
    """
    Store procedure steps in treehacks_reqs table.
    
    Args:
        steps (List[Dict[str, str]]): List of steps with their descriptions and phases
        
    Returns:
        bool: Success status
    """
    try:
        return bool(upload_requirements(steps))
        
    except Exception as e:
        print(f"Error storing procedure steps: {str(e)}")
        return False

def get_procedure_steps_by_phase(phase: str) -> List[Dict]:
    """
    Retrieve ordered steps for a specific phase.
    
    Args:
        phase (str): The phase to retrieve ('pre-op', 'intra-op', or 'post-op')
        
    Returns:
        List[Dict]: Ordered list of steps for the specified phase
    """
    return get_requirements_by_phase(phase)

def get_all_procedure_steps() -> List[Dict]:
    """
    Retrieve all procedure steps, ordered by phase and creation time.
    
    Returns:
        List[Dict]: All procedure steps
    """
    return get_all_requirements()

def test_procedure_processing():
    """Test function for procedure step processing"""
    # Add multiple debug prints
    print("Starting test procedure processing...")
    print("Checking environment variables:")
    print(f"SUPABASE_URL: {'Set' if os.getenv('SUPABASE_URL') else 'Not Set'}")
    print(f"SUPABASE_SERVICE_KEY: {os.getenv('SUPABASE_SERVICE_KEY')[:5] if os.getenv('SUPABASE_SERVICE_KEY') else 'Not Set'}...")
    
    test_procedure = """
    Appendectomy Procedure:
    Pre-operative:
    Verify patient identity and surgical site.
    Administer appropriate anesthesia.
    Position patient appropriately.
    
    Intra-operative:
    Make McBurney incision in right lower quadrant.
    Dissect through subcutaneous tissue and external oblique aponeurosis.
    Split muscle fibers of internal oblique and transversus.
    Identify and isolate appendix.
    Ligate and divide mesoappendix and appendiceal vessels.
    Remove appendix at base.
    Close cecal stump.
    Irrigate surgical site.
    Close layers anatomically.
    
    Post-operative:
    Verify instrument and sponge count.
    Apply sterile dressing.
    Monitor vital signs.
    Document procedure details.
    """
    
    print("Testing procedure step extraction...")
    steps = extract_procedure_steps(test_procedure)
    
    if steps:
        print("\nExtracted Steps:")
        for step in steps:
            print(f"[{step['phase']}] {step['requirement']}")
            
        # Store steps
        success = store_procedure_steps(steps)
        print(f"\nStorage success: {success}")
        
        # Retrieve steps by phase
        for phase in ['pre-op', 'intra-op', 'post-op']:
            phase_steps = get_procedure_steps_by_phase(phase)
            if phase_steps:
                print(f"\n{phase.upper()} Steps:")
                for step in phase_steps:
                    print(f"- {step['requirement']}")
    
if __name__ == "__main__":
    test_procedure_processing()