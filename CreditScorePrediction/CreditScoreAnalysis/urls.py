from django.urls import path

from . import views

urlpatterns = [
    # path('', views.preProcesing)
    path('', views.Welcome, name='Welcome'),
    path('second/', views.first_view, name='first_view'),
    path('third/', views.second_view, name='second_view'),
    path('fourth/', views.third_view, name='third_view'),
    path('customerList/', views.cutomerList, name='customerList')
    # path('result/', views.result_view, name='result_view')
]
