from hospital_pdf.functions.airequest import call_openai_live
import argparse

def main():
    parser = argparse.ArgumentParser(description='Make a request to OpenAI API.')
    parser.add_argument('--prompt-question', required=True, 
                        help='The question part of the prompt')
    parser.add_argument('--prompt-content', required=True, 
                        help='The content to be analyzed')
    
    args = parser.parse_args()
    
    # Make the request
    print("Making AI request...")
    response = call_openai_live(args.prompt_question, args.prompt_content)
    
    if response:
        print("\nAI Response:")
        print(response)
    else:
        print("Request failed. Please check the error messages above.")
        exit(1)

if __name__ == "__main__":
    main() 