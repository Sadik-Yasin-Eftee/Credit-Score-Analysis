from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    # path('', views.preProcesing)
    path('', views.welcome, name='welcome'),
    path('first/', views.formPage, name='formPage'),
    path('second/', views.first_view, name='first_view'),
    path('third/', views.second_view, name='second_view'),
    path('fourth/', views.third_view, name='third_view'),
    path('customerList/', views.cutomerList, name='customerList')
    # path('result/', views.result_view, name='result_view')
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
