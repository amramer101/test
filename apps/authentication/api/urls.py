from django.urls import path
from .views import RegisterView, LoginView, LogoutView, PasswordResetView, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
