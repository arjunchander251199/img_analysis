import google.generativeai as genai
from flask import current_app
from PIL import Image
import time

class GeminiService:
    """Service class for Gemini AI operations"""
    
    def __init__(self):
        self.model = None
        self._configure()
    
    def _configure(self):
        """Configure Gemini API"""
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        
        # Configure generation settings with timeout
        generation_config = {
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 8192,
        }
        
        self.model = genai.GenerativeModel(
            current_app.config['GEMINI_MODEL'],
            generation_config=generation_config
        )
    
    def _get_analysis_prompt(self):
        """Get the comprehensive analysis prompt for Gemini"""
        return """Analyze this image carefully and extract all information.

Think step by step:
1. Observe the entire image
2. Identify content type (handwritten, printed, forms, tables, etc.)
3. Note any special markings or formatting

Extract all text (printed and handwritten), numbers, dates, names, and any other information.

OUTPUT REQUIREMENTS:
- Plain text only, no markdown formatting
- No bold (**), no asterisks (*), no special formatting
- Use simple numbered lists (1., 2., 3.) when listing items
- Keep it clean and concise
- Just the facts, no extra explanations"""

    def analyze_image(self, image_path):
        """Analyze a single image with Gemini with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                img = Image.open(image_path)
                
                # Resize large images to reduce processing time
                max_size = 1536
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                prompt = self._get_analysis_prompt()
                
                # Generate content without request_options
                response = self.model.generate_content([prompt, img])
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    raise Exception("API quota exceeded. Please try again later.")
                
                if attempt < max_retries - 1:
                    if "deadline" in error_msg.lower() or "timeout" in error_msg.lower():
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                
                raise Exception(f"Error analyzing image: {error_msg}")
    
    def analyze_file(self, filepath):
        """Main method to analyze image file"""
        content = self.analyze_image(filepath)
        return {
            'type': 'image',
            'content': content
        }
