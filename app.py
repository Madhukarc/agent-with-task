import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Initialize Tavily Search tool
tavily_search = TavilySearchResults(max_results=3)

# In-memory storage for tasks, agents, and assignments
tasks: Dict[str, 'Task'] = {}
agents: Dict[str, 'Agent'] = {}
assignments: Dict[str, Dict[str, Any]] = {}

# Task class
class Task:
    def __init__(self, name: str, description: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.result = None

    def execute(self, agent, **kwargs):
        task_prompt = f"Complete the following task: {self.name}\n{self.description}\n\nAdditional Information:\n"
        for key, value in kwargs.items():
            task_prompt += f"{key}: {value}\n"
        self.result = agent.process_task(task_prompt)
        return self.result

# Agent class
class Agent:
    def __init__(self, name: str):
        self.name = name
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.tools = [tavily_search]
        self.agent_executor = self._create_agent()

    def _create_agent(self):
        template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

        prompt = PromptTemplate.from_template(template)
        
        agent = create_react_agent(llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, memory=self.memory)

    def process_task(self, task_prompt: str) -> str:
        response = self.agent_executor.invoke({"input": task_prompt})
        return response['output']

    def execute_task(self, task: Task, **kwargs):
        return task.execute(self, **kwargs)

# Flask API routes

@app.route('/add_task', methods=['POST'])
def add_task():
    """Add a new task."""
    data = request.json
    name = data.get('name')
    description = data.get('description')
    
    if not name or not description:
        return jsonify({"error": "Task name and description are required"}), 400

    task = Task(name=name, description=description)
    tasks[task.id] = task
    return jsonify({"task_id": task.id}), 201

@app.route('/add_agent', methods=['POST'])
def add_agent():
    """Add a new agent."""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Agent name is required"}), 400

    agent = Agent(name=name)
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

    return jsonify({"result": result})

@app.route('/get_agents', methods=['GET'])
def get_agents():
    """Get all agents."""
    return jsonify({"agents": list(agents.keys())})

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    return jsonify({"tasks": {task_id: {"name": task.name, "description": task.description} for task_id, task in tasks.items()}})

@app.route('/get_assignments', methods=['GET'])
def get_assignments():
    """Get all task assignments."""
    return jsonify({"assignments": assignments})

if __name__ == '__main__':
    app.run(debug=True)
