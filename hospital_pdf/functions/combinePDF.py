from PyPDF2 import PdfMerger
import io

def combine_pdfs(pdf1_data: bytes, pdf2_data: bytes) -> bytes:
    """
    Combines two PDF files (in bytes format) into a single PDF file.
    
    Args:
        pdf1_data (bytes): First PDF file as bytes
        pdf2_data (bytes): Second PDF file as bytes
        
    Returns:
        bytes: Combined PDF as bytes, or None if an error occurred
    """
    try:
        print("Starting PDF combination process...")
        
        # Create PDF merger object
        merger = PdfMerger()
        
        # Convert bytes to file-like objects
        pdf1_file = io.BytesIO(pdf1_data)
        pdf2_file = io.BytesIO(pdf2_data)
        
        # Add the PDFs to merger
        print("Adding first PDF...")
        merger.append(pdf1_file)
        print("Adding second PDF...")
        merger.append(pdf2_file)
        
        # Create output buffer
        output_buffer = io.BytesIO()
        
        # Write to output buffer
        print("Writing combined PDF...")
        merger.write(output_buffer)
        
        # Close the merger and input files
        merger.close()
        pdf1_file.close()
        pdf2_file.close()
        
        # Get the bytes from the buffer
        output_buffer.seek(0)
        combined_pdf = output_buffer.getvalue()
        output_buffer.close()
        
        print("Successfully created combined PDF in memory")
        return combined_pdf
        
    except Exception as e:
        print(f"An error occurred while combining PDFs: {str(e)}")
        return None