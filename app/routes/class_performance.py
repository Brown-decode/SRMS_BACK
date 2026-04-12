from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.student import StudentReportCard
from app.models.class_model import Class
from app.core.dependencies import require_admin
from app.models.user import User
from app.services.result_service import compute_class_results
from typing import List, Dict, Any

class_performance_router = APIRouter(prefix="/class-performance", tags=["class-performance"])

@class_performance_router.get("/", response_model=List[Dict[str, Any]])
async def get_class_performance_overview(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get class performance overview for all classes across all terms
    Returns real pass rates, student counts, and class names
    """
    try:
        # Get all classes
        classes = db.query(Class).all()
        
        if not classes:
            return []
        
        class_performance_data = []
        
        for class_obj in classes:
            # Get results for all terms (1, 2, 3)
            all_class_results = []
            for term in [1, 2, 3]:
                term_results = compute_class_results(db, class_obj.id, term)
                all_class_results.extend(term_results)
            
            if not all_class_results:
                # No results for this class
                class_performance_data.append({
                    "className": class_obj.name,
                    "passRate": 0,
                    "totalStudents": 0,
                    "passedStudents": 0
                })
                continue
            
            # Calculate overall class performance
            total_students = len(all_class_results)
            passed_students = len([
                result for result in all_class_results 
                if result.get("promotion_status") == "PROMOTED"
            ])
            
            pass_rate = round((passed_students / total_students) * 100) if total_students > 0 else 0
            
            class_performance_data.append({
                "className": class_obj.name,
                "passRate": pass_rate,
                "totalStudents": total_students,
                "passedStudents": passed_students
            })
        
        # Sort by pass rate (highest first)
        class_performance_data.sort(key=lambda x: x["passRate"], reverse=True)
        
        return class_performance_data
        
    except Exception as e:
        print(f"Error in class performance endpoint: {e}")
        return []
