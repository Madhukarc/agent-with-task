# AI Agent Task Management System

## Overview

This project implements an AI Agent Task Management System using Flask, LangChain, and OpenAI's GPT models. The system allows users to define task types, create agents with specific capabilities, assign tasks to agents, and execute those tasks dynamically.

## Features

- Define custom task types
- Create AI agents with specific tool sets
- Add generic tasks that can be reused with different parameters
- Assign tasks to agents
- Execute tasks with dynamic parameters
- Web search capability using Google Serper API
- In-memory storage for demonstration purposes

## Prerequisites

- Python 3.7+
- OpenAI API key
- Google Serper API key

## Installation and Local Setup

1. Clone the repository:
   ```
   git clone https://github.com/Madhukarc/ai-agent-task-management.git
   cd ai-agent-task-management
   ```

2. Set up a virtual environment:
   - On macOS and Linux:
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```
   - On Windows:
     ```
     python -m venv venv
     .\venv\Scripts\activate
     ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   ```

5. Run the Flask application:
   ```
   python app.py
   ```

   The server should start running on `http://127.0.0.1:5000/`.

6. (Optional) To run the application in debug mode, which will restart the server on code changes, use:
   ```
   export FLASK_ENV=development
   flask run
   ```

## Usage

Once the server is running, you can interact with the system using the following API endpoints:

### Define a Task Type

```bash
curl -X POST http://127.0.0.1:5000/define_task_type \
  -H "Content-Type: application/json" \
  -d '{"task_type": "Market Research", "description": "Research market trends and analyze competitor data."}'
```

### Define an Agent Type

```bash
curl -X POST http://127.0.0.1:5000/define_agent_type \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "Research Agent", "tools": ["Web Search"]}'
```

### Add a Task

```bash
curl -X POST http://127.0.0.1:5000/add_task \
  -H "Content-Type: application/json" \
  -d '{"name": "Analyze EV Market", "description": "Research the current state of the electric vehicle market", "task_type": "Market Research"}'
```

### Add an Agent

```bash
curl -X POST http://127.0.0.1:5000/add_agent \
  -H "Content-Type: application/json" \
  -d '{"name": "Market Analyst", "agent_type": "Research Agent"}'
```

### Assign a Task

```bash
curl -X POST http://127.0.0.1:5000/assign_task \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "Market Analyst", "task_id": "task_uuid_here"}'
```

### Execute a Task

```bash
curl -X POST http://127.0.0.1:5000/execute_task \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task_uuid_here", "additional_data": {"focus_area": "battery technology"}}'
```

## API Endpoints

- `/define_task_type`: Define a new task type
- `/define_agent_type`: Define a new agent type with specific tools
- `/add_task`: Add a new generic task
- `/add_agent`: Add a new agent
- `/assign_task`: Assign a task to an agent
- `/execute_task`: Execute an assigned task
- `/get_agents`: Get all agents
- `/get_tasks`: Get all tasks
- `/get_task_types`: Get all defined task types
- `/get_agent_types`: Get all defined agent types
- `/get_assignments`: Get all task assignments

## Notes

- This system uses in-memory storage for demonstration purposes. For production use, consider implementing a persistent database.
- The current implementation includes a web search tool. Additional tools can be added by extending the `tools` list in the `add_agent` function.
- Error handling and input validation are minimal in this demo. Enhance these for production use.

## Troubleshooting

- If you encounter a "ModuleNotFoundError", make sure you've activated your virtual environment and installed all requirements.
- If you get an "Invalid API key" error, double-check that you've set up your `.env` file correctly and that your API keys are valid.
- If the server doesn't start, ensure that port 5000 is not being used by another application.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.