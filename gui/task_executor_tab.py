import customtkinter as ctk
from tkinter import filedialog, messagebox

class TaskExecutorTab(ctk.CTkFrame):
    def __init__(self, parent, run_callback, stop_callback):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.run_callback = run_callback
        self.stop_callback = stop_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Main content
        self.grid_rowconfigure(1, weight=1) # Console output

        # --- Task Input Frame ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(2, weight=1)

        # Top bar with URL and controls
        self.top_bar_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.top_bar_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.top_bar_frame.grid_columnconfigure(1, weight=1)

        self.url_label = ctk.CTkLabel(self.top_bar_frame, text="URL (Optional):")
        self.url_label.grid(row=0, column=0, padx=(0, 5))
        self.url_entry = ctk.CTkEntry(self.top_bar_frame)
        self.url_entry.grid(row=0, column=1, sticky="ew")

        self.controls_frame = ctk.CTkFrame(self.top_bar_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=2, padx=(10, 0))

        self.run_button = ctk.CTkButton(self.controls_frame, text="Run", command=self.run_callback)
        self.run_button.pack(side="left", padx=5)
        self.stop_button = ctk.CTkButton(self.controls_frame, text="Stop", state="disabled", command=self.stop_callback)
        self.stop_button.pack(side="left", padx=5)
        self.pause_button = ctk.CTkButton(self.controls_frame, text="Pause", state="disabled")
        self.pause_button.pack(side="left", padx=5)

        self.export_button = ctk.CTkButton(self.top_bar_frame, text="Export Answer", width=120, command=self.export_answer)
        self.export_button.grid(row=0, column=3, padx=(10,0))

        # Task description text area
        self.task_description_label = ctk.CTkLabel(self.input_frame, text="Task Description:")
        self.task_description_label.grid(row=1, column=0, padx=10, pady=(10,0), sticky="w")
        self.task_description_entry = ctk.CTkTextbox(self.input_frame, font=("sans-serif", 14))
        self.task_description_entry.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # --- Console Output Frame ---
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.output_frame)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)

        self.console_output = ctk.CTkTextbox(self.output_frame, state="disabled", font=("monospace", 12))
        self.console_output.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    def get_task_details(self):
        return {
            "task": self.task_description_entry.get("0.0", "end-1c"),
            "url": self.url_entry.get()
        }

    def export_answer(self):
        content = self.console_output.get("0.0", "end-1c")
        if not content.strip():
            messagebox.showerror("Error", "There is no content to export.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export Answer",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Success", f"Answer successfully exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export answer:\n{e}")
