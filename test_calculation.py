#!/usr/bin/env python3
"""
Test script to verify result calculation fixes
"""

from app.services.result_service import compute_class_results
from app.db.session import SessionLocal
from app.models.assessment import Assessment
from app.models.score import Score
from app.models.student import Student
from app.models.class_subject import ClassSubject

def test_calculation():
    db = SessionLocal()
    
    try:
        # Get a sample class
        class_subject = db.query(ClassSubject).first()
        if not class_subject:
            print("No class subjects found. Please seed the database first.")
            return
            
        print(f"Testing calculations for Class ID: {class_subject.class_id}")
        
        # Get assessments and scores for this class
        assessments = db.query(Assessment).filter(
            Assessment.class_subject_id == class_subject.id,
            Assessment.term == 1
        ).all()
        
        print(f"\nFound {len(assessments)} assessments:")
        for a in assessments:
            print(f"  - {a.title}: max_score={a.max_score}, weight={a.weight_percentage}")
            scores = db.query(Score).filter(Score.assessment_id == a.id).limit(3).all()
            for s in scores:
                student = db.query(Student).filter(Student.id == s.student_id).first()
                print(f"    Student {student.matricule}: {s.score}/{a.max_score}")
        
        # Calculate results
        results = compute_class_results(db, class_subject.class_id, 1)
        
        print(f"\nCalculated results for {len(results)} students:")
        for result in results[:5]:  # Show first 5 students
            print(f"\nStudent: {result['student_name']} ({result['matricule']})")
            print(f"Overall Average: {result['average']}")
            print(f"Status: {result['promotion_status']}")
            for subject in result['subjects']:
                print(f"  {subject['subject_name']}: {subject['average']} ({subject['grade']})")
        
        # Check if averages are reasonable
        averages = [r['average'] for r in results]
        avg_avg = sum(averages) / len(averages) if averages else 0
        
        print(f"\nClass Statistics:")
        print(f"  Average of averages: {avg_avg:.2f}")
        print(f"  Highest average: {max(averages):.2f}")
        print(f"  Lowest average: {min(averages):.2f}")
        print(f"  Students >= 10: {sum(1 for a in averages if a >= 10)}/{len(averages)}")
        
        # Expected ranges
        if 8 <= avg_avg <= 14:
            print("✅ Class average looks reasonable!")
        else:
            print(f"❌ Class average {avg_avg} seems unusual (expected 8-14)")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_calculation()
