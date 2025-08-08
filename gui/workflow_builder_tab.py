import customtkinter as ctk
from tkinter import messagebox
from tknodesystem import NodeEditor

class WorkflowBuilderTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.grid_columnconfigure(0, weight=3) # Node editor gets more space
        self.grid_columnconfigure(1, weight=1) # Properties panel gets less
        self.grid_rowconfigure(0, weight=1)

        self.editor = NodeEditor(self, available_nodes={})
        self.editor.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # --- Properties Panel ---
        self.properties_frame = ctk.CTkFrame(self, border_width=1)
        self.properties_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.properties_frame.grid_columnconfigure(0, weight=1)

        prop_label = ctk.CTkLabel(self.properties_frame, text="Properties", font=ctk.CTkFont(size=16, weight="bold"))
        prop_label.pack(padx=10, pady=10, anchor="w")

        self.properties_content_frame = ctk.CTkFrame(self.properties_frame, fg_color="transparent")
        self.properties_content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Setup custom nodes and event binding
        self.setup_node_menu()
        self.editor.bind("<<NodeSelected>>", self.on_node_selected)
        self.editor.bind("<<NodeDeselected>>", self.on_node_deselected)

    def setup_node_menu(self):
        self.editor.add_node("Start", self.create_start_node)
        self.editor.add_node("End", self.create_end_node)
        self.editor.add_node("Script Action", self.create_script_action_node)
        self.editor.add_node("Agent Task", self.create_agent_task_node)

    def create_start_node(self):
        self.editor.create_node(
            node_type="Start",
            name="Start",
            outputs=[{"name": "Flow"}]
        )

    def create_end_node(self):
        self.editor.create_node(
            node_type="End",
            name="End",
            inputs=[{"name": "Flow"}]
        )

    def create_script_action_node(self):
        self.editor.create_node(
            node_type="Script Action",
            name="Script Action",
            inputs=[{"name": "Flow In"}],
            outputs=[{"name": "Flow Out"}]
        )
        # In a future step, we will add properties like script content here.

    def create_agent_task_node(self):
        node = self.editor.create_node(
            node_type="Agent Task",
            name="Agent Task",
            inputs=[{"name": "Flow In"}],
            outputs=[{"name": "Flow Out"}]
        )
        node.data["prompt"] = "Enter your natural language task here."

    def on_node_selected(self, event):
        self.populate_properties_panel()

    def on_node_deselected(self, event):
        self.clear_properties_panel()

    def clear_properties_panel(self):
        for widget in self.properties_content_frame.winfo_children():
            widget.destroy()

    def populate_properties_panel(self):
        self.clear_properties_panel()

        selected_nodes = self.editor.get_selected_nodes()
        if not selected_nodes:
            return

        node = selected_nodes[0] # For now, only handle single selection

        # Add a label for the node name
        name_label = ctk.CTkLabel(self.properties_content_frame, text=f"Node: {node.name}")
        name_label.pack(anchor="w", pady=(0, 10))

        if node.node_type == "Script Action":
            self.build_script_action_properties(node)
        elif node.node_type == "Agent Task":
            self.build_agent_task_properties(node)

    def build_script_action_properties(self, node):
        label = ctk.CTkLabel(self.properties_content_frame, text="Script Command:")
        label.pack(anchor="w")

        text_box = ctk.CTkTextbox(self.properties_content_frame, height=100)
        text_box.pack(fill="x", expand=True)
        text_box.insert("0.0", node.data.get("script", "# Enter script here"))

        def update_script_data(event):
            node.data["script"] = text_box.get("0.0", "end-1c")

        text_box.bind("<KeyRelease>", update_script_data)

    def build_agent_task_properties(self, node):
        label = ctk.CTkLabel(self.properties_content_frame, text="Task Prompt:")
        label.pack(anchor="w")

        text_box = ctk.CTkTextbox(self.properties_content_frame, height=100)
        text_box.pack(fill="x", expand=True)
        text_box.insert("0.0", node.data.get("prompt", "# Enter prompt here"))

        def update_prompt_data(event):
            node.data["prompt"] = text_box.get("0.0", "end-1c")

        text_box.bind("<KeyRelease>", update_prompt_data)
