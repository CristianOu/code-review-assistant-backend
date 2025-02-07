import os
from friendli import Friendli

# Set your Friendli API token
api_token = os.getenv("FRIENDLI_TOKEN")

# Initialize the Friendli client
client = Friendli(token=api_token)

# Define your prompt
prompt = '''Review these Git changes and provide concise feedback where relevant:
@@ -12,21 +13,62 @@

 # Function to Generate Review Comments

+def generate_code_review_comment(diff):
+  prompt = f"Review the following code changes and provide constructive feedback:\n{diff}"
+  print('prompt111', prompt, 'end prompt111')
+  inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
+  outputs = model.generate(inputs.input_ids, max_length=100, num_return_sequences=1)
+  comment = tokenizer.decode(outputs[0], skip_special_tokens=True)
+  return comment
+
+
+def filter_relevant_changes(diff):
+  return "\n".join([line for line in diff.splitlines() if line.startswith("+")])


 @router.get("/pr")
-async def analyze_pr(owner: str, repo: str, pr_number: int, token: str = Header(...)):
+async def analyze_pr(owner: str, repo: str, pr_number: int, token: str):        
   headers = {"Authorization": f"Bearer {token}"}

   try:
     # Fetch PR Changes from GitHub
-    async with httpx.AsyncClient() as client:
+    async with httpx.AsyncClient(verify=certifi.where()) as client:
       pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
       response = await client.get(pr_url, headers=headers)
       response.raise_for_status()

     files_changed = response.json()
-    print(f"Files changed in PR: {files_changed}")
+    # print(f"Files changed in PR: {files_changed}")
+
+    comments = []
+    for file in files_changed:
+      diff = file.get("patch", "")
+      if not diff:
+        continue
+
+      relevant_diff = filter_relevant_changes(diff)
+      print('====relevant_diff:', relevant_diff, '===========\n')
+      # Generate AI Comment
+      # print(diff, '===========')
+      suggestion = generate_code_review_comment(relevant_diff)
+      print('======suggestion:', suggestion, '======')
+
+      # print(f"Suggestion for {file['filename']}: {suggestion}")
+
+      # # Prepare Comment Data
+      # comment_data = {
+      #   "body": f"**AI Suggestion:** {suggestion}",
+      #   "path": file["filename"],
+      #   "position": 5  # Adjust based on diff context
+      # }
+      # comments.append(comment_data)
+
+      # # Post Comment Back to GitHub
+      # comment_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
+      # async with httpx.AsyncClient() as client:
+      #   await client.post(comment_url, headers=headers, json=comment_data)    
+
+
     return {"status": "Analysis complete", "files_changed": files_changed}      

   except httpx.HTTPStatusError as e:
'''

# Create the message payload
messages = [
    {
        "role": "user",
        "content": prompt,
    },
]

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
print('==========Content==========', response.choices[0].message.content, '==========Content==========')

