import customtkinter as ctk

class DigitalPersonasTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        label = ctk.CTkLabel(self, text="Digital Personas Tab Content (To be implemented)")
        label.pack(padx=20, pady=20)
