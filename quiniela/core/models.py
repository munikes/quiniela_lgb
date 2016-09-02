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


from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

OPCIONES = (
        ('1', '1'),
        ('X', 'X'),
        ('2', '2'),
        ('M-0', 'M-0'),
        ('M-1', 'M-1'),
        ('M-2', 'M-2'),
        ('M-M', 'M-M'),
        ('2-0', '2-0'),
        ('2-1', '2-1'),
        ('2-2', '2-2'),
        ('2-M', '2-M'),
        ('1-0', '1-0'),
        ('1-1', '1-1'),
        ('1-2', '1-2'),
        ('1-M', '1-M'),
        ('0-0', '0-0'),
        ('0-1', '0-1'),
        ('0-2', '0-2'),
        ('0-M', '0-M'),
        )
EQUIPOS = (
        ('Athletic Club', 'Athletic Club'),
        ('At. Madrid', 'At. Madrid'),
        ('Barcelona', 'Barcelona'),
        ('Betis', 'Betis'),
        ('Celta', 'Celta'),
        ('Deportivo', 'Deportivo'),
        ('Eibar', 'Eibar'),
        ('Espanyol', 'Espanyol'),
        ('Getafe', 'Getafe'),
        ('Granada', 'Granada'),
        ('Las Palmas', 'Las Palmas'),
        ('Levante', 'Levante'),
        ('R. Madrid', 'R. Madrid'),
        ('Malaga', 'Málaga'),
        ('Rayo Vallecano', 'Rayo Vallecano'),
        ('Sevilla', 'Sevilla'),
        ('Sporting', 'Sporting'),
        ('R. Sociedad', 'R. Sociedad'),
        ('Valencia', 'Valencia'),
        ('Villarreal', 'Villarreal'),
        ('Alaves', 'Alavés'),
        ('Albacete', 'Albacete'),
        ('Alcorcon', 'Alcorcón'),
        ('Almeria', 'Almería'),
        ('Cordoba', 'Córdoba'),
        ('Elche', 'Elche'),
        ('Girona', 'Girona'),
        ('Gimnastic', 'Gimnastic'),
        ('Huesca', 'Huesca'),
        ('Leganes', 'Leganés'),
        ('Llagostera', 'Llagostera'),
        ('Lugo', 'Lugo'),
        ('Mallorca', 'Mallorca'),
        ('Mirandes', 'Mirandés'),
        ('Numancia', 'Numancia'),
        ('Osasuna', 'Osasuna'),
        ('R. Oviedo', 'R. Oviedo'),
        ('Ponferradina', 'Ponferradina'),
        ('Tenerife', 'Tenerife'),
        ('Valladolid', 'Valladolid'),
        ('Zaragoza', 'Zaragoza'),
        )
TEMPORADA = (
        ('2013-2014', '2013-2014'),
        ('2014-2015', '2014-2015'),
        ('2015-2016', '2015-2016'),
        ('2016-2017', '2016-2017'),
        )

class Temporada (models.Model):
    temporada = models.CharField(max_length=9, verbose_name='Temporada', 
            choices=TEMPORADA)


class Jornada (models.Model):
    numero = models.PositiveSmallIntegerField(primary_key=True,
            help_text='Jornada de liga.', verbose_name = 'Número')
    anterior = models.ForeignKey('self', blank=True, null=True)
    temporada = models.ForeignKey(Temporada)


class Apuesta (models.Model):
    temporada = models.ForeignKey(Temporada)
    jornada = models.ForeignKey(Jornada)
    usuario = models.ForeignKey(User)
    numero = models.PositiveSmallIntegerField(help_text='Número de apuesta.',
            verbose_name = 'Número')

    class Meta:
        unique_together = (('temporada', 'jornada', 'usuario', 'numero'),)


class Partido (models.Model):
    temporada = models.ForeignKey(Temporada)
    jornada = models.ForeignKey(Jornada)
    signo = models.CharField(max_length=3, choices=OPCIONES,
            verbose_name = 'Resultado', default='')
    local = models.CharField(max_length=20, verbose_name='Local',
            choices=EQUIPOS)
    visitante = models.CharField(max_length=20, verbose_name='Visitante',
            choices=EQUIPOS)
    casilla = models.PositiveSmallIntegerField(verbose_name='Casilla', validators=[
            MaxValueValidator(15),
            MinValueValidator(1)
        ], help_text='La casilla del partido.', blank=True)

    class Meta:
        unique_together = (('temporada', 'local', 'visitante'),)


class Bolsa (models.Model):
    usuario = models.ForeignKey(User)
    temporada = models.ForeignKey(Temporada)
    jornada = models.ForeignKey(Jornada)
    premio = models.DecimalField(verbose_name='Premio', max_digits=10,
            decimal_places=2, help_text='Cantidad de euros ganados.')
    coste = models.DecimalField(verbose_name='Coste apuestas', max_digits=10,
            decimal_places=2, help_text='Coste de las apuestas.')

    class Meta:
        unique_together = (('temporada', 'jornada', 'usuario'),)


class Posicion (models.Model):
    usuario = models.ForeignKey(User)
    temporada = models.ForeignKey(Temporada)
    jornada = models.ForeignKey(Jornada)
    posicion = models.PositiveSmallIntegerField(verbose_name='Posicion',
            help_text='Posición que ocupas.')

    class Meta:
        unique_together = (('temporada', 'posicion', 'jornada', 'usuario'),)


class Resultado (models.Model):
    signo = models.CharField(max_length=18,
            verbose_name = 'Resultado')
    apuesta = models.ForeignKey(Apuesta)
    temporada = models.ForeignKey(Temporada)
    partido = models.ForeignKey(Partido)

    class Meta:
        unique_together = (('temporada', 'apuesta', 'partido'),)


class Premio (models.Model):
    OPCIONES = (
            (15, 'pleno al 15'),
            (14, '1ª categoría (14)'),
            (13, '2ª categoría (13)'),
            (12, '3ª categoría (12)'),
            (11, '4ª categoría (11)'),
            (10, '5ª categoría (10)'),
            )
    temporada = models.ForeignKey(Temporada)
    jornada = models.ForeignKey(Jornada)
    categoria = models.PositiveSmallIntegerField(verbose_name='categoria',
            choices=OPCIONES, default='')
    cantidad = models.DecimalField(verbose_name='Cantidad', max_digits=10,
            decimal_places=2)

    class Meta:
        unique_together = (('temporada', 'jornada', 'categoria'),)


class Pagador (models.Model):
    usuario = models.ForeignKey(User)
    temporada = models.ForeignKey(Temporada)
    jornada = models.ForeignKey(Jornada)

    class Meta:
        unique_together = (('usuario', 'temporada', 'jornada'),)
