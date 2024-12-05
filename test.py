import requests

body = {"sleep": 1, "eat": 1, "water": 1, 
              "social": 1, "overall": 1, "notes": "some shit"}
url = "https://4ihkk36ted.execute-api.us-east-2.amazonaws.com/test/upload-entry/80001"
res = requests.post(url, json=body)
print(res)