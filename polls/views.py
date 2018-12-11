from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.core.mail import send_mail
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from dateutil.relativedelta import relativedelta
from django.http import QueryDict
import datetime
import logging
import json

# Instanciando a classe que poderá ser utilizada como debugger
logger = logging.getLogger(__name__)

# Busca os dias restantes para o início do curso
def GetClassDaysLeft(request):
    if request.user.is_authenticated:
        classdateleft = datetime.datetime(2019, 1, 1) - datetime.datetime.now()
        classdaysleft = classdateleft.days
        if classdaysleft > 1:
            return str(classdaysleft) + " dias restantes"
        elif classdaysleft == 1:
            return "Amanhã"
        else:
            return "Seu curso já começou!"
    else:
        return ""

def home(request):
    return render(request, 'home.html', {"home": "active", "classtimeleft" : GetClassDaysLeft(request)})

def contact(request):
    if request.method == 'POST':
        form = request.POST
        contactButton = form.get('contact', None)
        if contactButton != None:
            firstname = form.get('firstname', None)
            lastname = form.get('lastname', None)
            email = form.get('email', None)
            comment = form.get('comment', None)

            # Enviando email para o usuário
            send_mail(
                subject='Trainme recebeu seu contato! ' + firstname,
                from_email='dev.fauser@gmail.com',
                recipient_list=[email],
                fail_silently=False,
                message='',
                html_message='Olá!<br/><br/> Ficamos felizes em receber seu contato, em breve um de nossos especialistas irá respondê-lo.<br/>Obrigado!<br/><br/> Att,<br/>Equipe Trainme'
            )

            # Notificando a equipe Trainme que uma mensagem foi submetida
            send_mail(
                subject='Contato recebido de ' + firstname,
                from_email='dev.fauser@gmail.com',
                recipient_list=['dev.fauser@gmail.com'],
                fail_silently=False,
                message='',
                html_message='<b>Contator:</b> ' + firstname + ' ' + lastname +
                '<br/><br/><b>Comment:</b><br/>' + comment + '<br/><br/> Email: ' + email
            )
            return render(request, 'contact.html', {"contato": "active", "message": "Mensagem enviada com sucesso!"})
    return render(request, 'contact.html', {"contato": "active"})

@login_required
def logout(request):
    auth_logout(request)
    return render(request, 'home.html', {"home": "active", "classtimeleft" : GetClassDaysLeft(request)})


def login(request):
    # Redirecionar o usuário caso ele já esteja logado e tente manualmente ou por cache voltar à tela de login
    if request.user.is_authenticated:
        return render(request, 'home.html', {"home": "active"})
        
    if request.method == 'POST':
        form = request.POST
        loginButton = form.get('login', None)
        registerButton = form.get('register', None)

        # Caso a chamada seja pelo botão de login
        if loginButton != None:
            email = form.get('email', None)
            password = form.get('password', None)
            user = authenticate(username=email, password=password)
            if user is not None:
                auth_login(request, user)
                return render(request, 'home.html', {"home": "active", "classtimeleft" : GetClassDaysLeft(request)})
            else:
                return render(request, 'login.html', {"loginerrormessage": "Email ou senha incorretos. Tente novamente!", "login": "active"})

        # Caso a chamada seja pelo botão de registro
        elif registerButton != None:
            # Checando se a idade do usuário é maior que 18 anos.
            birth_date = form.get('birthdate', None)
            birth_date_datetime = datetime.datetime.strptime(
                birth_date, '%Y-%m-%d')
            if birth_date_datetime > (datetime.datetime.now() - relativedelta(years=18)):
                return render(request, 'login.html', {"registererrormessage": "O usuário deve ter mais que 18 anos para se cadastrar. Tente novamente!", "login": "active"})

            # Chamando o get_or_create, que retorna informações do usuário ou cria o mesmo.
            email = form.get('email', None)
            user, created = User.objects.get_or_create(
                username=email, email=email)
            if created:
                # Recebendo as variáves do form
                name = form.get('name', None)
                phone = form.get('phone', None)
                password = form.get('password', None)
                classname = form.get('classname', None)

                # Setando os atributos do usuário em questão
                user.profile.birth_date = birth_date
                user.profile.phone = phone
                user.profile.classname = classname
                user.first_name = name
                user.set_password(password)
                user.save()

                # Autenticando o usuário automaticamente após o registro
                user = authenticate(username=email, password=password)
                auth_login(request, user)
                return render(request, 'home.html', {"home": "active", "classtimeleft" : GetClassDaysLeft(request), "registersuccess" : True})
            else:
                return render(request, 'login.html', {"registererrormessage": "O email que você está tentando cadastrar já existe. Tente novamente!", "login": "active"})
    
    # Informações de qual curso o usuário escolheu na página HOME
    choosedclassname = 'curso'
    cursoByQuery = request.GET.urlencode("curso")
    if cursoByQuery:
        choosedclassname = QueryDict(cursoByQuery)['curso']

    return render(request, 'login.html', {"login": "active", choosedclassname: "selected"})
