from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

@login_required
def chat_curso(request, curso_id):
    try:
        #obtém o curso pelo id
        curso = request.user.cursos_aluno.get(id=curso_id)
    except:
        # o aluno não está vinculado ao curso com o id informado
        return HttpResponseForbidden()
    return render(request, 'sala.html', {'curso': curso})
