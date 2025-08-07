import customtkinter as ctk
import json
import os
from tkinter import messagebox

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")

        self._create_widgets()
        self.load_settings()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Dummy row to push content up

        # --- Settings Form ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="new")
        self.form_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(self.form_frame, text="Application Settings", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 20), sticky="w")

        # API Key
        api_key_label = ctk.CTkLabel(self.form_frame, text="Notte API Key:")
        api_key_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.api_key_var = ctk.StringVar()
        self.api_key_entry = ctk.CTkEntry(self.form_frame, textvariable=self.api_key_var, show="*")
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Theme
        theme_label = ctk.CTkLabel(self.form_frame, text="Theme:")
        theme_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.theme_var = ctk.StringVar()
        self.theme_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.theme_var,
                                            values=["System", "Light", "Dark"],
                                            command=self.change_theme)
        self.theme_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Default Browser
        default_browser_label = ctk.CTkLabel(self.form_frame, text="Default Browser:")
        default_browser_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.default_browser_var = ctk.StringVar()
        self.default_browser_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.default_browser_var,
                                                      values=["chromium", "firefox", "webkit"])
        self.default_browser_menu.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Log Level
        log_level_label = ctk.CTkLabel(self.form_frame, text="Log Level:")
        log_level_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.log_level_var = ctk.StringVar()
        self.log_level_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.log_level_var,
                                                values=["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_menu.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # Auto-save
        self.auto_save_var = ctk.BooleanVar()
        self.auto_save_checkbox = ctk.CTkCheckBox(self.form_frame, text="Auto-save preferences", variable=self.auto_save_var)
        self.auto_save_checkbox.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Save Button
        self.save_button = ctk.CTkButton(self.form_frame, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=6, column=1, padx=10, pady=(20, 10), sticky="e")

    def load_settings(self):
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            self.api_key_var.set(config.get("api_key", ""))
            self.theme_var.set(config.get("theme", "System"))
            self.default_browser_var.set(config.get("default_browser", "chromium"))
            self.log_level_var.set(config.get("log_level", "INFO"))
            self.auto_save_var.set(config.get("auto_save", True))

            # Apply theme on load
            self.change_theme(self.theme_var.get())

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not load config file: {e}. Using default settings.")
            # In a real app, might want to create a default config here
            pass

    def save_settings(self):
        config = {
            "api_key": self.api_key_var.get(),
            "theme": self.theme_var.get(),
            "default_browser": self.default_browser_var.get(),
            "log_level": self.log_level_var.get(),
            "auto_save": self.auto_save_var.get()
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")

    def change_theme(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)
