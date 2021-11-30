"""educadist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_view
from cursos.views import ListarCursosView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_view.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_view.LogoutView.as_view(), name='logout'),
    path('meuscursos/', include('cursos.urls')),
    path('', ListarCursosView.as_view(), name='listar_cursos'),
    path('alunos/', include('alunos.urls', namespace='alunos')),
    path('chat/', include('chat.urls', namespace='chat'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
