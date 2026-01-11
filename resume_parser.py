import PyPDF2
import docx
import spacy
import re
import os
from pathlib import Path
import json

class ResumeParser:
    def __init__(self):
        # Load spaCy NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Please install spaCy model: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def read_pdf(self, file_path):
        """Extract text from PDF files"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
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
        # Multiple patterns for different phone formats
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
        """Extract candidate name (usually first line or first proper nouns)"""
        if not self.nlp:
            # Fallback: return first line
            lines = text.strip().split('\n')
            return lines[0].strip() if lines else "Unknown"
        
        doc = self.nlp(text[:500])  # Check first 500 chars
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        return persons[0] if persons else "Unknown"
    
    def extract_education(self, text):
        """Extract education information"""
        education = []
        
        # Common degree patterns
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
                # Get surrounding context (±100 chars)
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                education.append(context.strip())
        
        return education if education else ["Not specified"]
    
    def extract_skills(self, text):
        """Extract skills from resume"""
        # Common skills database
        common_skills = [
            'Python', 'Java', 'JavaScript', r'C\+\+', 'SQL', 'HTML', 'CSS',
            'React', 'Angular', r'Node\.js', 'Django', 'Flask',
            'Machine Learning', 'Data Analysis', 'AWS', 'Azure', 'Docker',
            'Communication', 'Leadership', 'Project Management', 'Teamwork',
            'Problem Solving', 'Marketing', 'SEO', 'Social Media',
            'Accounting', 'Financial Analysis', 'Excel', 'QuickBooks',
            'HR Management', 'Recruitment', 'Employee Relations',
            'MS Office', 'PowerPoint', 'Word', 'Outlook'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if re.search(skill.lower(), text_lower):
                # Remove regex special characters for display
                display_skill = skill.replace(r'\+\+', '++').replace(r'\.js', '.js')
                found_skills.append(display_skill)
        
        return found_skills if found_skills else ["Not specified"]
    
    def extract_experience(self, text):
        """Extract work experience"""
        experience = []
        
        # Look for experience section
        exp_section = re.search(
            r'(?:experience|employment|work history)(.*?)(?:education|skills|certifications|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if exp_section:
            exp_text = exp_section.group(1)
            
            # Look for year patterns (2020-2023, 2020-Present, etc.)
            year_patterns = re.finditer(
                r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)',
                exp_text,
                re.IGNORECASE
            )
            
            for match in year_patterns:
                # Get surrounding context
                start = max(0, match.start() - 200)
                end = min(len(exp_text), match.end() + 200)
                context = exp_text[start:end].strip()
                experience.append(context)
        
        return experience if experience else ["Not specified"]
    
    def extract_certifications(self, text):
        """Extract certifications from resume"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r"(?:Certified|Certification).*?(?:\n|$)",
            r"(?:PMP|CISSP|AWS|Azure|Google Cloud|CompTIA|CCNA|CCIE)",
            r"(?:Scrum Master|Product Owner|Six Sigma|ITIL)",
            r"(?:CPA|CFA|CMA|CIA)",  # Accounting certs
            r"(?:SHRM-CP|SHRM-SCP|PHR|SPHR)",  # HR certs
        ]
        
        # Look for certification section
        cert_section = re.search(
            r'(?:certifications?|licenses?)(.*?)(?:education|skills|experience|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if cert_section:
            cert_text = cert_section.group(1)
            
            for pattern in cert_patterns:
                matches = re.finditer(pattern, cert_text, re.IGNORECASE)
                for match in matches:
                    cert = match.group(0).strip()
                    if cert and len(cert) < 100:  # Reasonable length
                        certifications.append(cert)
        
        return certifications if certifications else ["None specified"]
    
    def parse_resume(self, file_path):
        """Main method to parse a resume and extract all information"""
        print(f"\nParsing: {os.path.basename(file_path)}")
        
        # Extract text
        text = self.extract_text(file_path)
        
        if not text:
            return None
        
        # Extract all information
        resume_data = {
            'file_name': os.path.basename(file_path),
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'education': self.extract_education(text),
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'certifications': self.extract_certifications(text),
            'raw_text': text[:500]  # Store first 500 chars
        }
        
        return resume_data


# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with a single file
    resume_data = parser.parse_resume("resumes/pdf/sample_resume.pdf")
    
    if resume_data:
        print("\nExtracted Information:")
        print(json.dumps(resume_data, indent=2))