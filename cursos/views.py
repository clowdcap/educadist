from django.db.models import Count
from django.views.generic import DetailView
from django.views.generic.list import ListView
from .models import Curso, Modulo, Conteudo, Assunto
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuloFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import JsonRequestResponseMixin
from alunos.forms import InscricaoCursoForm


class DonoMixin(object):
    def get_queryset(self):
        q = super().get_queryset()
        return q.filter(dono=self.request.user)


class DonoEditarMixin(object):
    def form_valid(self, form):
        form.instance.dono = self.request.user
        return super().form_valid(form)


class DonoCursoMixin(DonoMixin,
                     LoginRequiredMixin,
                     PermissionRequiredMixin):
    model = Curso
    fields = ['assunto', 'titulo', 'slug', 'desc_geral']
    success_url = reverse_lazy('gerenciar_cursos_list')


class DonoCursoEditMixin(DonoCursoMixin, DonoEditarMixin):
    template_name = 'gerenciar/curso/form.html'


class ListarCursosListView(DonoCursoMixin, ListView):
    template_name = 'gerenciar/curso/listar.html'
    permission_required = 'cursos.view_curso'


class CriarCursoCreateView(DonoCursoEditMixin, CreateView):
    permission_required = 'cursos.add_curso'


class AtualizarCursoUpdateView(DonoCursoEditMixin, UpdateView):
    permission_required = 'cursos.change_curso'


class ExcluirCursoDeleteView(DonoCursoMixin, DeleteView):
    template_name = 'gerenciar/curso/excluir.html'
    permission_required = 'cursos.delete_curso'


class ModuloCursoUpdateView(TemplateResponseMixin, View):
    template_name = 'gerenciar/modulo/formset.html'
    curso = None

    def get_formset(self, data=None):
        return ModuloFormSet(instance=self.curso,
                             data=data)

    def dispatch(self, request, pk, *args, **kwargs):
        self.curso = get_object_or_404(Curso,
                                       id=pk,
                                       dono = request.user)
        return super().dispatch(request, pk, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'curso': self.curso,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('gerenciar_cursos_list')
        return self.render_to_response({'curso':self.curso,
                                        'formset': formset})


class CriarAtualizarConteudoView(TemplateResponseMixin, View):
    modulo = None
    model = None
    obj = None
    template_name = 'gerenciar/conteudo/form.html'

    def get_model(self, model_name):
        if model_name in ['texto', 'video', 'imagem', 'arquivo']:
            return apps.get_model(app_label='cursos',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['dono',
                                                 'order',
                                                 'criado',
                                                 'atualizado'])
        return Form(*args,**kwargs)

    def dispatch(self, request, modulo_id, model_name, id=None):
        self.modulo = get_object_or_404(Modulo,
                                      id=modulo_id,
                                      curso__dono=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         dono=request.user)
        return super().dispatch(request, modulo_id, model_name, id)

    def get(self, request, modulo_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, modulo_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.dono = request.user
            obj.save()
            if not id:
                #é um novo conteúdo
                Conteudo.objects.create(modulo=self.modulo, item=obj)
            return redirect('listar_conteudo_modulo', self.modulo.id)
        return self.render_to_response({'form':form,
                                        'object':self.obj})


class ExcluirConteudoView(View):

    def post(self, request, id_cont):
        conteudo = get_object_or_404(Conteudo,
                                     id=id_cont,
                                     modulo__curso__dono=request.user)
        modulo = conteudo.modulo
        conteudo.item.delete()
        conteudo.delete()
        return redirect('listar_conteudo_modulo', modulo.id)


class ListarConteudoModuloView(TemplateResponseMixin, View):
    template_name = 'gerenciar/modulo/listar_conteudo.html'

    def get(self, request, modulo_id):
        modulo = get_object_or_404(Modulo,
                                   id=modulo_id,
                                   curso__dono=request.user)
        return self.render_to_response({'modulo': modulo})


class ReordenarModulosView(JsonRequestResponseMixin, View):

    def post(self, request):
        for id_modulo, order in self.request_json.items():
            Modulo.objects.filter(id=id_modulo,
                                  curso__dono=request.user)\
                                  .update(order=order)
        return self.render_json_response({'salvo': 'OK'})


class ReordenarConteudosView(JsonRequestResponseMixin, View):

    def post(self, request):
        for id_cont, order in self.request_json.items():
            Conteudo.objects.filter(id=id_cont,
                                    modulo__curso__dono=request.user)\
                                    .update(order=order)
        return self.render_json_response({'salvo': 'OK'})


class ListarCursosView(TemplateResponseMixin, View):
    model = Curso
    template_name = 'curso/listar.html'

    def get(self, request, assunto=None):
        assuntos = Assunto.objects.annotate(
                           total_cursos=Count('cursos'))
        cursos = Curso.objects.annotate(
                           total_modulos=Count('modulos'))

        if assunto:
            assunto = get_object_or_404(Assunto, slug=assunto)
            cursos = cursos.filter(assunto=assunto)

        return self.render_to_response({'assuntos': assuntos,
                                        'assunto': assunto,
                                        'cursos': cursos})


class DetalheCursoView(DetailView):
    model = Curso
    template_name = 'curso/detalhar.html'
    context_object_name = 'curso'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['inscricao_form'] = InscricaoCursoForm(
                                        initial={'curso':self.object})
        return contexto
