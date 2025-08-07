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
        self.task_executor_tab = TaskExecutorTab(self.tab_view.tab("Task Executor"),
                                                 run_callback=self.run_agent_task,
                                                 stop_callback=self.stop_agent_task)
        self.data_extraction_tab = DataExtractionTab(self.tab_view.tab("Data Extraction"), scrape_callback=self.scrape_data)
        self.credential_vault_tab = CredentialVaultTab(self.tab_view.tab("Credential Vault"))
        self.digital_personas_tab = DigitalPersonasTab(self.tab_view.tab("Digital Personas"))
        self.file_manager_tab = FileManagerTab(self.tab_view.tab("File Manager"))
        self.workflow_builder_tab = WorkflowBuilderTab(self.tab_view.tab("Workflow Builder"))
        self.settings_tab = SettingsTab(self.tab_view.tab("Settings"))
        self.current_agent_task_info = None

    def run_agent_task(self):
        agent_config = self.agent_controller_tab.get_agent_config()
        task_details = self.task_executor_tab.get_task_details()

        if not task_details.get("task"):
            from tkinter import messagebox
            messagebox.showerror("Error", "Task description cannot be empty.")
            return

        self.task_executor_tab.run_button.configure(state="disabled")
        self.task_executor_tab.stop_button.configure(state="normal")
        self.task_executor_tab.progress_bar.start()

        import threading
        thread = threading.Thread(target=self._run_agent_task_worker, args=(agent_config, task_details))
        thread.daemon = True
        thread.start()

    def stop_agent_task(self):
        if not self.current_agent_task_info:
            return

        self.task_executor_tab.stop_button.configure(state="disabled", text="Stopping...")

        import threading
        thread = threading.Thread(target=self._stop_agent_task_worker)
        thread.daemon = True
        thread.start()

    def _stop_agent_task_worker(self):
        try:
            info = self.current_agent_task_info
            if info and info.get("client"):
                client = info["client"]
                agent_id = info["agent_id"]
                session_id = info["session_id"]
                client.agents.stop(agent_id=agent_id, session_id=session_id)
                output = "Agent stopped by user."
                self.after(0, self.on_agent_task_complete, output)
        except Exception as e:
            import traceback
            output = f"An error occurred while stopping the agent:\n{traceback.format_exc()}"
            self.after(0, self.on_agent_task_complete, output)


    def _run_agent_task_worker(self, agent_config, task_details):
        import asyncio
        import json
        import os
        from notte_sdk import NotteClient

        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            api_key = config.get("api_key")

            if not api_key:
                raise ValueError("API Key not found in settings.")

            client = NotteClient(api_key=api_key)

            with client.Session(headless=True) as session:
                agent = client.Agent(session=session, **agent_config)

                start_response = agent.start(task=task_details["task"], url=task_details.get("url") or None)
                self.current_agent_task_info = {
                    "client": client,
                    "agent_id": start_response.agent_id,
                    "session_id": start_response.session_id,
                }

                asyncio.run(self._watch_agent_logs(client.agents, start_response.agent_id, start_response.session_id))

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
                # Need a way to break this loop if stop is requested
                while self.current_agent_task_info is not None:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    except asyncio.TimeoutError:
                        continue # Check the stop condition and continue waiting

                    if agent_id in message and "agent_id" in message:
                        response_message = AgentStatusResponse.model_validate_json(message)
                        final_output = f"Task Complete!\n\nAgent's Answer:\n{response_message.answer}"
                        break

                    step_data = AgentCompletion.model_validate_json(message)
                    self.after(0, self.update_agent_status, step_data)
        except Exception as e:
            # Ignore connection closed errors if we stopped the task
            if self.current_agent_task_info is None:
                final_output = "Agent stopped."
            else:
                import traceback
                final_output = f"An error occurred during log watching:\n{traceback.format_exc()}"
        finally:
            self.after(0, self.on_agent_task_complete, final_output)

    def update_agent_status(self, step_data):
        # This function is called from a worker thread via self.after(), so it's UI-safe

        # Update thoughts in Agent Controller
        thoughts_text = self.agent_controller_tab.thoughts_text
        thoughts_text.configure(state="normal")
        thoughts_text.delete("0.0", "end")
        thoughts_text.insert("0.0", f"Goal: {step_data.next_goal}\n\nSummary: {step_data.page_summary}")
        thoughts_text.configure(state="disabled")

        # Update history in Agent Controller
        history_text = self.agent_controller_tab.history_text
        action_text = f"- {step_data.action.to_natural_language()}\n"
        history_text.configure(state="normal")
        history_text.insert("end", action_text)
        history_text.configure(state="disabled")

        # Update console in Task Executor
        console = self.task_executor_tab.console_output
        console.configure(state="normal")
        console.insert("end", action_text)
        console.configure(state="disabled")

    def on_agent_task_complete(self, output):
        self.current_agent_task_info = None # Clear the current task info

        # Reset UI state
        self.task_executor_tab.run_button.configure(state="normal", text="Run")
        self.task_executor_tab.stop_button.configure(state="disabled", text="Stop")
        self.task_executor_tab.progress_bar.stop()
        self.task_executor_tab.progress_bar.set(0)

        # Display final output
        console = self.task_executor_tab.console_output
        console.configure(state="normal")
        console.insert("end", f"\n--- TASK FINISHED ---\n{output}")
        console.configure(state="disabled")

    def scrape_data(self):
        scrape_config = self.data_extraction_tab.get_scrape_config()
        if scrape_config is None: # Error occurred in get_scrape_config
            return

        if not scrape_config.get("url"):
            from tkinter import messagebox
            messagebox.showerror("Error", "URL cannot be empty.")
            return

        self.data_extraction_tab.scrape_button.configure(state="disabled", text="Scraping...")

        import threading
        thread = threading.Thread(target=self._scrape_data_worker, args=(scrape_config,))
        thread.daemon = True
        thread.start()

    def _scrape_data_worker(self, scrape_config):
        from notte_sdk import NotteClient
        import json, os

        output_parts = []
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            api_key = config.get("api_key")

            if not api_key:
                raise ValueError("API Key not found in settings.")

            client = NotteClient(api_key=api_key)

            batch_queue = self.data_extraction_tab.get_batch_queue()

            if batch_queue:
                # Batch mode
                for i, url in enumerate(batch_queue):
                    self.after(0, lambda url=url, i=i: self.update_batch_status(url, "In Progress...", i))
                    current_config = scrape_config.copy()
                    current_config["url"] = url

                    response = client.scrape(**current_config)

                    if isinstance(response, str):
                        output_parts.append(f"--- Result for {url} ---\n{response}\n")
                    else:
                        output_parts.append(f"--- Result for {url} ---\n{response.model_dump_json(indent=4)}\n")
                    self.after(0, lambda url=url, i=i: self.update_batch_status(url, "Done", i))
                output = "\n".join(output_parts)
                self.data_extraction_tab.url_queue.clear() # Clear queue after processing
            else:
                # Single mode
                response = client.scrape(**scrape_config)
                if isinstance(response, str):
                    output = response
                else: # Pydantic model
                    output = response.model_dump_json(indent=4)

        except Exception as e:
            import traceback
            output = f"An error occurred:\n{traceback.format_exc()}"
        finally:
            self.after(0, self.on_scrape_complete, output)

    def update_batch_status(self, url, status, index):
        # This is a simple way to show status. A better way would be a proper list/table view.
        for i, widget in enumerate(self.data_extraction_tab.batch_queue_frame.winfo_children()):
            if i == index:
                widget.configure(text=f"{url} [{status}]")
                break

    def on_scrape_complete(self, output):
        self.data_extraction_tab.scrape_button.configure(state="normal", text="Scrape Data")

        result_text = self.data_extraction_tab.result_text
        result_text.configure(state="normal")
        result_text.delete("0.0", "end")
        result_text.insert("0.0", output)
        result_text.configure(state="disabled")
