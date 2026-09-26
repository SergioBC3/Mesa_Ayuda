from django.urls import path
from . import views

app_name = 'tecnicos'

urlpatterns = [
    path('', views.lista_tecnicos, name='lista_tecnicos'),
    path('nuevo/', views.crear_tecnico, name='crear_tecnico'),
    path('<int:tecnico_id>/', views.detalle_tecnico, name='detalle_tecnico'),
    path('<int:tecnico_id>/editar/', views.editar_tecnico, name='editar_tecnico'),
    path('<int:tecnico_id>/eliminar/', views.eliminar_tecnico, name='eliminar_tecnico'),
]