import customtkinter as ctk
from tkinter import messagebox

class DigitalPersonasTab(ctk.CTkFrame):
    def __init__(self, parent, client):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.client = client
        self.personas = []
        self.selected_persona = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Personas List Panel ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.list_frame.grid_rowconfigure(1, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        list_label = ctk.CTkLabel(self.list_frame, text="Saved Personas", font=ctk.CTkFont(size=16, weight="bold"))
        list_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.personas_listbox = ctk.CTkScrollableFrame(self.list_frame)
        self.personas_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Details/Create Panel ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.form_frame.grid_columnconfigure(1, weight=1)

        form_label = ctk.CTkLabel(self.form_frame, text="Persona Details", font=ctk.CTkFont(size=16, weight="bold"))
        form_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Details Display
        self.details_text = ctk.CTkTextbox(self.form_frame, state="disabled", height=200)
        self.details_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Controls
        self.generate_button = ctk.CTkButton(self.form_frame, text="Generate New Persona")
        self.generate_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.create_phone_var = ctk.BooleanVar()
        self.create_phone_checkbox = ctk.CTkCheckBox(self.form_frame, text="Create Phone Number", variable=self.create_phone_var)
        self.create_phone_checkbox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.generate_button.configure(command=self.generate_persona)
        self.delete_button.configure(command=self.delete_persona, state="disabled")

        self.refresh_personas()

    def refresh_personas(self):
        if not self.client:
            return

        for widget in self.personas_listbox.winfo_children():
            widget.destroy()

        self.personas = self.client.personas.list()

        if not self.personas:
            label = ctk.CTkLabel(self.personas_listbox, text="No personas found.")
            label.pack()
            return

        for persona in self.personas:
            # Using a lambda with a default argument to capture the current persona
            persona_button = ctk.CTkButton(self.personas_listbox,
                                           text=f"{persona.first_name} {persona.last_name}",
                                           fg_color="transparent",
                                           command=lambda p=persona: self.select_persona(p))
            persona_button.pack(fill="x", padx=5, pady=2)

    def select_persona(self, persona):
        self.selected_persona = persona
        self.delete_button.configure(state="normal")

        details = (
            f"ID: {persona.id}\n"
            f"Name: {persona.first_name} {persona.last_name}\n"
            f"Email: {persona.email}\n"
            f"Phone: {persona.phone_number or 'N/A'}\n"
        )

        self.details_text.configure(state="normal")
        self.details_text.delete("0.0", "end")
        self.details_text.insert("0.0", details)
        self.details_text.configure(state="disabled")

    def generate_persona(self):
        if not self.client:
            messagebox.showerror("Error", "Client not initialized. Check API Key.")
            return

        try:
            create_phone = self.create_phone_var.get()
            new_persona = self.client.personas.create(create_phone_number=create_phone)
            messagebox.showinfo("Success", f"Created new persona: {new_persona.first_name} {new_persona.last_name}")
            self.refresh_personas()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create persona:\n{e}")

    def delete_persona(self):
        if not self.selected_persona:
            messagebox.showerror("Error", "No persona selected to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {self.selected_persona.first_name}?"):
            return

        try:
            self.client.personas.delete(self.selected_persona.id)
            messagebox.showinfo("Success", "Persona deleted successfully.")
            self.selected_persona = None
            self.delete_button.configure(state="disabled")
            self.details_text.configure(state="normal")
            self.details_text.delete("0.0", "end")
            self.details_text.configure(state="disabled")
            self.refresh_personas()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete persona:\n{e}")
