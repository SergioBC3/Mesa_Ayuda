from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.lista_tickets, name='lista_tickets'),
    path('nuevo/', views.crear_ticket, name='crear_ticket'),
    path('<int:ticket_id>/', views.detalle_ticket, name='detalle_ticket'),
    path('<int:ticket_id>/editar/', views.editar_ticket, name='editar_ticket'),
    path('<int:ticket_id>/eliminar/', views.eliminar_ticket, name='eliminar_ticket'),
    path('estado/<str:estado>/', views.tickets_por_estado, name='tickets_por_estado'),
    path('faqs/', views.preguntas_frecuentes, name='preguntas_frecuentes'),
    path('asistente/', views.asistente_ia, name='asistente_ia'),
]
