import requests

class NetworkHelper:
    def __init__(self, base_url, token=None):
        self.base_url = base_url.rstrip("/") + "/"
        self.headers = {"Authorization": f"Token {token}"} if token else {}

    def get(self, endpoint="", params=None):
        url = self.base_url + endpoint.lstrip("/")
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return response.text

    def post(self, endpoint="", data=None):
        url = self.base_url + endpoint.lstrip("/")
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint="", data=None):
        url = self.base_url + endpoint.lstrip("/")
        response = requests.put(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint=""):
        url = self.base_url + endpoint.lstrip("/")
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return {"status": response.status_code, "text": response.text}
    
    def get_clients(self):
        return self.get("clients/")
    
    def get_items(self):
        return self.get("items/")
    
    def get_client_by_id(self, client_id):
        return self.get(f"clients/{client_id}/")
    
    def get_item_by_id(self,item_id):
        return self.get(f"items/{item_id}/")

    
    def delete_client(self, pk):
        return self.delete(f"clients/{pk}/")
    
    def delete_item(self, pk):
        return self.delete(f"items/{pk}/")
