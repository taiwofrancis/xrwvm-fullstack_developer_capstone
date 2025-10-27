from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
import logging, json

# 👉 NEW IMPORTS FOR CARS:
from .models import CarMake, CarModel
from .populate import initiate

logger = logging.getLogger(__name__)

# LOGIN
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


# LOGOUT
@csrf_exempt
def logout_request(request):
    try:
        logout(request)
        return JsonResponse({"status": "Logged out"})
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return JsonResponse({"status": "Error", "message": str(e)})


# REGISTRATION
@csrf_exempt
def registration(request):
    """
    Handle user sign-up.
    Expected JSON:
    {
        "userName": "...",
        "password": "...",
        "firstName": "...",
        "lastName": "...",
        "email": "..."
    }
    Response when successful:
    {
        "userName": "...",
        "status": "Authenticated"
    }
    If username is taken:
    {
        "userName": "...",
        "error": "Already Registered"
    }
    """
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("userName")
        password = data.get("password")
        first_name = data.get("firstName")
        last_name = data.get("lastName")
        email = data.get("email")

        username_exist = False

        # Check if username already exists
        try:
            User.objects.get(username=username)
            username_exist = True
        except User.DoesNotExist:
            logger.debug(f"{username} is a new user")

        if not username_exist:
            # create user
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
                email=email,
            )
            # log them in
            login(request, user)
            return JsonResponse({
                "userName": username,
                "status": "Authenticated"
            })
        else:
            return JsonResponse({
                "userName": username,
                "error": "Already Registered"
            })
    else:
        return JsonResponse({"status": "Invalid request method"})


# PLACEHOLDER VIEWS TO SATISFY URLS
def get_dealer_details(request, dealer_id):
    return JsonResponse({
        "dealer_id": dealer_id,
        "message": "Dealer details placeholder"
    })


def add_review(request, dealer_id):
    return JsonResponse({
        "dealer_id": dealer_id,
        "message": "Add review placeholder"
    })


# ✅ THE MISSING VIEW: get_cars
def get_cars(request):
    """
    Returns a JSON list of all car models and their make.
    If the DB is empty, auto-populate it first.
    """
    # Check if we already have data
    if CarMake.objects.count() == 0:
        # Seed the database with default car makes/models
        initiate()

    # Query all car models + the related make in one shot
    car_models = CarModel.objects.select_related('car_make')

    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name,
        })

    return JsonResponse({"CarModels": cars})
