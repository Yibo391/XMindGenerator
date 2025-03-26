"""
Utility functions for the PDF to XMind converter
"""

def validate_pdf(file_path):
    """
    Validate if a file is a PDF file
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if file is a valid PDF, False otherwise
    """
    if not file_path.lower().endswith('.pdf'):
        return False
        
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            # Check for PDF file signature
            if header == b'%PDF-':
                return True
    except Exception:
        pass
        
    return False