from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from alunos.forms import InscricaoCursoForm
from cursos.models import Curso


class CadastroAlunoView(CreateView):
    template_name = 'aluno/cadastro.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('alunos:listar_cursos_aluno')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result


class InscricaoAlunoCursoView(LoginRequiredMixin, FormView):
    curso = None
    form_class = InscricaoCursoForm

    def form_valid(self, form):
        self.curso = form.cleaned_data['curso']
        self.curso.alunos.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('alunos:detalhe_curso_aluno',
                            args=[self.curso.id])


class ListarCursosAlunoView(LoginRequiredMixin, ListView):
    model = Curso
    template_name = 'cursos/listar.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(alunos__in=[self.request.user])


class DetalheCursoAlunoView(DetailView):
    model = Curso
    template_name = 'cursos/detalhar.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        curso = self.get_object()
        if 'modulo_id' in self.kwargs:
            # obter módulo atual
            contexto['modulo'] = curso.modulos.get(
                                id=self.kwargs['modulo_id'])
        else:
            # obtém o primeiro módulo do curso
            contexto['modulo'] = curso.modulos.first()

        return contexto
