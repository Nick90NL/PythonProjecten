import requests

def chat_with_gpt(prompt):
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY" # Vervang 'YOUR_API_KEY' door je eigen API-sleutel
    }
    data = {
        "model": "text-davinci-002", # Kies het gewenste model
        "prompt": prompt,
        "max_tokens": 150
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"]
    else:
        return "Er is een fout opgetreden bij het communiceren met de API."

while True:
    user_input = input("Jij: ")
    response = chat_with_gpt(user_input)
    print("AI: " + response)