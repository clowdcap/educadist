from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrdenaCampos


class Assunto(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class Curso(models.Model):
    dono = models.ForeignKey(User,
                             related_name='criador_curso',
                             on_delete= models.CASCADE)
    assunto = models.ForeignKey(Assunto,
                                related_name='cursos',
                                on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    desc_geral = models.TextField()
    criado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado']

    def __str__(self):
        return self.titulo


class Modulo (models.Model):
    curso = models.ForeignKey(Curso,
                              related_name='modulos',
                              on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    order = OrdenaCampos(blank=True, for_fields=['curso'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order} - {self.titulo}'


class Conteudo(models.Model):
    modulo = models.ForeignKey(Modulo,
                               related_name='conteudos',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model_in':(
                                         'texto',
                                         'video',
                                         'imagem',
                                         'arquivo',
                                     )})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrdenaCampos(blank=True, for_fields=['modulo'])

    class Meta:
        ordering = ['order']


class ItemConteudoBase(models.Model):
    dono = models.ForeignKey(User,
                             related_name='%(class)s_relacionados',
                             on_delete=models.CASCADE)
    titulo = models.CharField(max_length=250)
    criado = models.DateTimeField(auto_now_add=True)
    atualizado = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.titulo


class Texto(ItemConteudoBase):
    conteudo = models.TextField()


class Arquivo(ItemConteudoBase):
    conteudo = models.FileField(upload_to='arquivos')


class Imagem(ItemConteudoBase):
    conteudo = models.FileField(upload_to='imagens')


class Video(ItemConteudoBase):
    caminho = models.URLField()

