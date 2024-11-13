import os
import requests
import json

# Define directory and API key
directory = "LEGAL_FILE_DIRECTORY"
api_key = "OPENROUTER_API"

# Initialize a dictionary to store summaries
summaries

# Iterate over all .txt files in the specified directory
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        file_path = os.path.join(directory, filename)
        
        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            document = file.read()
        
        # Set up the request to OpenRouter API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://localhost:8000",  # Required by OpenRouter
                "X-Title": "Python Script"  # Optional but recommended
            },
            data=json.dumps({
                "model": "nousresearch/hermes-3-llama-3.1-405b:free",  # Optional
                "messages": [
                    {
                        "role": "user",
                        "content": f"donnez le résumé bref de ce document : {document}"
                    }
                ]
            })
        )

        # Parse and store the summary if the request was successful
        if response.status_code == 200:
            try:
                summary = response.json()['choices'][0]['message']['content']
                summaries[filename] = summary
            except (KeyError, IndexError) as e:
                print(f"Error retrieving summary for {filename}: {e}")
        else:
            print(f"Failed to retrieve summary for {filename}. Status code: {response.status_code}")
y_1 = ''
for key in summaries.keys():
    y +=f" '{key}' : {summaries[key]}"
    y += """---------------------------------------------------------------------------------------"""

with open("resume_docs_juridiques.txt", 'w', encoding = 'utf-8') as file:
    file.write(y_1)
