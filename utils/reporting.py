from fpdf import FPDF
import datetime
import os

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

class PhishingReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Phishing Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def sanitize_text(text):
    """
    Sanitizes text to be compatible with default FPDF fonts (latin-1).
    Replaces unsupported characters with '?'.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    
    # Encode to latin-1 and ignore characters that cannot be represented
    # This handles emojis and non-latin scripts by replacing them with '?'
    try:
        return text.encode('latin-1', 'replace').decode('latin-1')
    except Exception as e:
        print(f"Error sanitizing text: {e}")
        return "Error: Could not sanitize text"

def generate_pdf_report(detection_type, input_data, prediction, score, explanation):
    print("Generating PDF Report...") # Debug print to confirm reload
    try:
        pdf = PhishingReport()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, txt=sanitize_text(f"Analysis Type: {detection_type}"), ln=True)
        pdf.set_font("helvetica", size=12)
        
        # Ensure input_data is a string and limited length
        input_str = str(input_data)
        if len(input_str) > 500:
            input_str = input_str[:500] + "..."
            
        pdf.multi_cell(pdf.epw, 10, txt=sanitize_text(f"Input Data: {input_str}"))
        pdf.ln(5)
        
        status = "PHISHING" if prediction else "SAFE"
        if prediction:
            pdf.set_text_color(255, 0, 0)
        else:
            pdf.set_text_color(0, 128, 0)
        pdf.cell(0, 10, txt=sanitize_text(f"Result: {status}"), ln=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(0, 10, txt=sanitize_text(f"Confidence Score: {score*100:.2f}%"), ln=True)
        pdf.ln(10)
        
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, txt=sanitize_text("AI Explanation Factors:"), ln=True)
        pdf.set_font("helvetica", size=12)
        
        if explanation and 'key_factors' in explanation:
            for factor in explanation['key_factors']:
                pdf.multi_cell(pdf.epw, 10, txt=sanitize_text(f"- {factor}"))
        
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, txt=sanitize_text("Security Recommendations:"), ln=True)
        pdf.set_font("helvetica", size=12)
        
        if explanation and 'recommendations' in explanation:
            for rec in explanation['recommendations']:
                pdf.multi_cell(pdf.epw, 10, txt=sanitize_text(f"- {rec}"))
            
        report_name = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = os.path.join(LOGS_DIR, report_name)
        pdf.output(report_path)
        return report_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Return a dummy path or raise to not crash the app logic?
        # Streamlit will show the error trace if we raise
        raise e
