#!/usr/bin/env python3
"""
ReportGen Pro — CLI-based PDF Report Generator
Supports Student and Company (Employee) reports.
Usage: python main.py
"""

import os
import sys
import json
import csv
import uuid
from datetime import datetime
from typing import List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import StudentRecord, EmployeeRecord
from src.data_loader import auto_load
from src.pdf_generator import generate_student_report, generate_company_report
from src.logo_gen import create_logo
import src.charts as charts


# ─────────────── CONSTANTS ────────────────
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
ASSETS_DIR  = os.path.join(os.path.dirname(__file__), "assets")
DATA_DIR    = os.path.join(os.path.dirname(__file__), "data")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# In-memory session data
session_students: List[StudentRecord] = []
session_employees: List[EmployeeRecord] = []


# ─────────────── UI HELPERS ───────────────
def banner():
    print("\n" + "═" * 60)
    print("    ██████╗ ███████╗██████╗  ██████╗ ██████╗ ████████╗")
    print("    ██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝")
    print("    ██████╔╝█████╗  ██████╔╝██║   ██║██████╔╝   ██║   ")
    print("    ██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║██╔══██╗   ██║   ")
    print("    ██║  ██║███████╗██║     ╚██████╔╝██║  ██║   ██║   ")
    print("    ╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ")
    print("    ██████╗ ███████╗███╗   ██╗")
    print("    ██╔════╝██╔════╝████╗  ██║")
    print("    ██║  ███╗█████╗  ██╔██╗ ██║")
    print("    ██║   ██║██╔══╝  ██║╚██╗██║")
    print("    ╚██████╔╝███████╗██║ ╚████║")
    print("     ╚═════╝ ╚══════╝╚═╝  ╚═══╝  Pro v1.0")
    print("═" * 60)
    print("    Professional PDF Report Generator")
    print("    © 2024 ReportGen Pro. All rights reserved.")
    print("═" * 60)


def hr():
    print("─" * 60)


def info(msg):
    print(f"  ✓  {msg}")


def warn(msg):
    print(f"  ⚠  {msg}")


def err(msg):
    print(f"  ✗  {msg}")


def prompt(msg, default=None):
    if default:
        result = input(f"  → {msg} [{default}]: ").strip()
        return result if result else default
    return input(f"  → {msg}: ").strip()


def ask_yes_no(msg, default="y"):
    result = input(f"  → {msg} [{'Y/n' if default == 'y' else 'y/N'}]: ").strip().lower()
    if not result:
        return default == "y"
    return result == "y"


def unique_filename(prefix: str, ext: str = "pdf") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(REPORTS_DIR, f"{prefix}_{ts}.{ext}")


# ─────────────── STUDENT INPUT ─────────────
def input_student_manual() -> Optional[StudentRecord]:
    print("\n  ── Enter Student Details ──")
    try:
        sid   = prompt("Student ID (e.g. S001)")
        name  = prompt("Full Name")
        email = prompt("Email Address")
        course = prompt("Course (e.g. BSc Computer Science)")
        dept  = prompt("Department (e.g. Engineering)")
        print("  Enter subject scores (0-100):")
        math  = float(prompt("  Math"))
        sci   = float(prompt("  Science"))
        eng   = float(prompt("  English"))
        hist  = float(prompt("  History"))
        cs    = float(prompt("  CS"))
        att   = float(prompt("  Attendance %"))
        return StudentRecord(sid, name, email, course, dept, math, sci, eng, hist, cs, att)
    except (ValueError, KeyboardInterrupt):
        err("Invalid input. Student not added.")
        return None


def input_employee_manual() -> Optional[EmployeeRecord]:
    print("\n  ── Enter Employee Details ──")
    try:
        eid   = prompt("Employee ID (e.g. E001)")
        name  = prompt("Full Name")
        email = prompt("Email Address")
        dept  = prompt("Department (e.g. Engineering)")
        role  = prompt("Job Role (e.g. Senior Developer)")
        perf  = prompt("Performance [Outstanding/Excellent/Good/Average/Poor]", "Good")
        proj  = int(prompt("Projects Completed", "0"))
        sal   = float(prompt("Salary (PKR)", "100000"))
        exp   = int(prompt("Years of Experience", "0"))
        status = prompt("Status [Active/Inactive]", "Active")
        return EmployeeRecord(eid, name, email, dept, role, perf, proj, sal, exp, status)
    except (ValueError, KeyboardInterrupt):
        err("Invalid input. Employee not added.")
        return None


# ─────────────── LOAD FROM FILE ────────────
def load_from_file(report_type: str):
    print(f"\n  ── Load {report_type.title()} Data from File ──")
    print(f"  Available files in data/:")
    for f in os.listdir(DATA_DIR):
        print(f"    • {f}")
    filepath = prompt("Enter filename (or full path)")

    if not os.path.isabs(filepath):
        filepath = os.path.join(DATA_DIR, filepath)

    if not os.path.exists(filepath):
        err(f"File not found: {filepath}")
        return

    try:
        records = auto_load(filepath, report_type)
        if not records:
            warn("No records loaded (file may be empty or malformed).")
            return

        if report_type == "student":
            session_students.extend(records)
            info(f"Loaded {len(records)} student records. Total: {len(session_students)}")
        else:
            session_employees.extend(records)
            info(f"Loaded {len(records)} employee records. Total: {len(session_employees)}")
    except Exception as e:
        err(f"Error loading file: {e}")


# ─────────────── GENERATE PDF ──────────────
def generate_pdf(report_type: str):
    records = session_students if report_type == "student" else session_employees

    if not records:
        warn(f"No {report_type} data in session. Please add or load data first.")
        return

    print(f"\n  ── Generate {report_type.title()} PDF Report ──")
    print(f"  Records in session: {len(records)}")

    if report_type == "student":
        institution = prompt("Institution name", "National University of Technology")
        semester    = prompt("Semester / Period", "Fall 2024")
    else:
        company = prompt("Company name", "TechCorp International")
        period  = prompt("Report period", "Q4 2024")

    include_charts = ask_yes_no("Include charts/graphs in report?", "y")
    use_logo       = ask_yes_no("Include branding logo?", "y")
    use_password   = ask_yes_no("Password-protect the PDF?", "n")
    password       = None
    if use_password:
        password = prompt("Enter password")

    # Generate logo
    logo_path = None
    if use_logo:
        logo_path = os.path.join(ASSETS_DIR, f"logo_{report_type}.png")
        try:
            create_logo(logo_path, report_type)
            info("Logo generated.")
        except Exception as e:
            warn(f"Logo generation failed: {e}")
            logo_path = None

    # Generate charts
    chart_paths = {}
    if include_charts:
        print("  Generating charts...")
        try:
            if report_type == "student":
                charts.student_grade_pie(records, chart_paths.setdefault("grade_pie",
                    os.path.join(ASSETS_DIR, "chart_grade_pie.png")))
                charts.student_avg_bar(records, chart_paths.setdefault("avg_bar",
                    os.path.join(ASSETS_DIR, "chart_avg_bar.png")))
                charts.student_subject_radar(records, chart_paths.setdefault("radar",
                    os.path.join(ASSETS_DIR, "chart_radar.png")))
            else:
                charts.employee_perf_bar(records, chart_paths.setdefault("perf_bar",
                    os.path.join(ASSETS_DIR, "chart_perf_bar.png")))
                charts.employee_dept_pie(records, chart_paths.setdefault("dept_pie",
                    os.path.join(ASSETS_DIR, "chart_dept_pie.png")))
                charts.employee_salary_bar(records, chart_paths.setdefault("salary_bar",
                    os.path.join(ASSETS_DIR, "chart_salary_bar.png")))
            info("Charts generated.")
        except Exception as e:
            warn(f"Chart generation failed: {e}. Report will proceed without charts.")
            chart_paths = {}

    # Build PDF
    output_path = unique_filename(f"{report_type}_report")
    print(f"  Building PDF...")

    try:
        if report_type == "student":
            generate_student_report(
                records, output_path,
                institution=institution, semester=semester,
                logo_path=logo_path, chart_paths=chart_paths if chart_paths else None,
                password=password,
            )
        else:
            generate_company_report(
                records, output_path,
                company_name=company, period=period,
                logo_path=logo_path, chart_paths=chart_paths if chart_paths else None,
                password=password,
            )

        print()
        print("  " + "=" * 50)
        info(f"PDF Report generated successfully!")
        info(f"Location : {output_path}")
        info(f"Records  : {len(records)}")
        if password:
            info(f"Password : Protected ✓")
        print("  " + "=" * 50)
    except Exception as e:
        err(f"PDF generation failed: {e}")
        import traceback; traceback.print_exc()


# ─────────────── MULTI-EXPORT ──────────────
def export_all():
    """Export both student and company reports if data exists."""
    print("\n  ── Export All Reports ──")
    exported = 0
    for rtype in ["student", "company"]:
        records = session_students if rtype == "student" else session_employees
        if records:
            generate_pdf(rtype)
            exported += 1
    if exported == 0:
        warn("No data loaded for either report type. Load data first.")
    else:
        info(f"Exported {exported} report(s).")


# ─────────────── VIEW SESSION DATA ─────────
def view_session_data(report_type: str):
    records = session_students if report_type == "student" else session_employees
    if not records:
        warn("No data in session.")
        return

    print(f"\n  ── {report_type.title()} Records in Session ({len(records)}) ──")
    for i, r in enumerate(records, 1):
        if report_type == "student":
            print(f"  {i:2}. [{r.id}] {r.name:<20} {r.course:<30} Avg: {r.average}  Grade: {r.grade}")
        else:
            print(f"  {i:2}. [{r.id}] {r.name:<20} {r.role:<25} Perf: {r.performance}")
    hr()


# ─────────────── CLEAR SESSION ─────────────
def clear_session(report_type: str):
    global session_students, session_employees
    if report_type == "student":
        session_students.clear()
        info("Student session data cleared.")
    else:
        session_employees.clear()
        info("Employee session data cleared.")


# ─────────────── MENUS ─────────────────────
def student_menu():
    while True:
        print("\n  ┌─────────────────────────────────┐")
        print("  │       STUDENT REPORT MENU        │")
        print("  ├─────────────────────────────────┤")
        print("  │  1. Add Student Manually          │")
        print("  │  2. Load from CSV / JSON          │")
        print("  │  3. View Session Data             │")
        print("  │  4. Generate Student PDF          │")
        print("  │  5. Clear Session Data            │")
        print("  │  0. Back to Main Menu             │")
        print("  └─────────────────────────────────┘")
        choice = prompt("Enter choice").strip()

        if choice == "1":
            s = input_student_manual()
            if s:
                session_students.append(s)
                info(f"Student '{s.name}' added. Total: {len(session_students)}")
        elif choice == "2":
            load_from_file("student")
        elif choice == "3":
            view_session_data("student")
        elif choice == "4":
            generate_pdf("student")
        elif choice == "5":
            clear_session("student")
        elif choice == "0":
            break
        else:
            warn("Invalid choice.")


def company_menu():
    while True:
        print("\n  ┌─────────────────────────────────┐")
        print("  │       COMPANY REPORT MENU        │")
        print("  ├─────────────────────────────────┤")
        print("  │  1. Add Employee Manually         │")
        print("  │  2. Load from CSV / JSON          │")
        print("  │  3. View Session Data             │")
        print("  │  4. Generate Company PDF          │")
        print("  │  5. Clear Session Data            │")
        print("  │  0. Back to Main Menu             │")
        print("  └─────────────────────────────────┘")
        choice = prompt("Enter choice").strip()

        if choice == "1":
            e = input_employee_manual()
            if e:
                session_employees.append(e)
                info(f"Employee '{e.name}' added. Total: {len(session_employees)}")
        elif choice == "2":
            load_from_file("company")
        elif choice == "3":
            view_session_data("company")
        elif choice == "4":
            generate_pdf("company")
        elif choice == "5":
            clear_session("company")
        elif choice == "0":
            break
        else:
            warn("Invalid choice.")


def main_menu():
    banner()
    while True:
        print("\n  ╔═════════════════════════════════╗")
        print("  ║         MAIN MENU               ║")
        print("  ╠═════════════════════════════════╣")
        print("  ║  1. Student Report               ║")
        print("  ║  2. Company / Employee Report    ║")
        print("  ║  3. Export All Reports           ║")
        print("  ║  0. Exit                         ║")
        print("  ╚═════════════════════════════════╝")
        choice = prompt("Enter choice").strip()

        if choice == "1":
            student_menu()
        elif choice == "2":
            company_menu()
        elif choice == "3":
            export_all()
        elif choice == "0":
            print("\n  Thank you for using ReportGen Pro. Goodbye!\n")
            break
        else:
            warn("Invalid choice. Please try again.")


# ─────────────── AUTO-DEMO MODE ────────────
def run_demo():
    """Non-interactive demo: load sample data and generate both reports."""
    print("\n  ── DEMO MODE: Auto-generating sample reports ──\n")

    # Student report
    spath = os.path.join(DATA_DIR, "students.csv")
    if os.path.exists(spath):
        students = auto_load(spath, "student")
        session_students.extend(students)
        logo_path = os.path.join(ASSETS_DIR, "logo_student.png")
        create_logo(logo_path, "student")

        chart_paths = {
            "grade_pie": os.path.join(ASSETS_DIR, "chart_grade_pie.png"),
            "avg_bar":   os.path.join(ASSETS_DIR, "chart_avg_bar.png"),
            "radar":     os.path.join(ASSETS_DIR, "chart_radar.png"),
        }
        charts.student_grade_pie(students, chart_paths["grade_pie"])
        charts.student_avg_bar(students, chart_paths["avg_bar"])
        charts.student_subject_radar(students, chart_paths["radar"])

        out = unique_filename("student_report")
        generate_student_report(
            students, out,
            institution="National University of Technology",
            semester="Fall 2024",
            logo_path=logo_path, chart_paths=chart_paths,
        )
        info(f"Student report: {out}")

    # Company report
    epath = os.path.join(DATA_DIR, "employees.csv")
    if os.path.exists(epath):
        employees = auto_load(epath, "company")
        session_employees.extend(employees)
        logo_path = os.path.join(ASSETS_DIR, "logo_company.png")
        create_logo(logo_path, "company")

        chart_paths = {
            "perf_bar":  os.path.join(ASSETS_DIR, "chart_perf_bar.png"),
            "dept_pie":  os.path.join(ASSETS_DIR, "chart_dept_pie.png"),
            "salary_bar": os.path.join(ASSETS_DIR, "chart_salary_bar.png"),
        }
        charts.employee_perf_bar(employees, chart_paths["perf_bar"])
        charts.employee_dept_pie(employees, chart_paths["dept_pie"])
        charts.employee_salary_bar(employees, chart_paths["salary_bar"])

        out = unique_filename("company_report")
        generate_company_report(
            employees, out,
            company_name="TechCorp International",
            period="Q4 2024",
            logo_path=logo_path, chart_paths=chart_paths,
        )
        info(f"Company report: {out}")

    print("\n  Demo complete! Check the 'reports/' folder.")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        main_menu()
