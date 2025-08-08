import customtkinter as ctk
from tkinter import messagebox
import types

class DataExtractionTab(ctk.CTkFrame):
    def __init__(self, parent, scrape_callback):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.scrape_callback = scrape_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- Configuration Panel ---
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.config_frame.grid_columnconfigure(1, weight=1)
        self.config_frame.grid_rowconfigure(4, weight=1) # Pydantic model editor

        config_label = ctk.CTkLabel(self.config_frame, text="Scraping Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        config_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # URL Input
        url_label = ctk.CTkLabel(self.config_frame, text="URL:")
        url_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.url_entry = ctk.CTkEntry(self.config_frame)
        self.url_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Toggles
        self.scrape_links_var = ctk.BooleanVar()
        self.scrape_links_checkbox = ctk.CTkCheckBox(self.config_frame, text="Scrape Links", variable=self.scrape_links_var)
        self.scrape_links_checkbox.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.main_content_var = ctk.BooleanVar()
        self.main_content_checkbox = ctk.CTkCheckBox(self.config_frame, text="Only Main Content", variable=self.main_content_var)
        self.main_content_checkbox.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Custom Instructions
        instructions_label = ctk.CTkLabel(self.config_frame, text="Custom Instructions:")
        instructions_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        self.instructions_text = ctk.CTkTextbox(self.config_frame, height=100)
        self.instructions_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Pydantic Model
        pydantic_label = ctk.CTkLabel(self.config_frame, text="Pydantic Model for Structured Output:")
        pydantic_label.grid(row=5, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        self.pydantic_text = ctk.CTkTextbox(self.config_frame, height=150, font=("monospace", 12))
        self.pydantic_text.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.config_frame.grid_rowconfigure(6, weight=1)

        # Scrape Button
        self.scrape_button = ctk.CTkButton(self.config_frame, text="Scrape Data", command=self.scrape_callback)
        self.scrape_button.grid(row=7, column=1, padx=10, pady=10, sticky="e")

    def get_scrape_config(self):
        config = {
            "url": self.url_entry.get(),
            "scrape_links": self.scrape_links_var.get(),
            "only_main_content": self.main_content_var.get(),
            "instructions": self.instructions_text.get("0.0", "end-1c"),
        }

        pydantic_code = self.pydantic_text.get("0.0", "end-1c")
        if pydantic_code.strip():
            try:
                # This is a simplified and somewhat risky way to get the Pydantic model
                # It executes the code provided by the user.
                module = types.ModuleType("pydantic_model")
                exec(pydantic_code, module.__dict__)

                # Find the Pydantic model class in the executed code
                # Assumes there's only one BaseModel subclass defined.
                from pydantic import BaseModel
                model = None
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
                        model = obj
                        break

                if model:
                    config["response_format"] = model
                else:
                    messagebox.showwarning("Warning", "Could not find a Pydantic model in the provided code. Proceeding without structured output.")

            except Exception as e:
                messagebox.showerror("Pydantic Model Error", f"Error compiling Pydantic model:\n{e}")
                return None # Indicate failure

        return config

        # --- Result Display Panel ---
        self.result_frame = ctk.CTkFrame(self)
        self.result_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.result_frame.grid_rowconfigure(1, weight=1) # Result text
        self.result_frame.grid_rowconfigure(3, weight=1) # Batch queue
        self.result_frame.grid_columnconfigure(0, weight=1)

        result_label = ctk.CTkLabel(self.result_frame, text="Extracted Data", font=ctk.CTkFont(size=16, weight="bold"))
        result_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.export_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.export_frame.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.export_json_button = ctk.CTkButton(self.export_frame, text="Export JSON", width=100, command=lambda: self.export_data("json"))
        self.export_json_button.pack(side="left", padx=5)
        self.export_csv_button = ctk.CTkButton(self.export_frame, text="Export CSV", width=100, command=lambda: self.export_data("csv"))
        self.export_csv_button.pack(side="left", padx=5)
        self.export_excel_button = ctk.CTkButton(self.export_frame, text="Export Excel", width=100, command=lambda: self.export_data("excel"))
        self.export_excel_button.pack(side="left", padx=5)

        self.result_text = ctk.CTkTextbox(self.result_frame, state="disabled", font=("monospace", 12))
        self.result_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Batch Processing ---
        batch_label = ctk.CTkLabel(self.result_frame, text="Batch Processing", font=ctk.CTkFont(size=16, weight="bold"))
        batch_label.grid(row=2, column=0, padx=10, pady=(20, 10), sticky="w")

        self.import_csv_button = ctk.CTkButton(self.result_frame, text="Import URLs from CSV", command=self.import_csv)
        self.import_csv_button.grid(row=2, column=0, padx=10, pady=(20,10), sticky="e")

        self.batch_queue_frame = ctk.CTkScrollableFrame(self.result_frame, label_text="URL Queue")
        self.batch_queue_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.url_queue = []

    def import_csv(self):
        from tkinter import filedialog
        import csv

        filepath = filedialog.askopenfilename(
            title="Import URLs from CSV",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                self.url_queue = [row[0] for row in reader if row]

            # Clear existing queue UI
            for widget in self.batch_queue_frame.winfo_children():
                widget.destroy()

            # Populate UI
            if not self.url_queue:
                label = ctk.CTkLabel(self.batch_queue_frame, text="No URLs found in CSV.")
                label.pack()
            else:
                for url in self.url_queue:
                    label = ctk.CTkLabel(self.batch_queue_frame, text=url)
                    label.pack(anchor="w")

                self.url_entry.delete(0, 'end')
                self.url_entry.insert(0, f"{len(self.url_queue)} URLs loaded for batch processing.")


        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV:\n{e}")

    def get_batch_queue(self):
        return self.url_queue

    def export_data(self, format):
        content = self.result_text.get("0.0", "end-1c")
        if not content.strip():
            messagebox.showerror("Error", "There is no data to export.")
            return

        if format == "json":
            file_ext = ".json"
            file_types = [("JSON files", "*.json")]
        elif format == "csv":
            file_ext = ".csv"
            file_types = [("CSV files", "*.csv")]
        elif format == "excel":
            file_ext = ".xlsx"
            file_types = [("Excel files", "*.xlsx")]
        else:
            return

        filepath = filedialog.asksaveasfilename(
            title=f"Export Data as {format.upper()}",
            defaultextension=file_ext,
            filetypes=file_types
        )
        if not filepath:
            return

        try:
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                import pandas as pd
                import json
                try:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        # Handle nested structures if possible, simple case for now
                        if len(data.keys()) == 1:
                            key = list(data.keys())[0]
                            df = pd.DataFrame(data[key])
                        else:
                            df = pd.DataFrame([data])
                    elif isinstance(data, list):
                        df = pd.DataFrame(data)
                    else:
                        raise ValueError("JSON content is not a list of objects or a single object.")

                    if format == "csv":
                        df.to_csv(filepath, index=False)
                    elif format == "excel":
                        df.to_excel(filepath, index=False)

                except (json.JSONDecodeError, ValueError) as e:
                    raise ValueError(f"Could not parse data for {format.upper()} export. Ensure data is valid JSON representing a list of objects.\n\nError: {e}")

            messagebox.showinfo("Success", f"Data successfully exported to {filepath}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{e}")
