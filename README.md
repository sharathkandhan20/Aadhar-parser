Aadhaar Parser

This project helps you extract text from Aadhaar card files (images, PDFs, DOCX, and TXT) and saves the extracted text as `.txt` files. It’s designed to make digitizing Aadhaar card data easy and efficient, even if the files are scanned images or contain tables.


🚀 How It Works

1. Place your Aadhaar files

   Put all your Aadhaar card files (.pdf, .docx, .txt, .jpg, .png, etc.) inside the `aadhar` folder.

2. Run the extractor

   The script will automatically extract text from all files and save it in the `aadhar_txt` folder.

3. What’s Supported
   - PDF (including scanned/image-based PDFs)
   - DOCX (including tables)
   - TXT
   - Images: JPG, PNG, TIFF, BMP


🛠️ How to Use

1. Install Requirements

   pip install pdfplumber python-docx pytesseract pillow pandas pdf2image pymupdf

   ⚠️ Note: You also need to install Tesseract OCR:
   https://github.com/tesseract-ocr/tesseract

   After installing, update the Tesseract path in `textparser.py` if needed:
   Example (Windows):
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



2. Run the Script

   python textparser.py

   This will:
   - Read all files in the `aadhar` folder
   - Extract text using OCR for scanned images and PDFs
   - Save extracted `.txt` files into the `aadhar_txt` folder



3. Check Your Results

   Open the `aadhar_txt` folder to find your output text files.



📁 Project Structure

aadhar/         - Input folder for Aadhaar files  
aadhar_txt/     - Output folder for extracted text  
textparser.py   - Main script for text extraction

📌 Notes

- The script handles both text-based and image-based PDFs.
- Tables in PDFs and DOCX files are extracted and formatted as readable text.
- If a file fails to process, it's skipped and the error is logged without crashing the script.


👤 Created by: B A Sharath Kandhan  
Purpose: To make Aadhaar card digitization simple and accessible.
