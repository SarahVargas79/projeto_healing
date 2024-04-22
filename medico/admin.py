from django.contrib import admin
from .models import Especialidades, dadosMedico, datasAbertas

# Register your models here.

# Registrando no site na parte adm. as models 

admin.site.register(Especialidades) 
admin.site.register(dadosMedico)
admin.site.register(datasAbertas)

