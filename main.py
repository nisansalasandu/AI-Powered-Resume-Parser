import os
from pathlib import Path
from resume_parser import ResumeParser
from data_cleaner import DataCleaner
import json
import pandas as pd
from datetime import datetime

class ResumeProcessingSystem:
    """Main orchestrator for batch resume processing"""
    
    def __init__(self):
        self.parser = ResumeParser()
        self.cleaner = DataCleaner()
        self.resume_folders = ['resumes/pdf', 'resumes/docx', 'resumes/txt']
        self.output_folder = 'processed_data'
    
    def get_all_resume_files(self):
        """Scan all resume folders"""
        all_files = []
        for folder in self.resume_folders:
            if os.path.exists(folder):
                files = [os.path.join(folder, f) for f in os.listdir(folder)
                        if f.lower().endswith(('.pdf', '.docx', '.txt'))]
                all_files.extend(files)
        return all_files
    
    def process_all_resumes(self):
        """Process all resumes with error handling"""
        print("=" * 60)
        print("RESUME PROCESSING SYSTEM")
        print("=" * 60)
        
        resume_files = self.get_all_resume_files()
        if not resume_files:
            print("\n❌ No resumes found! Place files in: resumes/pdf, resumes/docx, resumes/txt")
            return
        
        print(f"\nFound {len(resume_files)} resume(s) to process\n")
        
        all_resumes = []
        successful = failed = 0
        
        for file_path in resume_files:
            try:
                resume_data = self.parser.parse_resume(file_path)
                if resume_data:
                    cleaned = self.cleaner.clean_resume_data(resume_data)
                    all_resumes.append(cleaned)
                    successful += 1
                    print(f"✓ {Path(file_path).name}")
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"✗ {Path(file_path).name}: {e}")
        
        if all_resumes:
            self.save_results(all_resumes)
            self.match_to_jobs(all_resumes)
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS: {successful} | ❌ FAILED: {failed}")
        print("=" * 60)
    
    def save_results(self, resumes_data):
        """Save JSON, CSV, Excel (FIXED)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(self.output_folder, exist_ok=True)
        
        # JSON (full data)
        json_file = f"{self.output_folder}/resumes_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(resumes_data, f, indent=2, ensure_ascii=False)
        
        # DataFrame + Excel-safe cleaning
        df = self.cleaner.to_dataframe(resumes_data)
        csv_file = f"{self.output_folder}/resumes_{timestamp}.csv"
        excel_file = f"{self.output_folder}/resumes_{timestamp}.xlsx"
        
        df.to_csv(csv_file, index=False)
        df.to_excel(excel_file, index=False)
        
        print(f"\n📊 SAVED:")
        print(f"  JSON:  {json_file}")
        print(f"  CSV:   {csv_file}")
        print(f"  Excel: {excel_file}")
        print(f"\n📋 PREVIEW:")
        print(df[['name', 'email', 'skills', 'years_of_experience']].head())

def main():
    system = ResumeProcessingSystem()
    system.process_all_resumes()

if __name__ == "__main__":
    main()
