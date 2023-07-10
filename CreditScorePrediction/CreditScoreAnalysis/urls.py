from django.urls import path

from . import views

urlpatterns = [
    # path('', views.preProcesing)
    path('', views.first_view, name='first_view'),
    path('second/', views.second_view, name='second_view'),
    path('third/', views.third_view, name='third_view'),
    path('result/', views.preProcessing, name='result')
]
