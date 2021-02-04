from django.urls import path
from caja import views


urlpatterns = [
    path('', views.ListadoView.as_view(), name='index'),
    path('finalizar/', views.finalizar, name='finalizar'),
]
