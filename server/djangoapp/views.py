from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
import logging, json

# Cars / seeding
from .models import CarMake, CarModel
from .populate import initiate

# Backend/microservice helpers
from .restapis import (
    get_request,
    analyze_review_sentiments,
    post_review,
)

logger = logging.getLogger(__name__)


# ===========================
# AUTH VIEWS
# ===========================

@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")

            user = authenticate(username=username, password=password)
            resp = {"userName": username}

            if user is not None:
                login(request, user)
                resp["status"] = "Authenticated"
            else:
                resp["status"] = "Invalid"

            return JsonResponse(resp)
        except Exception as e:
            logger.error(f"Login error: {e}")
            return JsonResponse({"status": "Error", "message": str(e)})
    else:
        return JsonResponse({"status": "Invalid request method"})


@csrf_exempt
def logout_request(request):
    try:
        logout(request)
        return JsonResponse({"status": "Logged out"})
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return JsonResponse({"status": "Error", "message": str(e)})


@csrf_exempt
def registration(request):
    """
    Expected JSON:
    {
        "userName": "...",
        "password": "...",
        "firstName": "...",
        "lastName": "...",
        "email": "..."
    }
    """
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("userName")
        password = data.get("password")
        first_name = data.get("firstName")
        last_name = data.get("lastName")
        email = data.get("email")

        # check if username exists
        try:
            User.objects.get(username=username)
            # already registered
            return JsonResponse({
                "userName": username,
                "error": "Already Registered"
            })
        except User.DoesNotExist:
            pass  # good, we can create

        # create user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )

        # auto-login new user
        login(request, user)

        return JsonResponse({
            "userName": username,
            "status": "Authenticated"
        })

    else:
        return JsonResponse({"status": "Invalid request method"})


# ===========================
# CAR INVENTORY VIEW
# ===========================

@csrf_exempt
def get_cars(request):
    """
    Returns a JSON list of all car models and their makes.
    Seeds the DB if empty.
    """
    if CarMake.objects.count() == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for cm in car_models:
        cars.append({
            "CarModel": cm.name,
            "CarMake": cm.car_make.name,
        })

    return JsonResponse({"CarModels": cars})


# ===========================
# DEALERSHIP / REVIEWS VIEWS
# ===========================

def get_dealerships(request, state="All"):
    """
    GET /djangoapp/get_dealers
    GET /djangoapp/get_dealers/<state>
    """
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    """
    GET /djangoapp/dealer/<dealer_id>
    Calls backend /fetchDealer/<id>
    """
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_reviews(request, dealer_id):
    """
    GET /djangoapp/reviews/dealer/<dealer_id>
    - Fetch reviews for this dealer from backend
    - For each review, call sentiment analyzer
    - Attach 'sentiment' to each review
    """
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)

        # reviews is expected to be a list of dicts
        for review_detail in reviews:
            # analyze the sentiment of 'review' field
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response.get('sentiment', 'unknown')

        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


@csrf_exempt
def add_review(request):
    """
    POST /djangoapp/add_review
    Body should contain review payload:
    {
        "dealership": <dealer_id>,
        "name": "...",
        "review": "...",
        "purchase": true/false,
        "purchase_date": "...",
        "car_make": "...",
        "car_model": "...",
        "car_year": 2024
    }

    Requires user to be authenticated (unless you remove that check for testing).
    """
    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Forward to backend Node service
            resp = post_review(data)

            return JsonResponse({"status": 200, "result": resp})
        except Exception as e:
            logger.error(f"Error in add_review: {e}")
            return JsonResponse({
                "status": 401,
                "message": "Error in posting review",
                "error": str(e)
            })
    else:
        return JsonResponse({"status": "Invalid request method"})
