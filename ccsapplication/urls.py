from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('index0/', views.index0, name='index0'),
    path('get_data/', views.get_data, name='get_data'),
    path('get_machine_list/', views.get_machine_list, name='get_machine_list'),
    path('update_data/', views.update_data, name='update_data'),
]
