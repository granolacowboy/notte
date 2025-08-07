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
        self.task_executor_tab = TaskExecutorTab(self.tab_view.tab("Task Executor"), run_callback=self.run_agent_task)
        self.data_extraction_tab = DataExtractionTab(self.tab_view.tab("Data Extraction"))
        self.credential_vault_tab = CredentialVaultTab(self.tab_view.tab("Credential Vault"))
        self.digital_personas_tab = DigitalPersonasTab(self.tab_view.tab("Digital Personas"))
        self.file_manager_tab = FileManagerTab(self.tab_view.tab("File Manager"))
        self.workflow_builder_tab = WorkflowBuilderTab(self.tab_view.tab("Workflow Builder"))
        self.settings_tab = SettingsTab(self.tab_view.tab("Settings"))

    def run_agent_task(self):
        # This is where the orchestration happens
        agent_config = self.agent_controller_tab.get_agent_config()
        task_details = self.task_executor_tab.get_task_details()

        # Simple validation
        if not task_details.get("task"):
            from tkinter import messagebox
            messagebox.showerror("Error", "Task description cannot be empty.")
            return

        # Update UI to show task is starting
        self.task_executor_tab.run_button.configure(state="disabled", text="Running...")
        self.task_executor_tab.progress_bar.start()

        import threading
        thread = threading.Thread(target=self._run_agent_task_worker, args=(agent_config, task_details))
        thread.daemon = True
        thread.start()

    def _run_agent_task_worker(self, agent_config, task_details):
        import asyncio
        import json
        import os
        from notte_sdk import NotteClient
        from notte_sdk.endpoints.agents import AgentsClient, AgentCompletion
        from websockets.asyncio import client as websocket_client

        try:
            # Get API key from config
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            api_key = config.get("api_key")

            if not api_key:
                raise ValueError("API Key not found in settings.")

            client = NotteClient(api_key=api_key)

            with client.Session(headless=True) as session:
                # Create the agent
                agent = client.Agent(session=session, **agent_config)

                # Start the agent run, which returns immediately with IDs
                start_response = agent.start(task=task_details["task"], url=task_details.get("url") or None)
                agent_id = start_response.agent_id
                session_id = start_response.session_id

                # Now, watch for logs using websockets
                asyncio.run(self._watch_agent_logs(client.agents, agent_id, session_id))

        except Exception as e:
            import traceback
            output = f"An error occurred:\n{traceback.format_exc()}"
            self.after(0, self.on_agent_task_complete, output)

    async def _watch_agent_logs(self, agents_client, agent_id, session_id):
        from notte_sdk.types import AgentStatusResponse
        from notte_core.agent_types import AgentCompletion
        from websockets.asyncio import client as websocket_client

        ws_path = agents_client.AGENT_LOGS_WS.format(agent_id=agent_id, token=agents_client.token, session_id=session_id)
        wss_url = f"{agents_client.server_url.replace('http', 'ws')}/agents/{ws_path}"

        final_output = ""
        try:
            async with websocket_client.connect(uri=wss_url, open_timeout=30, ping_interval=5, ping_timeout=40) as websocket:
                async for message in websocket:
                    if agent_id in message and "agent_id" in message:
                        response_message = AgentStatusResponse.model_validate_json(message)
                        final_output = f"Task Complete!\n\nAgent's Answer:\n{response_message.answer}"
                        break # End of task

                    step_data = AgentCompletion.model_validate_json(message)
                    self.after(0, self.update_agent_status, step_data)
        except Exception as e:
            import traceback
            final_output = f"An error occurred during log watching:\n{traceback.format_exc()}"
        finally:
            self.after(0, self.on_agent_task_complete, final_output)

    def update_agent_status(self, step_data: AgentCompletion):
        # Update thoughts
        thoughts_text = self.agent_controller_tab.thoughts_text
        thoughts_text.configure(state="normal")
        thoughts_text.delete("0.0", "end")
        thoughts_text.insert("0.0", f"Goal: {step_data.next_goal}\n\nSummary: {step_data.page_summary}")
        thoughts_text.configure(state="disabled")

        # Update history
        history_text = self.agent_controller_tab.history_text
        history_text.configure(state="normal")
        history_text.insert("end", f"- {step_data.action.to_natural_language()}\n")
        history_text.configure(state="disabled")

    def on_agent_task_complete(self, output):
        self.task_executor_tab.run_button.configure(state="normal", text="Run")
        self.task_executor_tab.progress_bar.stop()
        self.task_executor_tab.progress_bar.set(0)

        console = self.task_executor_tab.console_output
        console.configure(state="normal")
        console.delete("0.0", "end")
        console.insert("0.0", output)
        console.configure(state="disabled")
