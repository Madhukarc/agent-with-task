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
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

5. Run the Flask application:
   ```
   python app.py
   ```

   The server should start running on `http://127.0.0.1:5000/`.

   ```

## Usage

**1. Add a Task**

Endpoint: /add_task
Method: POST
Payload:
jsonCopy{
  "name": "Research AI trends",
  "description": "Investigate current trends in artificial intelligence and summarize key findings."
}

Example curl command:
Copycurl -X POST http://localhost:5000/add_task -H "Content-Type: application/json" -d '{"name": "Research AI trends", "description": "Investigate current trends in artificial intelligence and summarize key findings."}'


**2. Add an Agent**

Endpoint: /add_agent
Method: POST
Payload:
jsonCopy{
  "name": "ResearchBot"
}

Example curl command:
Copycurl -X POST http://localhost:5000/add_agent -H "Content-Type: application/json" -d '{"name": "ResearchBot"}'


**3. Assign a Task**

Endpoint: /assign_task
Method: POST
Payload:
jsonCopy{
  "agent_name": "ResearchBot",
  "task_id": "task_uuid_here"
}

Example curl command:
Copycurl -X POST http://localhost:5000/assign_task -H "Content-Type: application/json" -d '{"agent_name": "ResearchBot", "task_id": "task_uuid_here"}'


**4. Execute a Task**

Endpoint: /execute_task
Method: POST
Payload:
jsonCopy{
  "task_id": "task_uuid_here",
  "additional_data": {
    "focus_area": "machine learning"
  }
}

Example curl command:
Copycurl -X POST http://localhost:5000/execute_task -H "Content-Type: application/json" -d '{"task_id": "task_uuid_here", "additional_data": {"focus_area": "machine learning"}}'


**5. Get All Agents**

Endpoint: /get_agents
Method: GET
Example curl command:
Copycurl http://localhost:5000/get_agents


**6. Get All Tasks**

Endpoint: /get_tasks
Method: GET
Example curl command:
Copycurl http://localhost:5000/get_tasks


**7. Get All Assignments**

Endpoint: /get_assignments
Method: GET
Example curl command:
Copycurl http://localhost:5000/get_assignments


**Usage Flow**

Add a task using /add_task
Add an agent using /add_agent
Assign the task to the agent using /assign_task
Execute the task using /execute_task
Use the GET endpoints to retrieve information about agents, tasks, and assignments as needed

Note: Replace localhost:5000 with your server's address if running on a different machine or port.
```


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
