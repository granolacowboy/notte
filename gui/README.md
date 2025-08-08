# Notte Control Center

The Notte Control Center is a desktop GUI application for interacting with and managing the Notte web automation framework. It provides a user-friendly interface for all of Notte's core features, from managing sessions and agents to building complex workflows.

## Features

This application provides a tabbed interface with the following main sections:

-   **Session Manager**: Configure and manage browser sessions (headless, browser type, proxies, etc.) and view active sessions.
-   **Agent Controller**: Configure the parameters for the Notte agent and view its status, thoughts, and actions in real-time during a run.
-   **Task Executor**: Run agent tasks by providing a natural language description and an optional URL.
-   **Data Extraction**: Use the dedicated scraping client to extract data from websites, with support for structured output via Pydantic models.
-   **Credential Vault**: Securely manage credentials. The vault is encrypted and can be imported and exported with a password.
-   **Digital Personas**: Create and manage digital identities for your agents.
-   **File Manager**: Upload files to and download files from your Notte sessions.
-   **Workflow Builder**: A visual, node-based editor for creating complex automation workflows. *Note: Currently in Phase 1 (Visual layout and properties), execution is not yet implemented.*
-   **Settings**: Configure application-level settings, such as your Notte API key and theme preferences.

## Setup and Installation

The Notte Control Center is designed to be run from within the main `notte` repository.

### 1. Install Core Dependencies

First, ensure you have the `notte` framework and its dependencies installed. From the root of the repository, it is recommended to use `uv` for installation, as it correctly handles the local workspace packages:

```bash
# It is recommended to do this in a virtual environment
uv pip install -e .[dev,eval,mcp]
```
This command installs the core `notte` packages in editable mode, along with all development and optional dependencies required to run the test suite and examples.

### 2. Install GUI Dependencies

The GUI has its own set of dependencies. Install them using the provided `requirements.txt` file:

```bash
pip install -r gui/requirements.txt
```

### 3. Install Playwright Browsers

The underlying `notte` framework uses Playwright to control browsers. You need to install the necessary browser binaries:

```bash
python -m playwright install
```

## Configuration

Before running the application, you must configure your Notte API key.

1.  Launch the application once. It will create a `gui/config.json` file.
2.  Open the application and navigate to the **Settings** tab.
3.  Enter your Notte API key in the "Notte API Key" field and click "Save Settings".

The application will store your key securely for all subsequent operations.

## Running the Application

Once the setup and configuration are complete, you can run the application from the **root of the repository** with the following command:

```bash
python gui/main.py
```
