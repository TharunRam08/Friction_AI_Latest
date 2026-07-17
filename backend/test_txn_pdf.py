import os
import json
from dotenv import load_dotenv

load_dotenv()

from main import parse_pdf, extract_table_from_pdf_text_via_llm

pdf_path = r"c:\Users\tharu\Downloads\Friction_AI\FRICTION\backend\data\uploads\Friction_Sample_Strategic_Report (1).pdf"
pdf_text = parse_pdf(pdf_path)
print(f"PDF Text length: {len(pdf_text)}")
result = extract_table_from_pdf_text_via_llm(pdf_text)
print("Result:")
print(result)
