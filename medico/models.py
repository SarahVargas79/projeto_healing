from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
def is_medico(user):
    return dadosMedico.objects.filter(user=user).exists()

class Especialidades(models.Model):
    especialidade = models.CharField(max_length=100)
    
    def __str__(self):
        return self.especialidade
    
class dadosMedico(models.Model):
    crm = models.CharField(max_length=6)
    nome = models.CharField(max_length=100)
    cep = models.CharField(max_length=9)
    rua = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    numero = models.IntegerField()
    rg = models.ImageField(upload_to='rgs')
    cedula_identidade_medica = models.ImageField(upload_to='cim')
    foto = models.ImageField(upload_to='fotos_perfil')
    descricao = models.TextField()
    valor_consulta = models.FloatField(default=100)
    # on_delete=models.DO_NOTHING - nada acontecerá com os dados desse medico/user que foi deletado.
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    especialidade = models.ForeignKey(Especialidades, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return self.user.username
    
    @property # Método considerado como propriedade, atributo.
    def proxima_data(self):
        # data__gt - Seja maior do que algo (proxima_data poderá ser a gendada numa data atual  ) | gt - Maior do que
        proxima_data = datasAbertas.objects.filter(user=self.user).filter(data__gt=datetime.now()).filter(agendado=False).order_by('data').first()  
        return proxima_data
    
class datasAbertas(models.Model):
    data = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) # Médico
    agendado = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.data)
    
