from django.db import models
from tecnicos.models import Tecnico

ESTADOS = [
    ('abierto', 'Abierto'),
    ('cerrado', 'Cerrado'),
]


class Ticket(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='abierto')
    tecnico = models.ForeignKey(Tecnico, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')

    def __str__(self):
        return self.titulo
