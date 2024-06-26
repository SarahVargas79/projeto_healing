from django.shortcuts import render, redirect
from .models import Especialidades, dadosMedico, is_medico, datasAbertas
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from paciente.models import Consulta, Documento
from django.contrib.auth.decorators import login_required
from django.db.models import Count

# Create your views here.
@login_required
def cadastro_medico(request):
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já possui registro médico aqui')
        return redirect('/medicos/abrir_horario')
    if request.method == "GET":
        # Infor. do python para o HTML(Especialidades)
        # contex{} - Dicionário do Python
        # objects - Acessar os dados da tabela
        especialidades = Especialidades.objects.all() # Acessa os dados da tabela do BD (Especialidades), pega todas essas infor. e devolva para a váriavel (especialidades)
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades, 'is_medico': is_medico(request.user)})
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')
        
        dados_medico = dadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            descricao=descricao,
            especialidade_id=especialidade, # especilidade_id - Espera uma instância
            valor_consulta=valor_consulta,
            user=request.user
        )

        dados_medico.save()
        
        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso!')
        return redirect('/medicos/abrir_horario')

@login_required
def abrir_horario(request):
    
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos estão autorizados abrir horário')
        return redirect('/usuarios/logout') # !
    
    if request.method == "GET":
        dados_medicos = dadosMedico.objects.get(user=request.user)
        datas_abertas = datasAbertas.objects.filter(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    elif request.method == "POST":
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')
        
        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING, "Data não pode ser anterior a data atual")
            return redirect('/medicos/abrir_horario')
        
        horario_abrir = datasAbertas(
            data=data,
            user=request.user,
        )
        
        horario_abrir.save()
        
        messages.add_message(request, constants.SUCCESS, 'Horário registrado com sucesso')
        return redirect('/medicos/abrir_horario')
    
@login_required
def consultas_medico(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    # Busca todas as consultas do dia atual
    hoje = datetime.now().date()
    # Consulta que o médico vai ter nessa data atual
    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1)) # lt - Menor do que.(A data de hoje mais um dia) | timedelta Intervalo de tempo
    
    # Consulta(todas) que foi buscada se o id tiver dentro da lista de id consultas_hoje vai ser remov.do BD, vai trazer todas as consultas. 
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})

@login_required
def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    if request.method == "GET":
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'documentos': documentos}) 
    elif request.method == "POST":
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')
        
        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Consulta cancelada')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        elif consulta.status == "F":
            messages.add_message(request, constants.WARNING, 'Consulta finalizada, você não pode mais inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        consulta.link = link
        consulta.status = 'I'
        consulta.save()
        messages.add_message(request, constants.SUCCESS, 'Consulta inicializada!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
@login_required
def finalizar_consulta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta é de outro médico')
        return redirect(f'/medicos/abrir_horario/{id_consulta}')
    consulta.status = 'F'
    consulta.save()
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

@login_required
def add_documento(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta é de outro médico')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')
    
    if not documento:
        messages.add_message(request, constants.ERROR, 'Preencha o campo documento!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso.')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

@login_required
def dashboard(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir a dashboard')
        return redirect('/usuarios/sair')
    
    # Primeiro filtro, passo, é pegar todas as consultas de um único usuário.
    # Segundo filtro, filtrar pelas datas dos últimos 7 dias. | range - [datetime.now().date() - timedelta(days=7), datetime.now().date() + timedelta(days=1)], se utiliza para pegar uma qt de dados necessário.
    # annotate - Qt de consulta em cada data
    consultas = Consulta.objects.filter(data_aberta__user=request.user)\
    .filter(data_aberta__data__range=[datetime.now().date() - timedelta(days=7), datetime.now().date() + timedelta(days=1)])\
    .annotate().values('data_aberta__data').annotate(quantidade=Count('id'))
    print(consultas)
    datas = [i['data_aberta__data'].strftime("%d-%m-%Y") for i in consultas] # strftime - converte
    quantidade = [i['quantidade'] for i in consultas]
    
    return render(request, 'dashboard.html', {'datas': datas, 'quantidade': quantidade}) 