from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import asyncio
from typing import Tuple, Dict
import ast

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

def evaluate_python_code(code: str) -> Tuple[bool, str]:
    """
    Evaluates Python code for syntax and basic quality checks.
    Returns (passed, feedback).
    """
    # First check if code is syntactically valid
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax Error: {str(e)}"
    
    client = OpenAI()
    
    evaluation_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """You are a Python Code Evaluator. Evaluate the code for:
            1. Code style (PEP 8)
            2. Best practices
            3. Potential bugs
            4. Performance issues
            5. Security concerns
            
            Return a JSON-like response with two fields:
            - passed: true/false
            - feedback: detailed explanation of issues or confirmation of quality
            
            Be strict but fair in your evaluation."""},
            {"role": "user", "content": f"Evaluate this Python code:\n```python\n{code}\n```"}
        ]
    )
    
    # Parse the evaluation response
    eval_text = evaluation_response.choices[0].message.content
    try:
        # Extract passed/feedback from the response
        if "passed: true" in eval_text.lower():
            passed = True
        else:
            passed = False
        feedback = eval_text.split("feedback:", 1)[1].strip() if "feedback:" in eval_text else eval_text
        return passed, feedback
    except Exception as e:
        return False, f"Error parsing evaluation: {str(e)}"

def optimize_code(code: str, feedback: str) -> str:
    """
    Optimizes the code based on evaluation feedback.
    """
    client = OpenAI()
    
    optimization_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """You are a Python Code Optimizer. 
            Improve the code based on the provided feedback while maintaining its core functionality.
            Return ONLY the improved code without any explanations."""},
            {"role": "user", "content": f"""
            Original code:
            ```python
            {code}
            ```
            
            Feedback to address:
            {feedback}
            
            Please provide the optimized code:"""}
        ]
    )
    
    return optimization_response.choices[0].message.content

async def evaluator_optimizer_workflow(initial_code: str, max_iterations: int = 5) -> Tuple[bool, str, str]:
    """
    Main workflow that evaluates and optimizes code until it passes or hits max iterations.
    
    Args:
        initial_code (str): The initial Python code to evaluate
        max_iterations (int): Maximum number of optimization attempts
        
    Returns:
        Tuple[bool, str, str]: (success, final_code, feedback)
    """
    current_code = initial_code
    iteration = 0
    
    while iteration < max_iterations:
        print(f"\n=== Iteration {iteration + 1} ===")
        
        # Evaluate current code
        passed, feedback = evaluate_python_code(current_code)
        
        print("\nEvaluation Feedback:")
        print(feedback)
        
        if passed:
            print("\n✅ Code passed evaluation!")
            return True, current_code, feedback
        
        print("\nOptimizing code based on feedback...")
        # Optimize code based on feedback
        current_code = optimize_code(current_code, feedback)
        
        print("\nOptimized Code:")
        print(current_code)
        
        iteration += 1
    
    return False, current_code, "Max iterations reached without passing evaluation"

def run_code_evaluation(code: str) -> None:
    """
    Wrapper function to run the async workflow.
    
    Args:
        code (str): The Python code to evaluate and optimize
    """
    success, final_code, feedback = asyncio.run(evaluator_optimizer_workflow(code))
    
    print("\n=== Final Results ===")
    print("Status:", "✅ Passed" if success else "❌ Failed")
    print("\nFinal Code:")
    print(final_code)
    print("\nFinal Feedback:")
    print(feedback)

# Example usage:
code_to_evaluate = """
def calc(x,y):
    z=x+y
    return z
"""

run_code_evaluation(code_to_evaluate)