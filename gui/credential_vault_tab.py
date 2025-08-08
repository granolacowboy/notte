import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
from utils.validators import is_valid_url, is_valid_input
import json
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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

        self.list_toolbar = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        self.list_toolbar.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.import_button = ctk.CTkButton(self.list_toolbar, text="Import", width=80, command=self.import_vault)
        self.import_button.pack(side="left", padx=5)
        self.export_button = ctk.CTkButton(self.list_toolbar, text="Export", width=80, command=self.export_vault)
        self.export_button.pack(side="left", padx=5)

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

        if not is_valid_url(url):
            messagebox.showerror("Invalid Input", "Please enter a valid and secure URL (http/https). Internal or local URLs are not allowed.")
            return

        if not is_valid_input(username, max_length=100):
            messagebox.showerror("Invalid Input", "Username contains invalid characters or is too long.")
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

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def export_vault(self):
        if not self.credentials:
            messagebox.showerror("Error", "There are no credentials to export.")
            return

        password = simpledialog.askstring("Password", "Enter a password to encrypt the vault:", show='*')
        if not password:
            messagebox.showwarning("Cancelled", "Export cancelled.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export Vault",
            defaultextension=".nve", # Notte Vault Encrypted
            filetypes=(("Notte Vault File", "*.nve"), ("All files", "*.*"))
        )
        if not filepath:
            return

        try:
            # Serialize credentials to JSON
            creds_to_export = [cred.model_dump() for cred in self.credentials]
            json_data = json.dumps(creds_to_export).encode('utf-8')

            # Generate a salt and derive key
            salt = os.urandom(16)
            key = self._derive_key(password, salt)

            # Encrypt the data
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(json_data)

            # Save salt + encrypted data to file
            with open(filepath, 'wb') as f:
                f.write(salt)
                f.write(encrypted_data)

            messagebox.showinfo("Success", f"Vault successfully exported to {filepath}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export vault:\n{e}")

    def import_vault(self):
        if not self.vault:
            messagebox.showerror("Error", "Vault not initialized. Please set API key in Settings.")
            return

        filepath = filedialog.askopenfilename(
            title="Import Vault",
            filetypes=(("Notte Vault File", "*.nve"), ("All files", "*.*"))
        )
        if not filepath:
            return

        password = simpledialog.askstring("Password", "Enter the password for the vault file:", show='*')
        if not password:
            messagebox.showwarning("Cancelled", "Import cancelled.")
            return

        try:
            with open(filepath, 'rb') as f:
                salt = f.read(16)
                encrypted_data = f.read()

            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)

            credentials_to_import = json.loads(decrypted_data.decode('utf-8'))

            for cred in credentials_to_import:
                self.vault.add_credentials(
                    url=cred['url'],
                    username=cred['username'],
                    password=cred['password'],
                    totp_secret=cred.get('totp_secret')
                )

            self.refresh_credentials()
            messagebox.showinfo("Success", f"Successfully imported {len(credentials_to_import)} credential(s).")

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import vault. Check the password or file integrity.\n\nError: {e}")
