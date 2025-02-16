from .supabaseFunctions import initialize_supabase
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(
    filename='checklist_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_requirement_status(requirement: str) -> bool:
    """
    Update the completion status of a specific requirement from False to True.
    
    Args:
        requirement (str): The requirement text to search for
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        logging.info(f"Starting update process for requirement: {requirement[:100]}...")
        print(f"Starting update process for requirement: {requirement[:100]}...")
        
        # Initialize Supabase client
        logging.info("Initializing Supabase client...")
        supabase = initialize_supabase()
        
        # Log the current state before update
        current_state = supabase.table('treehacks_reqs') \
            .select('*') \
            .eq("requirement", requirement) \
            .execute()
        
        if current_state.data:
            logging.info(f"Current requirement state: {current_state.data[0]}")
            print(f"Found existing requirement with ID: {current_state.data[0].get('id')}")
        else:
            logging.warning(f"No existing requirement found matching: {requirement[:100]}")
            print(f"Warning: No existing requirement found matching: {requirement[:100]}")
        
        # Update the requirement's completion status
        logging.info("Attempting to update completion status...")
        result = supabase.table('treehacks_reqs') \
            .update({"completion_status": True}) \
            .eq("requirement", requirement) \
            .execute()
            
        # Check if update was successful
        if result.data:
            success_msg = f"Successfully updated status for: {requirement[:100]}"
            logging.info(success_msg)
            print(success_msg)
            
            # Log the updated state
            updated_state = supabase.table('treehacks_reqs') \
                .select('*') \
                .eq("requirement", requirement) \
                .execute()
            
            if updated_state.data:
                logging.info(f"Updated requirement state: {updated_state.data[0]}")
                print(f"Updated requirement state - completion_status: {updated_state.data[0].get('completion_status')}")
            
            return True
        else:
            error_msg = f"No matching requirement found for: {requirement[:100]}"
            logging.warning(error_msg)
            print(error_msg)
            return False
            
    except Exception as e:
        error_msg = f"Error updating requirement status: {str(e)}"
        logging.error(error_msg)
        print(error_msg)
        
        # Log additional error details if available
        if hasattr(e, 'response'):
            logging.error(f"Response status: {e.response.status_code}")
            logging.error(f"Response body: {e.response.text}")
            
        return False

if __name__ == "__main__":
    # Test the function with a sample requirement
    test_requirement = "Confirm patient's identity."
    print("\nTesting update_requirement_status function:")
    print("-" * 50)
    success = update_requirement_status(test_requirement)
    print(f"\nUpdate {'successful' if success else 'failed'}")
