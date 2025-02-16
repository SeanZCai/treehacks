from hospital_pdf.functions.combinePDF import combine_pdfs
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Combine two PDF files into one.')
    parser.add_argument('pdf1', help='Path to the first PDF file')
    parser.add_argument('pdf2', help='Path to the second PDF file')
    parser.add_argument('output', help='Path for the output combined PDF')

    # Parse arguments
    args = parser.parse_args()

    # Run the combination
    print(f"Attempting to combine:\n1. {args.pdf1}\n2. {args.pdf2}\nOutput: {args.output}")
    
    success = combine_pdfs(args.pdf1, args.pdf2, args.output)
    
    if not success:
        print("PDF combination failed. Please check the error messages above.")
        exit(1)

if __name__ == "__main__":
    main() 