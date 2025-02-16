from combinePDF import combine_pdfs
from run_ai_request import make_ai_request
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Combine PDFs and process with AI.')
    parser.add_argument('pdf1', help='Path to the first PDF file')
    parser.add_argument('pdf2', help='Path to the second PDF file')
    parser.add_argument('output', help='Path for the output combined PDF')
    parser.add_argument('--model', default="gpt-3.5-turbo", 
                        help='The OpenAI model to use (default: gpt-3.5-turbo)')
    parser.add_argument('--temperature', type=float, default=0.7,
                        help='Temperature setting (0.0-1.0)')

    # Parse arguments
    args = parser.parse_args()

    # First combine the PDFs
    print("Step 1: Combining PDFs...")
    success = combine_pdfs(args.pdf1, args.pdf2, args.output)
    
    if not success:
        print("PDF combination failed. Please check the error messages above.")
        exit(1)

    # Now make the AI request
    print("\nStep 2: Processing with AI...")
    prompt = f"I have combined two PDFs into one file at {args.output}. Please confirm this was successful."
    
    response = make_ai_request(prompt, args.model, args.temperature)
    
    if response:
        print("\nAI Confirmation:")
        print(response.choices[0].message.content)
    else:
        print("AI request failed. PDF combination was successful, but confirmation failed.")
        exit(1)

if __name__ == "__main__":
    main()