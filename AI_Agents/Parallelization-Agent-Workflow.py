from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import asyncio
from typing import Tuple, Dict

# Load environment variables from .env file
load_dotenv() 
    
async def perspective_agent_1(prompt: str) -> str:
    """First agent focusing on factual, analytical perspective."""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an analytical agent. Focus on providing factual, detailed analysis of the topic. Be thorough and precise."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

async def perspective_agent_2(prompt: str) -> str:
    """Second agent focusing on practical, real-world applications."""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a practical agent. Focus on real-world applications, examples, and practical implications of the topic."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

async def synthesis_agent(responses: Dict[str, str], original_prompt: str) -> str:
    """Third agent that synthesizes the parallel responses into a cohesive answer."""
    client = OpenAI()
    
    synthesis_prompt = f"""
    Original Question: {original_prompt}
    
    Perspective 1 (Analytical):
    {responses['analytical']}
    
    Perspective 2 (Practical):
    {responses['practical']}
    
    Please synthesize these perspectives into a comprehensive, well-balanced response.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a synthesis agent. Your role is to combine and harmonize different perspectives into a coherent, balanced response."},
            {"role": "user", "content": synthesis_prompt}
        ]
    )
    return response.choices[0].message.content

async def parallel_processing(prompt: str) -> Tuple[Dict[str, str], str]:
    """
    Process a prompt using parallel agents and synthesize their responses.
    
    Args:
        prompt (str): The input prompt to process
        
    Returns:
        Tuple[Dict[str, str], str]: Individual responses and final synthesis
    """
    # Run the first two agents in parallel
    analytical_task = asyncio.create_task(perspective_agent_1(prompt))
    practical_task = asyncio.create_task(perspective_agent_2(prompt))
    
    # Wait for both to complete
    analytical_response, practical_response = await asyncio.gather(
        analytical_task, practical_task
    )
    
    # Store individual responses
    responses = {
        'analytical': analytical_response,
        'practical': practical_response
    }
    
    # Get synthesis
    final_response = await synthesis_agent(responses, prompt)
    
    return responses, final_response

def run_parallel_agents(prompt: str) -> None:
    """
    Run the parallel processing workflow and print all responses.
    
    Args:
        prompt (str): The input prompt to process
    """
    responses, final_answer = asyncio.run(parallel_processing(prompt))
    
    print("\n=== Analytical Perspective ===")
    print(responses['analytical'])
    
    print("\n=== Practical Perspective ===")
    print(responses['practical'])
    
    print("\n=== Final Synthesized Answer ===")
    print(final_answer)

question = "How has AI been evolving in the Healthcare sector?"
run_parallel_agents(question)

