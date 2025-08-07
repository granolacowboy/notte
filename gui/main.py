import customtkinter as ctk
from app_window import AppWindow

def main():
    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    # Set appearance and color theme
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"
    main()
