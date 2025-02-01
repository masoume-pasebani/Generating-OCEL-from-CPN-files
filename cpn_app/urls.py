
from django.urls import path
from . import views


app_name = 'cpn_app'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('index/', views.index, name='index'),
    path('generate_ocel/<int:file_id>/', views.generate_ocel2, name='generate_ocel'),
    path('visualize/<int:file_id>/', views.visualize_cpn, name='visualize_cpn'),
    path('visualize_cpn_graph/<int:file_id>/', views.visualize_cpn2, name='visualize_cpn_graph'),
    path('login/', views.Login, name='login'),  # This is the correct URL name
    path('register/', views.Register, name='register'),  # Same here for 'register'
    path('logout/', views.Logout, name='logout'),

    ]