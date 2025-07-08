import os
import json
import time
from typing import List, Dict, Optional
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

class AadharConverter:
    """
    This class converts Aadhaar card text files to structured JSON format
    using Google's Gemini AI API
    """
    
    def __init__(self, api_keys: List[str], input_dir: str = "aadhar_txt", output_dir: str = "aadhar_data"):
        # Store the API keys for backup usage
        self.api_keys = api_keys
        self.current_key_index = 0
        
        # Set up directories
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure the first API key
        genai.configure(api_key=self.api_keys[0])
        
        # Keep track of how many files we process
        self.stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # This is the prompt I give to the AI to extract Aadhaar data
        self.prompt = """Extract the following information from this Aadhaar card text and return it as JSON:

        - aadhar_number: (12-digit number)
        - name: (Full name)
        - date_of_birth: (DD/MM/YYYY format)
        - gender: (Male/Female/Other)
        - father_name: (if available)
        - mother_name: (if available)
        - address: {
            "house_number": "",
            "street": "",
            "locality": "",
            "city": "",
            "district": "",
            "state": "",
            "pincode": ""
        }
        - mobile_number: (if available)
        - email: (if available)

        Instructions:
        1. Extract only visible information
        2. Use null for missing data
        3. Format Aadhaar number with spaces (XXXX XXXX XXXX)
        4. Return only valid JSON

        Aadhaar Text: {text}"""
    
    def switch_api_key(self):
        """Switch to the next API key if current one fails"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        genai.configure(api_key=self.api_keys[self.current_key_index])
    
    def call_gemini_api(self, text_content: str) -> Optional[str]:
        """Send text to Gemini AI and get JSON response"""
        full_prompt = self.prompt.replace("{text}", text_content)
        
        # Try with current API key first
        for attempt in range(len(self.api_keys)):
            try:
                # Use Gemini Flash model (it's faster and cheaper)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Configure AI settings
                config = {
                    "temperature": 0.1,  # Low temperature for consistent output
                    "max_output_tokens": 2048,
                }
                
                # Make the API call
                response = model.generate_content(full_prompt, generation_config=config)
                return response.text
                
            except Exception as e:
                # If quota exceeded, try next key
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    self.switch_api_key()
                    continue
                else:
                    time.sleep(2)  # Wait before retry
        
        return None
    
    def process_single_file(self, file_path: Path) -> bool:
        """Process one text file and convert it to JSON"""
        try:
            # Read the Aadhaar text file
            with open(file_path, 'r', encoding='utf-8') as f:
                aadhar_text = f.read()
            
            # Send to AI for processing
            ai_response = self.call_gemini_api(aadhar_text)
            
            if not ai_response:
                self.stats['errors'].append(f"AI failed to process {file_path.name}")
                return False
            
            # Clean up the AI response (remove markdown if present)
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0]
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0]
            
            # Parse the JSON response
            try:
                data = json.loads(ai_response)
                
                # Basic validation - check if we got the main fields
                if self.validate_data(data):
                    # Save as JSON file
                    output_file = self.output_dir / f"{file_path.stem}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    return True
                else:
                    self.stats['errors'].append(f"Invalid data structure from {file_path.name}")
                    return False
                    
            except json.JSONDecodeError:
                self.stats['errors'].append(f"Invalid JSON from {file_path.name}")
                return False
                
        except Exception as e:
            self.stats['errors'].append(f"Error processing {file_path.name}: {str(e)}")
            return False
    
    def validate_data(self, data: Dict) -> bool:
        """Check if the extracted data has required fields"""
        required_fields = ['aadhar_number', 'name', 'date_of_birth', 'gender']
        
        # Make sure basic fields are present
        for field in required_fields:
            if field not in data:
                return False
        
        # Check if address is properly structured
        if 'address' in data and not isinstance(data['address'], dict):
            return False
        
        return True
    
    def process_all_files(self):
        """Process all text files in the input directory"""
        # Find all .txt files
        txt_files = list(self.input_dir.glob("*.txt"))
        self.stats['total_files'] = len(txt_files)
        
        if not txt_files:
            return self.stats
        
        print("Processing...")
        
        # Process each file
        for txt_file in txt_files:
            if self.process_single_file(txt_file):
                self.stats['successful'] += 1
                print(f" aadhar file completed")
            else:
                self.stats['failed'] += 1
                print(f" aadhar file completed")
            
            # Small delay to avoid hitting rate limits
            time.sleep(1)
        
        return self.stats

def main():
    """Main function to run the Aadhaar converter"""
    try:
        # Load API keys from .env file
        load_dotenv()
        
        # Get API keys (I'm using multiple keys as backup)
        api_keys = []
        for i in range(1, 5):  # Check for keys 1-4
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                api_keys.append(key)
        
        if not api_keys:
            return
        
        # Create converter and process files
        converter = AadharConverter(api_keys)
        stats = converter.process_all_files()
        
        # Show final result
        print("Process completed")
        
    except Exception as e:
        pass

if __name__ == "__main__":
    main()