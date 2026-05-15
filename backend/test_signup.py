import json
from urllib.request import Request, urlopen

url = 'http://localhost:8000/signup'
data = {'name': 'Test User', 'email': 'test4@example.com', 'password': 'pass'}
b = json.dumps(data).encode('utf-8')
req = Request(url, data=b, headers={'Content-Type': 'application/json'})
with urlopen(req) as resp:
    print('status', resp.status)
    body = resp.read().decode('utf-8')
    print('body', body)
