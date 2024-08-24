import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.utilities import GoogleSerperAPIWrapper
from typing import List, Dict, Any
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the LLM with `gpt-3.5-turbo` using ChatOpenAI
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

# Initialize Serper API Wrapper for web search
search = GoogleSerperAPIWrapper()

# In-memory storage for task types, agent types, tasks, agents, and assignments
task_types: Dict[str, str] = {}  # Task type name to description
agent_types: Dict[str, List[str]] = {}  # Agent type name to tools
tasks: Dict[str, 'Task'] = {}
agents: Dict[str, 'Agent'] = {}
assignments: Dict[str, Dict[str, Any]] = {}  # {task_id: {agent_name, assigned: bool}}

# Tool functions
def web_search(query: str) -> str:
    return search.run(query)

# Task class
class Task:
    def __init__(self, name: str, description: str, task_type: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.task_type = task_type
        self.result = None

    def execute(self, agent, **kwargs):
        # Construct a more specific prompt
        task_prompt = f"Complete the following task: {self.name}\n{self.description}\n\nUse the following information:\n"
        for key, value in kwargs.items():
            task_prompt += f"{key}: {value}\n"
        
        # Add explicit instruction to format the output correctly
        task_prompt += "\nPlease provide your response in a clear and concise format, indicating any tools used and the final output.\n"

        # Execute the task
        self.result = agent.run(task_prompt)
        return self.result

# Agent class
class Agent:
    def __init__(self, name: str, llm, agent_type: str, memory=None, tools=None):
        self.name = name
        self.llm = llm
        self.agent_type = agent_type
        self.memory = memory
        self.tools = tools if tools else []
        self.agent = initialize_agent(
            self.tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=memory
        )

    def execute_task(self, task: Task, **kwargs):
        return task.execute(self.agent, **kwargs)

# Flask API routes

@app.route('/define_task_type', methods=['POST'])
def define_task_type():
    """Define a new task type."""
    data = request.json
    task_type = data.get('task_type')
    description = data.get('description', 'No description provided.')
    
    if not task_type:
        return jsonify({"error": "Task type is required"}), 400

    task_types[task_type] = description
    return jsonify({"message": f"Task type '{task_type}' defined."}), 201

@app.route('/define_agent_type', methods=['POST'])
def define_agent_type():
    """Define a new agent type with specific tools."""
    data = request.json
    agent_type = data.get('agent_type')
    tools = data.get('tools', [])

    if not agent_type:
        return jsonify({"error": "Agent type is required"}), 400

    agent_types[agent_type] = tools
    return jsonify({"message": f"Agent type '{agent_type}' defined."}), 201

@app.route('/add_task', methods=['POST'])
def add_task():
    """Add a new generic task that can be executed multiple times with different parameters."""
    data = request.json
    name = data.get('name')
    description = data.get('description')
    task_type = data.get('task_type')
    
    if not name or not description or not task_type:
        return jsonify({"error": "Task name, description, and type are required"}), 400

    if task_type not in task_types:
        return jsonify({"error": "Task type not defined"}), 400

    task = Task(name=name, description=description, task_type=task_type)
    tasks[task.id] = task
    return jsonify({"task_id": task.id}), 201

@app.route('/add_agent', methods=['POST'])
def add_agent():
    """Add a new agent."""
    data = request.json
    name = data.get('name')
    agent_type = data.get('agent_type')
    
    if not name or not agent_type:
        return jsonify({"error": "Agent name and type are required"}), 400

    if agent_type not in agent_types:
        return jsonify({"error": "Agent type not defined"}), 400

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Initialize tools based on the agent type
    tools = []
    for tool_name in agent_types[agent_type]:
        if tool_name == 'Web Search':
            tools.append(Tool(name="Web Search", func=web_search, description="Tool to perform web searches."))
        # Add other tools as needed

    agent = Agent(name=name, llm=llm, agent_type=agent_type, memory=memory, tools=tools)
    agents[name] = agent
    return jsonify({"agent_name": agent.name}), 201

@app.route('/assign_task', methods=['POST'])
def assign_task():
    """Assign a task to an agent without executing it."""
    data = request.json
    agent_name = data.get('agent_name')
    task_id = data.get('task_id')

    agent = agents.get(agent_name)
    task = tasks.get(task_id)

    if not agent or not task:
        return jsonify({"error": "Agent or task not found"}), 404

    # Assign task to agent
    assignments[task_id] = {"agent_name": agent_name, "assigned": True}
    return jsonify({"message": f"Task '{task_id}' assigned to agent '{agent_name}'."}), 200

@app.route('/execute_task', methods=['POST'])
def execute_task():
    """Execute an assigned task for an agent."""
    data = request.json
    task_id = data.get('task_id')
    additional_data = data.get('additional_data', {})

    assignment = assignments.get(task_id)

    if not assignment or not assignment['assigned']:
        return jsonify({"error": "Task is not assigned or does not exist."}), 404

    agent_name = assignment['agent_name']
    agent = agents.get(agent_name)
    task = tasks.get(task_id)

    result = agent.execute_task(task, **additional_data)

    # Allow re-execution of the same task with different parameters
    return jsonify({"result": result})

@app.route('/get_agents', methods=['GET'])
def get_agents():
    """Get all agents."""
    return jsonify({"agents": list(agents.keys())})

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    return jsonify({"tasks": list(tasks.keys())})

@app.route('/get_task_types', methods=['GET'])
def get_task_types():
    """Get all defined task types."""
    return jsonify({"task_types": task_types})

@app.route('/get_agent_types', methods=['GET'])
def get_agent_types():
    """Get all defined agent types."""
    return jsonify({"agent_types": agent_types})

@app.route('/get_assignments', methods=['GET'])
def get_assignments():
    """Get all task assignments."""
    return jsonify({"assignments": assignments})

if __name__ == '__main__':
    # Adding sample task types and agent types for demonstration
    task_types['Market Research'] = 'Research market trends and analyze competitor data.'
    agent_types['Research Agent'] = ['Web Search', 'Data Analysis']

    # Running the Flask app
    app.run(debug=True)
