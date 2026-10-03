from django import forms

from tecnicos.models import Tecnico
from .models import ESTADOS


class TicketForm(forms.Form):
    titulo = forms.CharField(max_length=150)
    descripcion = forms.CharField(widget=forms.Textarea)
    estado = forms.ChoiceField(choices=ESTADOS, initial='abierto')
    tecnico = forms.ModelChoiceField(queryset=Tecnico.objects.all(), required=False,
                                     empty_label='Sin asignar')

    def a_payload(self):
        """Diccionario que se envia a los microservicios."""
        d = self.cleaned_data
        return {
            'titulo': d['titulo'],
            'descripcion': d['descripcion'],
            'estado': d['estado'],
            'tecnico': d['tecnico'].nombre if d['tecnico'] else None,
        }
