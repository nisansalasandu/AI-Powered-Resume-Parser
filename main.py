import os
from resume_parser import ResumeParser
from data_cleaner import DataCleaner
from job_description_parser import JobDescriptionParser
from matching_system import AdvancedMatchingSystem
import json
import pandas as pd
from datetime import datetime

class EnhancedResumeProcessingSystem:
    def __init__(self):
        self.resume_parser = ResumeParser()
        self.data_cleaner = DataCleaner()
        self.jd_parser = JobDescriptionParser()
        self.matcher = AdvancedMatchingSystem()
        
        self.resume_folders = ['resumes/pdf', 'resumes/docx', 'resumes/txt']
        self.output_folder = 'processed_data'
    
    def get_all_resume_files(self):
        """Get all resume files from all folders"""
        all_files = []
        
        for folder in self.resume_folders:
            if os.path.exists(folder):
                files = [
                    os.path.join(folder, f) 
                    for f in os.listdir(folder)
                    if f.lower().endswith(('.pdf', '.docx', '.txt'))
                ]
                all_files.extend(files)
        
        return all_files
    
    def process_all_resumes(self):
        """Process all resumes and save results"""
        print("=" * 70)
        print("ENHANCED RESUME PROCESSING SYSTEM")
        print("=" * 70)
        
        resume_files = self.get_all_resume_files()
        
        if not resume_files:
            print("\n⚠️  No resume files found!")
            print("Please place resumes in:")
            for folder in self.resume_folders:
                print(f"  - {folder}/")
            return []
        
        print(f"\n📄 Found {len(resume_files)} resume(s) to process\n")
        
        all_resumes = []
        successful = 0
        failed = 0
        
        for file_path in resume_files:
            try:
                resume_data = self.resume_parser.parse_resume(file_path)
                
                if resume_data:
                    cleaned_data = self.data_cleaner.clean_resume_data(resume_data)
                    all_resumes.append(cleaned_data)
                    successful += 1
                    print(f"✓ Successfully processed: {os.path.basename(file_path)}")
                else:
                    failed += 1
                    print(f"✗ Failed to process: {os.path.basename(file_path)}")
            
            except Exception as e:
                failed += 1
                print(f"✗ Error processing {os.path.basename(file_path)}: {str(e)}")
        
        if all_resumes:
            self.save_results(all_resumes, 'resumes')
        
        print("\n" + "=" * 70)
        print("PROCESSING SUMMARY")
        print("=" * 70)
        print(f"Total files: {len(resume_files)}")
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {failed}")
        print("=" * 70)
        
        return all_resumes
    
    def process_job_descriptions(self):
        """Process all job descriptions"""
        print("\n" + "=" * 70)
        print("JOB DESCRIPTION PROCESSING")
        print("=" * 70)
        
        jobs = self.jd_parser.parse_all_job_descriptions()
        
        if jobs:
            self.save_results(jobs, 'job_descriptions')
            
            print(f"\n✓ Processed {len(jobs)} job description(s)")
            
            for job in jobs:
                print(f"\n📋 {job['job_title']}")
                print(f"   Skills: {', '.join(job['required_skills'][:5])}")
                if job['required_experience']:
                    print(f"   Experience: {job['required_experience']} years")
        else:
            print("\n⚠️  No job descriptions found in 'job_descriptions/' folder")
            print("   Please add job description files (PDF, DOCX, or TXT)")
        
        return jobs
    
    def match_candidates_to_jobs(self, candidates, jobs):
        """Match candidates to job descriptions with scoring"""
        if not candidates or not jobs:
            print("\n⚠️  Cannot perform matching: Missing candidates or job descriptions")
            return
        
        print("\n" + "=" * 70)
        print("CANDIDATE MATCHING & SCORING")
        print("=" * 70)
        
        all_matches = {}
        
        for job in jobs:
            job_title = job['job_title']
            ranked_candidates = self.matcher.rank_candidates(candidates, job)
            
            all_matches[job_title] = ranked_candidates
            
            print(f"\n{'='*70}")
            print(f"📋 Position: {job_title}")
            print(f"{'='*70}")
            
            if ranked_candidates:
                print(f"\n{'Rank':<6} {'Name':<25} {'Overall':<10} {'Skills':<10} {'Exp':<10} {'Edu':<10}")
                print("-" * 70)
                
                for i, match in enumerate(ranked_candidates[:10], 1):  # Top 10
                    candidate = match['candidate']
                    scores = match['scores']
                    
                    print(f"{i:<6} {candidate['name'][:24]:<25} "
                          f"{scores['overall_score']:<10.1f} "
                          f"{scores['skill_match']:<10.1f} "
                          f"{scores['experience_match']:<10.1f} "
                          f"{scores['education_match']:<10.1f}")
                
                # Show contact info for top 3
                print(f"\n{'Top 3 Candidates Contact Info:'}")
                print("-" * 70)
                for i, match in enumerate(ranked_candidates[:3], 1):
                    candidate = match['candidate']
                    print(f"{i}. {candidate['name']}")
                    print(f"   Email: {candidate.get('email', 'N/A')}")
                    print(f"   Phone: {candidate.get('phone', 'N/A')}")
                    print(f"   Match Score: {match['scores']['overall_score']:.1f}%\n")
            else:
                print("   No matching candidates found")
        
        # Save matching results
        self.save_matching_results(all_matches)
        
        return all_matches
    
    def save_results(self, data, data_type):
        """Save processed data in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(self.output_folder, exist_ok=True)
        
        # JSON
        json_file = os.path.join(
            self.output_folder, 
            f'{data_type}_{timestamp}.json'
        )
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved JSON: {json_file}")
        
        # Excel & CSV (if it's resume data)
        if data_type == 'resumes':
            df = self.data_cleaner.to_dataframe(data)
            
            excel_file = os.path.join(
                self.output_folder, 
                f'{data_type}_{timestamp}.xlsx'
            )
            df.to_excel(excel_file, index=False)
            print(f"✓ Saved Excel: {excel_file}")
            
            csv_file = os.path.join(
                self.output_folder, 
                f'{data_type}_{timestamp}.csv'
            )
            df.to_csv(csv_file, index=False)
            print(f"✓ Saved CSV: {csv_file}")
    
    def save_matching_results(self, matches):
        """Save matching results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare data for export
        match_data = []
        
        for job_title, candidates in matches.items():
            for rank, match in enumerate(candidates, 1):
                candidate = match['candidate']
                scores = match['scores']
                
                match_data.append({
                    'rank': rank,
                    'job_title': job_title,
                    'candidate_name': candidate['name'],
                    'email': candidate.get('email', 'N/A'),
                    'phone': candidate.get('phone', 'N/A'),
                    'overall_score': scores['overall_score'],
                    'skill_match': scores['skill_match'],
                    'experience_match': scores['experience_match'],
                    'education_match': scores['education_match'],
                    'years_experience': candidate.get('years_of_experience', 0)
                })
        
        # Save as Excel
        df = pd.DataFrame(match_data)
        excel_file = os.path.join(
            self.output_folder, 
            f'candidate_matches_{timestamp}.xlsx'
        )
        df.to_excel(excel_file, index=False)
        print(f"\n✓ Saved matching results: {excel_file}")
        
        # Save as CSV
        csv_file = os.path.join(
            self.output_folder, 
            f'candidate_matches_{timestamp}.csv'
        )
        df.to_csv(csv_file, index=False)
        print(f"✓ Saved CSV: {csv_file}")


def main():
    """Main execution function"""
    system = EnhancedResumeProcessingSystem()
    
    # Step 1: Process all resumes
    candidates = system.process_all_resumes()
    
    # Step 2: Process job descriptions
    jobs = system.process_job_descriptions()
    
    # Step 3: Match candidates to jobs
    if candidates and jobs:
        system.match_candidates_to_jobs(candidates, jobs)
    
    print("\n" + "=" * 70)
    print("✓ PROCESSING COMPLETE!")
    print("=" * 70)
    print(f"\nCheck the '{system.output_folder}/' folder for all results:")
    print("  • Resume data (JSON, Excel, CSV)")
    print("  • Job descriptions (JSON)")
    print("  • Candidate matches with scores (Excel, CSV)")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()