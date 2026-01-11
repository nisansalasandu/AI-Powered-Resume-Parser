class AdvancedMatchingSystem:
    """
    Advanced candidate-job matching with scoring
    """
    
    @staticmethod
    def calculate_skill_match(candidate_skills, required_skills):
        """Calculate skill match percentage"""
        if not required_skills or not candidate_skills:
            return 0
        
        candidate_set = set(s.lower() for s in candidate_skills)
        required_set = set(s.lower() for s in required_skills)
        
        matched = candidate_set.intersection(required_set)
        
        if len(required_set) == 0:
            return 0
        
        return (len(matched) / len(required_set)) * 100
    
    @staticmethod
    def calculate_experience_match(candidate_years, required_years):
        """Calculate experience match score"""
        if required_years is None or candidate_years is None:
            return 50  # Neutral score if unknown
        
        if candidate_years >= required_years:
            return 100
        else:
            # Partial credit for having some experience
            return (candidate_years / required_years) * 100
    
    @staticmethod
    def calculate_education_match(candidate_education, required_education):
        """Calculate education match score"""
        if not required_education or not candidate_education:
            return 50  # Neutral score
        
        candidate_text = ' '.join(candidate_education).lower()
        required_text = ' '.join(required_education).lower()
        
        # Check for degree level matches
        degree_hierarchy = ['phd', 'doctorate', 'master', 'bachelor', 'diploma']
        
        candidate_level = -1
        required_level = -1
        
        for i, degree in enumerate(degree_hierarchy):
            if degree in candidate_text and candidate_level == -1:
                candidate_level = i
            if degree in required_text and required_level == -1:
                required_level = i
        
        if candidate_level == -1 or required_level == -1:
            return 50  # Unknown, neutral score
        
        if candidate_level <= required_level:  # Higher or equal
            return 100
        else:
            return 70  # Has degree but lower level
    
    @staticmethod
    def calculate_overall_match(candidate, job_description):
        """Calculate overall match score"""
        weights = {
            'skills': 0.50,      # 50% weight
            'experience': 0.30,  # 30% weight
            'education': 0.20    # 20% weight
        }
        
        skill_score = AdvancedMatchingSystem.calculate_skill_match(
            candidate.get('skills', []),
            job_description.get('required_skills', [])
        )
        
        exp_score = AdvancedMatchingSystem.calculate_experience_match(
            candidate.get('years_of_experience'),
            job_description.get('required_experience')
        )
        
        edu_score = AdvancedMatchingSystem.calculate_education_match(
            candidate.get('education', []),
            job_description.get('required_education', [])
        )
        
        overall_score = (
            skill_score * weights['skills'] +
            exp_score * weights['experience'] +
            edu_score * weights['education']
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'skill_match': round(skill_score, 2),
            'experience_match': round(exp_score, 2),
            'education_match': round(edu_score, 2)
        }
    
    @staticmethod
    def rank_candidates(candidates, job_description):
        """Rank all candidates for a job"""
        ranked = []
        
        for candidate in candidates:
            scores = AdvancedMatchingSystem.calculate_overall_match(
                candidate, 
                job_description
            )
            
            ranked.append({
                'candidate': candidate,
                'scores': scores
            })
        
        # Sort by overall score descending
        ranked.sort(key=lambda x: x['scores']['overall_score'], reverse=True)
        
        return ranked


# Example usage
if __name__ == "__main__":
    # Sample candidate
    candidate = {
        'name': 'John Doe',
        'skills': ['Python', 'SQL', 'Communication', 'Leadership'],
        'years_of_experience': 5,
        'education': ['Bachelor of Science in Computer Science']
    }
    
    # Sample job description
    job = {
        'job_title': 'Software Engineer',
        'required_skills': ['Python', 'Java', 'SQL'],
        'required_experience': 3,
        'required_education': ['Bachelor']
    }
    
    matcher = AdvancedMatchingSystem()
    scores = matcher.calculate_overall_match(candidate, job)
    
    print("Matching Scores:")
    print(f"Overall: {scores['overall_score']}%")
    print(f"Skills: {scores['skill_match']}%")
    print(f"Experience: {scores['experience_match']}%")
    print(f"Education: {scores['education_match']}%")