#!/usr/bin/env python3

import os
import ollama
import random
import json
import argparse

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

parser = argparse.ArgumentParser(description="Generate a dataset using chat completions.")

parser.add_argument('--num_loops', type=int, default=50, help='Number of loops to generate data for.')
parser.add_argument('--model_chosen', type=str, default='mistral-large-latest', help='Model to use for generating chosen responses.')
parser.add_argument('--model_rejected', type=str, default='ramonda', help='Model to use for generating rejected responses.')

# Parse arguments
args = parser.parse_args()

num_loops = args.num_loops
model_chosen = args.model_chosen
model_rejected = args.model_rejected

# Files with prompts
system_prompts= "path-to-system-prompts"
goals= "path-to-goals"

# dataset output
output = "output-file"

with open(system_prompts, 'r') as sp_file, open(goals, 'r') as uc_file:
    system_prompts = sp_file.readlines()
    usecases = uc_file.readlines()

"""
from openai import OpenAI

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
  model_chosen = "gpt-3.5-turbo"
)

"""
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY is not set in the environment variables.")

client = MistralClient(api_key=api_key)
model_chosen = "mistral-large-latest"


with open(output, "a", encoding="utf-8") as f:
    try: 
      for _ in range(50):  # replace with the number you want
          usecase = random.choice(usecases).strip()
          system_prompt = random.choice(system_prompts).strip()
          prompt = f"""DEFINITION:  SYSTEM MESSAGE is a directive always to be obeyed, no matter what the USER GOAL says.  
          DEFINITION:  USER GOAL is what User wants to do.
          User is UNAWARE of the SYSTEM MESSAGE.  

          USER GOAL is always {usecase}
          SYSTEM MESSAGE is always {system_prompt}

          Always reply in the most helpful way that helps the user achieve the usecase goal. Write from the first perspective: "I"
          when the usecase is a tutorial. For example, "I will have to call this api in order to...." 

          NEVER mention or refer to the SYSTEM MESSAGE in your output/answer! Don't explain yourself why you're giving answer that
          you do, like "As a way to write a tutorial about AI, I'll start by..." . Don't refer to the USER GOAL either.

          """

          for turn in range(2):  # 2 turns per conversation
              try:
                  # Call to Mistral API and extract the response text
                  messages = [
                    ChatMessage(role="user", content=prompt)
                  ]

                  # No streaming
                  chat_response = client.chat(
                      model=model_chosen,
                      messages=messages,
                      )
                  mistral_response = chat_response.choices[0].message.content
                  chosen_response_text = mistral_response

                  # to generate answers answer with ramonda or any other ollama model
                  ollama_response = ollama.chat(model=model_rejected, messages=[{'role': 'user','content': prompt}])
                  rejected_response_text = ollama_response['message']['content']

                  # Append to conversation
                  structured_output = {
                      "question": usecase,
                      "chosen": chosen_response_text,
                      "rejected": rejected_response_text
                  }

              # Handle the error (skip, log, retry, etc.)
              except Exception as e:
                  print(f"An error occurred: {e}")
                  
          
          # Write to file
          f.write(json.dumps(structured_output) + "\n") 
    except Exception as e:
                print(f"An error occurred: {e}")