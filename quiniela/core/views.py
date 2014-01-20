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


from quiniela.core.models import Apuesta, Partido, Jornada, Resultado, Premio
from quiniela.core.forms import (JornadaForm, PartidoForm, PremioForm,
                                ResultadoForm, BaseResultadosFormSet)
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def principal(request, template_name = 'core/main.html'):
    usuarios = []
    respuesta = []
    total_premio = 0
    jornada = Jornada.objects.latest('numero')
    partidos = Partido.objects.filter(jornada=jornada)
    apuestas = Apuesta.objects.filter(jornada=jornada)
    for apuesta in apuestas:
        usuario = apuesta.usuario
        if not usuario in usuarios:
            usuarios.append(usuario)
    for usuario in usuarios:
        matriz_resultados = []
        lista_aciertos = []
        apuestas = Apuesta.objects.filter(jornada=jornada, usuario=usuario)
        for apuesta in apuestas:
            resultados = Resultado.objects.filter(apuesta=apuesta).values('signo')
            matriz_resultados.append(resultados)
            aciertos = obtener_aciertos(resultados, partidos.values('signo'))
            if aciertos >= 10:
                lista_aciertos.append(aciertos)
        premio = (Premio.objects.get(jornada=jornada, categoria=10).cantidad * lista_aciertos.count(10) +
        Premio.objects.get(jornada=jornada, categoria=11).cantidad * lista_aciertos.count(11) +
        Premio.objects.get(jornada=jornada, categoria=12).cantidad * lista_aciertos.count(12) +
        Premio.objects.get(jornada=jornada, categoria=13).cantidad * lista_aciertos.count(13) +
        Premio.objects.get(jornada=jornada, categoria=14).cantidad * lista_aciertos.count(14) +
        Premio.objects.get(jornada=jornada, categoria=15).cantidad * lista_aciertos.count(15))
        total_premio += premio
        entrada = {'usuario':usuario, 'aciertos_10':lista_aciertos.count(10),
                'aciertos_11':lista_aciertos.count(11),
                'aciertos_12':lista_aciertos.count(12),
                'aciertos_13':lista_aciertos.count(13),
                'aciertos_14':lista_aciertos.count(14),
                'aciertos_15':lista_aciertos.count(15),
                'aciertos':lista_aciertos,
                'apuesta':crear_lista_apuestas(matriz_resultados),
                'premio':premio}
        respuesta.append(entrada)
    return render_to_response('core/main.html', {'usuarios':usuarios, 'jornada':jornada,
        'respuesta':respuesta, 'partidos':partidos, 'total_premio':total_premio },
            context_instance=RequestContext (request))

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
            return redirect(principal)
    return render_to_response('core/partidos.html',
            {'jornada_form':jornada_form, 'partidos_formset':partidos_formset},
            context_instance=RequestContext(request))

@login_required
def crear_apuesta(request, template_name = 'core/apuesta.html'):
    x = 0
    lista_resultados = []
    jornada = Jornada.objects.latest('numero')
    partidos = Partido.objects.filter(jornada=jornada)
    ResultadosFormSet = formset_factory(ResultadoForm, extra=15, max_num=15,
            validate_max=True, formset=BaseResultadosFormSet)
    resultados_formset = ResultadosFormSet()
    if request.method == 'POST':
        resultados_formset = ResultadosFormSet(request.POST)
        if resultados_formset.is_valid():
            for form in resultados_formset:
                lista_resultados.append(form.cleaned_data.get('signo'))
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
                    partido = Partido.objects.get(casilla=y, jornada=jornada)
                    resultado.partido = partido
                    resultado.apuesta = apuesta
                    resultado.save()
            return redirect(principal)
    lista = zip(resultados_formset, partidos)
    return render_to_response('core/apuesta.html',
            {'jornada':jornada, 'partidos':partidos,
                'resultados_formset':resultados_formset, 'lista':lista},
            context_instance=RequestContext(request))

@login_required
def crear_resultado(request, template_name = 'core/resultados.html'):
    jornada = Jornada.objects.latest('numero')
    partidos = Partido.objects.filter(jornada=jornada)
    PremiosFormSet = formset_factory(PremioForm, extra=6)
    premios_formset = PremiosFormSet()
    premio = PremioForm()
    if request.method == 'POST':
        for i in range(1, 16):
            if 'signo-'+str(i) in request.POST.keys():
                partido = Partido.objects.get(jornada=jornada, casilla=i)
                partido.signo = request.POST.get('signo-'+str(i))
                partido.save()
        premios_formset = PremiosFormSet(request.POST)
        if premios_formset.is_valid():
            for form in premios_formset:
                premio = form.save(commit=False)
                premio.jornada = jornada
                premio.save()
            return redirect(principal)
    return render_to_response('core/resultados.html',
            {'jornada':jornada, 'partidos':partidos, 'premios_formset':premios_formset, 'premio':premio},
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

def crear_lista_apuestas(matriz):
    lista = []
    for i in range(len(matriz)):
        for j in range(len(matriz[i])):
            aux = []
            if i == 0:
                aux.append(matriz[0][j])
                lista.append(aux)
            if not matriz[i][j] in lista[j]:
                lista[j].append(matriz[i][j])
    return lista

def obtener_aciertos(apuesta, resultado):
    aciertos = 0
    for i in range(len(apuesta)-1):
        if apuesta[i] == resultado[i]:
            aciertos += 1
    if aciertos == len(apuesta)-1:
        if apuesta[len(apuesta)-1] == resultado[len(apuesta)-1]:
            aciertos += 1
    return aciertos
