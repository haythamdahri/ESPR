from django.shortcuts import render, redirect,resolve_url
from django.http import HttpResponse,Http404,HttpResponseRedirect
from .models import *
from .forms import *
from django.core.mail import send_mail
from django.template.loader import  get_template
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import  PasswordResetForm
from django.contrib.auth import logout , login , authenticate
from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.tokens import default_token_generator
from django.template.response import TemplateResponse

# Create your views here.


def home(request):
    context = dict()
    context['contact_form'] = ContactForm()
    return render(request, 'index1.html', context)


def test(request):
    return render(request,'index.html')

def signup(request):
    if request.user.is_authenticated:
        messages.info(request, "Vous êtes connecté")
        return redirect('main_app:home')
    if request.method == 'POST':
        form_inscription = FormProfilInscription(request.POST)
        if form_inscription.is_valid():
            userr = form_inscription.save(commit=False)
            user = User.objects.create_user(userr.username,userr.email,userr.password)
            user.is_active = False
            user.last_name = userr.last_name.lower()
            user.first_name = userr.first_name.lower()
            user.email = user.email.lower()
            user.save()
            profil = Profil.objects.get_or_create(user=user)[0]
            profil.genre = form_inscription.cleaned_data.get('genre')
            if profil.genre == 'homme':
                photo_profil = Image.objects.get(image="default_profil_m.png")
            else:
                photo_profil = Image.objects.get(image="default_profil_f.png")

            profil.photo_profil = photo_profil
            profil.photo_couverture = Image.objects.get(image="default_cover.png")
            profil.save()

            send_confirmation_signup_mail(request,user)# une méthode qu'on a nous meme défini ( un peu plus bas )

            return render(request, 'authentification/signupNew.html', {'form_inscription': form_inscription,})
    else:
        form_inscription = FormProfilInscription()

    return render(request, 'authentification/signupNew.html', {'form_inscription':form_inscription})


def confirm_email_signup(request,id_user,token_email):
    user = get_object_or_404(User, id=id_user)

    if user.is_active:
        messages.warning(request, "Votre email est déjà confirmé.")
        return redirect('main_app:log_in')

    if user.profil.token_email_expiration <= timezone.now():
        messages.warning(request,
                         "Votre lien a expiré. <strong><a href='/main/confirm_mail/resend'>Renvoyer l'email</a></strong> ")
        return redirect('main_app:log_in')
    else:
        if user.profil.token_email == token_email:
            user.is_active = True
            user.save()
            messages.success(request,"Votre email a été confirmé.")
            return redirect('main_app:log_in')
        else:
            raise Http404("Une erreur s'est produite.")

    return redirect('main_app:log_in')


def log_in(request):
    if request.user.is_authenticated:
        return redirect('main_app:home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email.lower())  # on le récupère juste pour vérifier s'il est actif
        except:
            user = None


        if user is not None:
            if not user.is_active:
                messages.warning(request,
                                 "Votre compte n'est pas encore activé, Veuiller l'activer en cliquant sur le lien vous a été envoyé via mail. <strong><a href='/confirm_mail/resend/'>Renvoyer l'email</a></strong> ")
                return redirect('main_app:log_in')
            else: # S'il a un email valide + est actif , on verifie son mdp
                user = authenticate(username=email,
                                        password=password)  # ici on le récupère pour voir s'il a tapé le bon mdp
                if user is not None: # Si l'email valide + password  valide + actif
                    login(request, user)
                    return redirect('main_app:home')
                else:
                    messages.error(request, "L'email ou le mot de passe est incorrect.")
                    return redirect('main_app:log_in')
        else:
            messages.error(request, "L'email ou le mot de passe est incorrect.")
            return redirect('main_app:log_in')

    form_login = loginform()
    return render(request, "authentification/login_ESPR.html", {'form_login':form_login})


def password_reset(request, is_admin_site=False,template_name='authentification/reset_password_form_ESPR.html',email_template_name='emails/reset_password_email.html',subject_template_name='authentification/reset_password_subject.txt',password_reset_form=PasswordResetForm,token_generator=default_token_generator,post_reset_redirect=None,from_email=None,current_app=None,extra_context=None,html_email_template_name='emails/reset_password_email.html'):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('main_app:password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form_reset_password': form,
        'title': ('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)

def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('main_app:home')
    else:
        return redirect('main_app:log_in')



def send_confirmation_signup_mail(request,user=None): # Methode normal , pas une vue, utilisée pour envoyer un mail dans la view signup et confirm_mail_resend

    if user is None :
        messages.error(request,'Une erreur s\'est produite.<br>Peut être que l\'email indiqué n\'est pas enregistré.<br>Veuillez Réessayer ')
    elif user.is_active:
        messages.warning(request,
                         'Votre compte est déjà activé')

    else:
        generated_token = get_random_string(length=32)
        user.profil.token_email = generated_token
        user.profil.token_email_expiration = timezone.now() + timedelta(days=2)
        user.profil.save()
        message = get_template('emails/signup_confirm_email.html').render({'user': user})

        send_mail(
            'ESPR : Finalisez votre inscription',
            message,
            'admin@socifly.com',
            [user.email],
            fail_silently=False,
            html_message=message,
        )

        messages.success(request,
                         'Un e-mail de vérification vous a été envoyé à l\'adresse '+user.email+'.<br>Cliquez sur le lien inclu dans l\'e-mail pour activer votre compte. ')


def confirm_mail_resend(request): #Vue utilisée quand on clique sur Renvoyer un autre email et qu'on tape l'email dans le formulaire, on le recupere par get
    if 'email' in request.GET:
        try:
            user = User.objects.get(email=request.GET.get('email').lower())
        except:
            user = None

        send_confirmation_signup_mail(request, user)

    return render(request, 'authentification/confirm_mail_form_ESPR.html')


def contactus(request):

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save(commit=True)
            messages.success(request,'Votre message a été envoyé.<br>Nous vous répondrons dans les plus bref délais.')
            if 'is_home' in request.POST:
                return redirect(resolve_url('main_app:home')+'#contact')
            return render(request, 'main/contactus.html', {'contact_form': contact_form})
    else:
        contact_form = ContactForm()

    return render(request,'main/contactus.html',{'contact_form':contact_form})

def error_400(request):
    return render(request, 'errors_pages/400.html')

def error_403(request):
    return render(request, 'errors_pages/403.html')

def error_404(request):
    return render(request, 'errors_pages/404.html')

def error_500(request):
    return render(request, 'errors_pages/500.html')