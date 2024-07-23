import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from pandastable import Table
import webbrowser
import csv
from dateutil import parser

class CleanupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Patrick's Cleanup Tool")
        self.geometry("800x1150")
        self.data = None
        self.action_data = None
        self.create_widgets()

    def create_widgets(self):
        # File selection
        self.file_frame = tk.Frame(self)
        self.file_frame.pack(pady=10)
        self.file_label = tk.Label(self.file_frame, text="Select CSV file:")
        self.file_label.pack(side=tk.LEFT)
        self.file_entry = tk.Entry(self.file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        self.file_button = tk.Button(self.file_frame, text="Browse", command=self.load_file)
        self.file_button.pack(side=tk.LEFT)

        # Instruction text
        self.instruction_label = tk.Label(self, text="Hier onder kun je aangeven waar je post minimaal aan moet voldoen om niet in aanmerking te komen voor verwijdering")
        self.instruction_label.pack(pady=10)

        # Thresholds
        self.threshold_frame = tk.Frame(self)
        self.threshold_frame.pack(pady=10)
        thresholds = [
            ("Sessions", 1000),
            ("Views", 1000),
            ("Clicks", 50),
            ("Impressions", 500),
            ("Average position", 19),
            ("Backlinks", 1),
            ("Word Count", 500),
            ("Older than (YYYY-MM-DD)", "2023-01-01")
        ]
        self.threshold_entries = {}
        self.threshold_checks = {}
        for i, (label, default) in enumerate(thresholds):
            tk.Label(self.threshold_frame, text=f"{label}:").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry = tk.Entry(self.threshold_frame, width=10)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=5, pady=2)
            check_var = tk.BooleanVar(value=True)
            check_button = tk.Checkbutton(self.threshold_frame, variable=check_var)
            check_button.grid(row=i, column=2, padx=5, pady=2)
            self.threshold_entries[label] = entry
            self.threshold_checks[label] = check_var

        # Output mode selection
        self.output_frame = tk.Frame(self)
        self.output_frame.pack(pady=10)

        self.output_mode = tk.StringVar(value="all")
        tk.Radiobutton(self.output_frame, text="Show all URLs", variable=self.output_mode, value="all").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(self.output_frame, text="Show only URLs with actions", variable=self.output_mode, value="action").pack(side=tk.LEFT, padx=5)

        # Process button
        self.process_button = tk.Button(self, text="Process Data", command=self.process_data)
        self.process_button.pack(pady=10)

        # Reset button
        self.reset_button = tk.Button(self, text="Reset", command=self.reset)
        self.reset_button.pack(pady=10)

        # Table
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Information text and hyperlink
        link_text = "Maak een kopie van het template hieronder en vul deze met jouw data.\nVervolgens kun je hem hierboven uploaden en zal de tool aan de hand van de door jou ingestelde criteria de URLs die wegkunnen markeren"
        self.link_label = tk.Label(self, text=link_text, justify=tk.CENTER, wraplength=780)
        self.link_label.pack(pady=10)
        self.template_link = tk.Label(self, text="het template hieronder", fg="blue", cursor="hand2")
        self.template_link.pack()
        self.template_link.bind("<Button-1>", lambda e: self.open_link("https://docs.google.com/spreadsheets/d/1GtaLaXO62Rf8Xo2gNiw6wkAXrHoE-bBJr8Uf3_e8lNw/edit?usp=sharing"))

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def process_data(self):
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a CSV file.")
            return

        try:
            # Read the first few lines to detect the delimiter
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample, delimiters=[',', ';'])
                delimiter = dialect.delimiter

            # Load the CSV file with the detected delimiter
            self.data = pd.read_csv(file_path, delimiter=delimiter)

            required_columns = ['Sessions', 'Views', 'Clicks', 'Impressions', 'Average position', 'Ahrefs Backlinks - Exact', 'Word Count', 'Laatste wijziging']
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            if missing_columns:
                messagebox.showerror("Error", f"Missing columns in CSV: {', '.join(missing_columns)}")
                return

            # Convert 'Average position' to float
            self.data['Average position'] = self.data['Average position'].astype(float)

            # Ensure 'Laatste wijziging' is treated as string
            self.data['Laatste wijziging'] = self.data['Laatste wijziging'].astype(str)

            # Convert 'Laatste wijziging' to datetime, handling multiple formats
            def parse_date(date_string):
                try:
                    return parser.parse(date_string).date()
                except (ValueError, TypeError):
                    return None

            self.data['Laatste wijziging'] = self.data['Laatste wijziging'].apply(parse_date)

            deletion_criteria = {
                key: float(self.threshold_entries[key].get())
                for key in self.threshold_entries
                if key != "Older than (YYYY-MM-DD)" and self.threshold_checks[key].get()
            }
            if self.threshold_checks["Older than (YYYY-MM-DD)"].get():
                older_than_date = pd.to_datetime(self.threshold_entries["Older than (YYYY-MM-DD)"].get()).date()
            else:
                older_than_date = None

            def should_delete(row):
                conditions = [
                    row['Sessions'] < deletion_criteria['Sessions'] if 'Sessions' in deletion_criteria else True,
                    row['Views'] < deletion_criteria['Views'] if 'Views' in deletion_criteria else True,
                    row['Clicks'] < deletion_criteria['Clicks'] if 'Clicks' in deletion_criteria else True,
                    row['Impressions'] < deletion_criteria['Impressions'] if 'Impressions' in deletion_criteria else True,
                    row['Average position'] > deletion_criteria['Average position'] if 'Average position' in deletion_criteria else True,
                    row['Word Count'] < deletion_criteria['Word Count'] if 'Word Count' in deletion_criteria else True,
                    row['Laatste wijziging'] < older_than_date if older_than_date is not None and row['Laatste wijziging'] is not None else False
                ]
                return all(conditions)

            self.data['To Delete'] = self.data.apply(should_delete, axis=1)
            self.data['Backlinks controleren'] = (self.data['To Delete'] & (self.data['Ahrefs Backlinks - Exact'] > deletion_criteria.get('Backlinks', float('inf'))))
            self.data['Action'] = 'Geen actie'
            self.data.loc[self.data['To Delete'], 'Action'] = 'Verwijderen'
            self.data.loc[self.data['Backlinks controleren'], 'Action'] = 'Backlinks controleren'

            # Filter the data based on the selected output mode
            if self.output_mode.get() == "action":
                self.action_data = self.data[self.data['Action'] != 'Geen actie']
            else:
                self.action_data = self.data

            self.display_results()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process CSV file: {str(e)}")
            return

    def display_results(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if self.action_data.empty:
            tk.Label(self.table_frame, text="No URLs require action.").pack(pady=20)
        else:
            table = Table(self.table_frame, dataframe=self.action_data, showtoolbar=True, showstatusbar=True)
            table.show()

        save_button = tk.Button(self, text="Save Results", command=self.save_results)
        save_button.pack(pady=10)

    def save_results(self):
        if self.action_data is not None and not self.action_data.empty:
            output_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if output_file_path:
                self.action_data.to_csv(output_file_path, index=False, sep=',')
                messagebox.showinfo("Success", f"Results saved to {output_file_path}")
        else:
            messagebox.showinfo("Info", "No data to save.")

    def reset(self):
        for check_var in self.threshold_checks.values():
            check_var.set(True)
        self.output_mode.set("all")
        for widget in self.table_frame.winfo_children():
            widget.destroy()

    def open_link(self, url):
        webbrowser.open_new(url)

if __name__ == "__main__":
    app = CleanupApp()
    app.mainloop()
