import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from datetime import datetime, date, timedelta
import math
import csv

DATA_FILE = 'data.json'
FIELDS = ['Date', 'Category', 'Sub-Category', 'Amount', 'Remarks']

COLOR_MAP = {
    "Food": "#FF9999", "Rent": "#FFB266", "Mobile Recharge": "#FFFF99",
    "Health": "#99FF99", "Travel": "#99CCFF", "Fuel": "#CC99FF", "Shopping": "#FF66B2", "Other": "#B2B2B2",
    "Allowance": "#7FC97F", "Salary": "#BEAED4", "Profit": "#FDC086", "Cash": "#FFFF99", "Bonus": "#386CB0", "Other Income": "#F0027F",
    "Income": "#66BB6A",
    "Expense": "#EF5350"
}

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1200x1000")
        self.root.configure(bg="black")
        self.show_splash_screen()
        self.editing_index = None

    def show_splash_screen(self):
        splash_frame = tk.Frame(self.root, bg="lightgray")
        splash_frame.pack(expand=True, fill=tk.BOTH)

        welcome_label = tk.Label(
            splash_frame,
            text="Welcome to the Expense Tracker App",
            font=("Arial", 28, "bold"),
            fg="steelblue",
            bg="lightgray"
        )
        welcome_label.pack(pady=(50, 20))

        instruction_text = (
            "This Expense Tracker App helps you manage your finances by easily recording and visualizing your income and expenses.\n\n"
            "Here's how to use it:\n\n"
            "1. Adding Records: To add a new income or expense, click the 'Record Data' button at the top, or the '+' (plus) button on the Home page. Fill in the date, choose a category (Income/Expense), select a sub-category, enter the amount, and add any remarks. Then, click 'Submit'.\n\n"
            "2. Viewing and Managing Records: Click 'Show Data' or 'Modify Data' at the top to see all your recorded transactions. From this page, you can select any record to edit or delete it. This gives you full control over your entries.\n\n"
            "3. Filtering Records: Use the 'Records' button in the bottom navigation to view your transactions with advanced filtering options by category, sub-category, and date ranges. This view is for reference only and does not allow direct editing or deletion.\n\n"
            "4. Analyzing Your Finances (Reports): Go to the 'Reports' section (at the bottom) to get visual insights into your spending and earnings. Here, you can:\n"
            "   - Select a Category Type (Income or Expense).\n"
            "   - Choose a Date within your desired period.\n"
            "   - Define the View By period (Day, Week, Month, or Year).\n"
            "   - Select how to Group By (Category or Sub-Category) to see breakdowns accordingly.\n"
            "   - Optionally, filter by a specific Sub-Category for more granular analysis.\n"
            "   This will generate a pie chart summarizing your financial activity.\n\n"
            "5. Navigation: The top buttons are for primary actions like adding, showing, or modifying data. The bottom navigation bar provides quick access to filtered record views, comprehensive reports, and future features like accounts and settings.\n\n"
            "We hope this app helps you gain better control over your financial journey!"
        )

        instruction_textbox = tk.Text(
            splash_frame,
            font=("Courier New", 16, "bold"),
            fg="black",
            bg="lightgray",
            wrap="word",
            relief="flat",
            height=30,
            width=100
        )
        instruction_textbox.insert(tk.END, instruction_text)
        instruction_textbox.config(state=tk.DISABLED)
        instruction_textbox.pack(padx=200, pady=20, fill="x", anchor="center")

        start_button = tk.Button(
            splash_frame,
            text="Get Started",
            font=("Arial", 18),
            bg="dodgerblue",
            fg="white",
            padx=50,
            pady=10,
            command=lambda: self.start_app(splash_frame)
        )
        start_button.pack(pady=30, padx=50, anchor="center")

    def start_app(self, splash_frame):
        splash_frame.destroy()

        self.records = self.load_data()
        self.amount_validate_cmd = self.root.register(self.validate_amount)
        self.editing_index = None

        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 12))
        self.style.configure('TLabel', font=('Arial', 13))
        self.style.configure('TEntry', font=('Arial', 13))
        self.style.configure('TCombobox', font=('Arial', 13))
        self.style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))
        self.style.configure('Treeview', font=('Arial', 11))

        self.create_top_buttons()
        self.create_bottom_nav()
        self.create_main_area()
        self.show_home_page()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.records, f, indent=2)

    def create_top_buttons(self):
        """Creates the navigation buttons at the top of the window."""
        self.top_frame = tk.Frame(self.root, bg="lightgray", bd=2, relief="raised")
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        buttons = [
            ("Record Data", self.show_add_record_form),
            ("Show Data", self.show_manage_records_page),
            ("Modify Data", self.edit_selected_record)  # ✅ New button
        ]
        for name, command in buttons:
            tk.Button(self.top_frame, text=name, command=command, font=("Arial", 14), height=2,
                      bd=0, bg="white", activebackground="#f0f0f0", fg="black").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=5)

    def create_bottom_nav(self):
        self.bottom_frame = tk.Frame(self.root, bg="lightgray")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        buttons_data = [
            ("Accounts", lambda: messagebox.showinfo("Info", "Accounts functionality coming soon!")),
            ("Categories", self.show_subcategory_selection_page),
            ("Records", self.show_filtered_records_view),
            ("Reports", self.show_dashboard),
            ("Settings", lambda: messagebox.showinfo("Info", "Settings functionality coming soon!"))
        ]
        for name, command in buttons_data:
            tk.Button(self.bottom_frame, text=name, font=("Arial", 12), height=2, bd=0,
                      bg="white", activebackground="white", command=command).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=5)

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def create_main_area(self):
        self.main_area = tk.Frame(self.root, bg="lightgray")
        self.main_area.pack(expand=True, fill=tk.BOTH)

    def create_circular_button(self, parent, size, color, command):
        canvas = tk.Canvas(parent, width=size, height=size, bd=0, highlightthickness=0, bg=parent.cget('bg'))

        radius = size / 2
        canvas.create_oval(0, 0, size, size, fill=color, outline="")

        line_width = 3
        plus_size = size * 0.4

        canvas.create_line(radius - plus_size / 2, radius, radius + plus_size / 2, radius, fill="white", width=line_width, capstyle=tk.ROUND)
        canvas.create_line(radius, radius - plus_size / 2, radius, radius + plus_size / 2, fill="white", width=line_width, capstyle=tk.ROUND)

        canvas.bind("<Button-1>", lambda event: command())
        canvas.bind("<Enter>", lambda event: canvas.config(cursor="hand2"))
        canvas.bind("<Leave>", lambda event: canvas.config(cursor=""))

        return canvas

    def show_home_page(self):
        self.clear_main_area()

        if not self.records:
            no_data_label = tk.Label(
                self.main_area,
                text="No Data Yet!",
                font=("Arial", 24, "bold"),
                fg="gray",
                bg="lightgray"
            )
            no_data_label.pack(pady=(50, 20))

            expense_matter_text = (
                "This space is currently empty because there's no expense or income data "
                "recorded for display. To start tracking your finances, click the "
                "'+' button in the bottom-right corner to add your first record.\n\n"
                "Once you start adding records, you'll see summaries, charts, "
                "or recent transactions here, giving you a quick overview of your finances."
            )
            expense_matter_label = tk.Label(
                self.main_area,
                text=expense_matter_text,
                font=("Arial", 16),
                fg="darkgray",
                bg="lightgray",
                wraplength=700,
                justify=tk.CENTER
            )
            expense_matter_label.pack(expand=True, fill=tk.BOTH, padx=50, pady=20)
        else:
            tk.Label(self.main_area, text="Recent Transactions", font=('Arial', 24, 'bold'), bg="lightgray", fg="steelblue").pack(pady=20)

            summary_frame = tk.Frame(self.main_area, bg="white", bd=2, relief="groove")
            summary_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

            columns = FIELDS
            recent_tree = ttk.Treeview(summary_frame, columns=columns, show='headings', height=5)
            for field in FIELDS:
                recent_tree.heading(field, text=field)
                recent_tree.column(field, width=130, anchor=tk.CENTER)

            sorted_records = sorted(self.records, key=lambda x: datetime.strptime(x['Date'], "%Y-%m-%d"), reverse=True)
            for i, record in enumerate(sorted_records[:5]):
                recent_tree.insert('', tk.END, values=[record[field] for field in FIELDS])

            recent_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            tk.Button(self.main_area, text="View All Records", command=self.show_filtered_records_view,
                      bg="green", fg="white", font=("Arial", 14), width=20).pack(pady=10)


        plus_button_frame = tk.Frame(self.main_area, bg="lightgray")
        plus_button_frame.pack(side=tk.BOTTOM, anchor=tk.SE, padx=20, pady=20)

        button_size = 60
        button_color = "dodgerblue"

        plus_button_canvas = self.create_circular_button(
            plus_button_frame,
            button_size,
            button_color,
            self.show_add_record_form
        )
        plus_button_canvas.pack()

    def show_subcategory_selection_page(self):
        from PIL import Image, ImageTk
        self.clear_main_area()
        tk.Label(self.main_area, text="Sub-Category", font=('Arial', 20), bg="lightgray").pack(pady=10)

        outer_frame = tk.Frame(self.main_area, bg="lightgray")
        outer_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(outer_frame, bg="lightgray", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        subcategory_frame = tk.Frame(canvas, bg="lightgray")
        canvas.create_window((0, 0), window=subcategory_frame, anchor="nw")

        image_dict = {
            "Allowance": "Images/allowance.png",
            "Salary": "Images/salary.png",
            "Profit": "Images/profit.png",
            "Cash": "Images/cash.png",
            "Bonus": "Images/bonus.png",
            "Other Income": "Images/income.png",
            "Food": "Images/food.png",
            "Rent": "Images/rent.png",
            "Mobile Recharge": "Images/mobile.png",
            "Health": "Images/health.png",
            "Travel": "Images/travel.png",
            "Fuel": "Images/fuel.png",
            "Shopping": "Images/shopping.png",
            "Other Expense": "Images/expenses.png"
        }

        self.subcat_images = {}

        known_income = ["Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        known_expense = ["Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other Expense"]

        def create_button_grid(parent, items, row_start):
            max_cols = 5
            for i, subcat in enumerate(items):
                image_path = image_dict.get(subcat)
                try:
                    img = Image.open(image_path).resize((40, 40), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.subcat_images[subcat] = photo

                    btn = tk.Button(
                        parent,
                        image=photo,
                        text=subcat,
                        compound="top",
                        font=("Arial", 10),
                        width=100,
                        height=100,
                        wraplength=90,
                        justify="center",
                        command=lambda s=subcat: self.show_records_by_subcategory(s)
                    )
                except FileNotFoundError:
                    btn = tk.Button(
                        parent,
                        text=subcat,
                        font=("Arial", 10),
                        width=100,
                        height=100,
                        wraplength=90,
                        justify="center",
                        command=lambda s=subcat: self.show_records_by_subcategory(s)
                    )
                btn.grid(row=row_start + i // max_cols, column=i % max_cols, padx=10, pady=10, sticky="nsew")

        # Income Label and Buttons
        tk.Label(subcategory_frame, text="Income", font=('Arial', 16, 'bold'), bg="lightgray", fg="green")\
            .grid(row=0, column=0, columnspan=10, sticky="w", pady=(10, 5))
        create_button_grid(subcategory_frame, known_income, row_start=1)

        spacer = tk.Frame(subcategory_frame, height=20, bg="lightgray")
        spacer.grid(row=3, column=0, columnspan=10)

        tk.Frame(subcategory_frame, height=2, bg="black")\
            .grid(row=4, column=0, columnspan=10, sticky="ew", pady=5)

        tk.Label(subcategory_frame, text="Expense", font=('Arial', 16, 'bold'), bg="lightgray", fg="red")\
            .grid(row=5, column=0, columnspan=10, sticky="w", pady=(10, 5))
        create_button_grid(subcategory_frame, known_expense, row_start=6)

        bottom_frame = tk.Frame(self.main_area, bg="lightgray")
        bottom_frame.pack(fill=tk.X, pady=5)

        tk.Button(bottom_frame, text="Back to Home", command=self.show_home_page,
                  bg="green", fg="white", font=("Arial", 14), padx=20, pady=5).pack(pady=10)


    def show_records_by_subcategory(self, selected_subcategory):
        self.clear_main_area()
        tk.Label(self.main_area, text=f"{selected_subcategory}", font=('Arial', 20), bg="lightgray").pack(pady=10)

        subcat_records = [r for r in self.records if r['Sub-Category'] == selected_subcategory]
        subcat_records.sort(key=lambda x: datetime.strptime(x['Date'], "%Y-%m-%d"), reverse=True)

        if not subcat_records:
            tk.Label(self.main_area, text="No data available for this sub-category.", font=('Arial', 16), bg="lightgray", fg="gray").pack(pady=20)
        else:
            columns = FIELDS
            tree = ttk.Treeview(self.main_area, columns=columns, show='headings')
            for field in FIELDS:
                tree.heading(field, text=field)
                tree.column(field, width=130)
            tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

            for record in subcat_records:
                tree.insert('', tk.END, values=[record[field] for field in FIELDS])

        tk.Button(self.main_area, text="Back to Sub-Categories", command=self.show_subcategory_selection_page,
                  bg="steelblue", fg="white", font=("Arial", 14)).pack(side="bottom", pady=10)

    def show_dashboard(self):
        self.clear_main_area()
        tk.Label(self.main_area, text="Reports Dashboard", font=('Arial', 20), bg="lightgray").pack(pady=10)

        self.filter_options_frame = tk.Frame(self.main_area, bg="lightgray")
        self.filter_options_frame.pack(pady=10)

        tk.Label(self.filter_options_frame, text="Category Type:", font=('Arial', 13), bg="lightgray").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.chart_type_var = tk.StringVar(value="Expense")
        type_options = ttk.Combobox(self.filter_options_frame, textvariable=self.chart_type_var,
                                     values=["Income", "Expense"], state="readonly",
                                     font=("Arial", 13), width=15)
        type_options.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        type_options.bind("<<ComboboxSelected>>", self.update_report_filters_and_chart)

        tk.Label(self.filter_options_frame, text="Select Date:", font=('Arial', 13), bg="lightgray").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.selected_date = DateEntry(self.filter_options_frame, date_pattern='yyyy-mm-dd',
                                             font=("Arial", 13), background='darkblue',
                                             foreground='white', borderwidth=2, width=15,
                                             maxdate=datetime.today().date())
        self.selected_date.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.selected_date.bind("<<DateEntrySelected>>", self.display_pie_chart)

        tk.Label(self.filter_options_frame, text="View By:", font=('Arial', 13), bg="lightgray").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.view_by_var = tk.StringVar(value="Day")
        view_by_combo = ttk.Combobox(self.filter_options_frame, textvariable=self.view_by_var,
                                     values=["Day", "Week", "Month", "Year"], state="readonly",
                                     font=("Arial", 13), width=15)
        view_by_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        view_by_combo.bind("<<ComboboxSelected>>", self.display_pie_chart)

        tk.Label(self.filter_options_frame, text="Group By:", font=('Arial', 13), bg="lightgray").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.group_by_var = tk.StringVar(value="Sub-Category")
        group_by_combo = ttk.Combobox(self.filter_options_frame, textvariable=self.group_by_var,
                                     values=["Category", "Sub-Category"], state="readonly",
                                     font=("Arial", 13), width=15)
        group_by_combo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        group_by_combo.bind("<<ComboboxSelected>>", self.display_pie_chart)

        tk.Label(self.filter_options_frame, text="Filter Sub-Category:", font=('Arial', 13), bg="lightgray").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.report_subcategory_var = tk.StringVar(value="")
        self.report_subcategory_combo = ttk.Combobox(self.filter_options_frame, textvariable=self.report_subcategory_var,
                                                     values=[""], state="readonly",
                                                     font=("Arial", 13), width=15)
        self.report_subcategory_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.report_subcategory_combo.bind("<<ComboboxSelected>>", self.display_pie_chart)

        self.chart_container_frame = tk.Frame(self.main_area, bg="lightgray")
        self.chart_container_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Button(self.main_area, text="Back to Home", command=self.show_home_page,
                  bg="green", fg="white", font=("Arial", 15), width=20).pack(pady=10)

        self.update_report_filters_and_chart()

    def update_report_filters_and_chart(self, event=None):
        selected_type = self.chart_type_var.get()
        income_categories = ["", "Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        expense_categories = ["", "Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other"]

        if selected_type == "Income":
            self.report_subcategory_combo['values'] = income_categories
        elif selected_type == "Expense":
            self.report_subcategory_combo['values'] = expense_categories
        else:
            self.report_subcategory_combo['values'] = [""]

        self.report_subcategory_var.set("")
        self.display_pie_chart()

    def display_pie_chart(self, event=None):
        for widget in self.chart_container_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4), facecolor='lightgray')
        data_group = defaultdict(float)

        selected_date = self.selected_date.get_date()
        selected_type = self.chart_type_var.get()
        view_by = self.view_by_var.get()
        group_by = self.group_by_var.get()
        filter_subcategory = self.report_subcategory_var.get()

        start_date, end_date = selected_date, selected_date
        if view_by == "Week":
            start_date = selected_date - timedelta(days=selected_date.weekday())
            end_date = start_date + timedelta(days=6)
        elif view_by == "Month":
            start_date = selected_date.replace(day=1)
            if selected_date.month == 12:
                end_date = selected_date.replace(year=selected_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = selected_date.replace(month=selected_date.month + 1, day=1) - timedelta(days=1)
        elif view_by == "Year":
            start_date = selected_date.replace(month=1, day=1)
            end_date = selected_date.replace(month=12, day=31)

        for record in self.records:
            try:
                record_date = datetime.strptime(record['Date'], "%Y-%m-%d").date()

                if not (start_date <= record_date <= end_date):
                    continue

                if record['Category'] != selected_type:
                    continue

                if filter_subcategory and record['Sub-Category'] != filter_subcategory:
                    continue

                group_key = ""
                if group_by == "Category":
                    group_key = record['Category']
                elif group_by == "Sub-Category":
                    group_key = record['Sub-Category']

                data_group[group_key] += float(record['Amount'])
            except ValueError:
                continue

        if not data_group:
            ax.text(0.5, 0.5, 'No data available for selected filters', ha='center', va='center', fontsize=14)
        else:
            labels = list(data_group.keys())
            sizes = list(data_group.values())
            
            colors = [COLOR_MAP.get(label, '#CCCCCC') for label in labels]

            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140,
                    textprops={'fontsize': 10, 'color': 'black'})
            ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container_frame)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(pady=10, fill=tk.BOTH, expand=True)
        plt.close(fig)

    def validate_amount(self, value):
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def show_add_record_form(self, edit=False):
        """
        Displays the form to add a new record or edit an existing one.
        If edit is True, it pre-fills the form with data from self.records[self.editing_index].
        """
        self.clear_main_area()
        self.build_record_form("Modify Expense Data" if edit else "Modify Expense Data", edit)
        if edit and self.editing_index is not None:
            record = self.records[self.editing_index]
            self.date_entry.set_date(record['Date'])
            self.category_var.set(record['Category'])
            self.show_subcategory_icons()
            self.subcategory_var.set(record['Sub-Category'])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, record['Amount'])
            self.remarks_entry.delete(0, tk.END)
            self.remarks_entry.insert(0, record['Remarks'])

    def show_manage_records_page(self):
        """
        Displays all records in a table, sorted by date (latest first),
        with Edit and Delete buttons for managing records.
        This is the page that "Show Data" and "Modify Data" buttons lead to.
        """
        self.clear_main_area()
        tk.Label(self.main_area, text="Manage Expense Records", font=('Arial', 20), bg="lightgray").pack(pady=10)

        columns = FIELDS
        self.tree = ttk.Treeview(self.main_area, columns=columns, show='headings')
        for field in FIELDS:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=130, anchor="center")

        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_record_select)

        sorted_records = sorted(self.records, key=lambda x: datetime.strptime(x['Date'], "%Y-%m-%d"), reverse=True)
        self.populate_records_treeview(sorted_records)

        button_frame = tk.Frame(self.main_area, bg="lightgray")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Edit Selected", command=self.edit_selected_record, # <--- Here's the Edit Selected button
                    bg="dodgerblue", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Delete Selected", command=self.delete_selected_record,
                    bg="red", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Back to Home", command=self.show_home_page,
                    bg="green", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, record in enumerate(self.records):
            values = [record[field] for field in FIELDS]
            self.tree.insert("", "end", iid=i, values=values)
        
    def load_record_for_edit(self):
        try:
            index = int(self.modify_index_var.get())
            if index < 0 or index >= len(self.records):
                raise IndexError
        except:
            messagebox.showerror("Error", "Invalid record number.")
            return

        self.editing_index = index
        self.show_add_record_form(edit=True)

    def build_record_form(self, title, edit=False):
        """
        Builds the detailed form for adding or editing a record.
        This is called by show_add_record_form.
        """
        tk.Label(self.main_area, text=title, font=('Arial', 20), bg="lightgray").pack(pady=10)
        form_frame = tk.Frame(self.main_area, bg="lightgray")
        form_frame.pack(pady=10)

        label_opts = {'font': ('Arial', 13), 'bg': 'lightgray'}
        entry_opts = {'font': ('Arial', 13), 'bd': 0, 'relief': 'flat', 'width': 40}

        tk.Label(form_frame, text="Date:", **label_opts).grid(row=0, column=0, sticky="e", padx=20, pady=10)
        self.date_entry = DateEntry(form_frame, background='darkblue', foreground='lightgray',
                                     borderwidth=0, date_pattern='yyyy-mm-dd',
                                     font=('Arial', 13), width=38,
                                     maxdate=datetime.today().date())
        self.date_entry.grid(row=0, column=1, sticky="w", pady=10)

        tk.Label(form_frame, text="Category:", **label_opts).grid(row=1, column=0, sticky="e", padx=20, pady=10)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var,
                                     values=["Income", "Expense"], state="readonly",
                                     font=('Arial', 13), width=38)
        category_combo.grid(row=1, column=1, sticky="w", pady=10)
        category_combo.bind("<<ComboboxSelected>>", self.update_subcategories)

        tk.Label(form_frame, text="Sub-Category:", **label_opts).grid(row=2, column=0, sticky="e", padx=20, pady=10)
        self.subcategory_var = tk.StringVar()
        self.subcategory_var = tk.StringVar()
        self.subcategory_entry = tk.Entry(form_frame, textvariable=self.subcategory_var,
                                        font=('Arial', 13), width=38)
        self.subcategory_entry.grid(row=2, column=1, sticky="w", pady=10)
        self.subcategory_entry.bind("<FocusIn>", self.show_subcategory_icons)

        self.icon_button_frame = tk.Frame(form_frame, bg="lightgray")
        self.icon_button_frame.grid(row=5, column=1, sticky="w", pady=5)

        tk.Label(form_frame, text="Amount:", **label_opts).grid(row=3, column=0, sticky="e", padx=20, pady=10)
        self.amount_entry = tk.Entry(form_frame, **entry_opts, validate='key',
                                     validatecommand=(self.amount_validate_cmd, '%P'))
        self.amount_entry.grid(row=3, column=1, sticky="w", pady=10)

        tk.Label(form_frame, text="Remarks:", **label_opts).grid(row=4, column=0, sticky="e", padx=20, pady=10)
        self.remarks_entry = tk.Entry(form_frame, **entry_opts)
        self.remarks_entry.grid(row=4, column=1, sticky="w", pady=10)

        button_frame = tk.Frame(self.main_area, bg="lightgray")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Submit",
                  command=self.update_record if edit else self.save_record,
                  bg="dodgerblue", fg="white", font=("Arial", 14), width=15).pack(side=tk.LEFT, padx=20)

        tk.Button(button_frame, text="Back to Home", command=self.show_home_page,
                  bg="green", fg="white", font=("Arial", 14), width=15).pack(side=tk.LEFT, padx=20)

        if edit and self.editing_index is not None:
            record = self.records[self.editing_index]
            self.date_entry.set_date(record['Date'])
            self.category_var.set(record['Category'])
            self.update_subcategories(None)  # if you clear/update icon buttons
            self.show_subcategory_icons()    # optional: to show the icons
            self.subcategory_var.set(record['Sub-Category'])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, record['Amount'])
            self.remarks_entry.delete(0, tk.END)
            self.remarks_entry.insert(0, record['Remarks'])
        elif edit:
            messagebox.showwarning("Warning", "No record selected for editing. Please select a record from the 'Manage Records' page.")
            self.show_manage_records_page()

    def show_subcategory_icons(self, event=None):
        for widget in self.icon_button_frame.winfo_children():
            widget.destroy()

        cat = self.category_var.get()
        if not cat:
            messagebox.showinfo("Info", "Please select Category first.")
            return

        icon_dict = {
            "Income": {
                "Allowance": "💸", "Salary": "💼", "Profit": "📈",
                "Cash": "💰", "Bonus": "🎁", "Other Income": "➕"
            },
            "Expense": {
                "Food": "🍔", "Rent": "🏠", "Mobile Recharge": "📱",
                "Health": "💊", "Travel": "✈️", "Fuel": "⛽",
                "Shopping": "🛍️", "Other": "❓"
            }
        }.get(cat, {})

        def select_subcat(name):
            self.subcategory_var.set(name)
            for btn in self.icon_button_frame.winfo_children():
                btn.configure(bg="SystemButtonFace")
            button_refs[name].configure(bg="lightblue")

        button_refs = {}
        for i, (name, icon) in enumerate(icon_dict.items()):
            btn = tk.Button(self.icon_button_frame, text=f"{icon} {name}", font=("Arial", 10),
                            command=lambda n=name: select_subcat(n), width=18)
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=2)
            button_refs[name] = btn


    def update_subcategories(self, event=None):
        self.subcategory_var.set("")
        for widget in self.icon_button_frame.winfo_children():
            widget.destroy()

    def get_form_data(self):
        date = self.date_entry.get()
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        amount = self.amount_entry.get().strip()
        remarks = self.remarks_entry.get().strip()

        if not (date and category and subcategory and amount):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return None

        try:
            float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return None

        return {
            'Date': date,
            'Category': category,
            'Sub-Category': subcategory,
            'Amount': amount,
            'Remarks': remarks
        }

    def save_record(self):
        if self.editing_index is not None:
            self.records[self.editing_index] = record
            self.editing_index = None
        else:
            self.records.append(record)

        self.save_data()
        messagebox.showinfo("Success", "Record saved successfully!")
        self.show_manage_records_page()

    def update_record(self):
        if self.editing_index is None or self.editing_index == -1:
            messagebox.showerror("Error", "No record selected to update. Please select a record from 'Manage Records' first.")
            self.show_manage_records_page()
            return

        record = self.get_form_data()
        if not record:
            return

        self.records[self.editing_index] = record
        self.save_data()
        messagebox.showinfo("Success", "Record updated successfully!")
        self.editing_index = None
        self.show_manage_records_page()

    def show_filtered_records_view(self):
        self.clear_main_area()
        tk.Label(self.main_area, text="Records", font=('Arial', 20), bg="lightgray").pack(pady=10)

        filter_frame = tk.Frame(self.main_area, bg="lightgray")
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Category:", font=('Arial', 11), bg="lightgray").grid(row=0, column=0, padx=5)
        self.filter_category_var = tk.StringVar(value="")
        filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                             values=["", "Income", "Expense"], state="readonly",
                                             font=('Arial', 11), width=15)
        filter_category_combo.grid(row=0, column=1, padx=5)
        filter_category_combo.bind("<<ComboboxSelected>>", self.update_filter_subcategories_and_apply)

        tk.Label(filter_frame, text="Sub-Category:", font=('Arial', 11), bg="lightgray").grid(row=0, column=2, padx=5)
        self.filter_subcategory_var = tk.StringVar(value="")
        self.filter_subcategory_combo = ttk.Combobox(filter_frame, textvariable=self.filter_subcategory_var,
                                                     values=[""], state="readonly",
                                                     font=('Arial', 11), width=15)
        self.filter_subcategory_combo.grid(row=0, column=3, padx=5)
        self.filter_subcategory_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())


        tk.Label(filter_frame, text="From Date:", font=('Arial', 11), bg="lightgray").grid(row=1, column=0, padx=5, pady=5)
        self.filter_from_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd',
                                             font=("Arial", 11), background='darkblue',
                                             foreground='white', borderwidth=2, width=15,
                                             maxdate=datetime.today().date())
        self.filter_from_date.delete(0, tk.END)
        self.filter_from_date.grid(row=1, column=1, padx=5, pady=5)
        self.filter_from_date.bind("<<DateEntrySelected>>", lambda e: self.apply_filters())


        tk.Label(filter_frame, text="To Date:", font=('Arial', 11), bg="lightgray").grid(row=1, column=2, padx=5, pady=5)
        self.filter_to_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd',
                                             font=("Arial", 11), background='darkblue',
                                             foreground='white', borderwidth=2, width=15,
                                             maxdate=datetime.today().date())
        self.filter_to_date.delete(0, tk.END)
        self.filter_to_date.grid(row=1, column=3, padx=5, pady=5)
        self.filter_to_date.bind("<<DateEntrySelected>>", lambda e: self.apply_filters())


        tk.Button(filter_frame, text="Apply Filter", command=self.apply_filters,
                  bg="steelblue", fg="white", font=("Arial", 11)).grid(row=2, column=1, pady=10)

        tk.Button(filter_frame, text="Clear Filters", command=self.clear_filters,
                  bg="gray", fg="white", font=("Arial", 11)).grid(row=2, column=2, pady=10)


        columns = FIELDS
        self.tree = ttk.Treeview(self.main_area, columns=columns, show='headings')
        for field in FIELDS:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=130)

        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        today = date.today()
        first_day_of_month = today.replace(day=1)
        self.filter_from_date.set_date(first_day_of_month)
        self.filter_to_date.set_date(today)
        self.apply_filters()

        tk.Button(self.main_area, text="Back to Home", command=self.show_home_page,
                  bg="green", fg="white", font=("Arial", 15), width=20).pack(pady=10)

        tk.Button(self.main_area, text="Download Filtered Data", command=self.download_filtered_data,
                  bg="orange", fg="white", font=("Arial", 14), width=20).pack(pady=10)

    def update_filter_subcategories_and_apply(self, event=None):
        income_categories = ["", "Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        expense_categories = ["", "Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other"]
        selected_category = self.filter_category_var.get()

        if selected_category == "Income":
            self.filter_subcategory_combo['values'] = income_categories
        elif selected_category == "Expense":
            self.filter_subcategory_combo['values'] = expense_categories
        else:
            all_subcategories = sorted(list(set(record['Sub-Category'] for record in self.records)))
            self.filter_subcategory_combo['values'] = [""] + all_subcategories
        self.filter_subcategory_var.set("")
        self.apply_filters()

    def apply_filters(self):
        category = self.filter_category_var.get()
        subcategory = self.filter_subcategory_var.get()
        from_date_str = self.filter_from_date.get()
        to_date_str = self.filter_to_date.get()

        filtered_records = []
        for record in self.records:
            match = True

            if category and record['Category'] != category:
                match = False
            if subcategory and record['Sub-Category'] != subcategory:
                match = False

            try:
                record_date = datetime.strptime(record['Date'], "%Y-%m-%d").date()
                if from_date_str:
                    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                    if record_date < from_date:
                        match = False
                if to_date_str:
                    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
                    if record_date > to_date:
                        match = False
            except ValueError:
                match = False

            if match:
                filtered_records.append(record)

        filtered_records.sort(key=lambda x: datetime.strptime(x['Date'], "%Y-%m-%d"), reverse=True)
        self.populate_records_treeview(filtered_records)
    
    def download_filtered_data(self):
        category = self.filter_category_var.get()
        subcategory = self.filter_subcategory_var.get()
        from_date_str = self.filter_from_date.get()
        to_date_str = self.filter_to_date.get()

        filtered_records = []
        for record in self.records:
            match = True

            if category and record['Category'] != category:
                match = False
            if subcategory and record['Sub-Category'] != subcategory:
                match = False

            try:
                record_date = datetime.strptime(record['Date'], "%Y-%m-%d").date()
                if from_date_str:
                    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                    if record_date < from_date:
                        match = False
                if to_date_str:
                    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
                    if record_date > to_date:
                        match = False
            except ValueError:
                match = False

            if match:
                filtered_records.append(record)

        if not filtered_records:
            messagebox.showinfo("Info", "No records to download for selected filters.")
            return

        file_path = "filtered_records.csv"
        with open(file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(filtered_records)

        messagebox.showinfo("Download Complete", f"Filtered records saved to {file_path}")


    def clear_filters(self):
        self.filter_category_var.set("")
        self.filter_subcategory_var.set("")

        self.filter_from_date.set_date(None)
        self.filter_from_date.delete(0, tk.END)

        self.filter_to_date.set_date(None)
        self.filter_to_date.delete(0, tk.END)

        self.update_filter_subcategories_and_apply()

    def populate_records_treeview(self, records_to_display):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, record in enumerate(records_to_display):
            self.tree.insert('', tk.END, iid=index, values=[record[field] for field in FIELDS])

    def on_record_select(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            self.editing_index = int(selected_items[0])
        else:
            self.editing_index = None

    def edit_selected_record(self):
        """
        Loads the selected record into the add/edit form for modification.
        """
        if self.editing_index is not None and 0 <= self.editing_index < len(self.records):
            self.show_add_record_form(edit=True)
        else:
            messagebox.showwarning("Warning", "Please select a record from the table to edit.")

    def delete_selected_record(self):
        """
        Checks if a record is selected, then confirms and deletes it.
        """
        if self.editing_index is not None and 0 <= self.editing_index < len(self.records):
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
            if confirm:
                del self.records[self.editing_index]
                self.save_data()
                self.editing_index = None
                self.show_manage_records_page()
        else:
            messagebox.showwarning("Warning", "Please select a record from the table to delete.")
            self.editing_index = None


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
