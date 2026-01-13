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
        """Extract email addresses - ENHANCED"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Filter out common noise
        valid_emails = [e for e in emails if not any(x in e.lower() for x in ['example.com', 'test.com'])]
        
        return valid_emails[0] if valid_emails else (emails[0] if emails else None)
    
    def extract_phone(self, text):
        """Extract phone numbers - ENHANCED"""
        # Multiple patterns for different phone formats including international
        patterns = [
            r'\+94\s?\d{9}',  # Sri Lankan format
            r'0\d{9}',  # Sri Lankan local format
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    def extract_name(self, text):
        """Extract candidate name - ENHANCED"""
        # Try multiple strategies
        
        # Strategy 1: Look for name in first few lines (before email/phone)
        lines = text.strip().split('\n')[:10]
        
        # Common location/address words to avoid
        location_words = ['lane', 'street', 'road', 'avenue', 'city', 'galle', 'colombo', 
                         'sri lanka', 'details', 'contact', 'address', 'location']
        
        for line in lines:
            line_clean = line.strip()
            
            # Skip empty lines or lines with email/phone
            if not line_clean or '@' in line_clean or re.search(r'\d{5,}', line_clean):
                continue
            
            # Skip if it's a location
            if any(loc in line_clean.lower() for loc in location_words):
                continue
            
            # If line has 2-4 words and looks like a name
            words = line_clean.split()
            if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words if word):
                return line_clean
        
        # Strategy 2: Use spaCy
        if self.nlp:
            doc = self.nlp(text[:500])
            persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            
            # Filter out locations and short names
            valid_persons = [p for p in persons 
                           if len(p.split()) >= 2 
                           and not any(loc in p.lower() for loc in location_words)]
            
            if valid_persons:
                return valid_persons[0]
        
        # Strategy 3: Fallback to first non-empty line
        for line in lines[:5]:
            line_clean = line.strip()
            if line_clean and len(line_clean.split()) >= 2:
                return line_clean
        
        return "Unknown"
    
    def extract_education(self, text):
        """Extract education information"""
        education = []
        
        # Common degree patterns
        degree_patterns = [
            r"Bachelor(?:'s)?\s+(?:of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce|Finance|Accounting)?",
            r"Master(?:'s)?\s+(?:of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce)?",
            r"B\.?(?:Sc|A|E|Tech|Com|B\.?A)\.?",
            r"M\.?(?:Sc|A|E|Tech|Com|B\.?A)\.?",
            r"Ph\.?D\.?",
            r"Diploma",
            r"Associate(?:'s)?\s+Degree",
            r"BA\s+in\s+\w+",
            r"BSc\s+in\s+\w+"
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
        """Extract skills from resume - ENHANCED with more skills"""
        # Expanded skills database
        common_skills = [
            # Programming & Tech
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'SQL', 'HTML', 'CSS', 'PHP', 'Ruby',
            'React', 'Angular', 'Node.js', 'Django', 'Flask', 'Vue.js', 'TypeScript',
            'Machine Learning', 'Data Analysis', 'Data Science', 'AI', 'Deep Learning',
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Git', 'DevOps',
            
            # Soft Skills
            'Communication', 'Leadership', 'Project Management', 'Teamwork', 'Team Building',
            'Problem Solving', 'Critical Thinking', 'Time Management', 'Adaptability',
            'Conflict Resolution', 'Negotiation', 'Presentation', 'Public Speaking',
            
            # Business & Marketing
            'Marketing', 'Digital Marketing', 'SEO', 'Social Media', 'Content Marketing',
            'Brand Management', 'Market Research', 'Sales', 'Customer Service',
            'Business Development', 'Strategic Planning', 'Analytics',
            
            # Finance & Accounting
            'Accounting', 'Financial Analysis', 'Financial Reporting', 'Budgeting', 
            'Forecasting', 'Excel', 'QuickBooks', 'SAP', 'Oracle', 'Bookkeeping',
            'Tax Preparation', 'Auditing', 'Cost Analysis', 'Financial Planning',
            
            # HR
            'HR Management', 'Recruitment', 'Employee Relations', 'Talent Acquisition',
            'Performance Management', 'Training', 'Onboarding', 'Compensation',
            'Benefits Administration', 'Labor Relations', 'HRIS',
            
            # Office & Productivity
            'MS Office', 'Microsoft Office', 'PowerPoint', 'Word', 'Outlook', 'Excel',
            'Google Suite', 'Data Entry', 'Administrative', 'Documentation',
            
            # Additional
            'Research', 'Analysis', 'Reporting', 'Documentation', 'Quality Assurance',
            'Process Improvement', 'Stakeholder Management', 'Risk Management'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            # Use word boundaries for better matching
            skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(skill_pattern, text_lower):
                found_skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills if unique_skills else ["Not specified"]
    
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
            r"(?:PMP|CISSP|AWS|Azure|Google Cloud|Google Analytics|CompTIA|CCNA|CCIE)",
            r"(?:Scrum Master|Product Owner|Six Sigma|ITIL)",
            r"(?:CPA|CFA|CMA|CIA|ACCA|CIMA)",  # Accounting certs
            r"(?:SHRM-CP|SHRM-SCP|PHR|SPHR)",  # HR certs
        ]
        
        # Look for certification section
        cert_section = re.search(
            r'(?:certifications?|licenses?)(.*?)(?:education|skills|experience|languages|$)',
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