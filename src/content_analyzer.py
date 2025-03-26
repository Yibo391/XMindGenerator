"""
Content Analyzer Module with Transformer-based extraction
"""

import re
import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline
from collections import defaultdict

class ContentAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        # Initialize transformer models
        print("Loading transformer models for text analysis...")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.keyword_extractor = pipeline("ner", grouped_entities=True, model="dslim/bert-base-NER")
        
    def generate_hierarchy(self, document_data):
        """
        Generate a hierarchical structure using transformer models
        """
        mind_map = {
            'central_topic': 'Document Summary',
            'main_topics': []
        }
        
        for doc_index, doc in enumerate(document_data):
            file_name = doc['file_path'].split('/')[-1]
            text_content = doc['text_content']
            
            # Create main topic for the document
            main_topic = {
                'text': f"Document {doc_index + 1}: {file_name}",
                'subtopics': []
            }
            
            # Extract sections or generate them using transformer models
            all_text = self._combine_text_content(text_content)
            
            # First try to find natural sections in the document
            sections = self._extract_sections(all_text)
            
            if sections and len(sections) <= 12:
                # Use extracted sections
                for section_title, content in sections.items():
                    section_topic = {
                        'text': self._clean_text(section_title),
                        'subtopics': []
                    }
                    
                    # Summarize section content using transformers
                    key_points = self._summarize_text(content)
                    for point in key_points:
                        section_topic['subtopics'].append({
                            'text': point
                        })
                    
                    main_topic['subtopics'].append(section_topic)
            else:
                # If no clear sections, use transformer to generate topics
                chunks = self._split_text_into_chunks(all_text)
                
                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue
                        
                    # Generate a title for this chunk using keywords
                    title = self._generate_topic_title(chunk, i)
                    
                    chunk_topic = {
                        'text': title,
                        'subtopics': []
                    }
                    
                    # Extract key points from this chunk
                    key_points = self._summarize_text(chunk)
                    for point in key_points:
                        chunk_topic['subtopics'].append({
                            'text': point
                        })
                    
                    main_topic['subtopics'].append(chunk_topic)
                    
                    # Limit number of topics for readability
                    if len(main_topic['subtopics']) >= 10:
                        break
            
            mind_map['main_topics'].append(main_topic)
        
        return mind_map
    
    def _combine_text_content(self, text_content):
        """Combine text content from all pages"""
        if isinstance(text_content, dict):
            return "\n".join([text_content[page] for page in sorted(text_content.keys())])
        return text_content
    
    def _extract_sections(self, text):
        """Extract document sections using heading patterns"""
        sections = {}
        current_section = None
        current_content = []
        
        # Enhanced patterns for section detection
        heading_patterns = [
            r'^(\d+(\.\d+)*\s+[A-Z][^.!?]*?)$',  # Numbered sections
            r'^(Chapter|Section|CHAPTER|SECTION)\s+\d+[:\s]+([^.!?]+)$',  # Chapter/Section headers
            r'^([A-Z][A-Z\s]{2,30})$',  # ALL CAPS headings
            r'^([A-Z][a-z]+(\s+[A-Z][a-z]+){1,5})$'  # Title Case headings
        ]
        
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_heading = False
            heading_text = line
            
            # Check for heading patterns
            for pattern in heading_patterns:
                match = re.match(pattern, line)
                if match and len(line) < 100:
                    groups = match.groups()
                    heading_text = groups[-1] if groups[-1] and isinstance(groups[-1], str) else match.group(1)
                    heading_text = heading_text.strip()
                    is_heading = True
                    break
            
            if is_heading:
                # Store previous section
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                
                # Start new section
                current_section = heading_text
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content)
            
        return sections
    
    def _split_text_into_chunks(self, text, max_chunks=10, max_length=1000):
        """Split text into chunks suitable for transformer processing"""
        # First try to split by paragraphs
        paragraphs = text.split("\n\n")
        
        # If paragraphs are too short, combine them
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            if current_length + len(para) < max_length:
                current_chunk.append(para)
                current_length += len(para)
            else:
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                current_chunk = [para]
                current_length = len(para)
        
        # Add the last chunk
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        # If still too many chunks, combine further
        if len(chunks) > max_chunks:
            combined_chunks = []
            chunk_size = max(1, len(chunks) // max_chunks)
            
            for i in range(0, len(chunks), chunk_size):
                combined_chunks.append("\n\n".join(chunks[i:i+chunk_size]))
            
            chunks = combined_chunks[:max_chunks]
        
        return chunks
    
    def _summarize_text(self, text, max_points=4):
        """Use transformer model to summarize text into key points"""
        if not text or len(text) < 100:
            return ["No significant content to summarize"]
            
        try:
            # Limit length for transformer model
            text = text[:4000]  # Most models have max input length
            
            # Generate summary
            summary = self.summarizer(text, max_length=150, min_length=30, 
                                    do_sample=False)
            
            # Split into sentences
            if summary and summary[0]['summary_text']:
                summary_text = summary[0]['summary_text']
                sentences = sent_tokenize(summary_text)
                return [self._clean_text(s) for s in sentences[:max_points]]
            
            # Fallback to sentence extraction if summarization fails
            return self._extract_key_sentences(text, max_points)
            
        except Exception as e:
            print(f"Summarization error: {e}")
            return self._extract_key_sentences(text, max_points)
    
    def _generate_topic_title(self, text, index):
        """Generate a topic title using named entities and keywords"""
        try:
            # Extract entities from first portion of text
            first_part = text[:2000]
            entities = self.keyword_extractor(first_part)
            
            # Filter to get meaningful entities
            significant_entities = [e['word'] for e in entities if e['score'] > 0.8 and len(e['word']) > 3]
            
            if significant_entities:
                # Take most frequent entities
                from collections import Counter
                entity_counts = Counter(significant_entities)
                top_entities = [e for e, _ in entity_counts.most_common(2)]
                
                # Create title from top entities
                title = " - ".join(top_entities)
                if len(title) > 5:
                    return title
            
            # Fallback to extracting noun phrases
            sentences = sent_tokenize(first_part)[:3]
            title_candidates = []
            
            for sentence in sentences:
                np_match = re.search(r'(the\s+)?([A-Z][a-z]+(\s+[a-z]+){0,3})', sentence)
                if np_match:
                    title_candidates.append(np_match.group(0))
            
            if title_candidates:
                return max(title_candidates, key=len)
                
            # Last resort - use generic title
            return f"Topic {index + 1}"
            
        except Exception as e:
            print(f"Title generation error: {e}")
            return f"Topic {index + 1}"
    
    def _extract_key_sentences(self, text, max_sentences=4):
        """Extract key sentences as fallback when transformer fails"""
        sentences = sent_tokenize(text)
        valid_sentences = [s for s in sentences if 30 < len(s) < 150]
        
        # Choose sentences with good indicators of importance
        scored_sentences = []
        indicators = ['important', 'significant', 'key', 'main', 'primary', 'essential',
                     'crucial', 'critical', 'fundamental', 'major', 'notable']
                     
        for sentence in valid_sentences:
            score = 1
            lower_s = sentence.lower()
            
            # Check for indicator words
            for indicator in indicators:
                if indicator in lower_s:
                    score += 2
            
            # Prefer sentences with numbers
            if re.search(r'\d+', sentence):
                score += 1
                
            # Prefer sentences with quotation marks
            if '"' in sentence or "'" in sentence:
                score += 1
                
            scored_sentences.append((sentence, score))
        
        # Sort by score and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [self._clean_text(s[0]) for s in scored_sentences[:max_sentences]]
    
    def _clean_text(self, text):
        """Clean up text by removing extra whitespace and truncating if too long"""
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > 100:
            text = text[:97] + "..."
        return text