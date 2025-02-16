from functions.perplexity import search_and_answer
import argparse

def main():
    parser = argparse.ArgumentParser(description='Search and answer questions using Perplexity API.')
    parser.add_argument('--question', required=True, 
                        help='The question to be answered')
    parser.add_argument('--context', default="",
                        help='Optional context to guide the answer')
    parser.add_argument('--temperature', type=float, default=0.2,
                        help='Temperature for response randomness (0.0-2.0)')
    
    args = parser.parse_args()
    
    print("Making Perplexity search request...")
    response = search_and_answer(
        question=args.question,
        context=args.context,
        temperature=args.temperature
    )
    
    if response:
        print("\nPerplexity Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    else:
        print("Request failed. Please check the error messages above.")
        exit(1)

if __name__ == "__main__":
    main() 