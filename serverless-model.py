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
	...
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
# print('==========Content==========', response.choices[0].message.content, '==========Content==========')

