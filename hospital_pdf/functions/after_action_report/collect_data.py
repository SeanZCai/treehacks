# Function for audio analysis? (Optional)
import requests
import json
import openai
from functions.supabase_functions.supabaseFunctions import get_all_requirements, initialize_supabase
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI()  # This will automatically use OPENAI_API_KEY from environment

def get_conversations():
    try:
        # Requires frontend to be running
        response = requests.get('http://localhost:3000/api/conversations')
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching conversations: {e}")
        raise

def get_checklist_performance():
    """
    Retrieve checklist performance data from the 'treehacks_reqs' table.
    """
    try:
        print("Fetching checklist performance data from 'treehacks_reqs' table...")
        # Using the existing function from supabaseFunctions to get all requirements
        data = get_all_requirements()
        print("Checklist performance data fetched successfully.")
        return data
    except Exception as e:
        print(f"Error fetching checklist performance data: {e}")
        return None

def get_supabase_vision_data_interpretations():
    """
    Retrieve vision data interpretations from the 'surgery_data' table.
    """
    try:
        print("Fetching vision data interpretations from 'surgery_data' table...")
        supabase = initialize_supabase()
        response = supabase.table('surgery_data').select('*').execute()
        print("Vision data interpretations fetched successfully.")
        return response.data
    except Exception as e:
        print(f"Error fetching vision data interpretations: {e}")
        return None

def get_live_surgeon_metrics():
    """
    Retrieve live surgeon metrics data from the 'alerts' table.
    """
    try:
        print("Fetching live surgeon metrics data from 'alerts' table...")
        supabase = initialize_supabase()
        response = supabase.table('alerts').select('*').execute()
        print("Live surgeon metrics data fetched successfully.")
        return response.data
    except Exception as e:
        print(f"Error fetching live surgeon metrics data: {e}")
        return None
    
def get_audio_analysis():
    """
    Retrieve audio analysis data from the 'audio_analysis' table.
    """
    # TODO: Implement this function
    return None

def get_preprocessing_data():
    """
    Retrieve preprocessing data from the 'preprocessing' table.
    """
    try:
        print("Fetching preprocessing data from 'preprocessing' table...")
        supabase = initialize_supabase()
        response = supabase.table('preprocessing').select('*').execute()
        print("Preprocessing data fetched successfully.")
        return response.data
    except Exception as e:
        print(f"Error fetching preprocessing data: {e}")
        return None

def collect_post_surgery_report_data():
    """
    Collect data from various sources and compile it into one JSON object
    intended to be fed to OpenAI for post surgery report generation.
    """
    print("Starting data collection for post surgery report...")

    checklist_data = get_checklist_performance()
    vision_data = get_supabase_vision_data_interpretations()
    live_metrics_data = get_live_surgeon_metrics()
    preprocessing_data = get_preprocessing_data()

    report_data = {
        "checklistPerformance": checklist_data,
        "visionInterpretations": vision_data,
        "liveSurgeonMetrics": live_metrics_data,
        "preprocessingData": preprocessing_data
    }

    print("Data collection complete.")
    return report_data

def synthesize_post_surgery_report():
    """
    Synthesize the post-surgery report by feeding the collected data to the OpenAI API,
    which generates a detailed report.
    """
    print("Starting synthesis of post-surgery report via OpenAI API call...")

    # Collect the raw data
    collected_data = collect_post_surgery_report_data()
    if collected_data is None:
        print("No data collected for the report. Exiting synthesis.")
        return None

    # Create a detailed prompt containing the JSON data to guide the synthesis
    prompt = (
        "Synthesize the following post surgery data into a detailed and comprehensive report for medical review:\n\n"
        f"{json.dumps(collected_data, indent=2)}\n\n"
        "The report should summarize checklist performance, vision data interpretations, and live surgeon metrics in a clear, concise, and professional manner.\n"
        "The report should also generate a score assessment of the surgeon's performance based on the data."
    )

    print("Sending prompt to OpenAI ChatCompletion API...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical report synthesis assistant. Your task is to generate a comprehensive post-surgery report based on the provided data."
                },
                {"role": "user", "content": prompt}
            ]
        )
        synthesized_report = response.choices[0].message.content.strip()
        print("Post-surgery report synthesis complete.")
        return synthesized_report
    except Exception as e:
        print(f"Error during report synthesis: {e}")
        return None
