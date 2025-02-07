from fastapi import APIRouter, HTTPException
import httpx
import certifi
import re
import os
from friendli import Friendli

# Set your Friendli API token
api_token = os.getenv("FRIENDLI_TOKEN")

# Initialize the Friendli client
client = Friendli(token=api_token)

# Dummy router for authentication
router = APIRouter()

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
  response = client.chat.completions.create(
    model='meta-llama-3.1-70b-instruct',
    messages=messages,
    stream=False,
    max_tokens=1024,  # Ensures concise yet informative reviews
    temperature=1,  # Reduces randomness, making feedback more factual
    top_p=0.8,  # Keeps responses focused while allowing some variation
    frequency_penalty=0.2,  # Minimizes repetitive phrases
    presence_penalty=0.1,  # Encourages introduction of new ideas
  )

  ai_comment = response.choices[0].message.content
  # END OF CAREFUL SECTION
  
  # Placeholder comment
  # ai_comment = "This is a placeholder comment from the AI model."
  
  return ai_comment


# Function to Split Diff into Hunks
def split_diff_into_hunks(diff):
  """
  Splits a Git diff into separate hunks while avoiding false matches
  inside string literals.
  """
  # Updated regex: Only match @@ ... @@ at the beginning of a line
  hunk_headers = re.finditer(r"^\s*@@ -\d+,\d+ \+(\d+),(\d+) @@", diff, re.MULTILINE)

  hunks = []
  last_index = 0

  for match in hunk_headers:
    start = match.start()
    
    # Append previous section (if any)
    if last_index < start:
      hunks.append(diff[last_index:start])

    last_index = start

  # Append the final hunk
  if last_index < len(diff):
    hunks.append(diff[last_index:])

  return hunks

# Function to Extract Line Position from Diff Hunk
def extract_line_position(hunk):
  match = re.search(r"\@\@ -\d+,\d+ \+(\d+),(\d+) \@\@", hunk)
  if match:
    start_line = int(match.group(1))  # Extract starting line of new file
    num_lines = int(match.group(2))   # Number of affected lines
    return start_line, num_lines
  return None, None  # In case of an invalid diff format

async def get_commit_sha(owner, repo, pr_number, token):
  """Fetches the latest commit SHA for the PR."""
  headers = {"Authorization": f"Bearer {token}"}
  async with httpx.AsyncClient(verify=certifi.where()) as client:
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response = await client.get(pr_url, headers=headers)
    response.raise_for_status()
    return response.json()["head"]["sha"]

@router.get("/pr")
async def analyze_pr(owner: str, repo: str, pr_number: int, token: str):
  try:
    # Fetch the latest commit SHA (Required for Reviews)
    commit_id = await get_commit_sha(owner, repo, pr_number, token)
    # print(f"Latest commit SHA: {commit_id}")

    # Fetch PR Changes from GitHub
    async with httpx.AsyncClient(verify=certifi.where()) as client:
      pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
      headers = {"Authorization": f"Bearer {token}"}  # GitHub API Token
      response = await client.get(pr_url, headers=headers)
      response.raise_for_status()
      files_changed = response.json()

    valid_positions = {
      file["filename"]: len(file["patch"].split("\n"))
      for file in response.json()
      if "patch" in file
    }

    # print(f"valid_positions: {valid_positions}")

    comments = []
    for file in files_changed:
      diff = file.get("patch", "")
      if not diff:
        continue

       # Split Diff into Hunks
      hunks = split_diff_into_hunks(diff)

      for hunk in hunks:
        # Extract starting line number
        start_line, num_lines = extract_line_position(hunk)
        if start_line is None:
          continue  # Skip if we cannot extract the position

        file_path = file["filename"]
        # Ensure AI comment position is within valid PR changes
        if file_path in valid_positions:
          max_valid_position = valid_positions[file_path]
          # Determine comment placement
          comment_position = min(start_line + (num_lines // 2), max_valid_position - 1)
         # Generate AI Comment for Each Hunk
          suggestion = generate_code_review_comment(hunk)
          # Construct Review Comment
          comments.append({
            "path": file_path,
            "position": comment_position,
            "body": suggestion
          })

    # print(f"AI Comments: {comments}")
    # Construct Review Payload
    if not comments or len(comments) == 0 or commit_id is None:
      return {"status": "No valid AI comments generated or commit_id is invalid. PR unchanged."}

    payload = {
      "commit_id": commit_id,
      "event": "COMMENT",  # Can be "APPROVE" or "REQUEST_CHANGES"
      "body": "AI-generated review comments for this PR.",
      "comments": comments
    }

    print(f"Review Payload: {payload}")

    # # Submit AI Review to GitHub
    headers = {
      "Authorization": f"Bearer {token}",
      "Accept": "application/vnd.github.v3+json"
    }
    review_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    async with httpx.AsyncClient(verify=certifi.where()) as client:
      review_response = await client.post(review_url, headers=headers, json=payload)
      review_response.raise_for_status()

    return {"status": "AI Review submitted successfully!", "comments": comments}

  except httpx.HTTPStatusError as e:
    print("GitHub API Response:", review_response.text)  # Full error details
    print(f"GitHub API error: {e}")
    raise HTTPException(status_code=400, detail="Failed to fetch PR data")
  except Exception as e:
    print(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal Server Error")