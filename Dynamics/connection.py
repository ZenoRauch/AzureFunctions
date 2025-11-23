import os
import msal
import requests
import json

## Maybe for later
class Dynamics_Field:
    name: str
    value: str

class Dynamics_Record:
    GUID: int
    fields:list[Dynamics_Field]
    

class Dynamics_Options:
    logical_names=[
        
    ]
    ecb_dimensions:list[Dynamics_Record]
    sector_l1:list[Dynamics_Record]
    issues:list[Dynamics_Record]
    risk_drivers:list[Dynamics_Record]
    geography:list[Dynamics_Record]
    time_horizon:list[Dynamics_Record]
    likelihood:list[Dynamics_Record]
    severity:list[Dynamics_Record]
    idio:list[Dynamics_Record]
    

class Connection:
    def __init__(self):
        self.ACCESS_TOKEN = None
        self.CLIENT_ID = os.environ.get("CLIENT_ID")
        self.CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
        self.TENANT_ID = os.environ.get("TENANT_ID")
        self.RESOURCE_URL = os.environ.get("RESOURCE_URL")
        self.AUTHORITY_URL = f"https://login.microsoftonline.com/{self.TENANT_ID}"
        self.azure_app = msal.ConfidentialClientApplication(
            client_id=self.CLIENT_ID,
            client_credential=self.CLIENT_SECRET,
            authority=self.AUTHORITY_URL
        )
        
    def get_access_token(self):
        result = self.azure_app.acquire_token_for_client(scopes=[f"{self.RESOURCE_URL}/.default"])
        if "access_token" in result:
            access_token = result['access_token']
            headers = {
                'Authorization': f'Bearer {access_token}',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=utf-8',
                'Prefer': 'odata.include-annotations="*"',
            }
            api_url = f"{self.RESOURCE_URL}api/data/v9.2/accounts?$top=10"
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                self.ACCESS_TOKEN = access_token
                return True
            else:
                return False
        else:
            return False
        
    def load_required_information(self, entities):
        return_list = []
        self.get_access_token()
        for entity_name, entity_id, field_name in entities:
            return_list.append(self.execute_fetch(call=f"{entity_name}?$select={entity_id},{field_name}", field_name=field_name, field_id=entity_id))
        return return_list
    
    def execute_fetch(self, version:str="v9.2", call:str="accounts", field_name:str="name", field_id:str="accountid"):
        if not self.get_access_token():
            raise Exception("Token acquisition failed, cannot proceed with fetch.")
        url = f"{self.RESOURCE_URL}api/data/{version}/{call}"
        headers = {
            'Authorization': f'Bearer {self.ACCESS_TOKEN}',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Prefer': 'odata.include-annotations="*"',
        }
        response = requests.get(url, headers=headers)
        return_list = []
        json_data = json.loads(response.text)
        for item in json_data["value"]:
            return_list.append((item[field_id],item[field_name]))
        return return_list
            