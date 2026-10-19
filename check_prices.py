import urllib.request, json

data = json.loads(urllib.request.urlopen('http://127.0.0.1:5000/api/catalog/1').read().decode('utf-8'))
for opt in data['product']['options']:
    print(f"{opt['duration']}: PHP {opt['price']}")
