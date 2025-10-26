from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'djangoapp'

urlpatterns = [
    # ---- AUTHENTICATION ROUTES ----
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('register/', views.registration, name='register'),  # <-- register endpoint

    # ---- DEALERSHIP PLACEHOLDER ROUTES ----
    path('dealer/<int:dealer_id>/', views.get_dealer_details, name='dealer_details'),
    path('review/<int:dealer_id>/', views.add_review, name='add_review'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
