from django.urls import path
from . import views

app_name = 'tecnicos'

urlpatterns = [
    path('', views.lista_tecnicos, name='lista_tecnicos'),
    path('<int:tecnico_id>/', views.detalle_tecnico, name='detalle_tecnico'),
]
