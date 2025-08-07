import customtkinter as ctk
import os
import threading
from dotenv import load_dotenv
from notte_sdk import NotteClient
from tkinter import messagebox

class SessionManagerTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.notte_client = None
        self.active_sessions = []
        self.session_widgets = {}

        self._init_client()
        self._create_widgets()

    def _init_client(self):
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
        api_key = os.getenv("NOTTE_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            # This is a basic way to handle this. A more robust app might show this in the UI.
            print("WARNING: NOTTE_API_KEY not found or not set. Please set it in gui/.env")
            self.notte_client = None
        else:
            self.notte_client = NotteClient(api_key=api_key)

    def _create_widgets(self):
        # Create main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- Configuration Panel ---
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.config_frame.grid_columnconfigure(1, weight=1)

        config_label = ctk.CTkLabel(self.config_frame, text="Session Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        config_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Headless mode
        self.headless_var = ctk.BooleanVar()
        self.headless_checkbox = ctk.CTkCheckBox(self.config_frame, text="Headless Mode", variable=self.headless_var)
        self.headless_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Browser type
        browser_label = ctk.CTkLabel(self.config_frame, text="Browser:")
        browser_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.browser_var = ctk.StringVar(value="chromium")
        self.browser_dropdown = ctk.CTkComboBox(self.config_frame, values=["chromium", "firefox", "webkit"], variable=self.browser_var)
        self.browser_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # CAPTCHA solving
        self.captcha_var = ctk.BooleanVar()
        self.captcha_checkbox = ctk.CTkCheckBox(self.config_frame, text="Enable CAPTCHA Solving", variable=self.captcha_var)
        self.captcha_checkbox.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Proxies
        self.proxy_var = ctk.BooleanVar()
        self.proxy_checkbox = ctk.CTkCheckBox(self.config_frame, text="Enable Proxies", variable=self.proxy_var)
        self.proxy_checkbox.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        # Proxy location
        proxy_location_label = ctk.CTkLabel(self.config_frame, text="Proxy Location:")
        proxy_location_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.proxy_location_var = ctk.StringVar(value="US")
        self.proxy_location_dropdown = ctk.CTkComboBox(self.config_frame, values=["US", "UK", "EU", "Random"], variable=self.proxy_location_var)
        self.proxy_location_dropdown.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # CDP URL
        cdp_label = ctk.CTkLabel(self.config_frame, text="Custom CDP URL:")
        cdp_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.cdp_url_var = ctk.StringVar()
        self.cdp_url_entry = ctk.CTkEntry(self.config_frame, textvariable=self.cdp_url_var)
        self.cdp_url_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Perception type
        perception_label = ctk.CTkLabel(self.config_frame, text="Perception Type:")
        perception_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.perception_var = ctk.StringVar(value="standard")
        self.perception_dropdown = ctk.CTkComboBox(self.config_frame, values=["fast", "standard", "detailed"], variable=self.perception_var)
        self.perception_dropdown.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        # Start Session Button
        self.start_session_button = ctk.CTkButton(self.config_frame, text="Start Session", command=self.on_start_session)
        self.start_session_button.grid(row=8, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

        # --- Active Sessions Panel ---
        self.sessions_frame = ctk.CTkFrame(self)
        self.sessions_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.sessions_frame.grid_rowconfigure(1, weight=1)
        self.sessions_frame.grid_columnconfigure(0, weight=1)

        sessions_label = ctk.CTkLabel(self.sessions_frame, text="Active Sessions", font=ctk.CTkFont(size=16, weight="bold"))
        sessions_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.sessions_list_frame = ctk.CTkScrollableFrame(self.sessions_frame)
        self.sessions_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.placeholder_label = ctk.CTkLabel(self.sessions_list_frame, text="No active sessions.")
        placeholder_label.pack(padx=10, pady=10)

    def on_start_session(self):
        if not self.notte_client:
            messagebox.showerror("API Key Error", "Notte API Key is not configured. Please set it in gui/.env")
            return

        self.start_session_button.configure(state="disabled", text="Starting...")

        # Run session creation in a separate thread to not block the UI
        thread = threading.Thread(target=self._start_session_worker)
        thread.daemon = True
        thread.start()

    def _start_session_worker(self):
        try:
            session_kwargs = {
                "headless": self.headless_var.get(),
                "browser_type": self.browser_var.get(),
                "solve_captchas": self.captcha_var.get(),
                "proxies": self.proxy_var.get(), # Simplified for now
                "perception_type": self.perception_var.get(),
            }
            cdp_url = self.cdp_url_var.get()
            if cdp_url:
                session_kwargs["cdp_url"] = cdp_url

            # The Notte SDK's Session is a context manager.
            # For a long-running GUI app, we need to manage its lifecycle.
            # We'll enter the context and store the session object.
            session = self.notte_client.Session(**session_kwargs)
            session_context = session.__enter__()

            self.active_sessions.append(session_context)

            # Schedule UI update on the main thread
            self.after(0, self._update_session_list)

        except Exception as e:
            # Show error in a thread-safe way
            self.after(0, lambda: messagebox.showerror("Session Error", f"Failed to start session:\n{e}"))
        finally:
            # Re-enable button on the main thread
            self.after(0, lambda: self.start_session_button.configure(state="normal", text="Start Session"))

    def _update_session_list(self):
        # Clear placeholder if it exists
        if self.placeholder_label:
            self.placeholder_label.destroy()
            self.placeholder_label = None

        # This is a simple implementation. A more robust one would update existing entries.
        # For now, we just clear and redraw.
        for widget in self.sessions_list_frame.winfo_children():
            widget.destroy()

        for i, session in enumerate(self.active_sessions):
            session_id = getattr(session, 'session_id', f"local-{i+1}")

            session_entry_frame = ctk.CTkFrame(self.sessions_list_frame)
            session_entry_frame.pack(fill="x", padx=5, pady=5)

            label = ctk.CTkLabel(session_entry_frame, text=f"Session: {session_id} (Running)")
            label.pack(side="left", padx=10)

            # We would add View, Pause, Resume, Terminate buttons here
            terminate_button = ctk.CTkButton(session_entry_frame, text="Terminate", width=80,
                                             command=lambda s=session: self._terminate_session(s))
            terminate_button.pack(side="right", padx=10)

    def _terminate_session(self, session_to_terminate):
        try:
            session_to_terminate.__exit__(None, None, None)
            self.active_sessions.remove(session_to_terminate)
            self._update_session_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to terminate session:\n{e}")
