from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict
from .supabase_functions.supabaseFunctions import initialize_supabase
import json
from .perplexity import search_and_answer
from .supabase_functions.checklist_update import update_requirement_status

# Load environment variables
load_dotenv()

# Initialize OpenAI with the API key
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Modified system role for compliance checking
SYSTEM_ROLE = """You are an AI assistant specifically designed to monitor surgical room compliance by analyzing conversation context.

Your ONLY role is to determine if a given compliance requirement (presented as a question) is satisfied by the conversation context.
You must ONLY respond with one of these three letters:

A - The conversation context DIRECTLY satisfies the compliance requirement
B - The conversation context contains a question ABOUT this compliance requirement but doesn't satisfy it
C - The conversation context is unrelated to this compliance requirement

Examples:
1. Requirement: "Has the patient stated their name?"
   Context: "My name is Henry Jones."
   Response: "A" (requirement satisfied)

2. Requirement: "Has the patient stated their name?"
   Context: "Doctor: Could you please state your name?"
   Response: "B" (asking about requirement but not satisfied)

3. Requirement: "Has the patient stated their name?"
   Context: "The surgery will take approximately two hours."
   Response: "C" (unrelated to requirement)

Rules:
1. ONLY return A, B, or C - no other characters or explanations
2. If in doubt between options, choose the more cautious response
3. Context must EXPLICITLY satisfy requirements for an 'A' response
4. Partial satisfaction of a requirement should be marked as 'B'
5. Any ambiguity should be marked as 'B'"""

def process_compliance_requirements(requirements: List[str], conversation_context: str) -> List[Dict[str, str]]:
    """
    Process multiple compliance requirements against conversation context.
    
    Args:
        requirements (List[str]): List of compliance requirements to check
        conversation_context (str): The conversation context to analyze
        
    Returns:
        List[Dict[str, str]]: List of results containing requirement and status (A/B/C)
    """
    try:
        print("Starting batch compliance check...")
        print(f"Processing {len(requirements)} requirements")
        print(f"Context length: {len(conversation_context)} characters")
        
        # Prepare the content message with all requirements
        content_message = f"""Conversation Context:
{conversation_context}

Please evaluate each of the following compliance requirements.
For each requirement, respond with ONLY A, B, or C according to the rules.
Format your response as a list, one letter per line, in order.

Compliance Requirements:
{chr(10).join(f"{i+1}. {req}" for i, req in enumerate(requirements))}

Remember: Respond ONLY with A, B, or C for each requirement, one per line."""
        
        print("Making OpenAI API call...")
        completion = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_ROLE
                },
                {
                    "role": "user",
                    "content": content_message
                }
            ]
        )
        
        # Process response
        response_lines = completion.choices[0].message.content.strip().split('\n')
        print(f"Received {len(response_lines)} responses")
        
        # Validate and pair responses with requirements
        results = []
        for i, (req, resp) in enumerate(zip(requirements, response_lines)):
            status = resp.strip()
            if status not in ['A', 'B', 'C']:
                print(f"Invalid response format for requirement {i+1}, defaulting to 'C'")
                status = 'C'
                
            results.append({
                "requirement": req,
                "status": status
            })
            
        return results
        
    except Exception as error:
        error_msg = f"Error processing compliance checks: {str(error)}"
        logging.error(error_msg)
        print(error_msg)
        return None

def test_compliance_processing(conversation_text: str):
    """
    Test function for the batch compliance checking system using real requirements from Supabase
    """
    try:
        # Get all requirements from Supabase
        supabase = initialize_supabase()
        result = supabase.table('treehacks_reqs') \
            .select('requirement') \
            .order('phase,order') \
            .execute()
            
        if not result.data:
            print("No requirements found in database")
            return
            
        # Extract requirements from result
        test_requirements = [item['requirement'] for item in result.data]
        
        results = process_compliance_requirements(test_requirements, conversation_text)
        
        if results:
            # Initialize a list to hold saved results across all requirements
            saved_results = []
            
            for result in results:
                requirement = result['requirement']
                status = result['status']
                
                print(f"\nProcessing requirement: {requirement[:50]}...")
                print(f"Status: {status}")
                
                if status == 'A':
                    print("✓ Requirement directly satisfied")
                    # Update the requirement status in Supabase
                    update_success = update_requirement_status(requirement)
                    saved_results.append(requirement)
                    if update_success:
                        print("✓ Requirement status updated in database")
                    else:
                        print("⚠ Failed to update requirement status in database")
                elif status == 'B':
                    print("⚠ Requirement needs clarification, querying Perplexity...")
                    perplexity_response = search_and_answer(
                        question=requirement,
                        context=conversation_text,
                        temperature=0.2
                    )
                    print(f"Perplexity response received: {perplexity_response[:100]}...")
                    # Return results as a structured dictionary instead of concatenating a list with a string
                    return perplexity_response + " " + ", ".join(saved_results)
                else:  # status == 'C'
                    print("➤ Requirement not relevant to current context")
            
            # If no "B" status was encountered, you may choose to return the saved results.
            return saved_results
        else:
            print("Test failed: No results received")
            return None
            
    except Exception as e:
        print(f"Error in test compliance processing: {str(e)}")
        return None

if __name__ == "__main__":
    test_compliance_processing() 