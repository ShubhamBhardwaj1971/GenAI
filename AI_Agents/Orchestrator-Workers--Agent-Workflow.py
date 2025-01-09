from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import asyncio
from typing import Tuple, Dict, List

# Load environment variables from .env file
load_dotenv() 
    
def llm_agent(prompt):
    """The llm agent is used to answer the user input."""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

class WorkerTask:
    """Represents a task assigned to a worker"""
    def __init__(self, task_description: str, task_type: str):
        self.description = task_description
        self.type = task_type
        self.result = None

async def orchestrator(prompt: str) -> Dict[str, str]:
    """
    Orchestrator agent that breaks down tasks and coordinates workers.
    Returns both the breakdown and final synthesis.
    """
    client = OpenAI()
    
    # First, have the orchestrator break down the task
    planning_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """You are an Orchestrator Agent. Your job is to:
            1. Analyze the given task
            2. Break it down into exactly 2 subtasks
            3. Return the subtasks in a clear, structured way
            
            Each subtask should be independent and able to be worked on in parallel.
            Format your response as:
            Subtask 1: [description]
            Subtask 2: [description]"""},
            {"role": "user", "content": f"Break down this task: {prompt}"}
        ]
    )
    
    # Parse the subtasks from the response
    subtasks_text = planning_response.choices[0].message.content
    print("\n=== Orchestrator's Task Breakdown ===")
    print(subtasks_text)
    
    # Extract subtasks (simple parsing, could be made more robust)
    subtasks = [line.split(": ", 1)[1] for line in subtasks_text.split("\n") if line.startswith("Subtask")]
    
    return subtasks

async def worker_1(task: str) -> str:
    """First worker agent focused on analytical processing"""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Worker Agent 1. You specialize in detailed analysis and technical aspects of tasks."},
            {"role": "user", "content": task}
        ]
    )
    return response.choices[0].message.content

async def worker_2(task: str) -> str:
    """Second worker agent focused on practical implementation"""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Worker Agent 2. You specialize in practical implementation and real-world applications."},
            {"role": "user", "content": task}
        ]
    )
    return response.choices[0].message.content

async def synthesize_results(original_prompt: str, worker_results: Dict[str, str]) -> str:
    """Synthesize the results from all workers into a final response"""
    client = OpenAI()
    
    synthesis_prompt = f"""
    Original Task: {original_prompt}
    
    Worker 1 Results:
    {worker_results['worker_1']}
    
    Worker 2 Results:
    {worker_results['worker_2']}
    
    Please synthesize these results into a comprehensive final response.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Synthesis Agent. Combine the workers' results into a coherent, comprehensive response."},
            {"role": "user", "content": synthesis_prompt}
        ]
    )
    return response.choices[0].message.content

async def orchestrator_workflow(prompt: str) -> None:
    """
    Main workflow function that coordinates the orchestrator and workers.
    
    Args:
        prompt (str): The initial task prompt
    """
    # Get task breakdown from orchestrator
    subtasks = await orchestrator(prompt)
    
    # Execute workers in parallel
    worker1_task = asyncio.create_task(worker_1(subtasks[0]))
    worker2_task = asyncio.create_task(worker_2(subtasks[1]))
    
    # Wait for both workers to complete
    worker1_result, worker2_result = await asyncio.gather(worker1_task, worker2_task)
    
    # Store worker results
    worker_results = {
        'worker_1': worker1_result,
        'worker_2': worker2_result
    }
    
    # Print worker results
    print("\n=== Worker 1 Results ===")
    print(worker_results['worker_1'])
    print("\n=== Worker 2 Results ===")
    print(worker_results['worker_2'])
    
    # Synthesize final result
    final_result = await synthesize_results(prompt, worker_results)
    
    print("\n=== Final Synthesized Result ===")
    print(final_result)

def run_orchestrator_workflow(prompt: str) -> None:
    """
    Wrapper function to run the async workflow.
    
    Args:
        prompt (str): The initial task prompt
    """
    asyncio.run(orchestrator_workflow(prompt))

prompt = "I need to create software in python to add 2 integers and sell this to a client."
run_orchestrator_workflow(prompt)