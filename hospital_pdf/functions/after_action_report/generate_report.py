from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import json
from datetime import datetime
from ..conversation_intake import test_compliance_processing
from .collect_data import synthesize_post_surgery_report
import os

def create_section_header(text):
    """Create a styled section header"""
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.HexColor('#2E5A88')
    )
    return Paragraph(text, header_style)

def create_content_paragraph(text):
    """Create a styled content paragraph"""
    styles = getSampleStyleSheet()
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=10
    )
    return Paragraph(text, content_style)

def format_data_table(data):
    """Format data into a table structure"""
    if not data:
        return None
    
    # Convert data to list of lists for table
    table_data = [[k, str(v)] for k, v in data.items()]
    
    # Create table with styling
    table = Table(table_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2E5A88')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC'))
    ]))
    return table

def generate_pdf_report(report_data, output_path):
    """Generate a PDF report from the synthesized data"""
    print("Starting PDF generation...")
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Initialize story (content elements)
    story = []
    
    # Add title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1B365D')
    )
    title = Paragraph("Post-Surgery Report", title_style)
    story.append(title)
    
    # Add timestamp
    timestamp = Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles['Normal']
    )
    story.append(timestamp)
    story.append(Spacer(1, 20))
    
    # Add synthesized report content
    if isinstance(report_data, str):
        # If report_data is a string, split it into sections
        sections = report_data.split('\n\n')
        for section in sections:
            if section.strip():
                story.append(create_content_paragraph(section))
                story.append(Spacer(1, 10))
    elif isinstance(report_data, dict):
        # If report_data is a dictionary, process each section
        for section_title, content in report_data.items():
            story.append(create_section_header(section_title.replace('_', ' ').title()))
            if isinstance(content, (dict, list)):
                table = format_data_table(content if isinstance(content, dict) else {str(i): item for i, item in enumerate(content)})
                if table:
                    story.append(table)
            else:
                story.append(create_content_paragraph(str(content)))
            story.append(Spacer(1, 20))
    
    # Build the PDF
    try:
        doc.build(story)
        print(f"PDF report generated successfully at: {output_path}")
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

def run_report_generation(conversation_text=None):
    """Main function to run the entire report generation process"""
    print("Starting post-surgery report generation process...")
    
    try:
        # Create output directory if it doesn't exist
        output_dir = "generated_reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"post_surgery_report_{timestamp}.pdf")
        
        # Process conversation if provided
        if conversation_text:
            print("Processing conversation text...")
            compliance_results = test_compliance_processing(conversation_text)
            if compliance_results:
                print("Compliance processing complete.")
        
        # Synthesize report
        print("Synthesizing post-surgery report...")
        synthesized_report = synthesize_post_surgery_report()
        
        if synthesized_report:
            print("Report synthesis complete. Generating PDF...")
            success = generate_pdf_report(synthesized_report, output_path)
            
            if success:
                return output_path
            else:
                print("Failed to generate PDF report.")
                return None
        else:
            print("Failed to synthesize report.")
            return None
            
    except Exception as e:
        print(f"Error in report generation process: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    output_file = run_report_generation()
    if output_file:
        print(f"Report generated successfully at: {output_file}")
    else:
        print("Report generation failed.")
