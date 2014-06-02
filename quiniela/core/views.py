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


from quiniela.core.models import (Apuesta, Partido, Jornada, Resultado, Premio,
                                Bolsa, Posicion, Pagador)
from quiniela.core.forms import (JornadaForm, PartidoForm, PremioForm,
                                ResultadoForm, BaseResultadosFormSet,
                                PagadorForm)
from django.contrib.auth.models import User
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
import datetime
import time

@login_required
def principal(request, template_name='core/main.html', jornada=None):
    usuarios = []
    respuesta = []
    premios = []
    total_premio = 0
    jornada_list = Jornada.objects.all()
    paginator = Paginator(jornada_list, 1)
    page = request.GET.get('page')
    try:
        jornada_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        jornada_page = paginator.page(paginator.num_pages)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        jornada_page = paginator.page(paginator.num_pages)
    jornada = jornada_page.object_list[0]
    partidos = Partido.objects.filter(jornada=jornada)
    apuestas = Apuesta.objects.filter(jornada=jornada).order_by('id')
    for apuesta in apuestas:
        usuario = apuesta.usuario
        if not usuario in usuarios:
            usuarios.append(usuario)
    for usuario in usuarios:
        matriz_resultados = []
        lista_aciertos = []
        cont_aciertos = 0
        cont_dobles = 0
        cont_pleno = 0
        apuestas = Apuesta.objects.filter(jornada=jornada, usuario=usuario)
        for apuesta in apuestas:
            resultados = Resultado.objects.filter(apuesta=apuesta).values('signo')
            matriz_resultados.append(resultados)
            if partidos.values('signo'):
                aciertos = obtener_aciertos(resultados, partidos.values('signo'))
                if aciertos >= 10:
                    lista_aciertos.append(aciertos)
        if partidos.values('signo'):
            # calcular aciertos dobles y pleno
            apuesta =  crear_lista_apuestas(matriz_resultados)
            cont = 0
            for signo in apuesta:
                for i in signo:
                    if (partidos[cont].signo == i.get('signo') and
                        len(signo) != 1):
                        cont_dobles += 1
                        cont_aciertos += 1
                    elif (partidos[cont].signo == i.get('signo') and
                        cont == len(partidos)-1):
                        cont_pleno = 1
                    elif partidos[cont].signo == i.get('signo'):
                        cont_aciertos += 1
                cont += 1
        # obtengo la posicion_anterior
        try :
            posicion_anterior = Posicion.objects.get(usuario=usuario,
                    jornada=jornada.anterior).posicion
        except Posicion.DoesNotExist:
            posicion_anterior = 0
        # calculo del premio
        premios = Premio.objects.filter(jornada=jornada)
        if premios:
            premio = (Premio.objects.get(jornada=jornada, categoria=10).cantidad * lista_aciertos.count(10) +
            Premio.objects.get(jornada=jornada, categoria=11).cantidad * lista_aciertos.count(11) +
            Premio.objects.get(jornada=jornada, categoria=12).cantidad * lista_aciertos.count(12) +
            Premio.objects.get(jornada=jornada, categoria=13).cantidad * lista_aciertos.count(13) +
            Premio.objects.get(jornada=jornada, categoria=14).cantidad * lista_aciertos.count(14) +
            Premio.objects.get(jornada=jornada, categoria=15).cantidad * lista_aciertos.count(15))
            # con los premios metemos a pagador
            pagador = Pagador.objects.get(jornada=jornada)
            # inserto la bolsa del usuario
            if not Bolsa.objects.filter(jornada=jornada, usuario=usuario):
                bolsa = Bolsa()
                bolsa.premio = premio
                bolsa.usuario = usuario
                if posicion_anterior == 0:
                    bolsa.coste = 8
                    posicion_anterior = 0
                elif posicion_anterior > len(usuarios)/2:
                    bolsa.coste = 16
                elif (posicion_anterior <= len(usuarios)/2 
                        and posicion_anterior != 0):
                    bolsa.coste = 0
                if pagador.usuario == bolsa.usuario:
                    bolsa.coste = bolsa.coste - 64
                bolsa.jornada = jornada
                bolsa.save()
            else:
                bolsa = Bolsa.objects.get(jornada=jornada, usuario=usuario)
        else:
            premio = 0
            try:
                bolsa = Bolsa.objects.get(jornada=jornada.anterior, usuario=usuario)
            except Bolsa.DoesNotExist:
                bolsa = ''
        costes_user = Bolsa.objects.filter(usuario=usuario).aggregate(Sum('coste'))
        entrada = {'usuario':usuario, 'aciertos_10':lista_aciertos.count(10),
            'aciertos_11':lista_aciertos.count(11),
            'aciertos_12':lista_aciertos.count(12),
            'aciertos_13':lista_aciertos.count(13),
            'aciertos_14':lista_aciertos.count(14),
            'aciertos_15':lista_aciertos.count(15),
            'aciertos':lista_aciertos,
            'numero_aciertos':cont_aciertos,
            'dobles_aciertos':cont_dobles,
            'pleno':cont_pleno,
            'apuesta':crear_lista_apuestas(matriz_resultados),
            'premio':premio,
            'posicion_anterior':posicion_anterior,
            'bolsa':bolsa,
            'costes_user':costes_user.get('coste__sum'),
            }
        respuesta.append(entrada)
    # inserto posiciones
    if (not Partido.objects.filter(jornada=jornada, signo__exact='')
            and not Posicion.objects.filter(jornada=jornada)):
        insertar_posiciones(respuesta, jornada)
    posiciones = Posicion.objects.filter(jornada=jornada)
    for entrada in respuesta:
        for posicion in posiciones:
            if entrada.get('usuario') == posicion.usuario:
                entrada['posicion'] = posicion
                break
    total_premio = Bolsa.objects.filter(jornada=jornada).aggregate(Sum('premio'))
    if total_premio.get('premio__sum'):
        bolsa = Bolsa.objects.get(usuario=pagador.usuario, jornada=jornada)
        bolsa.coste = 16 - 64 + total_premio.get('premio__sum')
        bolsa.save()
    return render_to_response('core/main.html', {'usuarios':usuarios,
        'jornada':jornada,'respuesta':respuesta, 'partidos':partidos,
        'total_premio':total_premio.get('premio__sum'),'posiciones':posiciones,'premios':premios,
        'jornada_page':jornada_page}, context_instance=RequestContext (request))

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
            jornada = jornada_form.save(commit=False)
            try:
                jornada.anterior = Jornada.objects.latest('numero')
                jornada.save()
            except Jornada.DoesNotExist:
                jornada.save()
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
def crear_apuesta(request, template_name = 'core/apuesta.html', jornada=None):
    x = 0
    lista_resultados = []
    jornada = Jornada.objects.get(numero=jornada)
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
def crear_resultado(request, template_name = 'core/resultados.html', jornada=None):
    jornada = Jornada.objects.get(numero=jornada)
    partidos = Partido.objects.filter(jornada=jornada)
    PremiosFormSet = formset_factory(PremioForm, extra=6)
    premios_formset = PremiosFormSet()
    pagador_form = PagadorForm(initial={'jornada':jornada.numero})
    if request.method == 'POST':
        premios_formset = PremiosFormSet(request.POST)
        pagador_form = PagadorForm(request.POST)
        if premios_formset.is_valid() and  pagador_form.is_valid():
            for form in premios_formset:
                premio = form.save(commit=False)
                premio.jornada = jornada
                premio.save()
            pagador = pagador_form.save(commit=False)
            pagador.jornada = jornada
            pagador.save()
        for i in range(1, 16):
            if 'signo-'+str(i) in request.POST.keys():
                partido = Partido.objects.get(jornada=jornada, casilla=i)
                partido.signo = request.POST.get('signo-'+str(i))
                partido.save()
        return redirect(principal)
    return render_to_response('core/resultados.html',
            {'jornada':jornada, 'partidos':partidos,
                'premios_formset':premios_formset, 'pagador_form':pagador_form},
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

def insertar_posiciones(lista, jornada):
    '''
    Devuelve las posiciones segun las normas de la quiniela LGB, que
    considera primero el pleno, luego los dobles y finalmente la jornada
    anterior. La entrada es una lista que contiene los usuarios, sus
    aciertos, sus dobles, si tiene el pleno y sus posiciones anteriores.
    '''
    lista = sorted(lista, key=lambda entrada: (entrada.get('numero_aciertos'),
        entrada.get('pleno'),
        entrada.get('dobles_aciertos'),
        -entrada.get('posicion_anterior')),
            reverse=True)
    for position, item in enumerate(lista):
        posicion = Posicion()
        posicion.usuario = item.get('usuario')
        posicion.jornada = jornada
        posicion.posicion = position + 1
        posicion.save()

def obtener_aciertos(apuesta, resultado):
    aciertos = 0
    for i in range(len(apuesta)-1):
        if apuesta[i] == resultado[i]:
            aciertos += 1
    if aciertos == len(apuesta)-1:
        if apuesta[len(apuesta)-1] == resultado[len(apuesta)-1]:
            aciertos += 1
    return aciertos

@login_required
def crear_grafico(request, template_name='core/graficos.html'):
    users = User.objects.all()
    jugadores_deuda = {}
    jugadores_premio = {}
    jugadores_posicion= {}
    jornadas = Jornada.objects.all().order_by('numero')
    for user in users:
        #suma_deuda = (Bolsa.objects.filter(usuario=user).aggregate(Sum('premio')) + Bolsa.objects.filter(usuario=user).aggregate(Sum('coste')))
        deuda = Bolsa.objects.filter(usuario=user).aggregate(Sum('coste'))
        jugadores_deuda[user.username] = float(deuda.get('coste__sum'))
        premio = Bolsa.objects.filter(usuario=user).aggregate(Sum('premio'))
        if float(premio.get('premio__sum')) > 0:
            jugadores_premio[user.username] = float(premio.get('premio__sum'))
        posiciones = Posicion.objects.filter(usuario=user).order_by('jornada')
        jugadores_posicion[user.username] = posiciones.values_list('posicion', flat=True)
    xdata = jugadores_deuda.keys()
    ydata = jugadores_deuda.values()
    extra_diagrama = {"tooltip": {"y_start": "€ ", "y_end": ""}}
    chartdata = {'x': xdata, 'name1': 'costes', 'y1': ydata, 'extra1': extra_diagrama,}
    charttype = "discreteBarChart"
    chartcontainer = 'deuda_container'
    data_deuda = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra':{},
    }
    xdata = jugadores_premio.keys()
    ydata = jugadores_premio.values()
    extra_diagrama = {"tooltip": {"y_start": "€ ", "y_end": ""}}
    chartdata = {'x': xdata, 'y1': ydata, 'extra1': extra_diagrama}
    charttype = "pieChart"
    chartcontainer = 'premio_container'
    data_premio = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra':{},
    }
    xdata = jornadas.values_list('numero', flat=True)
    ydata1 = jugadores_posicion['pardi']
    ydata2 = jugadores_posicion['quique']
    ydata3 = jugadores_posicion['tuco']
    ydata4 = jugadores_posicion['josu']
    ydata5 = jugadores_posicion['willie']
    ydata6 = jugadores_posicion['luisito']
    ydata7 = jugadores_posicion['zorro']
    ydata8 = jugadores_posicion['puma']
    extra_diagrama = {"tooltip": {"y_start": "Tu posición es : ", "y_end": " jornada "}}
    chartdata = {'x': xdata,
            'name1': 'Pardi', 'y1': ydata1, 'extra1': extra_diagrama,
            'name2': 'Quique', 'y2': ydata2, 'extra2': extra_diagrama,
            'name3': 'Tuco', 'y3': ydata3, 'extra3': extra_diagrama,
            'name4': 'Josu', 'y4': ydata4, 'extra4': extra_diagrama,
            'name5': 'Willie', 'y5': ydata5, 'extra5': extra_diagrama,
            'name6': 'Luisito', 'y6': ydata6, 'extra6': extra_diagrama,
            'name7': 'Zorro', 'y7': ydata7, 'extra7': extra_diagrama,
            'name8': 'Puma', 'y8': ydata8, 'extra8': extra_diagrama
        }
    charttype = "lineChart"
    chartcontainer = 'posicion_container'
    data_posicion = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        },
    }
    return render_to_response('core/graficos.html', {"data_deuda":data_deuda, "data_premio":data_premio,"data_posicion":data_posicion}, context_instance=RequestContext(request))
