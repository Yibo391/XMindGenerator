"""
Improved Mind Map Visualizer Module
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A2, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math
import random

class MindMapVisualizer:
    def __init__(self):
        # Try to register a nice font
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
            self.font_name = 'Arial'
        except:
            self.font_name = 'Helvetica'
        
        # Node styles
        self.central_node = {
            'width': 300,
            'height': 100,
            'fill_color': colors.HexColor('#4A86E8'),  # Blue
            'border_color': colors.HexColor('#2A66C8'),
            'text_color': colors.white,
            'font_size': 18
        }
        
        self.main_node = {
            'width': 250,
            'height': 80,
            'fill_color': colors.HexColor('#93C47D'),  # Green
            'border_color': colors.HexColor('#73A45D'),
            'text_color': colors.black,
            'font_size': 14
        }
        
        self.sub_node = {
            'width': 220,
            'height': 70,
            'fill_color': colors.HexColor('#FFD966'),  # Yellow
            'border_color': colors.HexColor('#DFB946'),
            'text_color': colors.black,
            'font_size': 12
        }
        
        self.leaf_node = {
            'width': 200,
            'height': 60,
            'fill_color': colors.HexColor('#F9CB9C'),  # Orange
            'border_color': colors.HexColor('#D9AB7C'),
            'text_color': colors.black,
            'font_size': 10
        }
        
        # Default layout parameters
        self.debug_mode = False  # Set to True to see node positions
        
    def create_mindmap(self, hierarchy, output_path):
        """Create a mind map PDF from hierarchical structure"""
        # Use A2 for larger mindmap
        c = canvas.Canvas(output_path, pagesize=landscape(A2))
        width, height = landscape(A2)
        
        # Draw page border in debug mode
        if self.debug_mode:
            c.setStrokeColor(colors.red)
            c.rect(10, 10, width-20, height-20)
        
        # Center of the page
        center_x = width / 2
        center_y = height / 2
        
        # Draw central topic
        central_topic = hierarchy.get('central_topic', 'Mind Map')
        self._draw_node(c, central_topic, center_x, center_y, 'central')
        
        # Get main topics
        main_topics = hierarchy.get('main_topics', [])
        
        if not main_topics:
            c.save()
            return
        
        # Debug info
        if self.debug_mode:
            c.setFont(self.font_name, 12)
            c.setFillColor(colors.black)
            c.drawString(50, height-50, f"Number of main topics: {len(main_topics)}")
        
        # Distribute main topics in a radial pattern
        self._draw_radial_layout(c, main_topics, center_x, center_y)
        
        c.save()
    
    def _draw_radial_layout(self, canvas, main_topics, center_x, center_y):
        """Draw main topics in a radial layout around central topic"""
        num_topics = len(main_topics)
        if num_topics == 0:
            return
            
        # Each topic gets an equal slice of the circle
        angle_step = 2 * math.pi / num_topics
        
        # Radius from center to main topics
        radius = 300
        
        # Draw each main topic
        for i, topic in enumerate(main_topics):
            # Position around the circle, starting from top and going clockwise
            angle = (3 * math.pi / 2) + (i * angle_step)
            
            topic_x = center_x + radius * math.cos(angle)
            topic_y = center_y + radius * math.sin(angle)
            
            # Debug point
            if self.debug_mode:
                canvas.setFillColor(colors.red)
                canvas.circle(topic_x, topic_y, 5, fill=1)
                canvas.setFillColor(colors.black)
                canvas.drawString(topic_x, topic_y, f"Topic {i}")
            
            # Draw connection line to central topic
            self._draw_curved_connection(canvas, center_x, center_y, 
                                       topic_x, topic_y, colors.HexColor('#4A86E8'))
            
            # Draw the main topic node
            self._draw_node(canvas, topic['text'], topic_x, topic_y, 'main')
            
            # Draw its subtopics in a branch layout
            subtopics = topic.get('subtopics', [])
            if subtopics:
                # Determine which side of the central node we're on
                is_right_side = topic_x > center_x
                
                # Draw branch of subtopics
                self._draw_branch_layout(canvas, subtopics, topic_x, topic_y, 
                                       angle, is_right_side)
    
    def _draw_branch_layout(self, canvas, subtopics, parent_x, parent_y, 
                          parent_angle, is_right_side):
        """Draw subtopics in a branch layout"""
        if not subtopics:
            return
            
        # Parameters for layout
        branch_length = 230  # Distance from parent to subtopic
        
        # Angle range for the branch (radians)
        if is_right_side:
            # For right side, angle range is upward & downward from horizontal right
            angle_range = math.pi / 3  # 60 degrees total range
            base_angle = 0  # horizontal right
        else:
            # For left side, angle range is upward & downward from horizontal left
            angle_range = math.pi / 3  # 60 degrees total range
            base_angle = math.pi  # horizontal left
        
        num_subtopics = len(subtopics)
        
        # Calculate angle step between subtopics
        if num_subtopics > 1:
            angle_step = angle_range / (num_subtopics - 1)
        else:
            angle_step = 0
            
        # Calculate start angle
        start_angle = base_angle - (angle_range / 2)
        
        # Draw each subtopic
        for i, subtopic in enumerate(subtopics):
            # Calculate position using the angle
            subtopic_angle = start_angle + (i * angle_step)
            
            subtopic_x = parent_x + branch_length * math.cos(subtopic_angle)
            subtopic_y = parent_y + branch_length * math.sin(subtopic_angle)
            
            # Debug information
            if self.debug_mode:
                canvas.setFillColor(colors.blue)
                canvas.circle(subtopic_x, subtopic_y, 3, fill=1)
                canvas.setFillColor(colors.black)
                canvas.drawString(subtopic_x, subtopic_y, f"Sub {i}")
            
            # Draw connecting line
            self._draw_curved_connection(canvas, parent_x, parent_y, 
                                     subtopic_x, subtopic_y, colors.HexColor('#93C47D'))
            
            # Draw the subtopic node
            self._draw_node(canvas, subtopic['text'], subtopic_x, subtopic_y, 'sub')
            
            # Draw leaf nodes if any
            leaf_nodes = subtopic.get('subtopics', [])
            if leaf_nodes:
                self._draw_leaf_layout(canvas, leaf_nodes, subtopic_x, subtopic_y, 
                                    subtopic_angle, is_right_side)
    
    def _draw_leaf_layout(self, canvas, leaf_nodes, parent_x, parent_y, 
                         parent_angle, is_right_side):
        """Draw leaf nodes in a vertical layout"""
        if not leaf_nodes:
            return
            
        # Parameters
        leaf_distance = 180  # Distance from parent to leaf nodes
        v_spacing = 80       # Vertical spacing between leaf nodes
        
        # Horizontal direction based on which side we're on
        h_direction = 1 if is_right_side else -1
        
        # Calculate total height needed
        total_height = (len(leaf_nodes) - 1) * v_spacing
        
        # Calculate starting y position (centered vertically)
        start_y = parent_y + (total_height / 2)
        
        # Fixed x position (horizontal from parent)
        leaf_x = parent_x + (h_direction * leaf_distance)
        
        # Draw each leaf node
        for i, leaf in enumerate(leaf_nodes):
            leaf_y = start_y - (i * v_spacing)
            
            # Debug point
            if self.debug_mode:
                canvas.setFillColor(colors.green)
                canvas.circle(leaf_x, leaf_y, 2, fill=1)
            
            # Draw connecting line
            self._draw_connection(canvas, parent_x, parent_y, leaf_x, leaf_y, 
                               colors.HexColor('#FFD966'))
            
            # Draw the leaf node
            self._draw_node(canvas, leaf['text'], leaf_x, leaf_y, 'leaf')
    
    def _draw_node(self, canvas, text, x, y, node_type):
        """Draw a node with text"""
        # Select node style based on type
        if node_type == 'central':
            style = self.central_node
        elif node_type == 'main':
            style = self.main_node
        elif node_type == 'sub':
            style = self.sub_node
        else:  # leaf
            style = self.leaf_node
            
        width = style['width']
        height = style['height']
        
        # Draw shadow for 3D effect
        canvas.setFillColor(colors.Color(0, 0, 0, alpha=0.1))
        canvas.roundRect(x - width/2 + 3, y - height/2 - 3, width, height, 10, stroke=0, fill=1)
        
        # Draw the node
        canvas.setFillColor(style['fill_color'])
        canvas.setStrokeColor(style['border_color'])
        canvas.setLineWidth(2)
        canvas.roundRect(x - width/2, y - height/2, width, height, 10, stroke=1, fill=1)
        
        # Prepare text
        wrapped_text = self._wrap_text(text, int(width / (style['font_size'] * 0.6)))
        
        # Draw text
        canvas.setFillColor(style['text_color'])
        canvas.setFont(self.font_name, style['font_size'])
        
        # Calculate text positioning
        line_height = style['font_size'] * 1.2
        total_text_height = len(wrapped_text) * line_height
        text_y = y + (total_text_height / 2) - line_height
        
        for line in wrapped_text:
            canvas.drawCentredString(x, text_y, line)
            text_y -= line_height
    
    def _draw_connection(self, canvas, x1, y1, x2, y2, color=colors.black):
        """Draw a straight connection line"""
        canvas.setStrokeColor(color)
        canvas.setLineWidth(2)
        canvas.line(x1, y1, x2, y2)
    
    def _draw_curved_connection(self, canvas, x1, y1, x2, y2, color):
        """Draw a curved connection using a Bezier curve"""
        canvas.setStrokeColor(color)
        canvas.setLineWidth(2.5)
        
        # Calculate midpoint for control points
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Distance between points
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Calculate control points offset perpendicular to the line
        dx = x2 - x1
        dy = y2 - y1
        
        # Normalize and rotate 90 degrees
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            udx = dx / length
            udy = dy / length
            perpx = -udy
            perpy = udx
        else:
            perpx = 0
            perpy = 0
        
        # Control point distance from midpoint
        ctrl_distance = distance * 0.2
        
        # Calculate control point positions
        cx1 = mid_x + perpx * ctrl_distance
        cy1 = mid_y + perpy * ctrl_distance
        
        # Draw the curve
        p = canvas.beginPath()
        p.moveTo(x1, y1)
        p.curveTo(cx1, cy1, cx1, cy1, x2, y2)
        canvas.drawPath(p, stroke=1, fill=0)
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if current_line and len(' '.join(current_line + [word])) > max_width:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
                
        if current_line:
            lines.append(' '.join(current_line))
            
        # Limit number of lines to avoid overflow
        if len(lines) > 4:
            lines = lines[:3]
            lines.append("...")
            
        return lines