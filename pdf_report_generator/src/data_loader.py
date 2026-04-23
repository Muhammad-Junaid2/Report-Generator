"""
Load student or employee data from CSV or JSON files.
"""
import csv
import json
from typing import List, Union
from src.models import StudentRecord, EmployeeRecord


def load_students_csv(filepath: str) -> List[StudentRecord]:
    records = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                records.append(StudentRecord(
                    id=row["ID"].strip(),
                    name=row["Name"].strip(),
                    email=row["Email"].strip(),
                    course=row["Course"].strip(),
                    department=row["Department"].strip(),
                    math=float(row.get("Math", 0)),
                    science=float(row.get("Science", 0)),
                    english=float(row.get("English", 0)),
                    history=float(row.get("History", 0)),
                    cs=float(row.get("CS", 0)),
                    attendance=float(row.get("Attendance", 0)),
                ))
            except (KeyError, ValueError) as e:
                print(f"  Warning: Skipping row due to error: {e}")
    return records


def load_employees_csv(filepath: str) -> List[EmployeeRecord]:
    records = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                records.append(EmployeeRecord(
                    id=row["ID"].strip(),
                    name=row["Name"].strip(),
                    email=row["Email"].strip(),
                    department=row["Department"].strip(),
                    role=row["Role"].strip(),
                    performance=row["Performance"].strip(),
                    projects=int(row.get("Projects", 0)),
                    salary=float(row.get("Salary", 0)),
                    years_experience=int(row.get("YearsExperience", 0)),
                    status=row.get("Status", "Active").strip(),
                ))
            except (KeyError, ValueError) as e:
                print(f"  Warning: Skipping row due to error: {e}")
    return records


def load_students_json(filepath: str) -> List[StudentRecord]:
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    students_data = data.get("students", data) if isinstance(data, dict) else data
    records = []
    for row in students_data:
        try:
            records.append(StudentRecord(
                id=str(row["ID"]),
                name=row["Name"],
                email=row["Email"],
                course=row["Course"],
                department=row["Department"],
                math=float(row.get("Math", 0)),
                science=float(row.get("Science", 0)),
                english=float(row.get("English", 0)),
                history=float(row.get("History", 0)),
                cs=float(row.get("CS", 0)),
                attendance=float(row.get("Attendance", 0)),
            ))
        except (KeyError, ValueError) as e:
            print(f"  Warning: Skipping entry due to error: {e}")
    return records


def load_employees_json(filepath: str) -> List[EmployeeRecord]:
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    emp_data = data.get("employees", data) if isinstance(data, dict) else data
    records = []
    for row in emp_data:
        try:
            records.append(EmployeeRecord(
                id=str(row["ID"]),
                name=row["Name"],
                email=row["Email"],
                department=row["Department"],
                role=row["Role"],
                performance=row["Performance"],
                projects=int(row.get("Projects", 0)),
                salary=float(row.get("Salary", 0)),
                years_experience=int(row.get("YearsExperience", 0)),
                status=row.get("Status", "Active"),
            ))
        except (KeyError, ValueError) as e:
            print(f"  Warning: Skipping entry due to error: {e}")
    return records


def auto_load(filepath: str, report_type: str):
    """Auto-detect format and load."""
    ext = filepath.rsplit(".", 1)[-1].lower()
    if report_type == "student":
        if ext == "csv":
            return load_students_csv(filepath)
        elif ext == "json":
            return load_students_json(filepath)
    elif report_type == "company":
        if ext == "csv":
            return load_employees_csv(filepath)
        elif ext == "json":
            return load_employees_json(filepath)
    raise ValueError(f"Unsupported file type: .{ext}")
