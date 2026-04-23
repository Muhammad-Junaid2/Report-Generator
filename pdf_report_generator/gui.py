#!/usr/bin/env python3
"""
ReportGen Pro — Tkinter GUI
Professional PDF Report Generator with a modern dark UI.
Run: python gui.py
"""

import os
import sys
import threading
import csv
import json
from datetime import datetime
from typing import List
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import StudentRecord, EmployeeRecord
from src.data_loader import auto_load
from src.pdf_generator import generate_student_report, generate_company_report
from src.logo_gen import create_logo
import src.charts as charts

# ─────────────── PATHS ───────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
ASSETS_DIR  = os.path.join(BASE_DIR, "assets")
DATA_DIR    = os.path.join(BASE_DIR, "data")
for d in [REPORTS_DIR, ASSETS_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# ─────────────── PALETTE ─────────────────
C = {
    "bg":        "#0F1117",
    "surface":   "#1A1D27",
    "card":      "#21263A",
    "border":    "#2D3350",
    "primary":   "#4F8EF7",
    "primary_d": "#3A6FD8",
    "accent":    "#7C5CFC",
    "green":     "#34D399",
    "red":       "#F87171",
    "yellow":    "#FBBF24",
    "text":      "#E8ECF4",
    "muted":     "#6B7280",
    "white":     "#FFFFFF",
    "student":   "#1565C0",
    "company":   "#1B5E20",
    "tab_act":   "#4F8EF7",
    "tab_inact": "#21263A",
}

FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_HEAD   = ("Segoe UI", 13, "bold")
FONT_SUB    = ("Segoe UI", 10, "bold")
FONT_BODY   = ("Segoe UI", 9)
FONT_SMALL  = ("Segoe UI", 8)
FONT_MONO   = ("Consolas", 9)
FONT_BTN    = ("Segoe UI", 9, "bold")


def unique_filename(prefix):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(REPORTS_DIR, f"{prefix}_{ts}.pdf")


# ─────────────── STYLED WIDGETS ──────────
class StyledButton(tk.Button):
    def __init__(self, parent, text, command=None, color=None, width=14, **kw):
        c = color or C["primary"]
        super().__init__(
            parent, text=text, command=command,
            bg=c, fg=C["white"], relief="flat",
            font=FONT_BTN, cursor="hand2",
            padx=12, pady=6, width=width,
            activebackground=C["primary_d"],
            activeforeground=C["white"],
            bd=0, **kw
        )
        self.bind("<Enter>", lambda e: self.config(bg=self._darken(c)))
        self.bind("<Leave>", lambda e: self.config(bg=c))

    def _darken(self, hex_color):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r, g, b = max(0, r - 25), max(0, g - 25), max(0, b - 25)
        return f"#{r:02x}{g:02x}{b:02x}"


class Card(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C["card"],
                         highlightbackground=C["border"],
                         highlightthickness=1, **kw)


class SectionLabel(tk.Label):
    def __init__(self, parent, text, **kw):
        super().__init__(parent, text=text, bg=C["surface"],
                         fg=C["primary"], font=FONT_SUB, anchor="w", **kw)


class FieldRow(tk.Frame):
    """Label + Entry pair."""
    def __init__(self, parent, label, default="", width=28, **kw):
        super().__init__(parent, bg=C["card"], **kw)
        tk.Label(self, text=label, bg=C["card"], fg=C["muted"],
                 font=FONT_SMALL, width=16, anchor="w").pack(side="left")
        self.var = tk.StringVar(value=default)
        e = tk.Entry(self, textvariable=self.var, width=width,
                     bg=C["surface"], fg=C["text"],
                     insertbackground=C["text"], relief="flat",
                     font=FONT_BODY, bd=4)
        e.pack(side="left", fill="x", expand=True)

    def get(self):
        return self.var.get().strip()

    def set(self, val):
        self.var.set(val)


# ─────────────── LOG PANEL ───────────────
class LogPanel(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C["surface"], **kw)
        tk.Label(self, text="Console Output", bg=C["surface"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", padx=8, pady=(6, 2))
        self.text = scrolledtext.ScrolledText(
            self, bg=C["bg"], fg=C["green"],
            font=FONT_MONO, height=8, relief="flat",
            insertbackground=C["green"], bd=0,
            state="disabled",
        )
        self.text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.text.tag_config("info",  foreground=C["green"])
        self.text.tag_config("warn",  foreground=C["yellow"])
        self.text.tag_config("error", foreground=C["red"])
        self.text.tag_config("head",  foreground=C["primary"])

    def log(self, msg, kind="info"):
        self.text.config(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.text.insert("end", f"[{ts}] {msg}\n", kind)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


# ─────────────── DATA TABLE ──────────────
class DataTable(tk.Frame):
    def __init__(self, parent, columns, **kw):
        super().__init__(parent, bg=C["card"], **kw)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
            background=C["card"], foreground=C["text"],
            fieldbackground=C["card"], rowheight=26,
            font=FONT_BODY, borderwidth=0,
        )
        style.configure("Dark.Treeview.Heading",
            background=C["surface"], foreground=C["primary"],
            font=("Segoe UI", 9, "bold"), relief="flat",
        )
        style.map("Dark.Treeview",
            background=[("selected", C["primary_d"])],
            foreground=[("selected", C["white"])],
        )

        self.tree = ttk.Treeview(self, columns=columns, show="headings",
                                  style="Dark.Treeview", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=max(60, len(col) * 9), anchor="center")

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def set_data(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))
        self.tree.tag_configure("even", background=C["card"])
        self.tree.tag_configure("odd",  background=C["surface"])

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)


# ─────────────── KPI CARD ────────────────
class KpiCard(tk.Frame):
    def __init__(self, parent, value, label, color=None, **kw):
        super().__init__(parent, bg=C["card"],
                         highlightbackground=color or C["border"],
                         highlightthickness=2, padx=14, pady=10, **kw)
        tk.Label(self, text=value, bg=C["card"],
                 fg=color or C["primary"],
                 font=("Segoe UI", 18, "bold")).pack()
        tk.Label(self, text=label, bg=C["card"],
                 fg=C["muted"], font=FONT_SMALL).pack()


# ─────────────── STUDENT TAB ─────────────
class StudentTab(tk.Frame):
    def __init__(self, parent, log):
        super().__init__(parent, bg=C["surface"])
        self.log      = log
        self.records: List[StudentRecord] = []
        self._build()

    def _build(self):
        # ── Top controls row ──
        ctrl = tk.Frame(self, bg=C["surface"])
        ctrl.pack(fill="x", padx=14, pady=(12, 0))

        SectionLabel(ctrl, "👨‍🎓  Student Report").pack(side="left")

        btn_frame = tk.Frame(ctrl, bg=C["surface"])
        btn_frame.pack(side="right")
        StyledButton(btn_frame, "＋ Add Student",  self._open_add,   color=C["primary"], width=14).pack(side="left", padx=3)
        StyledButton(btn_frame, "📂 Load File",     self._load_file,  color=C["accent"],  width=12).pack(side="left", padx=3)
        StyledButton(btn_frame, "🗑 Clear All",     self._clear,      color="#374151",    width=10).pack(side="left", padx=3)
        StyledButton(btn_frame, "📄 Generate PDF",  self._gen_pdf,    color=C["student"], width=14).pack(side="left", padx=3)

        # ── KPI row ──
        self.kpi_frame = tk.Frame(self, bg=C["surface"])
        self.kpi_frame.pack(fill="x", padx=14, pady=8)
        self._update_kpis()

        # ── Table ──
        cols = ("ID", "Name", "Math", "Sci", "Eng", "Hist", "CS", "Attend%", "Avg", "Grade", "Result")
        self.table = DataTable(self, cols)
        self.table.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        # ── PDF options ──
        opts = Card(self)
        opts.pack(fill="x", padx=14, pady=(0, 12))

        tk.Label(opts, text="Report Options", bg=C["card"],
                 fg=C["muted"], font=FONT_SMALL).grid(row=0, column=0, columnspan=6,
                 sticky="w", padx=10, pady=(8, 4))

        self.inst_var     = tk.StringVar(value="National University of Technology")
        self.sem_var      = tk.StringVar(value="Fall 2024")
        self.charts_var   = tk.BooleanVar(value=True)
        self.logo_var     = tk.BooleanVar(value=True)
        self.pwd_var      = tk.BooleanVar(value=False)
        self.pwd_entry_var= tk.StringVar()

        self._opt_label(opts, "Institution:", 0, 1)
        tk.Entry(opts, textvariable=self.inst_var, width=32, bg=C["surface"],
                 fg=C["text"], insertbackground=C["text"],
                 relief="flat", font=FONT_BODY, bd=4).grid(row=1, column=1, padx=4, pady=4, sticky="w")

        self._opt_label(opts, "Semester:", 0, 3)
        tk.Entry(opts, textvariable=self.sem_var, width=16, bg=C["surface"],
                 fg=C["text"], insertbackground=C["text"],
                 relief="flat", font=FONT_BODY, bd=4).grid(row=1, column=3, padx=4, pady=4, sticky="w")

        tk.Checkbutton(opts, text="Include Charts", variable=self.charts_var,
                       bg=C["card"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["card"], font=FONT_BODY).grid(row=1, column=4, padx=8)
        tk.Checkbutton(opts, text="Logo", variable=self.logo_var,
                       bg=C["card"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["card"], font=FONT_BODY).grid(row=1, column=5, padx=4)

        pwd_row = tk.Frame(opts, bg=C["card"])
        pwd_row.grid(row=2, column=0, columnspan=6, sticky="w", padx=10, pady=(0, 8))
        tk.Checkbutton(pwd_row, text="Password Protect:", variable=self.pwd_var,
                       bg=C["card"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["card"], font=FONT_BODY).pack(side="left")
        tk.Entry(pwd_row, textvariable=self.pwd_entry_var, width=20, show="●",
                 bg=C["surface"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", font=FONT_BODY, bd=4).pack(side="left", padx=6)

    def _opt_label(self, parent, text, row, col):
        tk.Label(parent, text=text, bg=C["card"], fg=C["muted"],
                 font=FONT_SMALL).grid(row=row, column=col, sticky="e", padx=(10, 2), pady=4)

    def _update_kpis(self):
        for w in self.kpi_frame.winfo_children():
            w.destroy()
        r = self.records
        if not r:
            tk.Label(self.kpi_frame, text="No student records loaded.",
                     bg=C["surface"], fg=C["muted"], font=FONT_BODY).pack(side="left", padx=4)
            return
        avg_all  = round(sum(x.average for x in r) / len(r), 1)
        passed   = sum(1 for x in r if x.status == "Pass")
        avg_att  = round(sum(x.attendance for x in r) / len(r), 1)
        top      = max(r, key=lambda x: x.average)
        kpis = [
            (str(len(r)),         "Students",       C["primary"]),
            (str(avg_all),        "Class Avg",      C["accent"]),
            (f"{passed}/{len(r)}","Passed",         C["green"]),
            (f"{avg_att}%",       "Attendance",     C["yellow"]),
            (top.name.split()[0], "Top Student",    C["primary"]),
        ]
        for val, lbl, col in kpis:
            KpiCard(self.kpi_frame, val, lbl, col).pack(side="left", padx=4)

    def _refresh_table(self):
        rows = [r.to_table_row() for r in self.records]
        self.table.set_data(rows)
        self._update_kpis()

    def _open_add(self):
        AddStudentDialog(self, self._on_student_added)

    def _on_student_added(self, s: StudentRecord):
        self.records.append(s)
        self._refresh_table()
        self.log.log(f"Student added: {s.name}  (Total: {len(self.records)})", "info")

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Load Student Data",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All", "*.*")],
            initialdir=DATA_DIR,
        )
        if not path:
            return
        try:
            loaded = auto_load(path, "student")
            self.records.extend(loaded)
            self._refresh_table()
            self.log.log(f"Loaded {len(loaded)} students from {os.path.basename(path)}", "info")
        except Exception as e:
            self.log.log(f"Load failed: {e}", "error")
            messagebox.showerror("Load Error", str(e))

    def _clear(self):
        if not self.records:
            return
        if messagebox.askyesno("Clear", "Clear all student records?"):
            self.records.clear()
            self.table.clear()
            self._update_kpis()
            self.log.log("Student data cleared.", "warn")

    def _gen_pdf(self):
        if not self.records:
            messagebox.showwarning("No Data", "Please add or load student data first.")
            return

        password = self.pwd_entry_var.get().strip() if self.pwd_var.get() else None
        self.log.log("Generating student PDF...", "head")

        def worker():
            try:
                logo_path = None
                if self.logo_var.get():
                    logo_path = os.path.join(ASSETS_DIR, "logo_student.png")
                    create_logo(logo_path, "student")

                chart_paths = {}
                if self.charts_var.get():
                    self.log.log("  Rendering charts...", "info")
                    chart_paths = {
                        "grade_pie": os.path.join(ASSETS_DIR, "chart_grade_pie.png"),
                        "avg_bar":   os.path.join(ASSETS_DIR, "chart_avg_bar.png"),
                        "radar":     os.path.join(ASSETS_DIR, "chart_radar.png"),
                    }
                    charts.student_grade_pie(self.records, chart_paths["grade_pie"])
                    charts.student_avg_bar(self.records, chart_paths["avg_bar"])
                    charts.student_subject_radar(self.records, chart_paths["radar"])

                out = unique_filename("student_report")
                generate_student_report(
                    self.records, out,
                    institution=self.inst_var.get(),
                    semester=self.sem_var.get(),
                    logo_path=logo_path,
                    chart_paths=chart_paths or None,
                    password=password,
                )
                self.log.log(f"✓ PDF saved: {os.path.basename(out)}", "info")
                self.log.log(f"  Path: {out}", "info")
                messagebox.showinfo("Success", f"Report saved!\n\n{out}")
            except Exception as e:
                self.log.log(f"PDF generation failed: {e}", "error")
                messagebox.showerror("Error", str(e))

        threading.Thread(target=worker, daemon=True).start()


# ─────────────── COMPANY TAB ─────────────
class CompanyTab(tk.Frame):
    def __init__(self, parent, log):
        super().__init__(parent, bg=C["surface"])
        self.log      = log
        self.records: List[EmployeeRecord] = []
        self._build()

    def _build(self):
        ctrl = tk.Frame(self, bg=C["surface"])
        ctrl.pack(fill="x", padx=14, pady=(12, 0))

        SectionLabel(ctrl, "🏢  Company / Employee Report").pack(side="left")

        btn_frame = tk.Frame(ctrl, bg=C["surface"])
        btn_frame.pack(side="right")
        StyledButton(btn_frame, "＋ Add Employee", self._open_add,  color=C["primary"], width=14).pack(side="left", padx=3)
        StyledButton(btn_frame, "📂 Load File",    self._load_file, color=C["accent"],  width=12).pack(side="left", padx=3)
        StyledButton(btn_frame, "🗑 Clear All",    self._clear,     color="#374151",    width=10).pack(side="left", padx=3)
        StyledButton(btn_frame, "📄 Generate PDF", self._gen_pdf,   color=C["company"], width=14).pack(side="left", padx=3)

        self.kpi_frame = tk.Frame(self, bg=C["surface"])
        self.kpi_frame.pack(fill="x", padx=14, pady=8)
        self._update_kpis()

        cols = ("ID", "Name", "Dept", "Role", "Performance", "Projects", "Salary", "Exp", "Status")
        self.table = DataTable(self, cols)
        self.table.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        opts = Card(self)
        opts.pack(fill="x", padx=14, pady=(0, 12))

        tk.Label(opts, text="Report Options", bg=C["card"],
                 fg=C["muted"], font=FONT_SMALL).grid(row=0, column=0, columnspan=6,
                 sticky="w", padx=10, pady=(8, 4))

        self.comp_var    = tk.StringVar(value="TechCorp International")
        self.period_var  = tk.StringVar(value="Q4 2024")
        self.charts_var  = tk.BooleanVar(value=True)
        self.logo_var    = tk.BooleanVar(value=True)
        self.pwd_var     = tk.BooleanVar(value=False)
        self.pwd_e_var   = tk.StringVar()

        tk.Label(opts, text="Company:", bg=C["card"], fg=C["muted"],
                 font=FONT_SMALL).grid(row=1, column=0, sticky="e", padx=(10, 2))
        tk.Entry(opts, textvariable=self.comp_var, width=30, bg=C["surface"],
                 fg=C["text"], insertbackground=C["text"],
                 relief="flat", font=FONT_BODY, bd=4).grid(row=1, column=1, padx=4, pady=4, sticky="w")

        tk.Label(opts, text="Period:", bg=C["card"], fg=C["muted"],
                 font=FONT_SMALL).grid(row=1, column=2, sticky="e", padx=(10, 2))
        tk.Entry(opts, textvariable=self.period_var, width=14, bg=C["surface"],
                 fg=C["text"], insertbackground=C["text"],
                 relief="flat", font=FONT_BODY, bd=4).grid(row=1, column=3, padx=4, pady=4, sticky="w")

        tk.Checkbutton(opts, text="Include Charts", variable=self.charts_var,
                       bg=C["card"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["card"], font=FONT_BODY).grid(row=1, column=4, padx=8)
        tk.Checkbutton(opts, text="Logo", variable=self.logo_var,
                       bg=C["card"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["card"], font=FONT_BODY).grid(row=1, column=5, padx=4)

        pwd_row = tk.Frame(opts, bg=C["card"])
        pwd_row.grid(row=2, column=0, columnspan=6, sticky="w", padx=10, pady=(0, 8))
        tk.Checkbutton(pwd_row, text="Password Protect:", variable=self.pwd_var,
                       bg=C["card"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["card"], font=FONT_BODY).pack(side="left")
        tk.Entry(pwd_row, textvariable=self.pwd_e_var, width=20, show="●",
                 bg=C["surface"], fg=C["text"], insertbackground=C["text"],
                 relief="flat", font=FONT_BODY, bd=4).pack(side="left", padx=6)

    def _update_kpis(self):
        for w in self.kpi_frame.winfo_children():
            w.destroy()
        r = self.records
        if not r:
            tk.Label(self.kpi_frame, text="No employee records loaded.",
                     bg=C["surface"], fg=C["muted"], font=FONT_BODY).pack(side="left", padx=4)
            return
        depts     = len(set(x.department for x in r))
        avg_proj  = round(sum(x.projects for x in r) / len(r), 1)
        avg_sal   = int(sum(x.salary for x in r) / len(r))
        top_perf  = sum(1 for x in r if x.performance in ["Excellent", "Outstanding"])
        kpis = [
            (str(len(r)),         "Employees",     C["primary"]),
            (str(depts),          "Departments",   C["accent"]),
            (str(avg_proj),       "Avg Projects",  C["yellow"]),
            (f"PKR {avg_sal//1000}K", "Avg Salary",C["green"]),
            (f"{top_perf}/{len(r)}", "High Perf",  C["primary"]),
        ]
        for val, lbl, col in kpis:
            KpiCard(self.kpi_frame, val, lbl, col).pack(side="left", padx=4)

    def _refresh_table(self):
        rows = [r.to_table_row() for r in self.records]
        self.table.set_data(rows)
        self._update_kpis()

    def _open_add(self):
        AddEmployeeDialog(self, self._on_employee_added)

    def _on_employee_added(self, e: EmployeeRecord):
        self.records.append(e)
        self._refresh_table()
        self.log.log(f"Employee added: {e.name}  (Total: {len(self.records)})", "info")

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Load Employee Data",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All", "*.*")],
            initialdir=DATA_DIR,
        )
        if not path:
            return
        try:
            loaded = auto_load(path, "company")
            self.records.extend(loaded)
            self._refresh_table()
            self.log.log(f"Loaded {len(loaded)} employees from {os.path.basename(path)}", "info")
        except Exception as e:
            self.log.log(f"Load failed: {e}", "error")
            messagebox.showerror("Load Error", str(e))

    def _clear(self):
        if not self.records:
            return
        if messagebox.askyesno("Clear", "Clear all employee records?"):
            self.records.clear()
            self.table.clear()
            self._update_kpis()
            self.log.log("Employee data cleared.", "warn")

    def _gen_pdf(self):
        if not self.records:
            messagebox.showwarning("No Data", "Please add or load employee data first.")
            return

        password = self.pwd_e_var.get().strip() if self.pwd_var.get() else None
        self.log.log("Generating company PDF...", "head")

        def worker():
            try:
                logo_path = None
                if self.logo_var.get():
                    logo_path = os.path.join(ASSETS_DIR, "logo_company.png")
                    create_logo(logo_path, "company")

                chart_paths = {}
                if self.charts_var.get():
                    self.log.log("  Rendering charts...", "info")
                    chart_paths = {
                        "perf_bar":   os.path.join(ASSETS_DIR, "chart_perf_bar.png"),
                        "dept_pie":   os.path.join(ASSETS_DIR, "chart_dept_pie.png"),
                        "salary_bar": os.path.join(ASSETS_DIR, "chart_salary_bar.png"),
                    }
                    charts.employee_perf_bar(self.records, chart_paths["perf_bar"])
                    charts.employee_dept_pie(self.records, chart_paths["dept_pie"])
                    charts.employee_salary_bar(self.records, chart_paths["salary_bar"])

                out = unique_filename("company_report")
                generate_company_report(
                    self.records, out,
                    company_name=self.comp_var.get(),
                    period=self.period_var.get(),
                    logo_path=logo_path,
                    chart_paths=chart_paths or None,
                    password=password,
                )
                self.log.log(f"✓ PDF saved: {os.path.basename(out)}", "info")
                self.log.log(f"  Path: {out}", "info")
                messagebox.showinfo("Success", f"Report saved!\n\n{out}")
            except Exception as e:
                self.log.log(f"PDF generation failed: {e}", "error")
                messagebox.showerror("Error", str(e))

        threading.Thread(target=worker, daemon=True).start()


# ─────────────── ADD STUDENT DIALOG ───────
class AddStudentDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Add Student")
        self.configure(bg=C["surface"])
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Add New Student", bg=C["surface"],
                 fg=C["primary"], font=FONT_HEAD).pack(pady=(16, 8))

        frame = Card(self)
        frame.pack(padx=20, pady=8, fill="x")

        self.fields = {}
        field_defs = [
            ("ID",         "S001"),
            ("Name",       ""),
            ("Email",      "student@university.edu"),
            ("Course",     "BSc Computer Science"),
            ("Department", "Engineering"),
        ]
        for label, default in field_defs:
            row = FieldRow(frame, label + ":", default)
            row.pack(fill="x", padx=10, pady=3)
            self.fields[label] = row

        score_frame = Card(self)
        score_frame.pack(padx=20, pady=4, fill="x")
        tk.Label(score_frame, text="Subject Scores (0–100)", bg=C["card"],
                 fg=C["muted"], font=FONT_SMALL).grid(row=0, column=0, columnspan=6,
                 sticky="w", padx=10, pady=(8, 4))

        self.scores = {}
        subjects = ["Math", "Science", "English", "History", "CS", "Attendance%"]
        defaults  = ["85",  "80",      "78",      "82",     "90", "95"]
        for i, (sub, default) in enumerate(zip(subjects, defaults)):
            col = i * 2
            tk.Label(score_frame, text=sub + ":", bg=C["card"],
                     fg=C["muted"], font=FONT_SMALL).grid(row=1, column=col, padx=(10, 2))
            var = tk.StringVar(value=default)
            tk.Entry(score_frame, textvariable=var, width=6,
                     bg=C["surface"], fg=C["text"], insertbackground=C["text"],
                     relief="flat", font=FONT_BODY, bd=4).grid(row=1, column=col + 1, padx=(0, 10), pady=8)
            self.scores[sub] = var

        btn_row = tk.Frame(self, bg=C["surface"])
        btn_row.pack(pady=14)
        StyledButton(btn_row, "Add Student", self._submit, color=C["student"], width=14).pack(side="left", padx=6)
        StyledButton(btn_row, "Cancel", self.destroy, color="#374151", width=10).pack(side="left", padx=6)

        self.update_idletasks()
        x = parent.winfo_rootx() + 80
        y = parent.winfo_rooty() + 60
        self.geometry(f"+{x}+{y}")

    def _submit(self):
        try:
            s = StudentRecord(
                id         = self.fields["ID"].get(),
                name       = self.fields["Name"].get(),
                email      = self.fields["Email"].get(),
                course     = self.fields["Course"].get(),
                department = self.fields["Department"].get(),
                math       = float(self.scores["Math"].get()),
                science    = float(self.scores["Science"].get()),
                english    = float(self.scores["English"].get()),
                history    = float(self.scores["History"].get()),
                cs         = float(self.scores["CS"].get()),
                attendance = float(self.scores["Attendance%"].get()),
            )
            if not s.name:
                raise ValueError("Name is required.")
            self.callback(s)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e), parent=self)


# ─────────────── ADD EMPLOYEE DIALOG ─────
class AddEmployeeDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Add Employee")
        self.configure(bg=C["surface"])
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Add New Employee", bg=C["surface"],
                 fg=C["primary"], font=FONT_HEAD).pack(pady=(16, 8))

        frame = Card(self)
        frame.pack(padx=20, pady=8, fill="x")

        self.fields = {}
        field_defs = [
            ("ID",         "E001"),
            ("Name",       ""),
            ("Email",      "employee@company.com"),
            ("Department", "Engineering"),
            ("Role",       "Software Developer"),
        ]
        for label, default in field_defs:
            row = FieldRow(frame, label + ":", default)
            row.pack(fill="x", padx=10, pady=3)
            self.fields[label] = row

        extra = Card(self)
        extra.pack(padx=20, pady=4, fill="x")

        tk.Label(extra, text="Performance:", bg=C["card"],
                 fg=C["muted"], font=FONT_SMALL).grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.perf_var = tk.StringVar(value="Good")
        perf_cb = ttk.Combobox(extra, textvariable=self.perf_var, width=16,
                                values=["Outstanding", "Excellent", "Good", "Average", "Poor"],
                                state="readonly", font=FONT_BODY)
        perf_cb.grid(row=0, column=1, padx=4)

        tk.Label(extra, text="Status:", bg=C["card"],
                 fg=C["muted"], font=FONT_SMALL).grid(row=0, column=2, padx=10, sticky="e")
        self.status_var = tk.StringVar(value="Active")
        ttk.Combobox(extra, textvariable=self.status_var, width=10,
                     values=["Active", "Inactive"], state="readonly",
                     font=FONT_BODY).grid(row=0, column=3, padx=4)

        num_frame = Card(self)
        num_frame.pack(padx=20, pady=4, fill="x")
        num_defs = [("Projects", "proj", "10"), ("Salary (PKR)", "salary", "100000"), ("Experience (Yrs)", "exp", "3")]
        self.num_vars = {}
        for i, (lbl, key, default) in enumerate(num_defs):
            tk.Label(num_frame, text=lbl + ":", bg=C["card"],
                     fg=C["muted"], font=FONT_SMALL).grid(row=0, column=i*2, padx=(10, 2), pady=10, sticky="e")
            var = tk.StringVar(value=default)
            tk.Entry(num_frame, textvariable=var, width=12, bg=C["surface"],
                     fg=C["text"], insertbackground=C["text"],
                     relief="flat", font=FONT_BODY, bd=4).grid(row=0, column=i*2+1, padx=(0, 10))
            self.num_vars[key] = var

        btn_row = tk.Frame(self, bg=C["surface"])
        btn_row.pack(pady=14)
        StyledButton(btn_row, "Add Employee", self._submit, color=C["company"], width=14).pack(side="left", padx=6)
        StyledButton(btn_row, "Cancel", self.destroy, color="#374151", width=10).pack(side="left", padx=6)

        self.update_idletasks()
        x = parent.winfo_rootx() + 80
        y = parent.winfo_rooty() + 60
        self.geometry(f"+{x}+{y}")

    def _submit(self):
        try:
            e = EmployeeRecord(
                id              = self.fields["ID"].get(),
                name            = self.fields["Name"].get(),
                email           = self.fields["Email"].get(),
                department      = self.fields["Department"].get(),
                role            = self.fields["Role"].get(),
                performance     = self.perf_var.get(),
                projects        = int(self.num_vars["proj"].get()),
                salary          = float(self.num_vars["salary"].get()),
                years_experience= int(self.num_vars["exp"].get()),
                status          = self.status_var.get(),
            )
            if not e.name:
                raise ValueError("Name is required.")
            self.callback(e)
            self.destroy()
        except ValueError as ex:
            messagebox.showerror("Invalid Input", str(ex), parent=self)


# ─────────────── MAIN APP ────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ReportGen Pro — PDF Report Generator")
        self.configure(bg=C["bg"])
        self.geometry("1100x780")
        self.minsize(900, 640)
        self._build_ui()

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self, bg=C["surface"], pady=0)
        header.pack(fill="x")

        tk.Frame(header, bg=C["primary"], width=5).pack(side="left", fill="y")

        title_block = tk.Frame(header, bg=C["surface"])
        title_block.pack(side="left", padx=16, pady=10)
        tk.Label(title_block, text="ReportGen Pro", bg=C["surface"],
                 fg=C["text"], font=FONT_TITLE).pack(anchor="w")
        tk.Label(title_block, text="Professional PDF Report Generator  ·  v1.0",
                 bg=C["surface"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        right = tk.Frame(header, bg=C["surface"])
        right.pack(side="right", padx=16)
        StyledButton(right, "📂 Open Reports Folder", self._open_reports, color="#374151", width=20).pack(pady=8)

        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # ── Tab bar ──
        tab_bar = tk.Frame(self, bg=C["bg"])
        tab_bar.pack(fill="x")

        self.notebook = ttk.Notebook(self)
        nb_style = ttk.Style()
        nb_style.configure("TNotebook", background=C["bg"], borderwidth=0)
        nb_style.configure("TNotebook.Tab",
            background=C["surface"], foreground=C["muted"],
            padding=[18, 8], font=FONT_SUB, borderwidth=0,
        )
        nb_style.map("TNotebook.Tab",
            background=[("selected", C["card"])],
            foreground=[("selected", C["primary"])],
        )

        # ── Log panel (shared) ──
        self.log = LogPanel(self)
        self.log.pack(fill="x", side="bottom")
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", side="bottom")

        # ── Tabs ──
        self.student_tab = StudentTab(self.notebook, self.log)
        self.company_tab = CompanyTab(self.notebook, self.log)

        self.notebook.add(self.student_tab, text="  👨‍🎓  Student Report  ")
        self.notebook.add(self.company_tab, text="  🏢  Company Report  ")
        self.notebook.pack(fill="both", expand=True)

        self.log.log("ReportGen Pro started. Load data or add records manually.", "head")
        self.log.log(f"Reports directory: {REPORTS_DIR}", "info")

    def _open_reports(self):
        import subprocess
        try:
            if sys.platform == "win32":
                os.startfile(REPORTS_DIR)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", REPORTS_DIR])
            else:
                subprocess.Popen(["xdg-open", REPORTS_DIR])
        except Exception:
            messagebox.showinfo("Reports Folder", REPORTS_DIR)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
