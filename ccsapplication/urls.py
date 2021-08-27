from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('index0/', views.index0, name='index0'),
    path('get_data/', views.get_data, name='get_data'),
    path('get_data0/', views.get_data0, name='get_data0'),
    path('get_machine_list/', views.get_machine_list, name='get_machine_list'),
    path('get_exp_hrs/', views.get_exp_hrs, name='get_exp_hrs'),
    path('update_data/', views.update_data, name='update_data'),
]
