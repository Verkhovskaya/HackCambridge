import requests
import json


def translate(sentence, language_code):
    subscriptionKey = "8d5513fd10064d7c94e415a30e438c4f"
    base_url = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&to=' + language_code
    constructed_url = base_url + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-type': 'application/json'
    }

    # You can pass more than one object in body.
    body = [{
        'text': sentence
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()

    return response[0]["translations"][0]["text"]