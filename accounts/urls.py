from django.contrib import admin
from django.urls import path, include
from .views import SignUpView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', 
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True
        ),
        name="login",),
    path('signup/', SignUpView.as_view(), name="signup")
]
