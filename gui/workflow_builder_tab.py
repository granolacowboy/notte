import customtkinter as ctk
import threading
import io
import contextlib
from tkinter import filedialog, messagebox
from utils.validators import is_safe_path, SAFE_BASE_DIR

class WorkflowBuilderTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Main paned window to split editor and output
        self.paned_window = ctk.CTkFrame(self, fg_color="transparent")
        self.paned_window.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.paned_window.grid_rowconfigure(0, weight=2) # Editor gets more space
        self.paned_window.grid_rowconfigure(1, weight=1) # Output gets less
        self.paned_window.grid_columnconfigure(0, weight=1)

        # --- Editor Frame ---
        self.editor_frame = ctk.CTkFrame(self.paned_window)
        self.editor_frame.grid(row=0, column=0, sticky="nsew")
        self.editor_frame.grid_rowconfigure(1, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        self.editor_toolbar = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        self.editor_toolbar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.run_button = ctk.CTkButton(self.editor_toolbar, text="Run", command=self.run_script)
        self.run_button.pack(side="left", padx=5)
        self.load_button = ctk.CTkButton(self.editor_toolbar, text="Load", command=self.load_script)
        self.load_button.pack(side="left", padx=5)
        self.save_button = ctk.CTkButton(self.editor_toolbar, text="Save", command=self.save_script)
        self.save_button.pack(side="left", padx=5)

        self.script_editor = ctk.CTkTextbox(self.editor_frame, font=("monospace", 13))
        self.script_editor.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.script_editor.insert("0.0", "# Your Notte workflow script here\n\n"
                                         "from notte_sdk import NotteClient\n\n"
                                         "# Note: The script will use the API key from Settings\n"
                                         "client = NotteClient()\n\n"
                                         "with client.Session(headless=False) as session:\n"
                                         "    session.goto('https://www.google.com')\n"
                                         "    print('Successfully navigated to Google!')\n")

        # --- Output Frame ---
        self.output_frame = ctk.CTkFrame(self.paned_window)
        self.output_frame.grid(row=1, column=0, sticky="nsew", pady=(10,0))
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.output_console = ctk.CTkTextbox(self.output_frame, font=("monospace", 12), state="disabled")
        self.output_console.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def run_script(self):
        self.output_console.configure(state="normal")
        self.output_console.delete("0.0", "end")
        self.output_console.insert("0.0", "Running script...\n\n")
        self.output_console.configure(state="disabled")

        script_content = self.script_editor.get("0.0", "end")

        thread = threading.Thread(target=self._execute_script_worker, args=(script_content,))
        thread.daemon = True
        thread.start()

    def _execute_script_worker(self, script_content):
        # Redirect stdout to capture print statements
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stdout_capture):
            try:
                # We need to provide the NotteClient with the API key from config
                # A better implementation would inject a pre-configured client
                import os, json
                from notte_sdk import NotteClient
                config_path = os.path.join(os.path.dirname(__file__), "config.json")
                with open(config_path, 'r') as f:
                    config = json.load(f)
                api_key = config.get("api_key")

                # Make the client available in the script's scope
                exec_globals = {
                    "NotteClient": lambda: NotteClient(api_key=api_key)
                }
                exec(script_content, exec_globals)

            except Exception as e:
                print(f"An error occurred:\n{e}")

        output = stdout_capture.getvalue()
        self.after(0, self.update_output, output)

    def update_output(self, output):
        self.output_console.configure(state="normal")
        self.output_console.insert("end", output)
        self.output_console.configure(state="disabled")

    def load_script(self):
        filepath = filedialog.askopenfilename(
            title="Open Workflow Script",
            initialdir=SAFE_BASE_DIR,
            filetypes=(("Python files", "*.py"), ("All files", "*.*"))
        )
        if not filepath:
            return

        if not is_safe_path(filepath):
            messagebox.showerror("Security Error", "Cannot load files from outside the allowed user data directory.")
            return

        try:
            with open(filepath, 'r') as f:
                content = f.read()
            self.script_editor.delete("0.0", "end")
            self.script_editor.insert("0.0", content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load script:\n{e}")

    def save_script(self):
        filepath = filedialog.asksaveasfilename(
            title="Save Workflow Script",
            initialdir=SAFE_BASE_DIR,
            defaultextension=".py",
            filetypes=(("Python files", "*.py"), ("All files", "*.*"))
        )
        if not filepath:
            return

        if not is_safe_path(filepath):
            messagebox.showerror("Security Error", "Cannot save files outside the allowed user data directory.")
            return

        try:
            with open(filepath, 'w') as f:
                f.write(self.script_editor.get("0.0", "end"))
            messagebox.showinfo("Success", f"Script saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save script:\n{e}")
