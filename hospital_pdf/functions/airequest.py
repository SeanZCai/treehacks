from openai import OpenAI
import base64
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import time
import PyPDF2

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI with the API key
client = OpenAI(api_key = os.environ['OPENAI_API_KEY'])

# System role definition
SYSTEM_ROLE = """You are an AI assistant specifically designed to answer questions based on provided PDF documents and guidelines.
Your primary responsibilities are:
1. Only answer questions using information directly found in the provided PDF content
2. If the PDF content doesn't contain enough information to confidently answer the question, respond with 'n'
3. Do not use external knowledge or make assumptions beyond what's in the PDF
4. Be precise and direct in your answers, citing specific sections when possible
5. If multiple interpretations are possible from the PDF content, respond with 'n' to ensure safety

Remember: When in doubt or if information is not explicitly stated in the PDF, always respond with 'n'."""

def call_openai_live(prompt_question, prompt_content, pdf_path=None):
    """Live/immediate OpenAI API call for single requests with optional PDF context"""
    try:
        # Prepare the content message
        content_message = prompt_question + prompt_content
        
        # If PDF is provided, add its content to the message
        if pdf_path and os.path.exists(pdf_path):
            print("Processing PDF file...")
            try:
                # Read PDF content
                with open(pdf_path, 'rb') as file:
                    print("Reading PDF...")
                    pdf_reader = PyPDF2.PdfReader(file)
                    pdf_text = ""
                    total_pages = len(pdf_reader.pages)
                    
                    for i, page in enumerate(pdf_reader.pages):
                        print(f"Processing page {i+1}/{total_pages}")
                        pdf_text += page.extract_text() + "\n"
                
                content_message = f"PDF Content:\n{pdf_text}\n\nQuestion:\n{content_message}"
                print("PDF processing complete")
            
            except Exception as pdf_error:
                print(f"Error processing PDF: {pdf_error}")
                return "Error processing PDF"

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
        
        return completion.choices[0].message.content

    except Exception as error:
        print("Error during OpenAI call:", error)
        return f"Error during API call: {str(error)}"