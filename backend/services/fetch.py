#API Requests
import requests
import base64
from requests.exceptions import Timeout, RequestException
 
def fetch_data(url):
    try:
        #response = requests.get(url, timeout=10)
        #print("Status:", response.status_code)
        #print("Response:", response.text)
   
        #if response.status_code == 200:

        if True: #DELETE WHEN NEW API IS RECEIVED

            #packet_data = response.json()
            #raw_b64 = packet_data.get("raw")

            #DELETE BELOW LINE WHEN API IS RECEIVED
            raw_b64 = "jv////8KBgHJkeEAAAAA8Q8AAGvNTdYiAEJSSyBNVyBWRVI6MDVhXzAxAAAAAAAUAQDNCwAAAAIeAAizCpqo3QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACUAAwDy//f/AAAAAAAAHQQEDw8PDw8PABgBomSSIAioMgIAAAwAAK0DKgriBBwdGQAgEJ4gaxY="
       
            if raw_b64:
                hex_data = base64.b64decode(raw_b64).hex().upper()
                raw_data = base64.b64decode(raw_b64)
                print("Packet Found")
                print(f"Raw Hex: {hex_data}")
                return [raw_data, hex_data]
            else:
                print("No raw data found in response.")
        else:
            print("Failed to contact server.")
    except Timeout:
        print("Response timed out.")
    except RequestException as e:
        print(f"Request error: {e}")