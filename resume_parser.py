import PyPDF2
import docx    # python-docx library for DOCX parsing
import spacy    # NLP for NER (name extraction)
import re    # Regular expressions for patterns (email, phone, dates)
import os     # File system operations
from pathlib import Path    # Modern path handling
import json    # Save structured data as JSON

class ResumeParser: 
    # Complete resume parser for PDF/DOCX/TXT formats.
    # Extracts: name, email, phone, education, skills, experience.
    # Handles encoding errors, uses spaCy NER for accuracy.
    
    def __init__(self):
        """Initialize spaCy NLP model (NER for names)"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy loaded successfully")
        except OSError:
            print("⚠️ spaCy model missing. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def read_pdf(self, file_path):
        """Extract text from PDF using PyPDF2"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"⚠️ PDF error {file_path}: {e}")
            return None
    
    # In resume_parser.py, read_docx() - add table extraction:
def read_docx(self, file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        # Paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        # TABLES (common DOCX issue)
        for table in doc.tables:
            for row in table.rows:
                row_text = ' '.join([cell.text for cell in row.cells])
                if row_text.strip():
                    text += row_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"⚠️ DOCX error {file_path}: {e}")
        return None

    
    def read_txt(self, file_path):
        """Extract text from TXT with encoding fallback"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        print(f"⚠️ TXT encoding error {file_path}")
        return None
    
    def extract_text(self, file_path):
        """Route to correct parser by file extension"""
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf': return self.read_pdf(file_path)
        elif ext == '.docx': return self.read_docx(file_path)
        elif ext == '.txt': return self.read_txt(file_path)
        else:
            print(f"❌ Unsupported format: {ext}")
            return None
    
    def extract_email(self, text):
        """Extract first valid email with regex"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text, re.IGNORECASE)
        return emails[0] if emails else None
    
    def extract_phone(self, text):
        """Extract Sri Lankan + international phones"""
        patterns = [
            r'\+?94[17]\d{8}',  # Sri Lanka: +947xxxxxxxx, 07xxxxxxxx
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # International
            r'\d{10}'  # 10 digits
        ]
        for pattern in patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0].strip()
        return None
    
    def extract_name(self, text):
        """spaCy NER for PERSON or first line fallback"""
        if self.nlp:
            doc = self.nlp(text[:1000])  # First page usually has name
            names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
            if names: return names[0]
        
        # Fallback: First non-empty line
        lines = [line.strip() for line in text.split('\n')[:5] if len(line.strip().split()) <= 3]
        for line in lines:
            if re.match(r'^[A-Z][a-z]+(\s[A-Z][a-z]+){1,2}$', line):
                return line
        return "Unknown"
    
    def extract_education(self, text):
        """Regex patterns for degrees/universities"""
        patterns = [
            r"(?:Bachelor|Master|PhD|Diploma)[^.\n]*?(?:\d{4}|University)",
            r"B\.Sc|A\.Sc|M\.Sc|BS|MS|BA|MA",
            r"(degree|graduat)[^.\n]*?(?:\d{4}|from\s+\w+)"
        ]
        education = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            education.extend(matches)
        return education[:3] if education else ["Not specified"]
    
    def extract_skills(self, text):
        """Keyword matching - FIXED RAW STRINGS"""
        skills = [
            'Python', 'Java', 'JavaScript', r'C\+\+', 'SQL', 'HTML', 'CSS',  # Raw strings fix warnings
            r'Node\.js', 'React', 'Angular', 'Django', 'Flask', 'solidity', 'blockchain',
            'HR', 'recruitment', 'marketing', 'accounting', 'finance', 'excel',
            'leadership', 'communication', 'teamwork', 'management'
        ]
        found = []
        text_lower = text.lower()
        for skill in skills:
            skill_lower = skill if isinstance(skill, str) else skill.lower()
            if re.search(skill_lower, text_lower):
                found.append(skill.replace(r'C\+\+', 'C++').replace(r'Node\.js', 'Node.js'))
        return list(set(found))[:10] or ["Not specified"]
    
    def extract_experience(self, text):
        """Extract experience section with years"""
        exp_match = re.search(
            r'(?:experience|work history).*?(?=(?:education|skills|$))',
            text, re.IGNORECASE | re.DOTALL
        )
        if exp_match:
            years = re.findall(r'\b(20\d{2})\b|(\d+ years?)', exp_match.group(0))
            return [y[0] or y[1] for y in years][:3]
        return ["Not specified"]
    
    def parse_resume(self, file_path):
        """Complete parsing pipeline"""
        print(f"Parsing: {Path(file_path).name}")
        text = self.extract_text(file_path)
        
        if not text:
            print(f"✗ No text extracted from {Path(file_path).name}")
            return None
        
        return {
            'file_name': Path(file_path).name,
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'education': self.extract_education(text),
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'raw_text': text[:500]  # Preview
        }

if __name__ == "__main__":
    parser = ResumeParser()
    result = parser.parse_resume("resumes/pdf/Dian.pdf")
    print(result)