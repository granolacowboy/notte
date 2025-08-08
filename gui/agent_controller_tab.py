import customtkinter as ctk

class AgentControllerTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Agent Configuration Panel ---
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.config_frame.grid_columnconfigure(1, weight=1)

        config_label = ctk.CTkLabel(self.config_frame, text="Agent Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        config_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Reasoning Model
        model_label = ctk.CTkLabel(self.config_frame, text="Reasoning Model:")
        model_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.model_var = ctk.StringVar(value="gemini/gemini-2.5-flash")
        self.model_dropdown = ctk.CTkComboBox(self.config_frame,
                                              values=["gemini/gemini-2.5-flash", "gemini/gemini-2.5", "openai/gpt-4o"],
                                              variable=self.model_var)
        self.model_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Max Steps
        max_steps_label = ctk.CTkLabel(self.config_frame, text="Max Steps (1-100):")
        max_steps_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.max_steps_var = ctk.IntVar(value=30)
        self.max_steps_slider = ctk.CTkSlider(self.config_frame, from_=1, to=100, number_of_steps=99,
                                              variable=self.max_steps_var)
        self.max_steps_slider.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Attachments
        self.attach_vault_var = ctk.BooleanVar()
        self.attach_vault_checkbox = ctk.CTkCheckBox(self.config_frame, text="Attach Vault", variable=self.attach_vault_var)
        self.attach_vault_checkbox.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.attach_persona_var = ctk.BooleanVar()
        self.attach_persona_checkbox = ctk.CTkCheckBox(self.config_frame, text="Attach Persona", variable=self.attach_persona_var)
        self.attach_persona_checkbox.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.attach_files_var = ctk.BooleanVar()
        self.attach_files_checkbox = ctk.CTkCheckBox(self.config_frame, text="Attach File Storage", variable=self.attach_files_var)
        self.attach_files_checkbox.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        # --- Agent Status Panel ---
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.status_frame.grid_rowconfigure(1, weight=1) # Thoughts
        self.status_frame.grid_rowconfigure(3, weight=1) # History
        self.status_frame.grid_columnconfigure(0, weight=1)

        status_label = ctk.CTkLabel(self.status_frame, text="Agent Status", font=ctk.CTkFont(size=16, weight="bold"))
        status_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Thoughts
        thoughts_label = ctk.CTkLabel(self.status_frame, text="Thoughts:")
        thoughts_label.grid(row=1, column=0, padx=10, pady=(5,0), sticky="sw")
        self.thoughts_text = ctk.CTkTextbox(self.status_frame, state="disabled", font=("sans-serif", 13))
        self.thoughts_text.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # Action History
        history_label = ctk.CTkLabel(self.status_frame, text="Action History:")
        history_label.grid(row=3, column=0, padx=10, pady=(5,0), sticky="sw")
        self.history_text = ctk.CTkTextbox(self.status_frame, state="disabled", font=("monospace", 12))
        self.history_text.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

        # Screenshot (placeholder)
        screenshot_label = ctk.CTkLabel(self.config_frame, text="Screenshot:")
        screenshot_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.screenshot_frame = ctk.CTkFrame(self.config_frame, border_width=1, fg_color="gray20")
        self.screenshot_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.config_frame.grid_rowconfigure(7, weight=1)

    def get_agent_config(self):
        return {
            "reasoning_model": self.model_var.get(),
            "max_steps": self.max_steps_var.get(),
            "attach_vault": self.attach_vault_var.get(),
            "attach_persona": self.attach_persona_var.get(),
            "attach_files": self.attach_files_var.get(),
        }
