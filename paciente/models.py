from django.db import models
from django.contrib.auth.models import User
from medico.models import datasAbertas

# Create your models here.
class Consulta(models.Model):
    # Opcões
    status_choices = (
        ('A', 'Agendada'),
        ('F', 'Finalizada'),
        ('C', 'Cancelada'),
        ('I', 'Iniciada')
    )
    paciente = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    data_aberta = models.ForeignKey(datasAbertas, on_delete=models.DO_NOTHING)
    # default - Se não for passado nada ao salvar vai ser definido como A.
    status = models.CharField(max_length=1, choices=status_choices, default='A')
    # Pode ficar vazio até o m´dico inserir o link da consulta e inicializar
    link = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return self.paciente.username
    
class Documento(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    documento = models.FileField(upload_to='documentos')

    def __str__(self):
        return self.titulo
    