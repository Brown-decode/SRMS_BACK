from fastapi import APIRouter, Depends, HTTPException, Query
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.dependencies import require_student
from app.services.result_service import compute_class_results
from fastapi.responses import StreamingResponse
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import datetime

results_pdf_router = APIRouter(prefix="/students", tags=["student"])

# Mock school header data
SCHOOL_HEADER = {
    "name": "Government Bilingual High School Bepanda",
    "motto": "Peace-Work-Fatherland",
    "address": "P.O BOX/B.P 24039, Douala, Cameroon",
    "phone": "+237 233 123 456",
    "email": "info@govsec-Douala.cm",
}


def calculate_grade(score):
    """Calculate grade based on 0-20 scale"""
    if score >= 16:
        return "A"
    elif score >= 14:
        return "B"
    elif score >= 12:
        return "C"
    elif score >= 10:
        return "D"
    else:
        return "F"


def generate_results_pdf(school_header, student_data, term):
    """Generate PDF report card using ReportLab"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
    )

    # Logo style for GBHS
    logo_style = ParagraphStyle(
        "Logo",
        parent=styles["Heading1"],
        fontSize=32,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName="Helvetica-Bold",
    )

    header_style = ParagraphStyle(
        "Header",
        parent=styles["Normal"],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "Normal", parent=styles["Normal"], fontSize=10, spaceAfter=6
    )

    # Add GBHS Logo using image from login page
    logo_elements = []

    # Add logo image instead of text
    try:
        from reportlab.platypus import Image as RLImage

        logo_path = "app/routes/gbhs_bepanda.jpg"
        logo_elements.append(Spacer(1, 25))
        logo_elements.append(RLImage(logo_path, width=80, height=80))
        logo_elements.append(Spacer(1, 15))
    except:
        # Fallback to text if image not found
        logo_elements.append(Spacer(1, 25))
        logo_elements.append(Paragraph("GBHS", logo_style))
        logo_elements.append(Spacer(1, 15))

    logo_elements.append(Paragraph(school_header["name"], title_style))
    logo_elements.append(Spacer(1, 8))
    logo_elements.append(Paragraph(school_header["motto"], header_style))
    logo_elements.append(Spacer(1, 35))

    elements.extend(logo_elements)

    # School Header
    elements.append(Paragraph(school_header["name"], title_style))
    elements.append(Paragraph(school_header["motto"], header_style))
    elements.append(Paragraph(school_header["address"], header_style))
    elements.append(
        Paragraph(
            f"Tel: {school_header['phone']} | Email: {school_header['email']}",
            header_style,
        )
    )
    elements.append(Spacer(1, 20))

    # Report Card Title
    elements.append(Paragraph("END OF TERM REPORT CARD", title_style))
    elements.append(Spacer(1, 12))

    # Academic Year and Term
    current_year = datetime.datetime.now().year
    academic_year = f"{current_year-1}/{current_year}"
    elements.append(Paragraph(f"Academic Year: {academic_year}", header_style))
    elements.append(Paragraph(f"Term: {term}", header_style))
    elements.append(Spacer(1, 20))

    # Student Information
    elements.append(Paragraph("STUDENT INFORMATION", styles["Heading2"]))
    student_info_data = [
        ["Name:", student_data["student_name"]],
        ["Matricule:", student_data["matricule"]],
        ["Class:", f"Form {student_data.get('class', 'N/A')}"],
    ]

    student_info_table = Table(student_info_data, colWidths=[2 * inch, 4 * inch])
    student_info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    elements.append(student_info_table)
    elements.append(Spacer(1, 20))

    # Subjects Results
    elements.append(Paragraph("ACADEMIC PERFORMANCE", styles["Heading2"]))

    # Prepare subjects data
    subjects_data = [["SUBJECT", "COEFF", "SCORE", "GRADE", "POSITION", "REMARKS"]]

    total_score = 0
    total_coefficient = 0

    for subject in student_data.get("subjects", []):
        subject_name = subject.get("subject_name", "N/A")
        coefficient = subject.get("coefficient", 1)
        score = subject.get("average", 0)
        grade = calculate_grade(score)
        position = subject.get("position", "-")
        remark = "Passed" if score >= 10 else "Failed"

        subjects_data.append(
            [
                subject_name,
                str(coefficient),
                f"{score:.2f}",
                grade,
                str(position),
                remark,
            ]
        )

        total_score += score * coefficient
        total_coefficient += coefficient

    subjects_table = Table(
        subjects_data,
        colWidths=[2.5 * inch, 0.8 * inch, 1 * inch, 0.8 * inch, 1 * inch, 1.2 * inch],
    )
    subjects_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(subjects_table)
    elements.append(Spacer(1, 20))

    # Summary Statistics
    elements.append(Paragraph("SUMMARY STATISTICS", styles["Heading2"]))

    overall_average = total_score / total_coefficient if total_coefficient > 0 else 0
    class_position = student_data.get("position", 0)
    total_students = student_data.get(
        "total_students", student_data.get("class_size", 0)
    )  # Use real data
    promotion_status = student_data.get("promotion_status", "REPEAT")

    summary_data = [
        ["Overall Average:", f"{overall_average:.2f}"],
        ["Class Position:", f"{class_position} out of {total_students}"],
        ["Promotion Status:", promotion_status],
    ]

    summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # Signatures
    elements.append(Paragraph("SIGNATURES", styles["Heading2"]))

    signature_data = [
        ["Class Teacher:", "", "Principal:", ""],
        ["_____________________", "", "_____________________", ""],
        ["Name & Signature", "", "Name & Signature", ""],
        ["Date: _______________", "", "Date: _______________", ""],
    ]

    signature_table = Table(
        signature_data, colWidths=[2 * inch, 0.5 * inch, 2 * inch, 0.5 * inch]
    )
    signature_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    elements.append(signature_table)
    elements.append(Spacer(1, 20))

    # Footer
    elements.append(
        Paragraph(
            f"Generated on: {datetime.datetime.now().strftime('%d/%m/%Y')}",
            normal_style,
        )
    )
    elements.append(
        Paragraph(
            "This is a computer generated document and does not require a signature",
            normal_style,
        )
    )

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


@results_pdf_router.post("/me/results/pdf")
async def download_results_pdf(
    term: int = Query(..., description="Term number (1, 2, or 3)"),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    """Generate and download PDF report card for student results"""
    try:
        student = current_user.student
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Get real student results
        all_results = compute_class_results(db, student.class_id, term)
        student_report = next(
            (res for res in all_results if res["matricule"] == student.matricule), None
        )

        if not student_report:
            raise HTTPException(
                status_code=404, detail=f"No results found for term {term}"
            )

        # Generate PDF
        pdf_buffer = generate_results_pdf(SCHOOL_HEADER, student_report, term)

        return StreamingResponse(
            io.BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=results_term_{term}.pdf"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
