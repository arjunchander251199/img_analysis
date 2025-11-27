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
        return """You are an expert OCR and handwriting recognition system. Analyze this image with extreme precision and extract ALL information accurately.

## CRITICAL ANALYSIS PROCESS - THINK BEFORE YOU EXTRACT:

### Step 1: Initial Observation
- Scan the ENTIRE image systematically (top to bottom, left to right)
- Identify document type: form, table, receipt, note, mixed content, etc.
- Note the layout: boxes, fields, lines, columns, sections
- Identify all text types: printed, handwritten, typed, stamps, signatures

### Step 2: Handwriting Edge Cases - BE EXTREMELY CAREFUL:
**Character Confusion - Analyze Context Before Deciding:**
- **0 vs O**: In numbers → likely 0 (zero) | In names/words → likely O (letter)
- **1 vs I vs l**: In numbers → 1 | In names → I or l (check word context)
- **5 vs S**: In numbers → 5 | In words → S
- **8 vs B**: In numbers → 8 | In words → B
- **2 vs Z**: In numbers → 2 | In words → Z
- **6 vs G**: In numbers → 6 | In words → G
- **9 vs g vs q**: Analyze carefully - check position and surrounding context
- **u vs v vs n**: Look at the flow and connection to other letters
- **rn vs m**: Very common confusion - examine carefully

**Form Field Challenges:**
- **Text OUTSIDE boxes**: People often write ABOVE, BELOW, or to the SIDE of designated boxes
- **Text OVERLAPPING boxes**: Handwriting may cross box boundaries or be written ON TOP of box lines
- **Account numbers in boxes**: Extract even if digits spill outside individual box cells
- **Dates**: Handle all formats (MM/DD/YYYY, DD-MM-YYYY, written out, etc.) - check slashes vs ones
- **Checkboxes**: Note if checked (✓, X, filled) or unchecked
- **Crossed-out text**: Indicate clearly with ~~strikethrough~~ or mention "crossed out"

**Handwriting Quality Issues:**
- Poor/messy handwriting: Make best effort, indicate uncertainty with [?] if needed
- Faded/light writing: Enhance mentally and extract
- Smudged/blurred: Analyze carefully, use surrounding context
- Partial characters: Infer from context and partial shapes
- Different writing angles: Mentally rotate and read
- Cursive vs print mixing: Handle seamlessly
- Variable letter sizes: Don't let size affect recognition

**Spatial Awareness:**
- Text written in margins or corners
- Multi-line entries in single-line fields
- Vertical text or rotated text
- Arrows or annotations pointing to specific areas
- Notes written in empty spaces

### Step 3: Context-Driven Accuracy:
- **For number fields** (Account #, Phone, ZIP, etc.): Prioritize numeric interpretation
- **For name fields**: Prioritize letter interpretation, handle capitalization
- **For date fields**: Validate reasonable date ranges, common formats
- **For signature areas**: Extract any printed name near signature
- **For amounts/currency**: Handle decimals, commas, dollar signs correctly

### Step 4: Systematic Extraction:
Extract in logical order (top to bottom, left to right) maintaining document structure.

## OUTPUT FORMAT - CONCISE AND CLEAN:

**ONLY extract the main information in bullet points with proper markdown formatting.**

Use this format:
- **Field Name:** Value
- **Account Number:** [number]
- **Date:** [date]
- **Name:** [name]
- **Amount:** [amount with currency]

**IMPORTANT RULES:**
- DO NOT include "Document Type", "Header Information", "Footer Information" sections
- DO NOT include "Additional Observations", "Handwriting Style", or analysis commentary
- DO NOT create verbose tables or multiple sections
- DO include any important notes or special markings as brief bullet points
- USE bold (**) for field labels
- Keep it SHORT and TO THE POINT - only essential extracted data
- If there are crossed-out items or corrections, mention them briefly

## QUALITY STANDARDS:
✓ **Accuracy over speed** - Think before deciding on ambiguous characters
✓ **Context matters** - Use field labels to guide interpretation
✓ **Be thorough** - Don't skip text written outside boxes or in margins
✓ **Concise output** - Only main information, no verbose explanations
✓ **Proper formatting** - Use markdown bold for labels, bullets for structure
✓ **Indicate uncertainty** - Use [?] for truly unreadable characters only after careful analysis

Extract the essential information now with maximum precision and conciseness:"""

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
