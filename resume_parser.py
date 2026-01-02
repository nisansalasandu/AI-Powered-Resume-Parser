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
        # Initialize spaCy NLP model for entity recognition
        try:
            self.nlp = spacy.load("en_core_web_sm")    # English model with PERSON tags
        except:
            print("Please install spaCy model: python -m spacy download en_core_web_sm")
            self.nlp = None    # Fallback to regex
    
    def read_pdf(self, file_path):
        """Extract text from PDF files using PyPDF2"""
        text = ""
        try:
            with open(file_path, 'rb') as file:     # Binary mode for PDFs
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error reading PDF {file_path}: {str(e)}")
            return None
    
    def read_docx(self, file_path):
        """Extract text from DOCX files"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {str(e)}")
            return None
    
    def read_txt(self, file_path):
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Error reading TXT {file_path}: {str(e)}")
                return None
    
    def extract_text(self, file_path):
        """Main method to extract text based on file type"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.read_pdf(file_path)
        elif file_ext == '.docx':
            return self.read_docx(file_path)
        elif file_ext == '.txt':
            return self.read_txt(file_path)
        else:
            print(f"Unsupported file format: {file_ext}")
            return None
    
    def extract_email(self, text):
        """Extract email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text):
        """Extract phone numbers"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10}'
        ]
        
        for pattern in patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    def extract_name(self, text):
        """Extract candidate name"""
        if not self.nlp:
            lines = text.strip().split('\n')
            return lines[0].strip() if lines else "Unknown"
        
        doc = self.nlp(text[:500])
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        return persons[0] if persons else "Unknown"
    
    def extract_education(self, text):
        """Extract education information"""
        education = []
        
        degree_patterns = [
            r"Bachelor(?:'s)?\s+(?:of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce)?",
            r"Master(?:'s)?\s+(?:of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce)?",
            r"B\.?(?:Sc|A|E|Tech|Com|B\.?A)\.?",
            r"M\.?(?:Sc|A|E|Tech|Com|B\.?A)\.?",
            r"Ph\.?D\.?",
            r"Diploma",
            r"Associate(?:'s)?\s+Degree"
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                education.append(context.strip())
        
        return education if education else ["Not specified"]
    
    def extract_skills(self, text):
        """Extract skills from resume"""
        common_skills = [
            'Python', 'Java', 'JavaScript', 'C\+\+', 'SQL', 'HTML', 'CSS',
            'React', 'Angular', 'Node\.js', 'Django', 'Flask',
            'Machine Learning', 'Data Analysis', 'AWS', 'Azure', 'Docker',
            'Communication', 'Leadership', 'Project Management', 'Teamwork',
            'Problem Solving', 'Marketing', 'SEO', 'Social Media',
            'Accounting', 'Financial Analysis', 'Excel', 'QuickBooks',
            'HR Management', 'Recruitment', 'Employee Relations'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if re.search(skill.lower(), text_lower):
                found_skills.append(skill)
        
        return found_skills if found_skills else ["Not specified"]
    
    def extract_experience(self, text):
        """Extract work experience"""
        experience = []
        
        exp_section = re.search(
            r'(?:experience|employment|work history)(.*?)(?:education|skills|certifications|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if exp_section:
            exp_text = exp_section.group(1)
            
            year_patterns = re.finditer(
                r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)',
                exp_text,
                re.IGNORECASE
            )
            
            for match in year_patterns:
                start = max(0, match.start() - 200)
                end = min(len(exp_text), match.end() + 200)
                context = exp_text[start:end].strip()
                experience.append(context)
        
        return experience if experience else ["Not specified"]
    
    def parse_resume(self, file_path):
        """Main method to parse a resume"""
        print(f"\nParsing: {os.path.basename(file_path)}")
        
        text = self.extract_text(file_path)
        
        if not text:
            return None
        
        resume_data = {
            'file_name': os.path.basename(file_path),
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'education': self.extract_education(text),
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'raw_text': text[:500]
        }
        
        return resume_data