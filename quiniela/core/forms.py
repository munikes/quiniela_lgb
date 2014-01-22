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

from django.forms import (ModelForm, CharField, HiddenInput, MultipleChoiceField,
                        CheckboxSelectMultiple, ValidationError)
from django.forms.formsets import BaseFormSet

from quiniela.core.models import Partido, Jornada, Resultado, Premio


class JornadaForm(ModelForm):

    class Meta:
        model = Jornada
        exclude = ('anterior',)


class PartidoForm(ModelForm):

    casilla = CharField(widget=HiddenInput(), required=False)

    class Meta:
        model = Partido
        fields = ('casilla', 'local', 'visitante',)


class ResultadoForm(ModelForm):
    OPCIONES = (
            ('1', '1'),
            ('X', 'X'),
            ('2', '2'),
            )
    signo = MultipleChoiceField(widget=CheckboxSelectMultiple, choices=OPCIONES)

    class Meta:
        model = Resultado
        fields = ('signo',)


class BaseResultadosFormSet(BaseFormSet):
    def clean(self):
        """Mira si el conjunto de formularios tiene siete dobles."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        dobles = 0
        for form in self.forms:
            if not form.cleaned_data.get('signo'):
                raise ValidationError("Debes de insertar todos los resultados.")
            signo = form.cleaned_data['signo']
            if len(signo) == 3:
                raise ValidationError("No se puede insertar ningún triple.")
            if len(signo) == 2:
                dobles += 1
        if dobles != 7:
            raise ValidationError("El número de dobles es distinto de 7.")


class PremioForm(ModelForm):

    class Meta:
        model = Premio
        fields = ('categoria', 'cantidad',)
