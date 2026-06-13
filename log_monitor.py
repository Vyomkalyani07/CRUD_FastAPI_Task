import requests
import time

LOKI_URL = "http://localhost:3100/loki/api/v1/query_range"

while True:
    
    response=requests.get(
        LOKI_URL,
        params={
            "query": '{namespace="default"}' , 
            "limit": 5,
            "direction": "backward"
        }
    )
    
    data=response.json()
    
    for stream in data["data"]["result"]:
        for log in stream["values"]:
            message=log[1]
            print(message + "\n")
            
            if "error" in message.lower() or "warning" in message.lower():
                with open("alerts.log", "a") as f:
                    f.write(message + "\n")

    time.sleep(5)