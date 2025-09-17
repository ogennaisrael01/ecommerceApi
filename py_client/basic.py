import requests
import json

endpoint = "http://localhost:8000/product/?slug=chike-and-the-river"

get_response = requests.get(endpoint) # Get an endpoint 
print(get_response.text)