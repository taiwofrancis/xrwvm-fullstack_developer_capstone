import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', default="http://localhost:5050/")

# 1. Helper to GET data from backend service (dealers, reviews, etc.)
def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params += f"{key}={value}&"

    # build full URL
    request_url = backend_url + endpoint
    if params:
        request_url += "?" + params

    print(f"[GET] {request_url}")
    try:
        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"❌ Network exception occurred in get_request: {err}")
        return {"error": str(err)}

# 2. Helper to call sentiment analyzer microservice
def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    print(f"[SENTIMENT] {request_url}")
    try:
        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")
        return {"sentiment": "unknown"}

# 3. Helper to POST a new review to backend
def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    print(f"[POST] {request_url} with data {data_dict}")
    try:
        response = requests.post(request_url, json=data_dict)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"❌ Network exception occurred in post_review: {err}")
        return {"error": str(err)}
