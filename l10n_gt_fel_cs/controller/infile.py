import requests
import json

class InFile:
   
    def _testapi(self):
        api_url  = "http://168.232.76.230:8083/api/SSCApi/test/1"
        response = requests.get(api_url)
        #data = json.loads(response.text)        
        return response.text
    
    def _getapi(self):
        api_url  = "http://168.232.76.230:8083/api/SSCApi/clientes"
        response = requests.get(api_url)
        data = json.loads(response.text)
        return data

