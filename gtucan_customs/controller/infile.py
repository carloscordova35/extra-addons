import requests


def _testapi():
    api_url  = "http://168.232.76.230:8083/api/SSCApi/test/1"
    response = requests.get(api_url)
    response.json()