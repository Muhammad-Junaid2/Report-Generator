# Report-Genenerator 

**Professional PDF Report Generator for Students & Companies**

Report-Genenerator is a Python CLI and GUI application that generates polished, data-rich PDF reports for academic institutions and businesses. It supports manual data entry, CSV/JSON loading, embedded charts, branding logos, and password protection.

---

##  Features

| Feature | Details |
|---|---|
|  Report Types | Student Academic + Company/Employee reports |
|  Data Input | Manual entry, CSV, or JSON |
|  Charts | Bar charts, pie charts, radar charts via Matplotlib |
|  Branding | Auto-generated logo for each report type |
|  Security | Optional PDF password protection |
|  Auto-save | Timestamped filenames in `reports/` folder |
|  Multi-export | Export all loaded data at once |
|  Menu System | Interactive CLI with numbered menus |

---

##  Project Structure

```
pdf_report_generator/
├── main.py                  # Entry point (CLI + demo mode)
├── src/
│   ├── models.py            # StudentRecord, EmployeeRecord dataclasses
│   ├── data_loader.py       # CSV/JSON loaders with auto-detection
│   ├── pdf_generator.py     # ReportLab PDF generation (student + company)
│   ├── charts.py            # Matplotlib chart generators
│   └── logo_gen.py          # PIL-based logo creator
├── data/
│   ├── students.csv         # Sample student data (8 records)
│   ├── employees.csv        # Sample employee data (8 records)
│   └── students.json        # Sample JSON data
├── reports/                 # Generated PDFs saved here (auto-created)
├── assets/                  # Charts & logos cached here (auto-created)
├── requirements.txt
└── README.md
```

---

##  Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the CLI

```bash
python main.py
```

### 3. Run Demo Mode (auto-generates sample reports)

```bash
python main.py --demo
```

---

##  Requirements

```
reportlab>=4.0
matplotlib>=3.7
Pillow>=10.0
pypdf>=3.0
numpy>=1.24
```

Install all at once:
```bash
pip install reportlab matplotlib Pillow pypdf numpy
```

---

##  Menu Navigation

```
MAIN MENU
  1. Student Report       → Enter student sub-menu
  2. Company Report       → Enter company sub-menu
  3. Export All Reports   → Generate PDFs for all loaded data
  0. Exit

STUDENT / COMPANY MENU
  1. Add Data Manually    → Enter records one by one
  2. Load from CSV/JSON   → Load file from data/ folder
  3. View Session Data    → List all records in memory
  4. Generate PDF         → Build and save the PDF
  5. Clear Session Data   → Reset in-memory records
  0. Back
```

---

##  Report Contents

### Student Report
- Header banner with institution name, semester, and timestamp
- KPI cards: Total Students, Class Average, Pass Count, Attendance, Top Performer
- Full results table: ID, Name, subject scores, average, grade, pass/fail
- Grade distribution pie chart
- Performance bar chart
- Subject radar chart

### Company Report
- Header banner with company name, period, and timestamp
- KPI cards: Total Employees, Departments, Avg Projects, Avg Salary, High Performers
- Employee table: ID, Name, Dept, Role, Performance, Projects, Salary, Experience, Status
- Performance ratings bar chart
- Department distribution pie chart
- Salary overview chart

---

##  Sample Data Files

### `data/students.csv` columns:
`ID, Name, Email, Course, Department, Math, Science, English, History, CS, Attendance`

### `data/employees.csv` columns:
`ID, Name, Email, Department, Role, Performance, Projects, Salary, YearsExperience, Status`

Performance values: `Outstanding | Excellent | Good | Average | Poor`

### `data/students.json` format:
```json
{
  "report_type": "student",
  "institution": "...",
  "semester": "...",
  "students": [ { "ID": "...", "Name": "...", ... } ]
}
```

---

##  Password Protection

When generating a report, choose `y` when asked about password protection. The PDF will be encrypted and require a password to open in any PDF viewer.

---

##  Output Example

Reports are saved to the `reports/` directory with timestamped filenames:

```
reports/
  student_report_20241215_143022.pdf
  company_report_20241215_143055.pdf
```

---

##  Module Reference

| Module | Description |
|---|---|
| `src/models.py` | Data classes with computed properties (grade, average, score) |
| `src/data_loader.py` | `auto_load(path, type)` — detect and load CSV or JSON |
| `src/pdf_generator.py` | `generate_student_report()` and `generate_company_report()` |
| `src/charts.py` | 6 chart types: pie, bar, horizontal bar, radar |
| `src/logo_gen.py` | `create_logo(path, type)` — PIL-based branded header image |

---

##  Contributing

Pull requests welcome. For major changes, please open an issue first.

---

##  License

MIT License. See LICENSE for details.

## Developer By

Muhammad Junaid# Report-Generator
