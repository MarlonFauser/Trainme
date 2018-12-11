from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contato', views.contact, name='contato'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
]
