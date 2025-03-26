#!/usr/bin/env python3
"""
PDF to XMind-style PDF Converter
Main script to coordinate the conversion process
"""

import argparse
import os
import sys
from src.pdf_processor import PDFProcessor
from src.content_analyzer import ContentAnalyzer
from src.visualizer import MindMapVisualizer

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert PDF files to XMind-style mind map PDF')
    parser.add_argument('input_files', nargs='+', help='Input PDF files to process')
    parser.add_argument('-o', '--output', default='mindmap_output.pdf', help='Output PDF file name')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def ensure_dependencies():
    """Ensure necessary dependencies are installed"""
    try:
        import transformers
        print("Transformers library already installed.")
    except ImportError:
        print("Installing required transformers library. This may take a few minutes...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                             "transformers", "torch", "sentencepiece"])
        print("Transformers installed successfully.")

def main():
    # Ensure dependencies
    ensure_dependencies()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Validate input files
    for file_path in args.input_files:
        if not os.path.exists(file_path):
            print(f"Error: File not found - {file_path}")
            return
        if not file_path.lower().endswith('.pdf'):
            print(f"Error: Not a PDF file - {file_path}")
            return
    
    # Process PDF files
    pdf_processor = PDFProcessor()
    document_data = []
    
    for file_path in args.input_files:
        print(f"Processing {file_path}...")
        text_content = pdf_processor.extract_text(file_path)
        document_data.append({
            'file_path': file_path,
            'text_content': text_content
        })
    
    # Analyze content
    print("Analyzing content using transformer models (this may take a moment)...")
    analyzer = ContentAnalyzer()
    hierarchy = analyzer.generate_hierarchy(document_data)
    
    # Create mind map visualization
    print("Generating mind map PDF...")
    visualizer = MindMapVisualizer()
    if args.debug:
        visualizer.debug_mode = True
    visualizer.create_mindmap(hierarchy, args.output)
    
    print(f"Mind map PDF created: {args.output}")

if __name__ == "__main__":
    main()