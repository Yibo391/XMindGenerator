"""
Content Analyzer Module
Analyzes PDF text content to identify hierarchical structure and key elements
"""

import re
import nltk
from nltk.tokenize import sent_tokenize
from collections import defaultdict

class ContentAnalyzer:
    def __init__(self):
        # Download required NLTK data if not already present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def generate_hierarchy(self, document_data):
        """
        Generate a hierarchical structure from document data
        
        Args:
            document_data (list): List of dictionaries containing file paths and text content
            
        Returns:
            dict: Hierarchical structure suitable for mind map generation
        """
        # Create a mind map structure
        mind_map = {
            'central_topic': 'Document Summary',
            'main_topics': []
        }
        
        # Process each document
        for doc_index, doc in enumerate(document_data):
            file_name = doc['file_path'].split('/')[-1]
            text_content = doc['text_content']
            
            # Create a main topic for each document
            main_topic = {
                'text': f"Document {doc_index + 1}: {file_name}",
                'subtopics': []
            }
            
            # Extract key sections and headings
            sections = self._extract_sections(text_content)
            
            # If no sections found, use key sentences
            if not sections:
                key_sentences = self._extract_key_sentences(text_content)
                for sentence in key_sentences:
                    main_topic['subtopics'].append({
                        'text': sentence,
                        'subtopics': []
                    })
            else:
                for section_title, content in sections.items():
                    subtopic = {
                        'text': section_title,
                        'subtopics': []
                    }
                    
                    # Add key points from section as subtopics
                    key_points = self._extract_key_points(content)
                    for point in key_points:
                        subtopic['subtopics'].append({
                            'text': point
                        })
                    
                    main_topic['subtopics'].append(subtopic)
            
            mind_map['main_topics'].append(main_topic)
        
        return mind_map
    
    def _extract_sections(self, text_content):
        """
        Extract sections based on headings found in the text
        """
        sections = {}
        current_section = None
        current_content = []
        
        # Combine all pages' text
        if isinstance(text_content, dict):
            all_text = "\n".join([text_content[page] for page in sorted(text_content.keys())])
        else:
            all_text = text_content
        
        # Simple heading pattern (may need to be adjusted)
        heading_pattern = re.compile(r'^(?:\d+[\.\s]+)?([A-Z][^.!?]*?)$', re.MULTILINE)
        
        lines = all_text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line looks like a heading
            heading_match = heading_pattern.match(line)
            
            if heading_match and len(line) < 100:  # Heading should not be too long
                # If we had a previous section, add it to sections
                if current_section:
                    sections[current_section] = "\n".join(current_content)
                
                # Start new section
                current_section = line
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section:
            sections[current_section] = "\n".join(current_content)
            
        return sections
    
    def _extract_key_sentences(self, text_content):
        """
        Extract key sentences from text when no clear sections are found
        """
        # Combine all pages' text
        if isinstance(text_content, dict):
            all_text = "\n".join([text_content[page] for page in sorted(text_content.keys())])
        else:
            all_text = text_content
            
        # Tokenize into sentences
        sentences = sent_tokenize(all_text)
        
        # Filter to keep only reasonably sized sentences
        valid_sentences = [s for s in sentences if 20 < len(s) < 200]
        
        # Limit to 10 sentences for readability
        return valid_sentences[:10]
    
    def _extract_key_points(self, section_text):
        """
        Extract key points from a section's text
        """
        # For now, just use sentences as key points
        sentences = sent_tokenize(section_text)
        
        # Filter to meaningful sentences (not too short or long)
        key_points = [s for s in sentences if 20 < len(s) < 150]
        
        # Limit number of points to avoid overwhelming the mind map
        return key_points[:5]