import customtkinter as ctk
from session_manager_tab import SessionManagerTab
from agent_controller_tab import AgentControllerTab
from task_executor_tab import TaskExecutorTab
from data_extraction_tab import DataExtractionTab
from credential_vault_tab import CredentialVaultTab
from digital_personas_tab import DigitalPersonasTab
from file_manager_tab import FileManagerTab
from workflow_builder_tab import WorkflowBuilderTab
from settings_tab import SettingsTab

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Notte Control Center")
        self.geometry("1200x800")

        # Create tab view
        self.tab_view = ctk.CTkTabview(self, width=1180)
        self.tab_view.pack(padx=10, pady=10, fill="both", expand=True)

        # Add tabs
        self.tab_view.add("Session Manager")
        self.tab_view.add("Agent Controller")
        self.tab_view.add("Task Executor")
        self.tab_view.add("Data Extraction")
        self.tab_view.add("Credential Vault")
        self.tab_view.add("Digital Personas")
        self.tab_view.add("File Manager")
        self.tab_view.add("Workflow Builder")
        self.tab_view.add("Settings")

        # Add content to tabs
        self.session_manager_tab = SessionManagerTab(self.tab_view.tab("Session Manager"))
        self.agent_controller_tab = AgentControllerTab(self.tab_view.tab("Agent Controller"))
        self.task_executor_tab = TaskExecutorTab(self.tab_view.tab("Task Executor"))
        self.data_extraction_tab = DataExtractionTab(self.tab_view.tab("Data Extraction"))
        self.credential_vault_tab = CredentialVaultTab(self.tab_view.tab("Credential Vault"))
        self.digital_personas_tab = DigitalPersonasTab(self.tab_view.tab("Digital Personas"))
        self.file_manager_tab = FileManagerTab(self.tab_view.tab("File Manager"))
        self.workflow_builder_tab = WorkflowBuilderTab(self.tab_view.tab("Workflow Builder"))
        self.settings_tab = SettingsTab(self.tab_view.tab("Settings"))
