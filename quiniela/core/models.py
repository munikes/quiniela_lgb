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
        )
EQUIPOS = (
        ('Almeria', 'Almería'),
        ('Athletic Club', 'Athletic Club'),
        ('At. Madrid', 'At. Madrid'),
        ('Barcelona', 'Barcelona'),
        ('Betis', 'Betis'),
        ('Celta', 'Celta'),
        ('Elche', 'Elche'),
        ('Espanyol', 'Espanyol'),
        ('Getafe', 'Getafe'),
        ('Granada', 'Granada'),
        ('Levante', 'Levante'),
        ('R. Madrid', 'R. Madrid'),
        ('Malaga', 'Málaga'),
        ('Osasuna', 'Osasuna'),
        ('Rayo Vallecano', 'Rayo Vallecano'),
        ('Sevilla', 'Sevilla'),
        ('R. Sociedad', 'R. Sociedad'),
        ('Valencia', 'Valencia'),
        ('Valladolid', 'Valladolid'),
        ('Villarreal', 'Villarreal'),
        ('Alaves', 'Alavés'),
        ('Alcorcon', 'Alcorcón'),
        ('Cordoba', 'Córdoba'),
        ('Deportivo', 'Deportivo'),
        ('Eibar', 'Eibar'),
        ('Girona', 'Girona'),
        ('Hercules', 'Hércules'),
        ('Jaen', 'Jaen'),
        ('Las Palmas', 'Las Palmas'),
        ('Lugo', 'Lugo'),
        ('Mallorca', 'Mallorca'),
        ('Murcia', 'Murcia'),
        ('Numancia', 'Numancia'),
        ('Ponferradina', 'Ponferradina'),
        ('Recreativo', 'Recreativo'),
        ('Sabadell', 'Sabadell'),
        ('Sporting', 'Sporting'),
        ('Tenerife', 'Tenerife'),
        ('Zaragoza', 'Zaragoza'),
        )
class Jornada (models.Model):
    numero = models.PositiveSmallIntegerField(primary_key=True,
            help_text='Jornada de liga.', verbose_name = 'Número')


class Apuesta (models.Model):
    jornada = models.ForeignKey(Jornada)
    usuario = models.ForeignKey(User)
    numero = models.PositiveSmallIntegerField(help_text='Número de apuesta.', 
            verbose_name = 'Número')

    class Meta:
        unique_together = (('jornada', 'usuario', 'numero'),)


class Partido (models.Model):
    jornada = models.ForeignKey(Jornada)
    signo = models.CharField(max_length=1, choices=OPCIONES,
            verbose_name = 'Resultado')
    local = models.CharField(max_length=20, verbose_name='Local',
            choices=EQUIPOS)
    visitante = models.CharField(max_length=20, verbose_name='Visitante',
            choices=EQUIPOS)
    casilla = models.PositiveSmallIntegerField(verbose_name='Casilla', validators=[
            MaxValueValidator(15),
            MinValueValidator(1)
        ], help_text='La casilla del partido.', blank=True)


class Bolsa (models.Model):
    usuario = models.OneToOneField(User)
    cantidad = models.DecimalField(verbose_name='Cantidad', max_digits=8,
            decimal_places=2, help_text='Cantidad de euros.')


class Posicion (models.Model):
    usuario = models.OneToOneField(User)
    posicion = models.PositiveSmallIntegerField(verbose_name='Posicion',
            help_text='Posición que ocupas.')


class Resultado (models.Model):
    signo = models.CharField(max_length=1, choices=OPCIONES,
            verbose_name = 'Resultado')
    apuesta = models.ForeignKey(Apuesta)
    casilla = models.PositiveSmallIntegerField(verbose_name='Casilla', validators=[
            MaxValueValidator(15),
            MinValueValidator(1)
        ], help_text='La casilla del partido.')

    class Meta:
        unique_together = (('apuesta', 'casilla'),)


class Premio (models.Model):
    OPCIONES = (
            (0, 'pleno al 15'),
            (1, '1ª categoría (14)'),
            (2, '2ª categoría (13)'),
            (3, '3ª categoría (12)'),
            (4, '4ª categoría (11)'),
            (5, '5ª categoría (10)'),
            )
    jornada = models.ForeignKey(Jornada)
    categoria = models.PositiveSmallIntegerField(verbose_name='categoria',
            help_text ='categoria del premio', choices=OPCIONES)
    cantidad = models.DecimalField(verbose_name='Cantidad', max_digits=8,
            decimal_places=2, help_text='Cantidad de euros.')
