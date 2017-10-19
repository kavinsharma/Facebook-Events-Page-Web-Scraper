import requests

address = "Pllazio Hotel, Gurgaon 292-296, Sector 29,  Gurgaon, Gurgaon, Haryana 122001"
response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address= '+ address)
resp_json_payload = response.json()

a = (resp_json_payload['results'][0]['geometry']['location']).values()

