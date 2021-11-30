from django.urls import path
from alunos import views

app_name = "alunos"

urlpatterns = [
    path('cadastrar/',
         views.CadastroAlunoView.as_view(),
         name='cadastro_aluno'),
    path('inscricao-curso/',
         views.InscricaoAlunoCursoView.as_view(),
         name='inscricao_aluno_curso'),
    path('cursos/',
         views.ListarCursosAlunoView.as_view(),
         name='listar_cursos_aluno'),
    path('cursos/<pk>/',
         views.DetalheCursoAlunoView.as_view(),
         name='detalhe_curso_aluno'),
    path('cursos/<pk>/<modulo_id>/',
         views.DetalheCursoAlunoView.as_view(),
         name='detalhe_modulo_curso_aluno'),
]