from django.shortcuts import render, redirect
from medico.models import dadosMedico, Especialidades, datasAbertas, is_medico
from datetime import datetime
from .models import Consulta, Documento
from django.contrib import messages
from django.contrib.messages import constants

# Create your views here.
def home(request):
    if request.method == "GET":
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        medicos = dadosMedico.objects.all()
        
        if medico_filtrar:
            # nome__icontais - Trazer todo os médicos onde o nome contiver o valor digitado pelo usuário.
            medicos = medicos.filter(nome__icontains=medico_filtrar)
            
        if especialidades_filtrar:
            # in - Traz os médicos onde sua especilidade esteja dentro de algum desses valor
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)
        
        especialidades = Especialidades.objects.all()
        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades, 'is_medico': is_medico(request.user)})
    
def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = dadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = datasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})

def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        # busca do BD o data_aberta que o id seja, o id passado na url, altera o valor da coluna agend. para True
        
        data_aberta = datasAbertas.objects.get(id=id_data_aberta)

        # Relação paciente e data
        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta    
        )
        
        horario_agendado.save()
        
        # Muda só na memória
        data_aberta.agendado = True
        # Salva no BD
        data_aberta.save()
        
        messages.add_message(request, constants.SUCCESS, 'Consulta agendada com sucesso.')
        return redirect('/pacientes/minhas_consultas/')
    
def minhas_consultas(request):
    # Realizar os filtros, trazer somen. esoecial. e data a tende ao valor colocado pelo usuário
    # __ - Acessa o atributo de uma outra tabela.
    minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
    return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user)})

def consulta(request, id_consulta):
    if request.method == "GET":
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = dadosMedico.objects.get(user=consulta.data_aberta.user)
        documentos = Documento.objects.filter(consulta=consulta)
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'documentos': documentos})