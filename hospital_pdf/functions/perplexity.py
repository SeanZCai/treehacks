from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client with Perplexity's base URL
client = OpenAI(
    api_key=os.environ.get('PERPLEXITY_API_KEY'),
    base_url="https://api.perplexity.ai",
)

def search_and_answer(question: str, context: str = "", temperature: float = 0.2) -> str:
    """
    Uses Perplexity's Sonar model to answer a question with optional context.
    
    Args:
        question (str): The question to be answered
        context (str, optional): Additional context to help guide the answer
        temperature (float, optional): Controls randomness in the response (0.0-2.0)
        
    Returns:
        str: The model's response or None if there's an error
    """
    try:
        print(f"Making Perplexity API request for question: {question[:50]}...")
        
        # Combine question and context if provided
        content = question
        if context:
            content = f"Context: {context}\n\nQuestion: {question}"
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Provide accurate, concise answers, while also maintaining that your output should resemble that of a conversational answer to the asker rather than a written researched response."
            },
            {
                "role": "user",
                "content": content
            }
        ]
        
        response = client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-chat",
            messages=messages,
            temperature=temperature,
            top_p=0.9,
            stream=False
        )
        
        print("Received response from Perplexity API")
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in Perplexity API call: {str(e)}")
        return None