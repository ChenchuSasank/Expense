'''
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from datetime import datetime

DATA_FILE = 'data.json'
FIELDS = ['Date', 'Category', 'Sub-Category', 'Amount', 'Remarks']

COLOR_MAP = {
    "Food": "#FF9999", "Rent": "#FFB266", "Mobile Recharge": "#FFFF99",
    "Health": "#99FF99", "Travel": "#99CCFF", "Fuel": "#CC99FF", "Shopping": "#FF66B2", "Other": "#B2B2B2",
    "Allowance": "#7FC97F", "Salary": "#BEAED4", "Profit": "#FDC086", "Cash": "#FFFF99", "Bonus": "#386CB0", "Other Income": "#F0027F"
}

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1000x700")
        self.root.configure(bg="black")

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
        self.show_dashboard()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.records, f, indent=2)

    def create_top_buttons(self):
        top_frame = tk.Frame(self.root, bg="lightgray")
        top_frame.pack(side=tk.TOP, fill=tk.X)
        buttons = [("Record Data", self.show_add_record_form),
                   ("Show Data", self.show_records_table),
                   ("Modify Data", self.show_modify_page)]
        for name, command in buttons:
            tk.Button(top_frame, text=name, command=command, font=("Arial", 14), height=2,
                      bd=0, bg="white", activebackground="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=5)

    def create_bottom_nav(self):
        bottom_frame = tk.Frame(self.root, bg="lightgray")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        for item in ["Accounts", "Categories", "Records", "Reports", "Settings"]:
            tk.Button(bottom_frame, text=item, font=("Arial", 12), height=2, bd=0,
                      bg="white", activebackground="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=5)

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def create_main_area(self):
        self.main_area = tk.Frame(self.root, bg="lightgray")
        self.main_area.pack(expand=True, fill=tk.BOTH)

    def show_dashboard(self):
        self.clear_main_area()
        filter_options_frame = tk.Frame(self.main_area, bg="lightgray")
        filter_options_frame.pack(pady=10)

        self.chart_type_var = tk.StringVar(value="Expense")
        type_options = ttk.Combobox(filter_options_frame, textvariable=self.chart_type_var,
                                     values=["Income", "Expense"], state="readonly",
                                     font=("Arial", 13), width=15)
        type_options.pack(side=tk.LEFT, padx=5)
        type_options.bind("<<ComboboxSelected>>", lambda e: self.display_pie_chart())

        self.selected_date = DateEntry(filter_options_frame, date_pattern='yyyy-mm-dd',
                                 font=("Arial", 13), background='darkblue',
                                 foreground='white', borderwidth=2, width=15,
                                 maxdate=datetime.today().date())
        self.selected_date.pack(side=tk.LEFT, padx=5)
        self.selected_date.bind("<<DateEntrySelected>>", lambda e: self.display_pie_chart())
        
        self.display_pie_chart()

    def display_pie_chart(self):
        for widget in self.main_area.winfo_children():
            if widget not in (self.main_area.winfo_children()[0],):
                widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4), facecolor='lightgray')
        data_group = defaultdict(float)
        selected_date = self.selected_date.get_date()
        selected_type = self.chart_type_var.get()

        income_cats = ["Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        expense_cats = ["Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other"]
        target_categories = income_cats if selected_type == "Income" else expense_cats

        for record in self.records:
            try:
                record_date = datetime.strptime(record['Date'], "%Y-%m-%d").date()
                if record_date == selected_date and record['Sub-Category'] in target_categories:
                    data_group[record['Sub-Category']] += float(record['Amount'])
            except ValueError:
                continue

        if not data_group:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
        else:
            labels = list(data_group.keys())
            sizes = list(data_group.values())
            colors = [COLOR_MAP.get(label, '#dddddd') for label in labels]
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.main_area)
        canvas.draw()
        canvas.get_tk_widget().pack()
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
        self.clear_main_area()
        self.build_record_form("Edit Expense Data" if edit else "Record Expense Data", edit)

    def show_modify_page(self):
        if self.editing_index is None:
            messagebox.showerror("Error", "No record selected to modify. Please use 'Show Data' to select a record.")
            return
        self.clear_main_area()
        tk.Label(self.main_area, font=('Arial', 20), bg="lightgray").pack(pady=10)
        self.build_record_form("Modify Expense Record", edit=True)

    def build_record_form(self, title, edit=False):
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
        self.subcategory_combo = ttk.Combobox(form_frame, textvariable=self.subcategory_var,
                                              state="readonly", font=('Arial', 13), width=38)
        self.subcategory_combo.grid(row=2, column=1, sticky="w", pady=10)

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

        tk.Button(button_frame, text="Back", command=self.show_records_table,
                  bg="green", fg="white", font=("Arial", 14), width=15).pack(side=tk.LEFT, padx=20)

        if edit and self.editing_index is not None:
            record = self.records[self.editing_index]
            self.date_entry.set_date(record['Date'])
            self.category_var.set(record['Category'])
            self.update_subcategories(None)
            self.subcategory_var.set(record['Sub-Category'])
            self.amount_entry.insert(0, record['Amount'])
            self.remarks_entry.insert(0, record['Remarks'])

    def update_subcategories(self, event):
        income_categories = ["Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        expense_categories = ["Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other"]
        if self.category_var.get() == "Income":
            self.subcategory_combo['values'] = income_categories
        else:
            self.subcategory_combo['values'] = expense_categories
        self.subcategory_var.set("")

    def get_form_data(self):
        date = self.date_entry.get()
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        amount = self.amount_entry.get().strip()
        remarks = self.remarks_entry.get().strip()

        if not (category and subcategory and amount):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return None

        return {
            'Date': date,
            'Category': category,
            'Sub-Category': subcategory,
            'Amount': amount,
            'Remarks': remarks
        }

    def save_record(self):
        record = self.get_form_data()
        if not record:
            return
        self.records.append(record)
        self.save_data()
        messagebox.showinfo("Success", "Record added successfully!")
        self.show_records_table()

    def update_record(self):
        if self.editing_index is None:
            messagebox.showerror("Error", "No record selected to update. Please select a record from 'Show Data' first.")
            return

        record = self.get_form_data()
        if not record:
            return

        self.records[self.editing_index] = record
        self.save_data()
        messagebox.showinfo("Success", "Record updated successfully!")
        self.editing_index = None
        self.show_records_table()

    def show_records_table(self):
        self.clear_main_area()
        tk.Label(self.main_area, text="Expense Records", font=('Arial', 20), bg="lightgray").pack(pady=10)

        columns = FIELDS
        self.tree = ttk.Treeview(self.main_area, columns=columns, show='headings')
        for field in FIELDS:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=130)

        for index, record in enumerate(self.records):
            self.tree.insert('', tk.END, iid=index, values=[record[field] for field in FIELDS])

        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_record_select)

        button_frame = tk.Frame(self.main_area, bg="lightgray")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Edit Selected", command=self.edit_selected_record,
                  bg="dodgerblue", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Delete Selected", command=self.delete_selected_record,
                  bg="red", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Back to Dashboard", command=self.show_dashboard,
                  bg="green", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

    def on_record_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.editing_index = int(selected[0])

    def edit_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to edit.")
            return
        self.editing_index = int(selected[0])
        self.show_modify_page()

    def delete_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        index = int(selected[0])
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if confirm:
            del self.records[index]
            self.save_data()
            self.show_records_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
'''















































import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from datetime import datetime

DATA_FILE = 'data.json'
FIELDS = ['Date', 'Category', 'Sub-Category', 'Amount', 'Remarks']

COLOR_MAP = {
    "Food": "#FF9999", "Rent": "#FFB266", "Mobile Recharge": "#FFFF99",
    "Health": "#99FF99", "Travel": "#99CCFF", "Fuel": "#CC99FF", "Shopping": "#FF66B2", "Other": "#B2B2B2",
    "Allowance": "#7FC97F", "Salary": "#BEAED4", "Profit": "#FDC086", "Cash": "#FFFF99", "Bonus": "#386CB0", "Other Income": "#F0027F"
}

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1000x700")
        self.root.configure(bg="black")
        self.show_splash_screen()  # Show splash screen first

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
        welcome_label.pack(pady=200)

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
        start_button.pack(pady=100)

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
        self.show_dashboard()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.records, f, indent=2)

    def create_top_buttons(self):
        top_frame = tk.Frame(self.root, bg="lightgray")
        top_frame.pack(side=tk.TOP, fill=tk.X)
        buttons = [("Record Data", self.show_add_record_form),
                   ("Show Data", self.show_records_table),
                   ("Modify Data", self.show_modify_page)]
        for name, command in buttons:
            tk.Button(top_frame, text=name, command=command, font=("Arial", 14), height=2,
                      bd=0, bg="white", activebackground="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=5)

    def create_bottom_nav(self):
        bottom_frame = tk.Frame(self.root, bg="lightgray")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        for item in ["Accounts", "Categories", "Records", "Reports", "Settings"]:
            tk.Button(bottom_frame, text=item, font=("Arial", 12), height=2, bd=0,
                      bg="white", activebackground="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=5)

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def create_main_area(self):
        self.main_area = tk.Frame(self.root, bg="lightgray")
        self.main_area.pack(expand=True, fill=tk.BOTH)

    def show_dashboard(self):
        self.clear_main_area()
        filter_options_frame = tk.Frame(self.main_area, bg="lightgray")
        filter_options_frame.pack(pady=10)

        self.chart_type_var = tk.StringVar(value="Expense")
        type_options = ttk.Combobox(filter_options_frame, textvariable=self.chart_type_var,
                                     values=["Income", "Expense"], state="readonly",
                                     font=("Arial", 13), width=15)
        type_options.pack(side=tk.LEFT, padx=5)
        type_options.bind("<<ComboboxSelected>>", lambda e: self.display_pie_chart())

        self.selected_date = DateEntry(filter_options_frame, date_pattern='yyyy-mm-dd',
                                 font=("Arial", 13), background='darkblue',
                                 foreground='white', borderwidth=2, width=15,
                                 maxdate=datetime.today().date())
        self.selected_date.pack(side=tk.LEFT, padx=5)
        self.selected_date.bind("<<DateEntrySelected>>", lambda e: self.display_pie_chart())

        self.display_pie_chart()

    def display_pie_chart(self):
        for widget in self.main_area.winfo_children():
            if widget not in (self.main_area.winfo_children()[0],):
                widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4), facecolor='lightgray')
        data_group = defaultdict(float)
        selected_date = self.selected_date.get_date()
        selected_type = self.chart_type_var.get()

        income_cats = ["Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        expense_cats = ["Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other"]
        target_categories = income_cats if selected_type == "Income" else expense_cats

        for record in self.records:
            try:
                record_date = datetime.strptime(record['Date'], "%Y-%m-%d").date()
                if record_date == selected_date and record['Sub-Category'] in target_categories:
                    data_group[record['Sub-Category']] += float(record['Amount'])
            except ValueError:
                continue

        if not data_group:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
        else:
            labels = list(data_group.keys())
            sizes = list(data_group.values())
            colors = [COLOR_MAP.get(label, '#dddddd') for label in labels]
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.main_area)
        canvas.draw()
        canvas.get_tk_widget().pack()
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
        self.clear_main_area()
        self.build_record_form("Edit Expense Data" if edit else "Record Expense Data", edit)

    def show_modify_page(self):
        if self.editing_index is None:
            messagebox.showerror("Error", "No record selected to modify. Please use 'Show Data' to select a record.")
            return
        self.clear_main_area()
        tk.Label(self.main_area, font=('Arial', 20), bg="lightgray").pack(pady=10)
        self.build_record_form("Modify Expense Record", edit=True)

    def build_record_form(self, title, edit=False):
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
        self.subcategory_combo = ttk.Combobox(form_frame, textvariable=self.subcategory_var,
                                              state="readonly", font=('Arial', 13), width=38)
        self.subcategory_combo.grid(row=2, column=1, sticky="w", pady=10)

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

        tk.Button(button_frame, text="Back", command=self.show_records_table,
                  bg="green", fg="white", font=("Arial", 14), width=15).pack(side=tk.LEFT, padx=20)

        if edit and self.editing_index is not None:
            record = self.records[self.editing_index]
            self.date_entry.set_date(record['Date'])
            self.category_var.set(record['Category'])
            self.update_subcategories(None)
            self.subcategory_var.set(record['Sub-Category'])
            self.amount_entry.insert(0, record['Amount'])
            self.remarks_entry.insert(0, record['Remarks'])

    def update_subcategories(self, event):
        income_categories = ["Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        expense_categories = ["Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other"]
        if self.category_var.get() == "Income":
            self.subcategory_combo['values'] = income_categories
        else:
            self.subcategory_combo['values'] = expense_categories
        self.subcategory_var.set("")

    def get_form_data(self):
        date = self.date_entry.get()
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        amount = self.amount_entry.get().strip()
        remarks = self.remarks_entry.get().strip()

        if not (category and subcategory and amount):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return None

        return {
            'Date': date,
            'Category': category,
            'Sub-Category': subcategory,
            'Amount': amount,
            'Remarks': remarks
        }

    def save_record(self):
        record = self.get_form_data()
        if not record:
            return
        self.records.append(record)
        self.save_data()
        messagebox.showinfo("Success", "Record added successfully!")
        self.show_records_table()

    def update_record(self):
        if self.editing_index is None:
            messagebox.showerror("Error", "No record selected to update. Please select a record from 'Show Data' first.")
            return

        record = self.get_form_data()
        if not record:
            return

        self.records[self.editing_index] = record
        self.save_data()
        messagebox.showinfo("Success", "Record updated successfully!")
        self.editing_index = None
        self.show_records_table()

    def show_records_table(self):
        self.clear_main_area()
        tk.Label(self.main_area, text="Expense Records", font=('Arial', 20), bg="lightgray").pack(pady=10)

        columns = FIELDS
        self.tree = ttk.Treeview(self.main_area, columns=columns, show='headings')
        for field in FIELDS:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=130)

        for index, record in enumerate(self.records):
            self.tree.insert('', tk.END, iid=index, values=[record[field] for field in FIELDS])

        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_record_select)

        button_frame = tk.Frame(self.main_area, bg="lightgray")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Edit Selected", command=self.edit_selected_record,
                  bg="dodgerblue", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Delete Selected", command=self.delete_selected_record,
                  bg="red", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Back to Dashboard", command=self.show_dashboard,
                  bg="green", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

    def on_record_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.editing_index = int(selected[0])

    def edit_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to edit.")
            return
        self.editing_index = int(selected[0])
        self.show_modify_page()

    def delete_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        index = int(selected[0])
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if confirm:
            del self.records[index]
            self.save_data()
            self.show_records_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()








































'''
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from datetime import datetime

DATA_FILE = 'data.json'
FIELDS = ['Date', 'Category', 'Sub-Category', 'Amount', 'Remarks']

COLOR_MAP = {
    "Food": "#FF9999", "Rent": "#FFB266", "Mobile Recharge": "#FFFF99",
    "Health": "#99FF99", "Travel": "#99CCFF", "Fuel": "#CC99FF", "Shopping": "#FF66B2", "Other": "#B2B2B2",
    "Allowance": "#7FC97F", "Salary": "#BEAED4", "Profit": "#FDC086", "Cash": "#FFFF99", "Bonus": "#386CB0", "Other Income": "#F0027F"
}

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1000x700")
        self.root.configure(bg="black")
        self.show_splash_screen()

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
            welcome_label.pack(pady=200)

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
            start_button.pack(pady=100)

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
        self.show_dashboard()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.records, f, indent=2)

    def create_top_buttons(self):
        top_frame = tk.Frame(self.root, bg="lightgray")
        top_frame.pack(side=tk.TOP, fill=tk.X)
        buttons = [("Record Data", self.show_add_record_form),
                   ("Show Data", self.show_records_table),
                   ("Modify Data", self.show_modify_page)]
        for name, command in buttons:
            tk.Button(top_frame, text=name, command=command, font=("Arial", 14), height=2,
                      bd=0, bg="white", activebackground="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=5)

    def create_bottom_nav(self):
        bottom_frame = tk.Frame(self.root, bg="lightgray")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        for item in ["Accounts", "Categories", "Records", "Reports", "Settings"]:
            tk.Button(bottom_frame, text=item, font=("Arial", 12), height=2, bd=0,
                      bg="white", activebackground="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=5)

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def create_main_area(self):
        self.main_area = tk.Frame(self.root, bg="lightgray")
        self.main_area.pack(expand=True, fill=tk.BOTH)

    def show_dashboard(self):
        self.clear_main_area()
        filter_options_frame = tk.Frame(self.main_area, bg="lightgray")
        filter_options_frame.pack(pady=10)

        self.chart_type_var = tk.StringVar(value="Expense")
        type_options = ttk.Combobox(filter_options_frame, textvariable=self.chart_type_var,
                                     values=["Income", "Expense"], state="readonly",
                                     font=("Arial", 13), width=15)
        type_options.pack(side=tk.LEFT, padx=5)
        type_options.bind("<<ComboboxSelected>>", lambda e: self.display_pie_chart())

        self.selected_date = DateEntry(filter_options_frame, date_pattern='yyyy-mm-dd',
                                 font=("Arial", 13), background='darkblue',
                                 foreground='white', borderwidth=2, width=15,
                                 maxdate=datetime.today().date())
        self.selected_date.pack(side=tk.LEFT, padx=5)
        self.selected_date.bind("<<DateEntrySelected>>", lambda e: self.display_pie_chart())

        self.display_pie_chart()

    def display_pie_chart(self):
        for widget in self.main_area.winfo_children():
            if widget not in (self.main_area.winfo_children()[0],):
                widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4), facecolor='lightgray')
        data_group = defaultdict(float)
        selected_date = self.selected_date.get_date()
        selected_type = self.chart_type_var.get()

        income_cats = ["Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        expense_cats = ["Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other"]
        target_categories = income_cats if selected_type == "Income" else expense_cats

        for record in self.records:
            try:
                record_date = datetime.strptime(record['Date'], "%Y-%m-%d").date()
                if record_date == selected_date and record['Sub-Category'] in target_categories:
                    data_group[record['Sub-Category']] += float(record['Amount'])
            except ValueError:
                continue

        if not data_group:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
        else:
            labels = list(data_group.keys())
            sizes = list(data_group.values())
            colors = [COLOR_MAP.get(label, '#dddddd') for label in labels]
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.main_area)
        canvas.draw()
        canvas.get_tk_widget().pack()
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
        self.clear_main_area()
        self.build_record_form("Edit Expense Data" if edit else "Record Expense Data", edit)

    def show_modify_page(self):
        if self.editing_index is None:
            messagebox.showerror("Error", "No record selected to modify. Please use 'Show Data' to select a record.")
            return
        self.clear_main_area()
        tk.Label(self.main_area, font=('Arial', 20), bg="lightgray").pack(pady=10)
        self.build_record_form("Modify Expense Record", edit=True)

    def build_record_form(self, title, edit=False):
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
        self.subcategory_combo = ttk.Combobox(form_frame, textvariable=self.subcategory_var,
                                              state="readonly", font=('Arial', 13), width=38)
        self.subcategory_combo.grid(row=2, column=1, sticky="w", pady=10)

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

        tk.Button(button_frame, text="Back", command=self.show_records_table,
                  bg="green", fg="white", font=("Arial", 14), width=15).pack(side=tk.LEFT, padx=20)

        if edit and self.editing_index is not None:
            record = self.records[self.editing_index]
            self.date_entry.set_date(record['Date'])
            self.category_var.set(record['Category'])
            self.update_subcategories(None)
            self.subcategory_var.set(record['Sub-Category'])
            self.amount_entry.insert(0, record['Amount'])
            self.remarks_entry.insert(0, record['Remarks'])

    def update_subcategories(self, event):
        income_categories = ["Allowance", "Salary", "Profit", "Cash", "Bonus", "Other Income"]
        expense_categories = ["Food", "Rent", "Mobile Recharge", "Health", "Travel", "Fuel", "Shopping", "Other"]
        if self.category_var.get() == "Income":
            self.subcategory_combo['values'] = income_categories
        else:
            self.subcategory_combo['values'] = expense_categories
        self.subcategory_var.set("")

    def get_form_data(self):
        date = self.date_entry.get()
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        amount = self.amount_entry.get().strip()
        remarks = self.remarks_entry.get().strip()

        if not (category and subcategory and amount):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return None

        return {
            'Date': date,
            'Category': category,
            'Sub-Category': subcategory,
            'Amount': amount,
            'Remarks': remarks
        }

    def save_record(self):
        record = self.get_form_data()
        if not record:
            return
        self.records.append(record)
        self.save_data()
        messagebox.showinfo("Success", "Record added successfully!")
        self.show_records_table()

    def update_record(self):
        if self.editing_index is None:
            messagebox.showerror("Error", "No record selected to update. Please select a record from 'Show Data' first.")
            return

        record = self.get_form_data()
        if not record:
            return

        self.records[self.editing_index] = record
        self.save_data()
        messagebox.showinfo("Success", "Record updated successfully!")
        self.editing_index = None
        self.show_records_table()

    def show_records_table(self):
        self.clear_main_area()
        tk.Label(self.main_area, text="Expense Records", font=('Arial', 20), bg="lightgray").pack(pady=10)

        columns = FIELDS
        self.tree = ttk.Treeview(self.main_area, columns=columns, show='headings')
        for field in FIELDS:
            self.tree.heading(field, text=field)
            self.tree.column(field, width=130)

        for index, record in enumerate(self.records):
            self.tree.insert('', tk.END, iid=index, values=[record[field] for field in FIELDS])

        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_record_select)

        button_frame = tk.Frame(self.main_area, bg="lightgray")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Edit Selected", command=self.edit_selected_record,
                  bg="dodgerblue", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Delete Selected", command=self.delete_selected_record,
                  bg="red", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Back to Dashboard", command=self.show_dashboard,
                  bg="green", fg="white", font=("Arial", 15), width=20).pack(side=tk.LEFT, padx=10)

    def on_record_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.editing_index = int(selected[0])

    def edit_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to edit.")
            return
        self.editing_index = int(selected[0])
        self.show_modify_page()

    def delete_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        index = int(selected[0])
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if confirm:
            del self.records[index]
            self.save_data()
            self.show_records_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()































'''
'''
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
        welcome_label.pack(pady=200)

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
        start_button.pack(pady=100)
'''
