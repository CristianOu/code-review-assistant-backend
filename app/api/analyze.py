from fastapi import APIRouter, HTTPException, Header
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import httpx

# Dummy router for authentication
router = APIRouter()

# Load CodeT5+ Model
model_name = "Salesforce/codet5p-220m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Function to Generate Review Comments

def generate_code_review_comment(diff):
  prompt = f"Review the following code changes and provide constructive feedback:\n{diff}"
  inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
  outputs = model.generate(inputs.input_ids, max_length=100, num_return_sequences=1)
  comment = tokenizer.decode(outputs[0], skip_special_tokens=True)
  return comment

@router.get("/pr")
async def analyze_pr(owner: str, repo: str, pr_number: int, token: str = Header(...)):
  headers = {"Authorization": f"Bearer {token}"}

  try:
    # Fetch PR Changes from GitHub
    async with httpx.AsyncClient() as client:
      pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
      response = await client.get(pr_url, headers=headers)
      response.raise_for_status()

    files_changed = response.json()
    print(f"Files changed in PR: {files_changed}")
    return {"status": "Analysis complete", "files_changed": files_changed}

  except httpx.HTTPStatusError as e:
    print(f"GitHub API error: {e}")
    raise HTTPException(status_code=400, detail="Failed to fetch PR data")
  except Exception as e:
    print(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal Server Error")
  
# TODO 1: Implement the code review analysis logic
