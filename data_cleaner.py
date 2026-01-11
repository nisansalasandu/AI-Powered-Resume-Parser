import re
import pandas as pd

class DataCleaner:
    
    @staticmethod
    def clean_phone_number(phone):
        """Standardize phone number format"""
        if not phone:
            return None
        
        # Remove all non-numeric characters
        digits = re.sub(r'\D', '', phone)
        
        # Format as (XXX) XXX-XXXX
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone  # Return original if can't format
    
    @staticmethod
    def clean_email(email):
        """Clean and validate email"""
        if not email:
            return None
        
        email = email.lower().strip()
        
        # Basic email validation
        email_pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if re.match(email_pattern, email):
            return email
        return None
    
    @staticmethod
    def clean_name(name):
        """Clean and standardize name"""
        if not name or name == "Unknown":
            return "Unknown"
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Capitalize properly
        name = name.title()
        
        return name
    
    @staticmethod
    def extract_years_of_experience(experience_list):
        """Calculate total years of experience"""
        total_years = 0
        
        for exp in experience_list:
            if isinstance(exp, str):
                # Find year ranges
                years = re.findall(r'(\d{4})', exp)
                if len(years) >= 2:
                    try:
                        start_year = int(years[0])
                        end_year = int(years[1])
                        total_years += (end_year - start_year)
                    except:
                        pass
                # Check for "Present" or "Current"
                elif len(years) == 1 and re.search(r'present|current', exp, re.IGNORECASE):
                    try:
                        start_year = int(years[0])
                        current_year = 2024
                        total_years += (current_year - start_year)
                    except:
                        pass
        
        return total_years if total_years > 0 else None
    
    @staticmethod
    def clean_resume_data(resume_data):
        """Clean all data in resume"""
        if not resume_data:
            return None
        
        cleaned_data = {
            'file_name': resume_data.get('file_name', ''),
            'name': DataCleaner.clean_name(resume_data.get('name')),
            'email': DataCleaner.clean_email(resume_data.get('email')),
            'phone': DataCleaner.clean_phone_number(resume_data.get('phone')),
            'education': resume_data.get('education', []),
            'skills': resume_data.get('skills', []),
            'experience': resume_data.get('experience', []),
            'certifications': resume_data.get('certifications', []),
            'years_of_experience': DataCleaner.extract_years_of_experience(
                resume_data.get('experience', [])
            )
        }
        
        return cleaned_data
    
    @staticmethod
    def to_dataframe(resume_list):
        """Convert list of resumes to pandas DataFrame"""
        if not resume_list:
            return None
        
        # Flatten the data for DataFrame
        flattened_data = []
        
        for resume in resume_list:
            flat_resume = {
                'file_name': resume.get('file_name', ''),
                'name': resume.get('name', ''),
                'email': resume.get('email', ''),
                'phone': resume.get('phone', ''),
                'years_of_experience': resume.get('years_of_experience', 0),
                'education': ', '.join(resume.get('education', [])),
                'skills': ', '.join(resume.get('skills', [])),
                'certifications': ', '.join(resume.get('certifications', [])),
                'experience_summary': ' | '.join(resume.get('experience', [])[:2])
            }
            flattened_data.append(flat_resume)
        
        return pd.DataFrame(flattened_data)


# Example usage
if __name__ == "__main__":
    # Sample data
    sample_resume = {
        'file_name': 'john_doe.pdf',
        'name': 'JOHN DOE',
        'email': '  JOHN.DOE@GMAIL.COM  ',
        'phone': '1234567890',
        'education': ['Bachelor of Science in Computer Science'],
        'skills': ['Python', 'Java', 'SQL'],
        'experience': ['Software Engineer at ABC Corp 2020-2023'],
        'certifications': ['AWS Certified Developer']
    }
    
    cleaner = DataCleaner()
    cleaned = cleaner.clean_resume_data(sample_resume)
    
    print("Cleaned Data:")
    for key, value in cleaned.items():
        print(f"{key}: {value}")