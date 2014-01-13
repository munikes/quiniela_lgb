#    This Python file uses the following encoding: utf-8 .
#    See http://www.python.org/peps/pep-0263.html for details

#    Software as a service (SaaS), which allows play Quiniela LGB.
#
#    Copyright (C) 2014 Diego Pardilla Mata
#
#    This file is part of Quiniela LGB.
#
#    Quiniela LGB is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from quiniela.core.models import Apuesta, Partido, Jornada, Resultado
from quiniela.core.forms import JornadaForm, PartidoForm

from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from extra_views import ModelFormSetView, InlineFormSet, CreateWithInlinesView
from extra_views.generic import GenericInlineFormSet
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max

class Principal(TemplateView):
    template_name = 'core/main.html'

@login_required
def crear_jornada(request, template_name = 'core/partidos.html'):
    i = 0
    jornada_form = JornadaForm()
    PartidosFormSet = formset_factory(PartidoForm, extra=15)
    partidos_formset = PartidosFormSet()
    if request.method == 'POST':
        jornada_form = JornadaForm(request.POST)
        partidos_formset = PartidosFormSet(request.POST)
        if jornada_form.is_valid() and partidos_formset.is_valid():
            jornada = jornada_form.save()
            for form in partidos_formset:
                i += 1
                partido = form.save(commit=False)
                partido.casilla = i
                partido.jornada = jornada
                partido.save()
            return render_to_response('core/apuesta_list.html', {},
                context_instance=RequestContext(request))
    return render_to_response('core/partidos.html',
            {'jornada_form':jornada_form, 'partidos_formset':partidos_formset},
            context_instance=RequestContext(request))

@login_required
def crear_apuesta(request, template_name = 'core/apuesta.html'):
    x = 0
    lista_resultados = []
    jornada = Jornada.objects.latest('numero')
    partidos = Partido.objects.filter(jornada=jornada)
    if request.method == 'POST':
        for i in range(1, 16):
            if 'signo-'+str(i) in request.POST.keys():
                lista_resultados.append(request.POST.getlist('signo-'+str(i)))
        apuestas = reducir_apuestas(generar_apuestas(lista_resultados))
        for lista_resultados in apuestas:
            x += 1
            y = 0
            apuesta = Apuesta()
            apuesta.numero = x
            apuesta.usuario = request.user
            apuesta.jornada = jornada
            apuesta.save()
            for signo in lista_resultados:
                resultado = Resultado()
                y += 1
                resultado.signo = signo
                resultado.casilla = y
                resultado.apuesta = apuesta
                resultado.save()
    return render_to_response('core/apuesta.html',
            {'jornada':jornada, 'partidos':partidos},
            context_instance=RequestContext(request))

def generar_apuestas(lista):
    matriz = []
    for nodo in lista:
        if len(matriz) == 0:
            matriz.append([])
        for indice in range(len(matriz)):
            lista = matriz.pop(0)
            for indice_hoja in range(len(nodo)):
                # meter a cada elemento la hoja
                aux_lista = lista [:]
                aux_lista.append(nodo[indice_hoja])
                matriz.append(aux_lista)
    return matriz

def reducir_apuestas (matriz):
    apuesta_reduccion = [['1','X'],['1','X'],['1','X'],['1','X'],
        ['1','X'],['1','X'],['1','X']]
    lista_reducciones = [['1','1','1','1','1','1','1'],
        ['1','1','1','1','X','X','X'],['X','X','X','X','1','1','1'],
        ['X','X','X','X','X','X','X'],['X','X','1','1','X','1','1'],
        ['X','X','1','1','1','X','X'],['1','1','X','X','X','1','1'],
        ['1','1','X','X','1','X','X'],['X','1','X','1','1','X','1'],
        ['X','1','X','1','X','1','X'],['1','X','1','X','1','X','1'],
        ['1','X','1','X','X','1','X'],['X','1','1','X','1','1','X'],
        ['X','1','1','X','X','X','1'],['1','X','X','1','1','1','X'],
        ['1','X','X','1','X','X','1']]
    aux = []
    matriz_apuestas = generar_apuestas(apuesta_reduccion)
    for i in matriz_apuestas:
        for j in lista_reducciones:
            if i == j:
                aux.append(matriz[matriz_apuestas.index(i)])
    return aux

#class CrearApuesta(ListView):
#    model = Apuesta
#    success_url = reverse_lazy('principal')
#    template_name = 'core/apuesta.html'
#
#    def get_queryset(self):
#        apuesta = Apuesta.objects.filter(usuario=self.request.user).latest('jornada')
#        return Partido.objects.filter(jornada=apuesta.jornada)

class CrearJornada(CreateView):
    model = Jornada
    success_url = reverse_lazy('crear_partidos')

class CrearPartidos(ModelFormSetView):
    template_name = 'core/partidos_formset.html'
    model = Partido
    extra = 15
