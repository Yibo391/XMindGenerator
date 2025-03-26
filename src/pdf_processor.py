"""
PDF Processor Module
Handles extraction of text and basic structure from PDF files
"""

import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text

class PDFProcessor:
    def __init__(self):
        pass
        
    def extract_text(self, pdf_path):
        """
        Extract text from a PDF file using PyPDF2 and pdfminer as backup
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            dict: Dictionary containing text content organized by page
        """
        text_by_page = {}
        
        # Try with PyPDF2 first (faster but less accurate)
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    
                    # If PyPDF2 fails to extract meaningful text, use pdfminer
                    if not text or len(text.strip()) < 50:
                        text = self._extract_with_pdfminer(pdf_path, i)
                        
                    text_by_page[i] = text
        except Exception as e:
            print(f"Error with PyPDF2: {e}")
            # Fall back to pdfminer for the whole document
            text_by_page = self._extract_all_with_pdfminer(pdf_path)
            
        return text_by_page
    
    def _extract_with_pdfminer(self, pdf_path, page_num):
        """Extract text from a specific page using pdfminer"""
        # Note: This is a simplified approach. pdfminer doesn't easily extract by page number
        # without additional configuration
        try:
            text = pdfminer_extract_text(pdf_path, page_numbers=[page_num])
            return text
        except Exception as e:
            print(f"Error with pdfminer on page {page_num}: {e}")
            return ""
    
    def _extract_all_with_pdfminer(self, pdf_path):
        """Extract text from entire PDF using pdfminer"""
        try:
            text = pdfminer_extract_text(pdf_path)
            # Since pdfminer returns the whole document, we'll split by form feeds as a simple
            # way to separate pages (not always accurate)
            pages = text.split('\f')
            return {i: page for i, page in enumerate(pages)}
        except Exception as e:
            print(f"Error with pdfminer: {e}")
            return {0: ""}