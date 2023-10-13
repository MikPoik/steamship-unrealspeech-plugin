import requests

url = 'https://api.v6.unrealspeech.com/stream'
headers = {'Authorization': 'Bearer '}

data = {
    "Text": "Hi there",
    "VoiceId": "Liv",
    "Bitrate": "192k",
    "Pitch": 1.02,
    "Speed": 0.1
}

response = requests.post(url, headers=headers, json=data)

# Check the response
if response.status_code == 200:
  print("Request was successful")
  print(response.json())
else:
  print("Request failed with status code:", response.status_code)
  print(response.text)
