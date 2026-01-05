import os
from pathlib import Path
from resume_parser import ResumeParser
from data_cleaner import DataCleaner
import json
import pandas as pd
from datetime import datetime

class ResumeProcessingSystem:
    def __init__(self):
        self.parser = ResumeParser()
        self.cleaner = DataCleaner()
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
        print("=" * 60)
        print("RESUME PROCESSING SYSTEM")
        print("=" * 60)
        
        resume_files = self.get_all_resume_files()
        
        if not resume_files:
            print("\nNo resume files found!")
            print("Please place resumes in:")
            for folder in self.resume_folders:
                print(f"  - {folder}")
            return
        
        print(f"\nFound {len(resume_files)} resume(s) to process\n")
        
        all_resumes = []
        successful = 0
        failed = 0
        
        for file_path in resume_files:
            try:
                resume_data = self.parser.parse_resume(file_path)
                
                if resume_data:
                    cleaned_data = self.cleaner.clean_resume_data(resume_data)
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
            self.save_results(all_resumes)
        
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total files: {len(resume_files)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print("=" * 60)
    
    def save_results(self, resumes_data):
        """Save processed data in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        os.makedirs(self.output_folder, exist_ok=True)
        
        json_file = os.path.join(self.output_folder, f'resumes_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(resumes_data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved JSON: {json_file}")
        
        df = self.cleaner.to_dataframe(resumes_data)
        excel_file = os.path.join(self.output_folder, f'resumes_{timestamp}.xlsx')
        df.to_excel(excel_file, index=False)
        print(f"✓ Saved Excel: {excel_file}")
        
        csv_file = os.path.join(self.output_folder, f'resumes_{timestamp}.csv')
        df.to_csv(csv_file, index=False)
        print(f"✓ Saved CSV: {csv_file}")
        
        print("\n" + "=" * 60)
        print("DATA PREVIEW")
        print("=" * 60)
        print(df.to_string(max_rows=5))

def main():
    system = ResumeProcessingSystem()
    system.process_all_resumes()

if __name__ == "__main__":
    main()