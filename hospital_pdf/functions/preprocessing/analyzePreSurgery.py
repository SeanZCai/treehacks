import os
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv
import glob
import base64
from supabase import create_client
from datetime import datetime

load_dotenv()

def load_and_encode_images(path, max_images=10):
    """Load and encode images from folder or single file"""
    encoded_images = []
    
    print(f"Processing path: {path}")
    
    # Check if path is a directory or file
    if os.path.isfile(path):
        if path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            try:
                with open(path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    encoded_images.append(encoded)
                    print(f"Successfully encoded: {path}")
            except Exception as e:
                print(f"Error loading image {path}: {e}")
    else:
        image_files = glob.glob(os.path.join(path, "*.jpg")) + \
                     glob.glob(os.path.join(path, "*.jpeg")) + \
                     glob.glob(os.path.join(path, "*.png")) + \
                     glob.glob(os.path.join(path, "*.webp"))
        
        print(f"Found files in directory: {image_files}")
        
        for img_path in image_files[:max_images]:
            try:
                with open(img_path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    encoded_images.append(encoded)
                    print(f"Successfully encoded: {img_path}")
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")
    
    return encoded_images

def update_supabase(description):
    """Update Supabase table with analysis"""
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    # Clear the table
    print("Clearing previous data...")
    supabase.table('preprocessing').delete().neq('id', 0).execute()
    
    # Insert new description
    print("Uploading new analysis...")
    data = {
        'description': description
    }
    result = supabase.table('preprocessing').insert(data).execute()
    print("Successfully updated Supabase")
    return result

def analyze_pre_surgery_compliance(encoded_images):
    """Analyze pre-surgery images for compliance issues"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """You are a medical compliance expert analyzing a pre-surgery scene. Provide a detailed analysis in two parts:

Part 1 - Scene Description:
List everything you observe in the scene, including:
- Visible equipment and instruments
- Staff members and their positions
- Room setup and configuration
- Patient positioning (if visible)
- Documentation and paperwork
- PPE and sterile equipment

Part 2 - Compliance Analysis:
Based on what you observed above, list:
- Proper compliance measures being followed
- Clear violations or issues that need attention
- Missing required elements
- Improper positioning or setup

Be extremely specific and detailed. Describe exactly what you see.
Do not make recommendations or use hypothetical language.
Do not say "I'm unable to analyze" - just describe what is visible in the image."""
                }
            ]
        }
    ]
    
    for encoded_image in encoded_images:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
        })
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing images: {e}"

def main():
    load_dotenv()
    
    if len(sys.argv) != 2:
        print("Usage: python analyzePreSurgery.py <path_to_image_or_folder>")
        return
        
    path = sys.argv[1]
    
    print("Loading images...")
    encoded_images = load_and_encode_images(path)
    
    if not encoded_images:
        print("No images found in specified path")
        return
    
    print(f"Analyzing {len(encoded_images)} images...")
    
    # Get analysis
    analysis = analyze_pre_surgery_compliance(encoded_images)
    
    # Update Supabase
    update_supabase(analysis)
    
    # Also save locally for reference
    with open("pre_surgery_report.txt", "w") as f:
        f.write("Pre-Surgery Analysis Report\n")
        f.write("=========================\n")
        f.write(analysis)
    
    print("\nAnalysis complete! Check Supabase for results.")
    print("Local copy saved to pre_surgery_report.txt")

if __name__ == "__main__":
    import sys
    main() 