from functions.supabase.procedure_steps import extract_procedure_steps, store_procedure_steps
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent

def run_procedure_extraction():
    """Extract and store procedure steps from surgical checklist."""
    try:
        print("Starting procedure extraction and storage...")
        
        # Get the image path
        image_path = ROOT_DIR / 'data' / 'surgicalchecklist.jpeg'
        
        # Extract steps
        print("Extracting steps from checklist...")
        steps = extract_procedure_steps(str(image_path))
        
        if not steps:
            print("No steps were extracted!")
            return False
            
        print(f"Successfully extracted {len(steps)} steps")
        
        # Store steps
        print("Storing steps in database...")
        success = store_procedure_steps(steps)
        
        if success:
            print("Successfully stored all steps in database")
            return True
        else:
            print("Failed to store steps in database")
            return False
            
    except Exception as e:
        print(f"Error in procedure extraction pipeline: {str(e)}")
        return False

if __name__ == "__main__":
    run_procedure_extraction() 