import requests

base_url = "https://dummyjson.com"

def get_produtos():
    url = f"{base_url}/products"
    dados = requests.get(url)
    return dados.json()
