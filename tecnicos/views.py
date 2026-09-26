from django.shortcuts import render, get_object_or_404, redirect
from .models import Tecnico
from .forms import TecnicoForm


def lista_tecnicos(request):
    tecnicos = Tecnico.objects.all()
    contexto = {'tecnicos': tecnicos}
    return render(request, 'tecnicos/lista_tecnicos.html', contexto)


def detalle_tecnico(request, tecnico_id):
    tecnico = get_object_or_404(Tecnico, pk=tecnico_id)
    tickets = tecnico.tickets.all()
    contexto = {'tecnico': tecnico, 'tickets': tickets}
    return render(request, 'tecnicos/detalle_tecnico.html', contexto)


def crear_tecnico(request):
    if request.method == 'POST':
        form = TecnicoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tecnicos:lista_tecnicos')
    else:
        form = TecnicoForm()
    return render(request, 'tecnicos/formulario_tecnico.html',
                  {'form': form, 'titulo_pagina': 'Nuevo técnico'})


def editar_tecnico(request, tecnico_id):
    tecnico = get_object_or_404(Tecnico, pk=tecnico_id)
    if request.method == 'POST':
        form = TecnicoForm(request.POST, instance=tecnico)
        if form.is_valid():
            form.save()
            return redirect('tecnicos:detalle_tecnico', tecnico_id=tecnico.id)
    else:
        form = TecnicoForm(instance=tecnico)
    return render(request, 'tecnicos/formulario_tecnico.html',
                  {'form': form, 'titulo_pagina': 'Editar técnico'})


def eliminar_tecnico(request, tecnico_id):
    tecnico = get_object_or_404(Tecnico, pk=tecnico_id)
    if request.method == 'POST':
        tecnico.delete()
        return redirect('tecnicos:lista_tecnicos')
    return render(request, 'tecnicos/confirmar_eliminar.html', {'tecnico': tecnico})