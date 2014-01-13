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

from django.forms import ModelForm, CharField, HiddenInput
from django.forms.formsets import formset_factory

from quiniela.core.models import Apuesta, Partido, Jornada

class ApuestaForm(ModelForm):

    class Meta:
        model = Apuesta
        exclude = ('usuarios',)


class JornadaForm(ModelForm):

    class Meta:
        model = Jornada
        #exclude = ('usuarios',)


class PartidoForm(ModelForm):

    casilla = CharField(widget=HiddenInput(), required=False)

    class Meta:
        model = Partido
        fields = ('casilla', 'local', 'visitante',)


CrearApuestaFormSet = formset_factory(ApuestaForm, PartidoForm)

class CrearApuestaForm(ModelForm):

    class Meta:
        model = Apuesta
        exclude = ('usuarios',)
