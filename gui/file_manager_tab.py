import customtkinter as ctk
from tkinter import filedialog, messagebox

class FileManagerTab(ctk.CTkFrame):
    def __init__(self, parent, client):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.client = client
        self.storage = None

        if self.client:
            self.storage = self.client.FileStorage()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Upload
        self.grid_rowconfigure(1, weight=2) # Download

        # --- Upload Panel ---
        self.upload_frame = ctk.CTkFrame(self)
        self.upload_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.upload_frame.grid_columnconfigure(0, weight=1)

        upload_label = ctk.CTkLabel(self.upload_frame, text="Upload Files", font=ctk.CTkFont(size=16, weight="bold"))
        upload_label.pack(padx=10, pady=10, anchor="w")

        self.browse_button = ctk.CTkButton(self.upload_frame, text="Browse for file(s) to upload", command=self.upload_files)
        self.browse_button.pack(padx=10, pady=10, fill="x")

        # --- Download Panel ---
        self.download_frame = ctk.CTkFrame(self)
        self.download_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.download_frame.grid_rowconfigure(1, weight=1)
        self.download_frame.grid_columnconfigure(0, weight=1)

        download_label = ctk.CTkLabel(self.download_frame, text="Available Downloads", font=ctk.CTkFont(size=16, weight="bold"))
        download_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.refresh_downloads_button = ctk.CTkButton(self.download_frame, text="Refresh", command=self.refresh_downloads)
        self.refresh_downloads_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        self.downloads_listbox = ctk.CTkScrollableFrame(self.download_frame)
        self.downloads_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.refresh_downloads()

    def upload_files(self):
        if not self.storage:
            messagebox.showerror("Error", "Client not initialized.")
            return

        filepaths = filedialog.askopenfilenames(title="Select file(s) to upload")
        if not filepaths:
            return

        try:
            for fp in filepaths:
                self.storage.upload(fp)
            messagebox.showinfo("Success", f"{len(filepaths)} file(s) uploaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload files:\n{e}")

    def refresh_downloads(self):
        if not self.storage:
            return

        for widget in self.downloads_listbox.winfo_children():
            widget.destroy()

        try:
            downloaded_files = self.storage.list(type="downloads")
            if not downloaded_files:
                label = ctk.CTkLabel(self.downloads_listbox, text="No downloaded files found.")
                label.pack()
                return

            for filename in downloaded_files:
                file_frame = ctk.CTkFrame(self.downloads_listbox, fg_color="transparent")
                file_frame.pack(fill="x")

                label = ctk.CTkLabel(file_frame, text=filename)
                label.pack(side="left", padx=5)

                download_button = ctk.CTkButton(file_frame, text="Download", width=80,
                                                command=lambda f=filename: self.download_file(f))
                download_button.pack(side="right", padx=5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list downloads:\n{e}")

    def download_file(self, filename):
        if not self.storage:
            return

        save_path = filedialog.askdirectory(title="Select folder to save file")
        if not save_path:
            return

        try:
            self.storage.download(file_name=filename, local_dir=save_path)
            messagebox.showinfo("Success", f"Downloaded '{filename}' to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download file:\n{e}")
