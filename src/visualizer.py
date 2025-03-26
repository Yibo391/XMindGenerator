"""
Mind Map Visualizer Module
Creates visual representations of content hierarchies in XMind-style PDF format
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
import math

class MindMapVisualizer:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.node_width = 200
        self.node_height = 60
        self.h_spacing = 100
        self.v_spacing = 40
        
    def create_mindmap(self, hierarchy, output_path):
        """
        Create a mind map PDF from a hierarchical structure
        
        Args:
            hierarchy (dict): Hierarchical structure to visualize
            output_path (str): Path to save the output PDF
        """
        # Create a canvas
        c = canvas.Canvas(output_path, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Calculate center of the page
        center_x = width / 2
        center_y = height / 2
        
        # Draw central topic
        central_topic = hierarchy.get('central_topic', 'Mind Map')
        self._draw_node(c, central_topic, center_x, center_y, node_type='central')
        
        # Draw main topics and their connections
        main_topics = hierarchy.get('main_topics', [])
        
        if main_topics:
            # Calculate angles for main topics around the central topic
            angle_step = 2 * math.pi / len(main_topics)
            radius = 200  # Distance from center to main topics
            
            for i, topic in enumerate(main_topics):
                # Calculate position based on angle
                angle = i * angle_step
                topic_x = center_x + radius * math.cos(angle)
                topic_y = center_y + radius * math.sin(angle)
                
                # Draw connection line
                self._draw_connection(c, center_x, center_y, topic_x, topic_y)
                
                # Draw topic node
                self._draw_node(c, topic['text'], topic_x, topic_y, node_type='main')
                
                # Draw subtopics
                self._draw_subtopics(c, topic, topic_x, topic_y, angle)
        
        c.save()
    
    def _draw_node(self, canvas, text, x, y, node_type='normal'):
        """Draw a node with text"""
        if node_type == 'central':
            width, height = self.node_width * 1.2, self.node_height
            fill_color = colors.lightblue
            text_color = colors.darkblue
        elif node_type == 'main':
            width, height = self.node_width, self.node_height
            fill_color = colors.lightgreen
            text_color = colors.darkgreen
        else:
            width, height = self.node_width * 0.8, self.node_height * 0.7
            fill_color = colors.white
            text_color = colors.black
        
        # Draw node box
        canvas.setFillColor(fill_color)
        canvas.setStrokeColor(colors.black)
        canvas.roundRect(x - width/2, y - height/2, width, height, 10, stroke=1, fill=1)
        
        # Draw text
        canvas.setFillColor(text_color)
        
        # Handle long text by splitting it
        if len(text) > 40:
            lines = self._wrap_text(text, 40)
            line_height = height / (len(lines) + 1)
            start_y = y + (height / 2) - line_height
            
            for line in lines:
                canvas.setFont("Helvetica", 10)
                canvas.drawCentredString(x, start_y, line)
                start_y -= line_height
        else:
            canvas.setFont("Helvetica", 12)
            canvas.drawCentredString(x, y, text)
    
    def _draw_connection(self, canvas, x1, y1, x2, y2):
        """Draw a connection line between nodes"""
        canvas.setStrokeColor(colors.gray)
        canvas.setLineWidth(2)
        canvas.line(x1, y1, x2, y2)
    
    def _draw_subtopics(self, canvas, topic, parent_x, parent_y, parent_angle):
        """Draw subtopics recursively"""
        subtopics = topic.get('subtopics', [])
        if not subtopics:
            return
            
        # Calculate subtopic placement
        num_subtopics = len(subtopics)
        angle_spread = math.pi / 4  # Spread subtopics within this angle
        
        # Get base angle perpendicular to parent connection
        base_angle = parent_angle + math.pi / 2
        
        # Calculate starting angle for subtopics
        start_angle = base_angle - (angle_spread / 2)
        
        # Calculate spacing based on number of subtopics
        if num_subtopics > 1:
            angle_step = angle_spread / (num_subtopics - 1)
        else:
            angle_step = 0
        
        for i, subtopic in enumerate(subtopics):
            # Calculate position
            subtopic_angle = start_angle + (i * angle_step)
            distance = 150  # Distance from parent to subtopic
            
            subtopic_x = parent_x + distance * math.cos(subtopic_angle)
            subtopic_y = parent_y + distance * math.sin(subtopic_angle)
            
            # Draw connection
            self._draw_connection(canvas, parent_x, parent_y, subtopic_x, subtopic_y)
            
            # Draw subtopic node
            self._draw_node(canvas, subtopic['text'], subtopic_x, subtopic_y, 'normal')
            
            # Recursively draw any sub-subtopics
            if 'subtopics' in subtopic and subtopic['subtopics']:
                self._draw_subtopics(canvas, subtopic, subtopic_x, subtopic_y, subtopic_angle)
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is longer than max_width, need to split it
                    lines.append(word[:max_width])
                    current_line = [word[max_width:]]
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines