import PyPDF2
import docx
import re
import os
import json
from pathlib import Path

class JobDescriptionParser:
    """
    Parse job descriptions from multiple sources:
    - PDF files
    - DOCX files
    - TXT files
    - Email content
    - Web forms
    """
    
    def __init__(self):
        self.job_folder = 'job_descriptions'
    
    def read_pdf(self, file_path):
        """Extract text from PDF job description"""
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
        """Extract text from DOCX job description"""
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
        """Extract text from TXT job description"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Error reading TXT {file_path}: {str(e)}")
                return None
    
    def extract_text(self, file_path):
        """Extract text based on file type"""
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
    
    def extract_job_title(self, text):
        """Extract job title from description"""
        # Look for common patterns
        patterns = [
            r'(?:Position|Role|Job Title|Title):\s*([^\n]+)',
            r'^([^\n]{10,60})\n',  # First line (common in job posts)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # Fallback: return first line
        lines = text.strip().split('\n')
        return lines[0].strip() if lines else "Unknown Position"
    
    def extract_required_skills(self, text):
        """Extract required skills from job description"""
        skills = []
        
        # Find skills section
        skills_section = re.search(
            r'(?:required skills|qualifications|requirements|skills)(.*?)(?:responsibilities|duties|benefits|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if skills_section:
            skills_text = skills_section.group(1)
            
            # Common skills database
            common_skills = [
                'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'HTML', 'CSS',
                'React', 'Angular', 'Node.js', 'Django', 'Flask',
                'Machine Learning', 'Data Analysis', 'AWS', 'Azure', 'Docker',
                'Communication', 'Leadership', 'Project Management', 'Teamwork',
                'Problem Solving', 'Marketing', 'SEO', 'Social Media',
                'Accounting', 'Financial Analysis', 'Excel', 'QuickBooks',
                'HR Management', 'Recruitment', 'Employee Relations',
                'MS Office', 'PowerPoint', 'Word', 'Outlook'
            ]
            
            skills_lower = skills_text.lower()
            for skill in common_skills:
                if skill.lower() in skills_lower:
                    skills.append(skill)
        
        return skills if skills else ["Not specified"]
    
    def extract_experience_required(self, text):
        """Extract required years of experience"""
        # Patterns like "3-5 years", "3+ years", "minimum 3 years"
        patterns = [
            r'(\d+)\s*[-–to]+\s*(\d+)\s*years',
            r'(\d+)\+?\s*years',
            r'minimum\s+(\d+)\s*years',
            r'at least\s+(\d+)\s*years'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    # Range: return average
                    return (int(match.group(1)) + int(match.group(2))) / 2
                else:
                    return int(match.group(1))
        
        return None
    
    def extract_education_required(self, text):
        """Extract required education level"""
        education = []
        
        degree_patterns = [
            r"Bachelor(?:'s)?\s+(?:degree|of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce)?",
            r"Master(?:'s)?\s+(?:degree|of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce)?",
            r"B\.?(?:Sc|A|E|Tech|Com|B\.?A)\.?",
            r"M\.?(?:Sc|A|E|Tech|Com|B\.?A)\.?",
            r"Ph\.?D\.?",
            r"Diploma",
            r"High School|Secondary Education"
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append(match.group(0))
        
        return education if education else ["Not specified"]
    
    def parse_job_description(self, file_path):
        """Main method to parse a job description"""
        print(f"\nParsing Job Description: {os.path.basename(file_path)}")
        
        text = self.extract_text(file_path)
        
        if not text:
            return None
        
        job_data = {
            'file_name': os.path.basename(file_path),
            'job_title': self.extract_job_title(text),
            'required_skills': self.extract_required_skills(text),
            'required_experience': self.extract_experience_required(text),
            'required_education': self.extract_education_required(text),
            'raw_text': text[:1000]  # Store first 1000 chars
        }
        
        return job_data
    
    def parse_all_job_descriptions(self):
        """Parse all job descriptions in the job_descriptions folder"""
        if not os.path.exists(self.job_folder):
            print(f"Job descriptions folder not found: {self.job_folder}")
            return []
        
        job_files = [
            os.path.join(self.job_folder, f)
            for f in os.listdir(self.job_folder)
            if f.lower().endswith(('.pdf', '.docx', '.txt'))
        ]
        
        if not job_files:
            print("No job description files found!")
            return []
        
        all_jobs = []
        for file_path in job_files:
            job_data = self.parse_job_description(file_path)
            if job_data:
                all_jobs.append(job_data)
        
        return all_jobs
    
    def save_parsed_jobs(self, jobs_data, output_file='parsed_jobs.json'):
        """Save parsed job descriptions"""
        output_path = os.path.join('processed_data', output_file)
        os.makedirs('processed_data', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved parsed job descriptions: {output_path}")


# Usage example
if __name__ == "__main__":
    # Test job description parser
    jd_parser = JobDescriptionParser()
    jobs = jd_parser.parse_all_job_descriptions()
    
    if jobs:
        jd_parser.save_parsed_jobs(jobs)
        
        print("\n" + "="*60)
        print("PARSED JOB DESCRIPTIONS")
        print("="*60)
        for job in jobs:
            print(f"\nJob: {job['job_title']}")
            print(f"Required Skills: {', '.join(job['required_skills'][:5])}")
            print(f"Required Experience: {job['required_experience']} years")
            print(f"Required Education: {', '.join(job['required_education'])}")