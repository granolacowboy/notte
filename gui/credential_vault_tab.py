import customtkinter as ctk
from tkinter import messagebox

class CredentialVaultTab(ctk.CTkFrame):
    def __init__(self, parent, client, vault):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.client = client
        self.vault = vault
        self.credentials = []
        self.selected_credential_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Credentials List Panel ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.list_frame.grid_rowconfigure(1, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        list_label = ctk.CTkLabel(self.list_frame, text="Stored Credentials", font=ctk.CTkFont(size=16, weight="bold"))
        list_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.credentials_listbox = ctk.CTkScrollableFrame(self.list_frame)
        self.credentials_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Add/Edit Panel ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.form_frame.grid_columnconfigure(1, weight=1)

        form_label = ctk.CTkLabel(self.form_frame, text="Add/Edit Credential", font=ctk.CTkFont(size=16, weight="bold"))
        form_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # URL
        url_label = ctk.CTkLabel(self.form_frame, text="URL:")
        url_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.url_entry = ctk.CTkEntry(self.form_frame)
        self.url_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Username
        username_label = ctk.CTkLabel(self.form_frame, text="Username:")
        username_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = ctk.CTkEntry(self.form_frame)
        self.username_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Password
        password_label = ctk.CTkLabel(self.form_frame, text="Password:")
        password_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = ctk.CTkEntry(self.form_frame, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        self.show_password_var = ctk.BooleanVar()
        self.show_password_checkbox = ctk.CTkCheckBox(self.form_frame, text="Show Password",
                                                      variable=self.show_password_var, command=self.toggle_password_visibility)
        self.show_password_checkbox.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # MFA Token
        mfa_label = ctk.CTkLabel(self.form_frame, text="MFA Token:")
        mfa_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.mfa_entry = ctk.CTkEntry(self.form_frame)
        self.mfa_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # Buttons
        self.button_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.button_frame.grid(row=6, column=1, padx=10, pady=10, sticky="e")

        self.add_button = ctk.CTkButton(self.button_frame, text="Add/Update", command=self.add_or_update_credential)
        self.add_button.pack(side="left", padx=5)
        self.delete_button = ctk.CTkButton(self.button_frame, text="Delete", fg_color="red", hover_color="darkred", command=self.delete_credential)
        self.delete_button.pack(side="left", padx=5)
        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear", fg_color="gray50", hover_color="gray40", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        self.refresh_credentials()

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def refresh_credentials(self):
        if not self.vault:
            return

        for widget in self.credentials_listbox.winfo_children():
            widget.destroy()

        self.credentials = self.vault.list_credentials()

        if not self.credentials:
            label = ctk.CTkLabel(self.credentials_listbox, text="No credentials in vault.")
            label.pack()
            return

        for cred in self.credentials:
            # Using a lambda with a default argument to capture the current cred
            cred_button = ctk.CTkButton(self.credentials_listbox,
                                        text=f"{cred.username}@{cred.url}",
                                        fg_color="transparent",
                                        command=lambda c=cred: self.select_credential(c))
            cred_button.pack(fill="x", padx=5, pady=2)

    def select_credential(self, credential):
        self.clear_form(clear_selection=False)
        self.selected_credential_id = credential.id

        self.url_entry.insert(0, credential.url)
        self.username_entry.insert(0, credential.username)
        self.password_entry.insert(0, credential.password)
        self.mfa_entry.insert(0, credential.totp_secret or "")

    def clear_form(self, clear_selection=True):
        if clear_selection:
            self.selected_credential_id = None
        self.url_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.mfa_entry.delete(0, "end")
        self.show_password_var.set(False)
        self.toggle_password_visibility()

    def add_or_update_credential(self):
        if not self.vault:
            messagebox.showerror("Error", "Vault not initialized. Please set API key in Settings.")
            return

        url = self.url_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        mfa = self.mfa_entry.get() or None

        if not url or not username or not password:
            messagebox.showerror("Error", "URL, Username, and Password are required.")
            return

        try:
            # If we are updating, we first delete the old one
            if self.selected_credential_id:
                self.vault.delete_credentials(credential_id=self.selected_credential_id)

            self.vault.add_credentials(url=url, username=username, password=password, totp_secret=mfa)
            messagebox.showinfo("Success", "Credential saved successfully.")
            self.clear_form()
            self.refresh_credentials()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credential:\n{e}")

    def delete_credential(self):
        if not self.selected_credential_id:
            messagebox.showerror("Error", "No credential selected to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this credential?"):
            return

        try:
            self.vault.delete_credentials(credential_id=self.selected_credential_id)
            messagebox.showinfo("Success", "Credential deleted successfully.")
            self.clear_form()
            self.refresh_credentials()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete credential:\n{e}")
