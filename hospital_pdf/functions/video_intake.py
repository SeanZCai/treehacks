from pathlib import Path
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# System role definition for surgical context
SURGICAL_SYSTEM_ROLE = """You are an experienced surgical aide AI assistant, trained to:
1. Carefully observe and analyze surgical procedures
2. Identify any deviations from standard surgical protocols
3. Point out potential safety concerns or discrepancies
4. Monitor proper sterile technique and instrument handling
5. Pay attention to team communication and coordination
6. Note any unusual events or complications
7. Verify that surgical steps are being followed in the correct order
8. Monitor patient positioning and equipment setup

If you notice any concerning issues or safety risks, clearly highlight them with [ALERT] tags.
If something appears to deviate from standard protocol but isn't necessarily dangerous, mark it with [NOTE].
If you're uncertain about something you observe, explicitly state your uncertainty with [UNCERTAIN].

Always maintain a professional, clear, and precise communication style focused on patient safety."""

def process_surgical_video(video_data: bytes, conversation_text: str = None) -> str:
    """
    Process a surgical video file using Gemini Pro for medical context analysis.
    
    Args:
        video_data (bytes): Video file data
        conversation_text (str, optional): Transcribed conversation from the operating room
        
    Returns:
        str: Detailed analysis of the surgical procedure
    """
    try:
        print("Starting surgical video analysis...")
        
        # Create a temporary file-like object for the video
        video_buffer = BytesIO(video_data)
        
        # Initialize Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-pro-vision')
        
        print("Processing video with Gemini...")
        
        # Prepare content list with system role
        contents = [{
            "role": "system",
            "content": SURGICAL_SYSTEM_ROLE
        }]
        
        # Add conversation context if provided
        if conversation_text:
            print("Including conversation context in analysis...")
            contents.append({
                "role": "user",
                "content": f"Operating Room Conversation Context:\n{conversation_text}"
            })
        
        # Add video analysis request
        contents.append({
            "role": "user",
            "content": "Please analyze this surgical video segment and provide a detailed assessment of the procedure, noting any concerns or discrepancies.",
            "video": video_buffer
        })
        
        # Generate content with all context
        response = model.generate_content(
            contents=contents,
            generation_config={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
            },
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK",
            }
        )
        
        print("Video analysis complete")
        return response.text
        
    except Exception as e:
        error_msg = f"Error processing surgical video: {str(e)}"
        logging.error(error_msg)
        print(error_msg)
        return None

def test_video_analysis(test_video_path: str) -> None:
    """
    Test function for the video analysis system
    
    Args:
        test_video_path (str): Path to a test video file
    """
    try:
        print("Starting video analysis test...")
        result = process_surgical_video(test_video_path)
        
        if result:
            print("\nAnalysis Results:")
            print("-" * 50)
            print(result)
            print("-" * 50)
        else:
            print("Test failed: No analysis results received")
            
    except Exception as e:
        print(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    # Example usage
    test_video_path = "path/to/test/surgical_video.mp4"
    test_video_analysis(test_video_path)
