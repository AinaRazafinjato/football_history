from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('homepage-test/', views.homepage_test, name='homepage_test'),
]
