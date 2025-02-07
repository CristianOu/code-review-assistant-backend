from fastapi import APIRouter, HTTPException, Header
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import httpx
import certifi
import re
from huggingface_hub import InferenceClient
import os
from friendli import Friendli

# Set your Friendli API token
api_token = os.getenv("FRIENDLI_TOKEN")

# Initialize the Friendli client
client = Friendli(token=api_token)

# Dummy router for authentication
router = APIRouter()

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Running on: {device}")

# Function to Generate Review Comments

def generate_code_review_comment(diff_hunk):
  prompt = f"Review these Git changes and provide concise feedback:\n{diff_hunk}"
  # Create the message payload
  messages = [
    {
      "role": "user",
      "content": prompt,
    },
  ]
  
  # CAREFUL WITH THIS SECTION, RUNNING THIS WILL COST YOU MONEY
  # Send the request to the Friendli API
  # response = client.chat.completions.create(
  #   model='meta-llama-3.1-70b-instruct',
  #   messages=messages,
  #   stream=False,
  #   max_tokens=1024,  # Ensures concise yet informative reviews
  #   temperature=1,  # Reduces randomness, making feedback more factual
  #   top_p=0.8,  # Keeps responses focused while allowing some variation
  #   frequency_penalty=0.2,  # Minimizes repetitive phrases
  #   presence_penalty=0.1,  # Encourages introduction of new ideas
  # )

  # ai_comment = response.choices[0].message.content
  # END OF CAREFUL SECTION
  
  ai_comment = "This is a placeholder comment from the AI model."
  
  return ai_comment


# def filter_relevant_changes(diff):
#   return "\n".join([line for line in diff.splitlines() if line.startswith("+")])


# Function to Split Diff into Hunks
def split_diff_into_hunks(diff):
  hunks = re.split(r"(@@.*?@@)", diff)
  return [hunks[i] + hunks[i + 1] for i in range(1, len(hunks) - 1, 2)]

@router.get("/pr")
async def analyze_pr(owner: str, repo: str, pr_number: int, token: str):
  headers = {"Authorization": f"Bearer {token}"}

  try:
    # Fetch PR Changes from GitHub
    async with httpx.AsyncClient(verify=certifi.where()) as client:
      pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
      response = await client.get(pr_url, headers=headers)
      response.raise_for_status()

    files_changed = response.json()
    # print(f"Files changed in PR: {files_changed}")

    comments = []
    for file in files_changed:
      diff = file.get("patch", "")
      if not diff:
        continue

       # Split Diff into Hunks
      hunks = split_diff_into_hunks(diff)

      for hunk in hunks:
        # Generate AI Comment for Each Hunk
        suggestion = generate_code_review_comment(hunk)
        # print('====hunk:', hunk, '=====\n')

        # # Prepare Comment Data
        comment_data = {
            "body": f"**AI Suggestion:** {suggestion}",
            "path": file["filename"],
            "position": 5  # Adjust based on actual line position
        }
        comments.append(comment_data)

        # Post Comment Back to GitHub
        comment_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        async with httpx.AsyncClient() as client:
            await client.post(comment_url, headers=headers, json=comment_data)

    return {"status": "Analysis complete. Check GitHub for AI comments"}

  except httpx.HTTPStatusError as e:
    print(f"GitHub API error: {e}")
    raise HTTPException(status_code=400, detail="Failed to fetch PR data")
  except Exception as e:
    print(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal Server Error")
  
# TODO 1: Implement the code review analysis logic
