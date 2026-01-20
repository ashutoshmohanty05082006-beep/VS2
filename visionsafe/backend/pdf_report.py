"""
PDF Report generation.
Converts violation data to professional PDF reports.
"""

from fpdf import FPDF
import pandas as pd
from datetime import datetime
from typing import Optional


def create_pdf_report(df: pd.DataFrame) -> Optional[bytes]:
    """
    Generate PDF compliance report from violation data.
    
    Args:
        df: DataFrame with violation records
        
    Returns:
        PDF bytes, or None if generation failed
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt="VisionSafe Compliance Report", ln=True, align='C')
        pdf.ln(10)
        
        # Timestamp
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, 
                txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                ln=True, align='C')
        pdf.ln(10)
        
        # Summary Stats
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(200, 8, f"Total Violations: {len(df)}", ln=True)
        pdf.cell(200, 8, f"Unique Workers: {df['ID'].nunique()}", ln=True)
        pdf.ln(5)
        
        # Table
        pdf.set_font("Arial", style="B", size=10)
        col_width = 45
        headers = ["Time", "ID", "Violation", "Strikes"]
        
        for header in headers:
            pdf.cell(col_width, 10, header, border=1)
        pdf.ln()
        
        pdf.set_font("Arial", size=9)
        for _, row in df.iterrows():
            time_txt = str(row['Time'])[:19]
            id_txt = str(row['ID'])
            vio_txt = str(row['Violation'])[:20]
            strike_txt = str(row['Strikes'])
            
            pdf.cell(col_width, 10, time_txt, border=1)
            pdf.cell(col_width, 10, id_txt, border=1)
            pdf.cell(col_width, 10, vio_txt, border=1)
            pdf.cell(col_width, 10, strike_txt, border=1)
            pdf.ln()
        
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def generate_pdf_file(df: pd.DataFrame, filepath: str = "VisionSafe_Report.pdf") -> Optional[str]:
    """
    Generate PDF report and save to file.
    
    Args:
        df: DataFrame with violation records
        filepath: Output file path
        
    Returns:
        File path if successful, None otherwise
    """
    try:
        pdf_bytes = create_pdf_report(df)
        if pdf_bytes:
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)
            return filepath
        return None
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return None
