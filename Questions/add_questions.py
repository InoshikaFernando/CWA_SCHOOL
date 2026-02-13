#!/usr/bin/env python
"""
Master script to add/update all questions from all year/topic scripts
This script calls all add_year*_<topic>.py functions to populate the database
"""
import os
import sys
import django
import subprocess

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

# Import all the add functions from individual scripts
from add_year2_measurements import setup_measurements_topic as setup_year2_measurements, add_measurements_questions as add_year2_measurements
from add_year2_place_values import setup_place_values_topic, add_place_values_questions
from add_year3_measurements import setup_measurements_topic as setup_year3_measurements, add_measurements_questions as add_year3_measurements
from add_year3_fractions import setup_fractions_topic, add_fractions_questions
from add_year3_finance import setup_finance_topic, add_finance_questions
from add_year3_date_time import setup_date_time_topic, add_date_time_questions
from add_year4_fractions import setup_fractions_topic as setup_year4_fractions, add_fractions_questions as add_year4_fractions
from add_year4_integers import setup_integers_topic as setup_year4_integers, add_integers_questions as add_year4_integers
from add_year5_measurements import setup_measurements_topic as setup_year5_measurements, add_measurements_questions as add_year5_measurements
from add_year5_bodmas import setup_bodmas_topic as setup_year5_bodmas, add_bodmas_questions as add_year5_bodmas
from add_year6_measurements import setup_measurements_topic as setup_year6_measurements, add_measurements_questions as add_year6_measurements
from add_year6_bodmas import setup_bodmas_topic as setup_year6_bodmas, add_bodmas_questions as add_year6_bodmas
from add_year6_whole_numbers import setup_whole_numbers_topic as setup_year6_whole_numbers, add_whole_numbers_questions as add_year6_whole_numbers
from add_year6_factors import setup_factors_topic as setup_year6_factors, add_factors_questions as add_year6_factors
from add_year6_angles import setup_angles_topic as setup_year6_angles, add_angles_questions as add_year6_angles
from add_year7_measurements import setup_measurements_topic as setup_year7_measurements, add_measurements_questions as add_year7_measurements
from add_year7_bodmas import setup_bodmas_topic as setup_year7_bodmas, add_bodmas_questions as add_year7_bodmas
from add_year7_integers import setup_integers_topic as setup_year7_integers, add_integers_questions as add_year7_integers
from add_year8_trigonometry import setup_trigonometry_topic as setup_year8_trigonometry, add_trigonometry_questions as add_year8_trigonometry

def run_script_file(script_name, script_path):
    """
    Run a Python script file using subprocess
    """
    try:
        # Get the directory where this script is located (Questions folder)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the parent directory (project root)
        project_root = os.path.dirname(current_dir)
        
        # Handle paths that might be relative to project root or Questions folder
        if script_path.startswith('../') or script_path.startswith('Testing/'):
            # Path is relative to project root
            script_full_path = os.path.join(project_root, script_path.lstrip('../'))
        else:
            # Path is relative to Questions folder
            script_full_path = os.path.join(current_dir, script_path)
        
        # Normalize the path
        script_full_path = os.path.normpath(script_full_path)
        
        if not os.path.exists(script_full_path):
            print(f"[ERROR] Script file not found: {script_full_path}")
            return False
        
        result = subprocess.run(
            [sys.executable, script_full_path],
            capture_output=False,
            text=True,
            cwd=project_root  # Run from project root so imports work correctly
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Failed to run {script_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_question_scripts():
    """
    Run all question addition scripts in order
    """
    
    print("=" * 80)
    print("ADDING ALL QUESTIONS FROM ALL YEAR/TOPIC SCRIPTS")
    print("=" * 80)
    print()
    
    # Scripts that need to be run as files (no function structure)
    file_scripts = [
        ("Basic Facts - Topic Structure", "create_basic_facts.py"),
        ("Basic Facts - Generate Questions", "../generate_basic_facts_questions.py"),
    ]
    
    # Scripts that use function calls
    function_scripts = [
        # Year 2
        ("Year 2 - Measurements", setup_year2_measurements, add_year2_measurements),
        ("Year 2 - Place Values", setup_place_values_topic, add_place_values_questions),
        
        # Year 3
        ("Year 3 - Measurements", setup_year3_measurements, add_year3_measurements),
        ("Year 3 - Fractions", setup_fractions_topic, add_fractions_questions),
        ("Year 3 - Finance", setup_finance_topic, add_finance_questions),
        ("Year 3 - Date and Time", setup_date_time_topic, add_date_time_questions),
        
        # Year 4
        ("Year 4 - Fractions", setup_year4_fractions, add_year4_fractions),
        ("Year 4 - Integers", setup_year4_integers, add_year4_integers),
        
        # Year 5
        ("Year 5 - Measurements", setup_year5_measurements, add_year5_measurements),
        ("Year 5 - BODMAS/PEMDAS", setup_year5_bodmas, add_year5_bodmas),
        
        # Year 6
        ("Year 6 - Measurements", setup_year6_measurements, add_year6_measurements),
        ("Year 6 - BODMAS/PEMDAS", setup_year6_bodmas, add_year6_bodmas),
        ("Year 6 - Whole Numbers", setup_year6_whole_numbers, add_year6_whole_numbers),
        ("Year 6 - Factors", setup_year6_factors, add_year6_factors),
        ("Year 6 - Angles", setup_year6_angles, add_year6_angles),
        
        # Year 7
        ("Year 7 - Measurements", setup_year7_measurements, add_year7_measurements),
        ("Year 7 - BODMAS/PEMDAS", setup_year7_bodmas, add_year7_bodmas),
        ("Year 7 - Integers", setup_year7_integers, add_year7_integers),
        
        # Year 8
        ("Year 8 - Trigonometry", setup_year8_trigonometry, add_year8_trigonometry),
    ]
    
    success_count = 0
    error_count = 0
    errors = []
    
    # First, run file-based scripts (like create_basic_facts.py)
    for script_name, script_path in file_scripts:
        print("\n" + "=" * 80)
        print(f"Running: {script_name}")
        print("=" * 80)
        print()
        
        if run_script_file(script_name, script_path):
            print(f"\n[OK] Completed: {script_name}")
            success_count += 1
        else:
            print(f"\n[ERROR] Failed: {script_name}")
            error_count += 1
            errors.append(f"{script_name}: Script execution failed")
    
    # Then, run function-based scripts
    for script_name, setup_func, add_func in function_scripts:
        print("\n" + "=" * 80)
        print(f"Running: {script_name}")
        print("=" * 80)
        print()
        
        try:
            # Run setup function
            result = setup_func()
            
            if result:
                topic, level = result
                print(f"\n[OK] Setup complete for {script_name}")
                print("-" * 80)
                
                # Run add questions function
                add_func(topic, level)
                print(f"\n[OK] Completed: {script_name}")
                success_count += 1
            else:
                print(f"\n[ERROR] Setup failed for {script_name}")
                error_count += 1
                errors.append(f"{script_name}: Setup failed")
        
        except Exception as e:
            print(f"\n[ERROR] Failed to run {script_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            error_count += 1
            errors.append(f"{script_name}: {str(e)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_scripts = len(function_scripts) + len(file_scripts)
    print(f"Total scripts: {total_scripts}")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")
    
    if error_count == 0:
        print("\n[SUCCESS] All question scripts completed successfully!")
        return True
    else:
        print(f"\n[WARNING] {error_count} script(s) failed. See errors above.")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run all question addition scripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script runs all add_year*_<topic>.py scripts to populate the database
with questions from all years and topics.

Examples:
  # Run all scripts
  python add_questions.py
  
  # Run with verbose output
  python add_questions.py --verbose
        """
    )
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose output')
    
    args = parser.parse_args()
    
    success = run_all_question_scripts()
    sys.exit(0 if success else 1)
