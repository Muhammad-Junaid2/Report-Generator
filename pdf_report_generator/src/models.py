"""
Data models for Student and Employee records.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StudentRecord:
    id: str
    name: str
    email: str
    course: str
    department: str
    math: float = 0
    science: float = 0
    english: float = 0
    history: float = 0
    cs: float = 0
    attendance: float = 0

    @property
    def average(self) -> float:
        scores = [self.math, self.science, self.english, self.history, self.cs]
        return round(sum(scores) / len(scores), 2)

    @property
    def grade(self) -> str:
        avg = self.average
        if avg >= 90:
            return "A+"
        elif avg >= 85:
            return "A"
        elif avg >= 80:
            return "B+"
        elif avg >= 75:
            return "B"
        elif avg >= 70:
            return "C"
        elif avg >= 60:
            return "D"
        else:
            return "F"

    @property
    def status(self) -> str:
        return "Pass" if self.average >= 60 else "Fail"

    def to_table_row(self):
        return [
            self.id,
            self.name,
            str(self.math),
            str(self.science),
            str(self.english),
            str(self.history),
            str(self.cs),
            f"{self.attendance}%",
            str(self.average),
            self.grade,
            self.status,
        ]


@dataclass
class EmployeeRecord:
    id: str
    name: str
    email: str
    department: str
    role: str
    performance: str
    projects: int = 0
    salary: float = 0
    years_experience: int = 0
    status: str = "Active"

    @property
    def performance_score(self) -> int:
        mapping = {"Outstanding": 5, "Excellent": 4, "Good": 3, "Average": 2, "Poor": 1}
        return mapping.get(self.performance, 2)

    def to_table_row(self):
        return [
            self.id,
            self.name,
            self.department,
            self.role,
            self.performance,
            str(self.projects),
            f"PKR {int(self.salary):,}",
            str(self.years_experience),
            self.status,
        ]
