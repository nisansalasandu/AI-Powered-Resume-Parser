import re
import pandas as pd

class DataCleaner:
    """Clean and standardize extracted resume data"""
    
    @staticmethod
    def clean_phone_number(phone):
        """Format phone numbers consistently"""
        if not phone:
            return None
        # Remove non-digits, keep Sri Lankan format
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10 and digits.startswith(('7', '1')):
            return f"+94{''.join(['7' if d=='1' else d for d in digits])}"
        return phone
    
    @staticmethod
    def clean_email(email):
        """Validate and lowercase email"""
        if not email:
            return None
        email = email.lower().strip()
        pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        return email if re.match(pattern, email) else None
    
    @staticmethod
    def clean_name(name):
        """Title case name, handle Unknown"""
        if not name or name == "Unknown":
            return "Unknown"
        return ' '.join(name.split()).title()
    
    @staticmethod
    def extract_years_of_experience(experience):
        """Estimate total experience years"""
        total = 0
        for exp in experience:
            if isinstance(exp, str):
                years = re.findall(r'(\d+)\s*years?', exp, re.IGNORECASE)
                if years:
                    total += int(years[0])
                # Date ranges
                dates = re.findall(r'20\d{2}', exp)
                if len(dates) >= 2:
                    try:
                        total += int(dates[1]) - int(dates[0])
                    except:
                        pass
        return total if total > 0 else None
    
    @staticmethod
    def clean_resume_data(resume_data):
        """Apply all cleaning to single resume"""
        if not resume_data:
            return None
        
        return {
            'file_name': resume_data.get('file_name', ''),
            'name': DataCleaner.clean_name(resume_data.get('name')),
            'email': DataCleaner.clean_email(resume_data.get('email')),
            'phone': DataCleaner.clean_phone_number(resume_data.get('phone')),
            'education': resume_data.get('education', []),
            'skills': resume_data.get('skills', []),
            'experience': resume_data.get('experience', []),
            'years_of_experience': DataCleaner.extract_years_of_experience(
                resume_data.get('experience', [])
            )
        }
    
    @staticmethod
    def to_dataframe(resume_list):
        """Convert resumes to clean DataFrame for Excel/CSV"""
        if not resume_list:
            return pd.DataFrame()
        
        data = []
        for resume in resume_list:
            # CLEAN problematic chars for Excel
            flat = {
                'file_name': resume.get('file_name', ''),
                'name': str(resume.get('name', '')),
                'email': resume.get('email', ''),
                'phone': resume.get('phone', ''),
                'years_of_experience': resume.get('years_of_experience', 0),
                'num_skills': len(resume.get('skills', [])),
                'education': ' | '.join([str(e)[:50] for e in resume.get('education', [])[:2]]),
                'skills': ' | '.join([str(s)[:20] for s in resume.get('skills', [])[:5]]),
                'experience': ' | '.join([str(e)[:50] for e in resume.get('experience', [])[:2]])
            }
            data.append(flat)
        
        df = pd.DataFrame(data)
        # Final Excel-safe cleaning
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.replace(r'[\n\t\r\[]', ' ', regex=True)
        return df
