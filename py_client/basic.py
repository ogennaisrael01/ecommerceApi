import requests
import json

endpoint = "http://localhost:8000/product/"
data = {
    "email": "ogennaisrael@gmail.com",
    "password": "0987poiu"
}

get_response = requests.get(endpoint) # Get an endpoint 
print(get_response.text)