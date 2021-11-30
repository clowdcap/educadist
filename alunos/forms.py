from django.forms import Form, ModelChoiceField, HiddenInput
from cursos.models import Curso


class InscricaoCursoForm(Form):
    curso = ModelChoiceField(queryset=Curso.objects.all(),
                             widget=HiddenInput)
