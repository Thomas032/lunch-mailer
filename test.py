import requests

URL = "http://127.0.0.1:5000/auth"

data = {
    "email":"judobartos@seznam.cz",
    "time": "10:50",
    
}
response = requests.patch(URL, data)
print(response.json())