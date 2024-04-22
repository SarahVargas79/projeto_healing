from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants # constants Qual tipo de erro DEBUG...
from django.contrib import messages #messages - função responsável por criar a mensagem
from django.contrib import auth # auth - Faz a valid. dos dados

# Create your views here.
def cadastro(request):
    # Se a req. foi feita pelo navegador
    if request.method == "GET":
        return render(request, 'cadastro.html')
    # Se o tipo da req. for POST, ou seja, enviado form.
    elif request.method == "POST":
        # get() - Pegue esses dados
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, "Senhas não conferem!")
            return redirect('/usuarios/cadastro')
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, "Senha deve conter 6 ou mais caracteres!")
            return redirect('/usuarios/cadastro')
        
        # filter - Trazer alguns dados do BD, onde todos os dados seja igual ao nome digitado.
        # Validação para não cadastrar o mesmo username
        users = User.objects.filter(username=username)
        
        # exists - Se houver algum valor querySet exiba True, se não houver exiba false
        if users.exists():
            messages.add_message(request, constants.ERROR, "Já existe um usuário com esse username")
            return redirect('/usuarios/cadastro')
        
        # Salvando os dados.
        # objects - Acessar os atributos
        # create_user - função já criada pelo Django para salvar os usuários....
        # Vai criar uma linha no BD
        user = User.objects.create_user(
            # username antes - Campo do BD  = username depois - Valor que vai ser inserido no campo
            username=username,
            email=email,
            password=senha
        )
        
        return redirect('/usuarios/login')
    
def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        # authenticate - Verifica no BD se as credencias existem
        user = auth.authenticate(request, username=username, password=senha)
        
        # Vai pegar o usu e linkar, por ex: na req. tem o IP, vai ser ligado o usu a esse IP, em quanto estiver ativo e acessar a plataforma por esse IP, o usu vai estar longado com esse usuário, ou seja, conectou uma req. com um usuário
        if user:
            auth.login(request, user)
            return redirect('/pacientes/home')
        
        messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos')
        return redirect('/usuarios/login')

def logout(request):
    auth.logout(request)
    return redirect('/usuarios/login')