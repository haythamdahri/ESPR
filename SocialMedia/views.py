import re
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.template.defaultfilters import lower
from main_app.models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect, QueryDict, HttpResponseNotFound
from django.template.response import TemplateResponse
from .models import *
from .forms import *
from django.views.generic import ListView
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, timedelta
import warnings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout, login, authenticate
from django.core import serializers
from django.core.serializers import json
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.tokens import default_token_generator
from .models import *
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string


# Haytham

def home(request):
    if request.user.is_authenticated:
        context = {}
        page = request.GET.get('page', 1)
        context['mes_pages_entreprises'] = PageEntreprise.objects.filter(
            Q(moderateurs__in=[request.user.profil]) | Q(administrateurs__in=[request.user.profil]))
        statutsSignles = StatutSignales.objects.filter(signal_sender=request.user.profil)
        myPosts = Statut.objects.filter(publisher=request.user.profil).exclude(pk__in=statutsSignles)
        friendsAccept = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=1).values('emetteur')
        friendsSend = DemandeAmi.objects.filter(emetteur=request.user.profil, statut=1).values('recepteur')
        suivre = Suivie.objects.filter(follower=request.user.profil).values('followed_profil')
        friendsPosts = Statut.objects.filter(Q(publisher_id__in=friendsAccept) | Q(publisher_id__in=friendsSend) | Q(publisher_id__in=suivre))
        statuts = myPosts | friendsPosts
        statuts = statuts.distinct().order_by('-date_statut')
        paginator = Paginator(statuts, 20)
        context['statuts'] = paginator.get_page(page)
        context['statutForm'] = StatutsForm()
        context['amis'] = friendsAccept.count() + friendsSend.count()
        return render(request, 'SocialMedia/acceuil/acceuil.html', context)
    else:
        return render(request, 'SocialMedia/acceuil_deconnecte.html')

def profil(request):
    context = dict()
    if request.user.is_authenticated:
        p = Profil.objects.get(user=request.user)
        context['is_first'] = p.is_first_socialmedia
        if context['is_first']:
            p.is_first = False
            p.save()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['photoform'] = PhotoForm()
        context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
        context['FormAjouterLangue'] = FormAjouterLangue()
        context['langues'] = LangueProfil.objects.filter(profil=request.user.profil)
        context['experiences'] = Experience.objects.filter(profil=request.user.profil)
        context['formations'] = Formation.objects.filter(profil=request.user.profil)
        context['FormExperience'] = FormExperience()
        context['FormFormation'] = FormFormation()
        context['nom_entreprises'] = Entreprise.noms_entreprises()
        context['nom_postes'] = Poste.noms_postes()
        context['nom_ecoles'] = Ecole.noms_ecoles()
        context['nom_organismes'] = Organisme.noms_organismes()
        context['FormBenevolat'] = FormBenevolat()
        context['benevolats'] = ActionBenevole.get_user_benevolats(request.user)
        context['FormInformations'] = FormInformations()
        context['FormInformationsUser'] = FormInformationsUser()
        context['FormInformationsProfil'] = FormInformationsProfil(user=request.user)
        context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if
                                    request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()])

        return render(request, 'SocialMedia/myprofil/myprofil.html', context)
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('main_app:log_in')

def changephotoprofil(request):
    if request.user.is_authenticated:
        photoform = PhotoForm(data=request.POST, files=request.FILES or None)
        if request.method == "POST":
            if photoform.is_valid():
                photo = photoform.save()
                p = request.user.profil
                p.photo_profil = photo
                p.save()
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
                return JsonResponse(context)
        else:
            return redirect("SocialMedia:myprofil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")

def changephotocouverture(request):
    if request.user.is_authenticated:
        photoform = PhotoForm(data=request.POST, files=request.FILES or None)
        if request.method == "POST":
            if photoform.is_valid():
                photo = photoform.save()
                p = request.user.profil
                p.photo_couverture = photo
                p.save()
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
                return JsonResponse(context)
        else:
            return redirect("SocialMedia:myprofil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")

def ajaxUser(request):
    if request.user.is_authenticated:
        pid = request.GET.get('pid')
        p = Profil.objects.get(id=pid)
        if p.user.last_login is not None:
            last_login = p.user.last_login.strftime("%m %b %y %I:%M")
        else:
            last_login = "Non connecté"
        context = {'statut': True,
                   'username': p.user.first_name + ' ' + p.user.last_name,
                   'last_login': last_login,
                   'photo_profil': p.photo_profil.image.url
                   }
        return JsonResponse(context, safe=False)
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")

def log_in(request):
    if request.user.is_authenticated:
        return redirect('SocialMedia:myprofil')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                p = Profil.objects.get(user=user)
                p.user.last_login = now()
                login(request, user)
                return redirect('SocialMedia:login')
            else:
                messages.warning(request,
                                 "Compte Non Activé, Veuiller L'activer par l'email envoyé vers votre adresse electronique")
                return redirect('main_app:login')
        else:
            messages.warning(request, "Username Ou Mot De Passe Incorrect")
            return redirect('main_app:login')
    else:
        return redirect('main_app:login')

def groupesMyProfil(request):
    if request.user.is_authenticated:
        context = dict()
        if request.method == "GET" and 'is_ajax_request' in request.GET:
            groupes = list()
            for groupe in Groupe.objects.all():
                print(groupe.admins.all())
                if request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all() or request.user.profil in groupe.adherents.all() or request.user.profil == groupe.creator:
                    g = dict()
                    g['id'] = groupe.id
                    g['photo_profil'] = groupe.photo_profil.image.url
                    g['photo_couverture'] = groupe.photo_couverture.image.url
                    g['statut'] = groupe.statut_groupe
                    g['nom'] = groupe.nom
                    g['description'] = groupe.description
                    g[
                        'nbMembres'] = groupe.admins.all().count() + groupe.moderators.all().count() + groupe.adherents.all().count()
                    groupes.append(list(g.values()))
            paginator = Paginator(groupes, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            profilGroupes = list(paginator.get_page(page))
            isNumPagesExcessed = False
            previous_page_number = 1
            next_page_number = 1
            if page is None:
                page = 1
                previous_page_number = 1
                next_page_number = 2
            else:
                if int(page) > paginator.num_pages:
                    isNumPagesExcessed = True
                    page = paginator.num_pages
                    previous_page_number = page - 1
                    next_page_number = page
                elif int(page) < 1:
                    page = 1
                    previous_page_number = 1
                    next_page_number = 2
                else:
                    previous_page_number = int(page) - 1
                    next_page_number = int(page) + 1
            context = {
                'statut': True,
                'has_previous': paginator.get_page(page).has_previous(),
                'has_next': paginator.get_page(page).has_next(),
                'previous_page_number': previous_page_number,
                'next_page_number': next_page_number,
                'num_pages': paginator.num_pages,
                'current_page': page,
                'groupes': list(profilGroupes),
                'NumPagesExcessed': isNumPagesExcessed,
                'nbGroupes': len(groupes),
            }
            if context['nbGroupes'] == 0:
                context['msg'] = "Vous n'êtes pas membre d'aucun groupe"
            return JsonResponse(context, safe=False)
        else:
            p = Profil.objects.get(user=request.user)
            context['is_first'] = p.is_first_socialmedia
            if context['is_first']:
                p.is_first = False
                p.save()
            context['profiles'] = Profil.objects.all().order_by('-id')[:20]
            context['photoform'] = PhotoForm()
            context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
            context['FormAjouterLangue'] = FormAjouterLangue()
            context['langues'] = LangueProfil.objects.filter(profil=request.user.profil)
            context['FormExperience'] = FormExperience()
            context['FormFormation'] = FormFormation()
            context['nom_entreprises'] = Entreprise.noms_entreprises()
            context['nom_postes'] = Poste.noms_postes()
            context['nom_ecoles'] = Ecole.noms_ecoles()
            context['nom_organismes'] = Organisme.noms_organismes()
            context['FormBenevolat'] = FormBenevolat()
            context['benevolats'] = ActionBenevole.get_user_benevolats(request.user)
            context['FormInformations'] = FormInformations()
            context['FormInformationsUser'] = FormInformationsUser()
            context['FormInformationsProfil'] = FormInformationsProfil(user=request.user)
            context['profiles'] = Profil.objects.all().order_by('-id')[:20]
            context['photoform'] = PhotoForm()
            context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
            profilGroupes = [groupe for groupe in Groupe.objects.all() if
                             request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()]
            context['nbGroupes'] = len(profilGroupes)
            page = request.GET.get('page')
            paginator = Paginator(profilGroupes, 12)
            context['profilGroupes'] = paginator.get_page(page)
            context['nbGroupes'] = len(profilGroupes)
            if len(profilGroupes) == 0:
                context['msg'] = "Vous n'êtes pas membre d'aucun groupe"
                return render(request, 'SocialMedia/myprofil/groupesMyProfil.html', context)
            return render(request, 'SocialMedia/myprofil/groupesMyProfil.html', context)
        p = Profil.objects.get(user=request.user)
        context['is_first'] = p.is_first_socialmedia
        if context['is_first']:
            p.is_first = False
            p.save()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['photoform'] = PhotoForm()
        context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['photoform'] = PhotoForm()
        context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
        context['FormAjouterLangue'] = FormAjouterLangue()
        context['langues'] = LangueProfil.objects.filter(profil=request.user.profil)
        context['FormExperience'] = FormExperience()
        context['FormFormation'] = FormFormation()
        context['nom_entreprises'] = Entreprise.noms_entreprises()
        context['nom_postes'] = Poste.noms_postes()
        context['nom_ecoles'] = Ecole.noms_ecoles()
        context['nom_organismes'] = Organisme.noms_organismes()
        context['FormBenevolat'] = FormBenevolat()
        context['benevolats'] = ActionBenevole.get_user_benevolats(request.user)
        context['FormInformations'] = FormInformations()
        context['FormInformationsUser'] = FormInformationsUser()
        context['FormInformationsProfil'] = FormInformationsProfil(user=request.user)
        return render(request, 'SocialMedia/myprofil/groupesMyProfil.html', context)
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect('main_app:log_in')

def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('SocialMedia:home')
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect('main_app:log_in')

def demandesProfil(request):
    if request.user.is_authenticated:
        context = dict()
        formDemande = demandeForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid():
            demande = DemandeAmi.objects.get(id=formDemande.cleaned_data['demande'])
            demande.statut = formDemande.cleaned_data['statut']
            demande.save()
            demandesAmis = list(DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).values())
            context = {'statut': demande.statut,
                       'ami': demande.emetteur.user.first_name + ' ' + demande.emetteur.user.last_name,
                       'demande': demande.id,
                       'nbdemandes': len(demandesAmis),
                       'demandesAmis': demandesAmis,
                       }
            return JsonResponse(context, safe=False)
        else:
            demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).order_by('id')
            paginator = Paginator(demandesAmis, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            context['formDemande'] = formDemande
            context['nbdemandes'] = demandesAmis.count()
            context['demandesAmis'] = paginator.get_page(page)
            context['photoform'] = PhotoForm()
            context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if
                                        request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()])
            context['profiles'] = Profil.objects.all().order_by('-id')[:20]
            context['FormAjouterLangue'] = FormAjouterLangue()
            context['langues'] = LangueProfil.objects.filter(profil=request.user.profil)
            context['FormExperience'] = FormExperience()
            context['FormFormation'] = FormFormation()
            context['nom_entreprises'] = Entreprise.noms_entreprises()
            context['nom_postes'] = Poste.noms_postes()
            context['nom_ecoles'] = Ecole.noms_ecoles()
            context['nom_organismes'] = Organisme.noms_organismes()
            context['FormBenevolat'] = FormBenevolat()
            context['benevolats'] = ActionBenevole.get_user_benevolats(request.user)
            context['FormInformations'] = FormInformations()
            context['FormInformationsUser'] = FormInformationsUser()
            context['FormInformationsProfil'] = FormInformationsProfil(user=request.user)
            return render(request, 'SocialMedia/myprofil/demandesMyProfil.html', context)
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('main_app:log_in')

def demandeViaAjax(request):
    demandesAmis = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).order_by('id').values()
    paginator = Paginator(demandesAmis, 12)  # Show 3 Profiles per page
    page = request.GET.get('page')
    demAmis = list(paginator.get_page(page))
    isNumPagesExcessed = False
    previous_page_number = 1
    next_page_number = 1
    if page is None:
        page = 1
        previous_page_number = 1
        next_page_number = 2
    else:
        if int(page) > paginator.num_pages:
            isNumPagesExcessed = True
            page = paginator.num_pages
            previous_page_number = page - 1
            next_page_number = page
        elif int(page) < 1:
            page = 1
            previous_page_number = 1
            next_page_number = 2
        else:
            previous_page_number = int(page) - 1
            next_page_number = int(page) + 1
    context = {
        'statut': True,
        'has_previous': paginator.get_page(page).has_previous(),
        'has_next': paginator.get_page(page).has_next(),
        'previous_page_number': previous_page_number,
        'next_page_number': next_page_number,
        'num_pages': paginator.num_pages,
        'current_page': page,
        'demandesAmis': demAmis,
        'nbdemandes': demandesAmis.count(),
        'NumPagesExcessed': isNumPagesExcessed,
    }
    return JsonResponse(context, safe=False)


# EndHaytham

# Chipop

@login_required
def search(request):
    keywords = request.GET.get('keywords')
    if keywords is None or keywords == "":
        raise Http404
    # Contacts Search
    profils = Profil.objects.filter(Q(user__last_name__contains=keywords) | Q(user__first_name__contains=keywords),
                                    user__is_active=True).exclude(id=request.user.profil.id).exclude(Q(id__in=DemandeAmi.objects.filter().values('emetteur_id'))|Q(id__in=DemandeAmi.objects.filter().values('recepteur_id')))
    # Groupes Search
    groupes = Groupe.objects.filter(nom__contains=keywords)
    # Offres d'emploi Search
    offres = OffreEmploi.objects.filter(Q(type_contrat__contains=keywords) | Q(diplome_requis__contains=keywords) | Q(
        description_poste__contains=keywords) | Q(profil_recherche__contains=keywords) | Q(
        page_entreprise__presentation_entreprise__contains=keywords) | Q(type_emploi__contains=keywords) | Q(
        nom_poste__contains=keywords), en_cours=True)

    receivedRequest = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=request.user.profil, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    friends = dict()
    for f in emetteurs:
        p = Profil.objects.get(id=f)
        friends[f] = f
    for f in recepteurs:
        p = Profil.objects.get(id=f)
        friends[f] = f
    return render(request, 'SocialMedia/search/search_all.html',
                  {'keywords': keywords, 'friends':friends, 'profils': profils, 'groupes': groupes, 'offres': offres})

@login_required
def search_members(request):
    keywords = request.GET.get('keywords')
    if keywords is None or keywords == "":
        raise Http404

    # Contacts Search
    profils_list = Profil.objects.filter(Q(user__last_name__contains=keywords) | Q(user__first_name__contains=keywords),
                                         user__is_active=True).exclude(id=request.user.profil.id)

    paginator = Paginator(profils_list, 1)

    page = request.GET.get('page')
    profils = paginator.get_page(page)

    return render(request, 'SocialMedia/search/search_members.html', {'profils': profils, 'keywords': keywords})

@login_required
def getNextMembers(request):
    context = dict()
    keywords = request.GET.get('keywords')
    profils_list = Profil.objects.filter(Q(user__last_name__contains=keywords) | Q(user__first_name__contains=keywords),
                                         user__is_active=True).exclude(id=request.user.profil.id)

    paginator = Paginator(profils_list, 1)

    page = request.GET.get('page')
    profils = paginator.get_page(page)
    context['profils'] = profils
    ps = render_to_string('SocialMedia/search/profil_search.html', context, request)
    return JsonResponse(ps, safe=False)

@login_required
def getNextGroupes(request):
    context = dict()
    keywords = request.GET.get('keywords')
    groupes_list = Groupe.objects.filter(nom__contains=keywords)

    paginator = Paginator(groupes_list, 1)

    page = request.GET.get('page')
    groupes = paginator.get_page(page)
    context['groupes'] = groupes
    ps = render_to_string('SocialMedia/search/groupe_search.html', context, request)
    return JsonResponse(ps, safe=False)


@login_required
def search_groupes(request):
    keywords = request.GET.get('keywords')
    if keywords is None or keywords == "":
        raise Http404

    # Groupes Search
    groupes_list = Groupe.objects.filter(nom__contains=keywords)

    paginator = Paginator(groupes_list, 1)

    page = request.GET.get('page')
    groupes = paginator.get_page(page)

    return render(request, 'SocialMedia/search/search_groupes.html', {'groupes': groupes, 'keywords': keywords})

@login_required
def search_offres(request):
    keywords = request.GET.get('keywords')
    duree = request.GET.get('duree')
    if keywords is None or keywords is "":
        raise Http404

    # Offres d'emploi Search
    if keywords == "all":
        offres_list = OffreEmploi.objects.filter(en_cours=True)
    else:
        offres_list = OffreEmploi.objects.filter(
            Q(type_contrat__contains=keywords) | Q(diplome_requis__contains=keywords) | Q(
                description_poste__contains=keywords) | Q(profil_recherche__contains=keywords) | Q(
                page_entreprise__presentation_entreprise__contains=keywords) | Q(
                type_emploi__contains=keywords) | Q(
                nom_poste__contains=keywords), en_cours=True)

    if duree is not None and duree is not "":
        if duree is "semaine":
            one_week_ago = datetime.today() - timedelta(days=7)
            offres_list.filter(date_publication__gte=one_week_ago)
        elif duree is "mois":
            one_month_ago = datetime.today() - timedelta(days=31)
            offres_list.filter(date_publication__gte=one_month_ago)

    paginator = Paginator(offres_list, 1)

    page = request.GET.get('page')
    offres = paginator.get_page(page)

    return render(request, 'SocialMedia/search/search_offres.html', {'offres': offres, 'keywords': keywords, 'duree':duree})

@login_required
def getNextOffres(request):
    keywords = request.GET.get('keywords')
    duree = request.GET.get('duree')
    if keywords is None or keywords is "":
        raise Http404

    # Offres d'emploi Search
    if keywords == "all":
        offres_list = OffreEmploi.objects.filter(en_cours=True)
    else:
        offres_list = OffreEmploi.objects.filter(
            Q(type_contrat__contains=keywords) | Q(diplome_requis__contains=keywords) | Q(
                description_poste__contains=keywords) | Q(profil_recherche__contains=keywords) | Q(
                page_entreprise__presentation_entreprise__contains=keywords) | Q(
                type_emploi__contains=keywords) | Q(
                nom_poste__contains=keywords), en_cours=True)

    if duree is not None and duree is not "":
        if duree is "semaine":
            one_week_ago = datetime.today() - timedelta(days=7)
            offres_list.filter(date_publication__gte=one_week_ago)
        elif duree is "mois":
            one_month_ago = datetime.today() - timedelta(days=31)
            offres_list.filter(date_publication__gte=one_month_ago)

    paginator = Paginator(offres_list, 1)

    page = request.GET.get('page')
    offres = paginator.get_page(page)

    offres_list = render_to_string('SocialMedia/search/offre_search.html', {'offres': offres, 'keywords': keywords}, request)
    return JsonResponse(offres_list, safe=False)


def test(request):
    return render(request, 'SocialMedia/test.html')


def ajouterLangue(request):
    formAjouterLangue = FormAjouterLangue(request.POST)

    if formAjouterLangue.is_valid():
        langue_profil = formAjouterLangue.save(commit=False)
        langue_profil.profil = request.user.profil
        langue_profil.save()

        langues = LangueProfil.objects.filter(profil=request.user.profil)
        liste_langues = render_to_string('SocialMedia/myprofil/informations/liste_langues.html', {'langues': langues},
                                         request=request)
        return JsonResponse({'liste_langues': liste_langues})
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_ajouter_langue.html',
            {'FormAjouterLangue': formAjouterLangue},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def getModifierLangue(request):
    id_langue = request.GET.get('id_langue', None)

    if id_langue is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    langue_profil = LangueProfil.objects.get(id=id_langue)
    formModifierLangue = FormAjouterLangue(instance=langue_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_langue.html',
                  {'formModifierLangue': formModifierLangue, 'id_langue': id_langue})


def modifierLangue(request):
    id_langue = id = request.POST.get("id_langue")

    langue__profil = LangueProfil.objects.get(id=request.POST.get("id_langue"))

    formAjouterLangue = FormAjouterLangue(request.POST, instance=langue__profil)
    print(formAjouterLangue)

    if formAjouterLangue.is_valid():
        langue_profil = formAjouterLangue.save(commit=False)
        langue_profil.profil = request.user.profil
        langue_profil.save()

        langues = LangueProfil.objects.filter(profil=request.user.profil)

        liste_langues_profil = render_to_string('SocialMedia/myprofil/informations/liste_langues.html',
                                                {'langues': langues}, request=request)
        return JsonResponse({'liste_langues_profil': liste_langues_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_langue.html',
            {'formModifierLangue': formAjouterLangue, 'id_langue': id_langue},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def supprimerLangue(request):
    id_langue = request.GET.get('id_langue', None)
    if id_langue is None:
        return Http404()

    LangueProfil.objects.get(id=id_langue).delete()

    langues = LangueProfil.objects.filter(profil=request.user.profil)
    # return JsonResponse({'messagee': 'La langue a été ajoutée avec succès','langues':serializers.serialize('langues', langues) }, safe=False)
    return render(request, 'SocialMedia/myprofil/informations/liste_langues.html', {'langues': langues})


def ajouterExperience(request):
    formExperience = FormExperience(request.POST)

    if formExperience.is_valid():
        experience_profil = formExperience.save(commit=False)
        experience_profil.profil = request.user.profil

        experience_profil.regler_date()

        if experience_profil.actuel:
            experience_profil.date_fin = None

        entreprise = get_object_or_none(Entreprise, nom=experience_profil.nom_entreprise)
        poste = get_object_or_none(Poste, nom_poste=experience_profil.nom_poste)

        if entreprise:
            experience_profil.entreprise = entreprise
        if poste:
            experience_profil.poste = poste

        experience_profil.save()

        experiences = Experience.get_user_experiences(request.user)

        liste_experiences = render_to_string('SocialMedia/myprofil/informations/liste_experiences.html',
                                             {'experiences': experiences},
                                             request=request)
        return JsonResponse({'liste_experiences': liste_experiences})
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_ajouter_experience.html',
            {'FormExperience': formExperience},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def supprimerExperience(request):
    id_experience = request.GET.get('id_experience', None)
    if id_experience is None:
        return Http404()

    Experience.objects.get(id=id_experience).delete()

    experiences = Experience.get_user_experiences(request.user)
    # return JsonResponse({'messagee': 'La langue a été ajoutée avec succès','langues':serializers.serialize('langues', langues) }, safe=False)
    return render(request, 'SocialMedia/myprofil/informations/liste_experiences.html', {'experiences': experiences})


def getModifierExperience(request):
    id_experience = request.GET.get('id_experience', None)

    if id_experience is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    experience_profil = Experience.objects.get(id=id_experience)
    FormModifierExperience = FormExperience(instance=experience_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_experience.html',
                  {'FormModifierExperience': FormModifierExperience, 'id_experience': id_experience})


def modifierExperience(request):
    id_experience = request.POST.get("id_experience")
    experience__profil = Experience.objects.get(id=id_experience)

    formModifierExperience = FormExperience(request.POST, instance=experience__profil)

    if formModifierExperience.is_valid():
        experience = formModifierExperience.save(commit=False)
        experience.profil = request.user.profil

        experience.date_debut = experience.date_debut.replace(day=1)
        experience.date_fin = experience.date_fin.replace(day=1)

        if experience.actuel:
            experience.date_fin = None

        entreprise = get_object_or_none(Entreprise, nom=experience.nom_entreprise)
        poste = get_object_or_none(Poste, nom_poste=experience.nom_poste)

        if entreprise:
            experience.entreprise = entreprise
        else:
            experience.entreprise = None

        if poste:
            experience.poste = poste
        else:
            experience.poste = None

        experience.save()

        experiences = Experience.get_user_experiences(request.user)
        liste_benevolats_profil = render_to_string('SocialMedia/myprofil/informations/liste_experiences.html',
                                                   {'experiences': experiences}, request=request)
        return JsonResponse({'liste_experiences': liste_benevolats_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_experience.html',
            {'FormModifierExperience': formModifierExperience, 'id_experience': id_experience},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)


def ajouterFormation(request):
    formFormation = FormFormation(request.POST)

    if formFormation.is_valid():
        formation_profil = formFormation.save(commit=False)
        formation_profil.profil = request.user.profil

        formation_profil.regler_date()

        ecole = get_object_or_none(Ecole, nom=formation_profil.nom_ecole)

        if ecole:
            formation_profil.nom_ecole = ecole.nom

        formation_profil.save()

        formations = Formation.get_user_formations(request.user)

        liste_formations = render_to_string('SocialMedia/myprofil/informations/liste_formations.html',
                                            {'formations': formations},
                                            request=request)
        return JsonResponse({'liste_formations': liste_formations})
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_ajouter_formation.html',
            {'FormFormation': formFormation},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def supprimerFormation(request):
    id_formation = request.GET.get('id_formation', None)
    if id_formation is None:
        return Http404()

    Formation.objects.get(id=id_formation).delete()

    formations = Formation.get_user_formations(request.user)
    return render(request, 'SocialMedia/myprofil/informations/liste_formations.html', {'formations': formations})


def getModifierFormation(request):
    id_formation = request.GET.get('id_formation', None)

    if id_formation is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    formation_profil = Formation.objects.get(id=id_formation)
    formFormation = FormFormation(instance=formation_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_formation.html',
                  {'FormFormation': formFormation, 'id_formation': id_formation})


def modifierFormation(request):
    id_formation = request.POST.get("id_formation")
    formation__profil = Formation.objects.get(id=id_formation)

    formModifierFormation = FormFormation(request.POST, instance=formation__profil)

    if formModifierFormation.is_valid():
        formation = formModifierFormation.save(commit=False)
        formation.profil = request.user.profil

        formation.regler_date()

        ecole = get_object_or_none(Ecole, nom=formation.nom_ecole)

        if ecole:
            formation.ecole = ecole
        else:
            formation.ecole = None

        formation.save()

        formations = Formation.get_user_formations(request.user)
        liste_formations_profil = render_to_string('SocialMedia/myprofil/informations/liste_formations.html',
                                                   {'formations': formations}, request=request)
        return JsonResponse({'liste_formations': liste_formations_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_formation.html',
            {'FormFormation': formModifierFormation, 'id_formation': id_formation},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)


def ajouterBenevolat(request):
    formBenevolat = FormBenevolat(request.POST)

    if formBenevolat.is_valid():
        benevolat_profil = formBenevolat.save(commit=False)
        benevolat_profil.profil = request.user.profil

        benevolat_profil.regler_date()

        organisme = get_object_or_none(Organisme, nom=benevolat_profil.nom_organisme)
        poste = get_object_or_none(Poste, nom_poste=benevolat_profil.nom_poste)

        if organisme:
            benevolat_profil.organisme = organisme
        if poste:
            benevolat_profil.poste = poste

        benevolat_profil.save()

        benevolats = ActionBenevole.get_user_benevolats(request.user)
        liste_benevolats = render_to_string('SocialMedia/myprofil/informations/liste_benevolat.html',
                                            {'benevolats': benevolats},
                                            request=request)
        return JsonResponse({'liste_benevolats': liste_benevolats})
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_ajouter_benevolat.html',
            {'FormBenevolat': formBenevolat},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


def supprimerBenevolat(request):
    id_benevolat = request.GET.get('id_benevolat', None)
    if id_benevolat is None:
        return Http404()

    ActionBenevole.objects.get(id=id_benevolat).delete()

    benevolats = ActionBenevole.get_user_benevolats(request.user)
    return render(request, 'SocialMedia/myprofil/informations/liste_benevolat.html', {'benevolats': benevolats})


def getModifierBenevolat(request):
    id_benevolat = request.GET.get('id_benevolat', None)

    if id_benevolat is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite "}, safe=False)

    benevolat_profil = ActionBenevole.objects.get(id=id_benevolat)

    formBenevolat = FormBenevolat(instance=benevolat_profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_benevolat.html',
                  {'FormBenevolat': formBenevolat, 'id_benevolat': id_benevolat})


def modifierBenevolat(request):
    id_benevolat = request.POST.get("id_benevolat")

    benevolat__profil = ActionBenevole.objects.get(id=id_benevolat)

    formModifierBenevolat = FormBenevolat(request.POST, instance=benevolat__profil)

    if formModifierBenevolat.is_valid():
        benevolat = formModifierBenevolat.save(commit=False)
        benevolat.profil = request.user.profil

        benevolat.regler_date()

        poste = get_object_or_none(Poste, nom_poste=benevolat.nom_poste)
        organisme = get_object_or_none(Organisme, nom=benevolat.nom_organisme)

        if poste:
            benevolat.poste = poste
        else:
            benevolat.poste = None

        if organisme:
            benevolat.organisme = organisme
        else:
            benevolat.organisme = None

        benevolat.save()

        benevolats = ActionBenevole.get_user_benevolats(request.user)
        liste_benevolats_profil = render_to_string('SocialMedia/myprofil/informations/liste_benevolat.html',
                                                   {'benevolats': benevolats}, request=request)
        return JsonResponse({'liste_benevolats': liste_benevolats_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_benevolat.html',
            {'FormBenevolat': formModifierBenevolat, 'id_benevolat': id_benevolat},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)


def getModifierInformations(request):
    formInformations = FormInformations(instance=request.user.profil)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_informations.html',
                  {'FormInformations': formInformations})


def modifierInformations(request):
    formInformations = FormInformations(request.POST, instance=request.user.profil)

    if formInformations.is_valid():
        formInformations.save()

        liste_informations = render_to_string('SocialMedia/myprofil/informations/liste_informations.html',
                                              request=request)
        return JsonResponse({'liste_informations': liste_informations}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_informations.html',
            {'FormInformations': formInformations},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)

    return JsonResponse({'messagee': 'HELLO'}, safe=False)


def getModifierInformationsProfil(request):
    formInformationsProfil = FormInformationsProfil(user=request.user, instance=request.user.profil)
    formInformationsUser = FormInformationsUser(instance=request.user)

    return render(request, 'SocialMedia/myprofil/modals/modal_modifier_informations_profil.html',
                  {'FormInformationsProfil': formInformationsProfil, 'FormInformationsUser': formInformationsUser})


def modifierInformationsProfil(request):
    formInformationsProfil = FormInformationsProfil(request.user, request.POST, instance=request.user.profil)
    formInformationsUser = FormInformationsUser(request.POST, instance=request.user)

    if formInformationsProfil.is_valid() and formInformationsUser.is_valid():
        formInformationsProfil.save()
        formInformationsUser.save()
        liste_informations_profil = render_to_string('SocialMedia/myprofil/informations/liste_informations_profil.html',
                                                     {'user': request.user})
        return JsonResponse({'liste_informations_profil': liste_informations_profil}, safe=False)
    else:
        modal = render_to_string(
            'SocialMedia/myprofil/forms/form_modifier_informations_profil.html',
            {'FormInformationsProfil': formInformationsProfil, 'FormInformationsUser': formInformationsUser},
            request=request)
        return JsonResponse({'modal': modal}, safe=False)
    return JsonResponse({'error': 'Une erreur s\est produite.'}, safe=False)


# Offre d'emploi + page d'entreprise

def creer_entreprise(request):
    if request.method == "POST":
        formCreerEntreprise = FormCreerEntreprise(request.POST, request.FILES)
        formCreerPageEntreprise = FormCreerPageEntreprise(request.POST, request.FILES)
        if formCreerEntreprise.is_valid() and formCreerPageEntreprise.is_valid():
            entreprise = formCreerEntreprise.save()
            page_entreprise = formCreerPageEntreprise.save(commit=False)
            page_entreprise.entreprise = entreprise
            page_entreprise.save()
            page_entreprise.abonnees.add(request.user.profil)
            page_entreprise.administrateurs.add(request.user.profil)
            page_entreprise.save()

            return redirect('SocialMedia:page_entreprise',
                            id_page_entreprise=page_entreprise.id)  # affichage form Creer Offre
        else:
            return render(request, 'SocialMedia/entreprise/page_creer_entreprise.html',
                          {'formCreerEntreprise': formCreerEntreprise,
                           'formCreerPageEntreprise': formCreerPageEntreprise})
    formCreerEntreprise = FormCreerEntreprise()
    formCreerPageEntreprise = FormCreerPageEntreprise()

    return render(request, 'SocialMedia/entreprise/page_creer_entreprise.html',
                  {'formCreerEntreprise': formCreerEntreprise, 'formCreerPageEntreprise': formCreerPageEntreprise,
                   })

def creer_groupe(request):
    if request.method == "POST":
        form_creer_groupe = FormCreerGroupe(request.POST, request.FILES)
        form_photo_groupe = FormPhotosGroupe(request.POST, request.FILES)
        form_cover_groupe = FormPhotosGroupe(request.POST, request.FILES)
        if form_creer_groupe.is_valid() and form_photo_groupe.is_valid() and form_cover_groupe.is_valid():
            groupe = form_creer_groupe.save(commit=False)
            photo_groupe = form_photo_groupe.save()
            cover_groupe = form_cover_groupe.save()
            groupe.creator = request.user.profil
            groupe.date_creation = now()
            groupe.photo_profil = photo_groupe
            groupe.photo_couverture = cover_groupe
            groupe.save()
            groupe.admins.add(request.user.profil)
            groupe.save()
            messages.success(request,'Votre groupe {0} à été crée avec succé'.format(groupe.nom))
            return redirect('SocialMedia:groupe', pk=groupe.id)
        else:
            return render(request, 'SocialMedia/groupe/page_creer_groupe.html',
                          {'formCreerGroupe': form_creer_groupe, 'formPhotoGroupe': form_photo_groupe,
                           'formCoverGroupe': form_cover_groupe})

    form_creer_groupe = FormCreerGroupe()
    form_photo_groupe = FormPhotosGroupe()
    form_cover_groupe = FormPhotosGroupe()
    return render(request, 'SocialMedia/groupe/page_creer_groupe.html',
                  {'formCreerGroupe': form_creer_groupe, 'formPhotoGroupe':form_photo_groupe, 'formCoverGroupe':form_cover_groupe})


def creer_offre_emploi(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    if page_entreprise is None:
        raise Http404

    if not page_entreprise.is_administrateur(request.user) and not page_entreprise.is_moderateur(request.user):
        return redirect('SocialMedia:page_entreprise', id_page_entreprise=id_page_entreprise)

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    nom_postes = Poste.noms_postes()

    if request.method == "POST":
        formCreerOffreEmploi = FormCreerOffreEmploi(request.POST, request.FILES)
        if formCreerOffreEmploi.is_valid():
            offre = formCreerOffreEmploi.save(commit=False)
            offre.page_entreprise = PageEntreprise.objects.get(id=id_page_entreprise)
            offre.profil_publicateur = request.user.profil

            poste = get_object_or_none(Poste, nom_poste=offre.nom_poste)
            if poste:
                offre.poste = poste

            offre.save()
            return redirect('SocialMedia:page_offre_emploi', id_offre_emploi=offre.id)
        else:
            return render(request, 'SocialMedia/offre_emploi/creer_offre_emploi.html',
                          {'formCreerOffreEmploi': formCreerOffreEmploi,
                           'nom_postes': nom_postes, 'page_entreprise': page_entreprise, 'employes': employes,
                           'autres_entreprises': autres_entreprises})  # affichage form Creer Offre

    formCreerOffreEmploi = FormCreerOffreEmploi()
    return render(request, 'SocialMedia/entreprise/page_poster_offre.html',
                  {'formCreerOffreEmploi': formCreerOffreEmploi,
                   'nom_postes': nom_postes, 'page_entreprise': page_entreprise, 'employes': employes,
                   'autres_entreprises': autres_entreprises})  # affichage form Creer Offre


def page_offres_emploi_entreprise(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    if page_entreprise is None:
        raise Http404

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)
    offres_emploi = OffreEmploi.objects.filter(page_entreprise=page_entreprise)

    return render(request, 'SocialMedia/entreprise/page_offres_emplois_entreprise.html',
                  {'offres_emploi': offres_emploi, 'page_entreprise': page_entreprise, 'employes': employes,
                   'autres_entreprises': autres_entreprises})  # affichage form Creer Offre


def page_offre_emploi(request, id_offre_emploi):
    offre_emploi = get_object_or_none(OffreEmploi, id=id_offre_emploi)

    if offre_emploi is None:
        raise Http404

    id_page_entreprise = offre_emploi.page_entreprise.id
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)

    if page_entreprise is None:
        raise Http404

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    return render(request, 'SocialMedia/entreprise/page_offre_emploi.html',
                  {'offre': offre_emploi, 'page_entreprise': page_entreprise, 'employes': employes,
                   'autres_entreprises': autres_entreprises})


def page_offre_emploi_postuler(request, id_offre_emploi):
    offre_emploi = get_object_or_none(OffreEmploi, id=id_offre_emploi)

    if offre_emploi is None:
        raise Http404

    id_page_entreprise = offre_emploi.page_entreprise.id
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)

    if page_entreprise is None:
        raise Http404

    offre_emploi.profil_postulants.add(request.user.profil)
    messages.success(request, "Votre candidature a été envoyée.")

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    return render(request, 'SocialMedia/entreprise/page_offre_emploi.html',
                  {'offre': offre_emploi, 'page_entreprise': page_entreprise, 'employes': employes,
                   'autres_entreprises': autres_entreprises})


def page_offre_emploi_retirer_candidature(request, id_offre_emploi):
    offre_emploi = get_object_or_none(OffreEmploi, id=id_offre_emploi)

    if offre_emploi is None:
        raise Http404

    id_page_entreprise = offre_emploi.page_entreprise.id
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)

    if page_entreprise is None:
        raise Http404

    offre_emploi.profil_postulants.remove(request.user.profil)
    messages.success(request, "Votre candidature a été retirée.")

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    return render(request, 'SocialMedia/entreprise/page_offre_emploi.html',
                  {'offre': offre_emploi, 'page_entreprise': page_entreprise, 'employes': employes,
                   'autres_entreprises': autres_entreprises})


def page_offre_emploi_modifier(request, id_offre_emploi):
    offre_emploi = get_object_or_none(OffreEmploi, id=id_offre_emploi)
    if offre_emploi is None:
        raise Http404

    if not offre_emploi.page_entreprise.is_administrateur(
            request.user) and not offre_emploi.page_entreprise.is_moderateur(request.user):
        return redirect('SocialMedia:page_entreprise', id_page_entreprise=offre_emploi.page_entreprise.id)

    page_entreprise = get_object_or_none(PageEntreprise, id=offre_emploi.page_entreprise.id)

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    nom_postes = Poste.noms_postes()

    if request.method == "POST":
        formModifierOffreEmploi = FormModifierOffreEmploi(request.POST, request.FILES, instance=offre_emploi)
        if formModifierOffreEmploi.is_valid():
            offre = formModifierOffreEmploi.save(commit=False)

            poste = get_object_or_none(Poste, nom_poste=offre.nom_poste)
            if poste:
                offre.poste = poste

            offre.save()
            return render(request, 'SocialMedia/entreprise/page_offres_emplois_entreprise.html',
                          {'nom_postes': nom_postes, 'page_entreprise': page_entreprise, 'employes': employes,
                           'autres_entreprises': autres_entreprises,
                           'offres_emploi': page_entreprise.offreemploi_set.all()})
        else:
            return render(request, 'SocialMedia/entreprise/page_modifier_offre_emploi.html',
                          {'formModifierOffreEmploi': formModifierOffreEmploi,
                           'nom_postes': nom_postes, 'page_entreprise': page_entreprise, 'employes': employes,
                           'autres_entreprises': autres_entreprises})  # affichage form Creer Offre

    formModifierOffreEmploi = FormModifierOffreEmploi(instance=offre_emploi)
    return render(request, 'SocialMedia/entreprise/page_modifier_offre_emploi.html',
                  {'formModifierOffreEmploi': formModifierOffreEmploi,
                   'nom_postes': nom_postes, 'page_entreprise': page_entreprise, 'employes': employes,
                   'autres_entreprises': autres_entreprises})  # affichage form Creer Offre


# Page Entreprise

def page_entreprise(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    if page_entreprise is None:
        raise Http404

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    photo_profil_form = FormPhotoProfilEntreprise()
    photo_couverture_form = FormPhotoCouvertureEntreprise()

    return render(request, 'SocialMedia/entreprise/page_entreprise.html',
                  {'photo_profil_form': photo_profil_form, 'photo_couverture_form': photo_couverture_form,
                   "page_principale": True, 'page_entreprise': page_entreprise, 'employes': employes,
                   'autres_entreprises': autres_entreprises})

def changer_photo_profil_entreprise(request,id_page_entreprise):
    form = FormPhotoProfilEntreprise(request.POST, request.FILES)
    if form.is_valid():
        p_e = PageEntreprise.objects.get(id=id_page_entreprise)
        e = Entreprise.objects.get(id=p_e.entreprise.id)
        e.logo = form.cleaned_data['logo']
        e.save()
        context = {'status': 'success', 'url': e.logo.url}
        return JsonResponse(context)
    else:
        context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
        return JsonResponse(context)


@login_required
def changer_photo_couverture_entreprise(request,id_page_entreprise):
    form = FormPhotoCouvertureEntreprise(request.POST, request.FILES)
    if form.is_valid():
        p_e = PageEntreprise.objects.get(id=id_page_entreprise)
        p_e.img_couverture = form.cleaned_data['img_couverture']
        p_e.save()
        context = {'status': 'success', 'url': p_e.img_couverture.url}
        return JsonResponse(context)
    else:
        context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
        return JsonResponse(context)




# Page Entreprise ajax

def get_modifier_entreprise(request):
    id_page_entreprise = request.GET.get("id_page_entreprise", None)

    message_erreur = ""
    if id_page_entreprise is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite"}, safe=False)

    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    if not page_entreprise or request.user.profil not in page_entreprise.administrateurs.all():
        return JsonResponse({'message_erreur': "Une erreur s'est produite"}, safe=False)

    formModifierPageEntreprise = FormModifierPageEntreprise(instance=page_entreprise)
    formModifierEntreprise = FormModifierEntreprise(instance=page_entreprise.entreprise)

    html_modifier_page_entreprise = render_to_string('SocialMedia/entreprise/forms/form_modifier_infos_entreprise.html',
                                                     {'formModifierPageEntreprise': formModifierPageEntreprise,
                                                      'formModifierEntreprise': formModifierEntreprise,
                                                      'id': page_entreprise.id}, request)
    return JsonResponse({'form': html_modifier_page_entreprise}, safe=False)


def modifier_entreprise(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)

    if page_entreprise is None:
        return JsonResponse({'message_erreur': "Une erreur s'est produite"}, safe=False)

    if request.user.profil not in page_entreprise.administrateurs.all():
        return JsonResponse({'message_erreur': "Une erreur s'est produite"}, safe=False)

    if request.method == "POST":
        formModifierEntreprise = FormModifierEntreprise(request.POST, instance=page_entreprise.entreprise)
        formModifierPageEntreprise = FormModifierPageEntreprise(request.POST, instance=page_entreprise)
        if formModifierEntreprise.is_valid() and formModifierPageEntreprise.is_valid():
            formModifierEntreprise.save()
            formModifierPageEntreprise.save()
            messages.success(request, "Page modifiée avec succès.")
            return JsonResponse({'redirect_url': reverse('SocialMedia:page_entreprise', args=[id_page_entreprise])})
        else:
            html_modifier_page_entreprise = render_to_string(
                'SocialMedia/entreprise/forms/form_modifier_infos_entreprise.html',
                {'formModifierPageEntreprise': formModifierPageEntreprise,
                 'formModifierEntreprise': formModifierEntreprise, 'id': page_entreprise.id}, request)
            return JsonResponse({'form': html_modifier_page_entreprise}, safe=False)
    else:
        return redirect('SocialMedia:page_entreprise', id_page_entreprise=id_page_entreprise)


# Page Entreprise end ajax

def suivre_entreprise(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    next = request.GET.get("next", None)
    if page_entreprise is None or next is None:
        raise Http404

    page_entreprise.abonnees.add(request.user.profil)
    return redirect(next)


def neplussuivre_entreprise(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    next = request.GET.get("next", None)
    if page_entreprise is None or next is None:
        raise Http404

    page_entreprise.abonnees.remove(request.user.profil)
    return redirect(next)


def entreprise_abonnees(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    if page_entreprise is None:
        raise Http404

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    abonnees_list = PageEntreprise.objects.get(id=id_page_entreprise).abonnees.all()
    paginator = Paginator(abonnees_list, 12)

    page = request.GET.get('page')
    abonnees = paginator.get_page(page)

    return render(request, "SocialMedia/entreprise/page_abonnees.html", {'abonnees': abonnees,
                                                                         'page_entreprise': page_entreprise,
                                                                         'employes': employes,
                                                                         'autres_entreprises': autres_entreprises})


def page_administration_entreprise(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    if page_entreprise is None:
        raise Http404

    if not page_entreprise.is_administrateur(request.user):
        raise Http404

    employes = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    return render(request, 'SocialMedia/entreprise/page_administration.html', {
        'page_entreprise': page_entreprise, 'employes': employes, 'autres_entreprises': autres_entreprises})


def page_administration_edit_admins(request):
    if request.method == "POST":
        id_admin = request.POST.get("admin", None)
        ancienneval = request.POST.get("ancienneval", None)
        id_page_entreprise = request.POST.get("ent", None)
        nouvelleval = request.POST.get("nouvelleval", None)

        if id_admin is None or ancienneval is None or id_page_entreprise is None or nouvelleval is None:
            raise Http404

        page_entreprise = PageEntreprise.objects.get(id=id_page_entreprise)

        if request.user.profil not in page_entreprise.administrateurs.all():  # Si l'utilisateur n'est pas admin d dik la page
            raise Http404

        if ancienneval == "administrateur" or ancienneval == "moderateur":
            print("d1")
            print(nouvelleval)
            if nouvelleval != "administrateur" and nouvelleval != "moderateur" and nouvelleval != "retirer_droit":
                raise Http404

            profil = Profil.objects.get(id=id_admin)
            if ancienneval == "administrateur":
                if profil not in page_entreprise.administrateurs.all():
                    raise Http404

                if nouvelleval == "moderateur":
                    page_entreprise.administrateurs.remove(profil)
                    page_entreprise.moderateurs.add(profil)
                if nouvelleval == "retirer_droit":
                    page_entreprise.administrateurs.remove(profil)
            if ancienneval == "moderateur":
                if profil not in page_entreprise.moderateurs.all():
                    raise Http404

                if nouvelleval == "administrateur":
                    page_entreprise.moderateurs.remove(profil)
                    page_entreprise.administrateurs.add(profil)
                if nouvelleval == "retirer_droit":
                    page_entreprise.moderateurs.remove(profil)
            return redirect('SocialMedia:page_administration_entreprise', id_page_entreprise=id_page_entreprise)
        else:
            raise Http404

    return redirect("SocialMedia:home")


def page_administration_add_admins(request):
    if request.method == "POST":
        email = request.POST.get("email", None)
        val = request.POST.get("val", None)
        id_page_entreprise = request.POST.get("ent", None)

        if email is None or val is None or id_page_entreprise is None:
            raise Http404

        page_entreprise = PageEntreprise.objects.get(id=id_page_entreprise)
        if request.user.profil not in page_entreprise.administrateurs.all():  # Si l'utilisateur n'est pas admin d dik la page
            raise Http404

        profil = get_object_or_none(Profil, user__email__iexact=email)
        if profil is None:
            messages.error(request, "Cet e-mail ne correspond à aucun utilisateur.")
            messages.info(request, email)
            return redirect('SocialMedia:page_administration_entreprise', id_page_entreprise=id_page_entreprise)

        if (val != "administrateur" and val != "moderateur"):
            raise Http404

        if val == "administrateur":
            if profil in page_entreprise.moderateurs.all():
                page_entreprise.moderateurs.remove(profil)
            page_entreprise.administrateurs.add(profil)
        if val == "moderateur":
            if profil in page_entreprise.administrateurs.all():
                page_entreprise.administrateurs.remove(profil)
            page_entreprise.moderateurs.add(profil)

        return redirect('SocialMedia:page_administration_entreprise', id_page_entreprise=id_page_entreprise)
    else:
        raise Http404


def page_employes_entreprise(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    if page_entreprise is None:
        raise Http404

    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise)
                                                       | Q(siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)

    employes_listee = Experience.objects.filter(entreprise=page_entreprise.entreprise, actuel=True).values('profil')
    employes_liste = Profil.objects.filter(id__in=employes_listee)
    paginator = Paginator(employes_liste, 12)

    page = request.GET.get('page')
    employes = paginator.get_page(page)

    return render(request, "SocialMedia/entreprise/page_employes.html", {'employes': employes,
                                                                         'page_entreprise': page_entreprise,
                                                                         'employes': employes,
                                                                         'autres_entreprises': autres_entreprises})


def page_entreprise_poster_offre(request, id_page_entreprise):
    page_entreprise = get_object_or_none(PageEntreprise, id=id_page_entreprise)
    if page_entreprise is None:
        raise Http404

    autres_entreprises = PageEntreprise.objects.filter(Q(entreprise__nom__icontains=page_entreprise.entreprise.nom) | Q(
        entreprise__typeEntreprise=page_entreprise.entreprise.typeEntreprise) | Q(
        siege_social__icontains=page_entreprise.siege_social) | Q(
        specialisation__icontains=page_entreprise.specialisation)).exclude(id=page_entreprise.id)
    formCreerOffreEmploi = FormCreerOffreEmploi()
    return render(request, "SocialMedia/entreprise/page_poster_offre.html", {
        'page_entreprise': page_entreprise, 'autres_entreprises': autres_entreprises,
        'formCreerOffreEmploi': formCreerOffreEmploi})


# EndChipop

# Haytham
def getProfil(request, pk):
    context = dict()
    try:
        if request.user.profil == Profil.objects.get(id=pk):
            return redirect('SocialMedia:myprofil')
        profil = Profil.objects.get(id=pk)
        if DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                     Q(recepteur=profil) | Q(recepteur=request.user.profil), statut=3).exists():
            messages.warning(request, "Le profil recherché est bloqué!")
            return redirect('SocialMedia:myprofil')
        context['profil'] = profil
        context['poste_actuel'] = Experience.objects.filter(profil=profil, actuel=True).values('poste').values(
            'nom_poste').last()
        context['poste_actuel_renseigne'] = Experience.objects.filter(profil=profil, actuel=True).values(
            'nom_poste').last()
        context['ecole'] = Formation.objects.filter(profil=profil, ecole__isnull=False).values('ecole__nom').last()
        context['ecole_renseignee'] = Formation.objects.filter(profil=profil, ecole__isnull=True).values(
            'nom_ecole').last()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['experiences'] = Experience.objects.filter(profil=profil)
        context['formations'] = Formation.objects.filter(profil=profil)
        context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=profil)
        context['is_followed'] = Suivie.objects.filter(followed_profil=profil, follower=request.user.profil).exists()
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                         Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                         statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                   statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if
                                    profil == groupe.creator or profil in groupe.adherents.all() or profil in groupe.admins.all() or profil in groupe.moderators.all()])
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                         Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                         statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                   statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        context['sont_ami'] = DemandeAmi.sont_ami(request.user, profil.user)
        return render(request, 'SocialMedia/profil/profil.html', context)
    except Profil.DoesNotExist:
        raise Http404


def followProfil(request, pk):
    if request.user.is_authenticated:
        context = dict()
        try:
            s = Suivie.objects.get(followed_profil=Profil.objects.get(id=pk), follower=request.user.profil)
            s.delete()
            context['statut'] = True
            context['message'] = "Profile devient non suivi"
            context['follow'] = False
            return JsonResponse(context, safe=False)
        except Suivie.DoesNotExist:
            Suivie.objects.create(followed_profil=get_object_or_404(Profil, id=pk), follower=request.user.profil)
            context['statut'] = True
            context['message'] = "Profile est suivi"
            context['follow'] = True
            return JsonResponse(context, safe=False)
        except Profil.DoesNotExist:
            context['statut'] = False
            context['message'] = "Profil a ete supprimé, veuiller actualiser!"
            context['follow'] = False
            return JsonResponse(context, safe=False)

    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')


def FriendsRequests(request, pk):
    if request.user.is_authenticated:
        context = dict()
        rep = int(request.POST.get('rep'))
        try:
            profil = Profil.objects.get(id=pk)
            demande = DemandeAmi.objects.get(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                             Q(recepteur=request.user.profil) | Q(recepteur=profil))
            context['statut'] = True
            if rep == -1:
                context['message'] = "La demande de {} à été annulée".format(
                    profil.user.first_name + ' ' + profil.user.last_name)
                context['friend'] = False
                demande.delete()
            elif rep == -2:
                context['message'] = "{} à été supprimé de la liste des amis".format(
                    profil.user.first_name + ' ' + profil.user.last_name)
                context['friend'] = False
                demande.delete()
            elif rep == 0:
                demande.statut = rep
                demande.emetteur = request.user.profil
                demande.recepteur = profil
                context['message'] = "Demande à été envoyée à {}".format(
                    profil.user.first_name + ' ' + profil.user.last_name)
                context['friend'] = False
                demande.save()
            elif rep == 1:
                demande.statut = rep
                context['message'] = "Vous etes Ami Avec {}".format(
                    profil.user.first_name + ' ' + profil.user.last_name)
                context['friend'] = True
                demande.save()
            elif rep == 2:
                demande.statut = rep
                context['message'] = "Vous avez refuser la demande de {}".format(
                    profil.user.first_name + ' ' + profil.user.last_name)
                context['friend'] = False
                demande.save()
            elif rep == 3:
                demande.statut = rep
                context['message'] = "{} à été bloqué.".format(profil.user.first_name + ' ' + profil.user.last_name)
                context['friend'] = False
                demande.save()
            return JsonResponse(context, safe=False)
        except DemandeAmi.DoesNotExist:
            try:
                profil = Profil.objects.get(id=pk)
                if rep == 0:
                    DemandeAmi.objects.create(recepteur=profil, emetteur=request.user.profil, statut=rep)
                    context['statut'] = True
                    context['message'] = "Demande à été envoyée à {}".format(
                        profil.user.first_name + ' ' + profil.user.last_name)
                    context['friend'] = False
                elif rep == 3:
                    DemandeAmi.objects.create(emetteur=request.user.profil, recepteur=profil, statut=rep)
                    context['message'] = "{} à été bloqué.".format(profil.user.first_name + ' ' + profil.user.last_name)
                    context['friend'] = False
                return JsonResponse(context, safe=False)
            except Profil.DoesNotExist:
                context['statut'] = False
                context['message'] = "Profil a ete supprimé, veuiller actualiser!"
                context['friend'] = False
                return JsonResponse(context, safe=False)
        except Profil.DoesNotExist:
            context['statut'] = False
            context['message'] = "Profil a ete supprimé, veuiller actualiser!"
            context['friend'] = False
            return JsonResponse(context, safe=False)
    else:
        messages.error(request, "Veuiller vous connecter!")
        return redirect('SocialMedia:login')


def getRequestsUpdates(request, pk):
    if request.user.is_authenticated:
        context = dict()
        profil = Profil.objects.get(id=pk)
        context['statut'] = True
        context['is_blocked'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                          Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                          statut=3).exists()
        context['is_followed'] = Suivie.objects.filter(followed_profil=profil, follower=request.user.profil).exists()
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                         Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                         statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                   statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        return JsonResponse(context, safe=False)


def getProfilGroupes(request, pk):
    context = dict()
    try:
        profil = Profil.objects.get(id=pk)
        if request.method == "GET" and 'is_ajax_request' in request.GET:
            groupes = list()
            for groupe in Groupe.objects.all():
                print(groupe.admins.all())
                if profil in groupe.admins.all() or profil in groupe.moderators.all() or profil in groupe.adherents.all():
                    g = dict()
                    g['id'] = groupe.id
                    g['photo_profil'] = groupe.photo_profil.image.url
                    g['photo_couverture'] = groupe.photo_couverture.image.url
                    g['statut'] = groupe.statut_groupe
                    g['nom'] = groupe.nom
                    g['description'] = groupe.description
                    g[
                        'nbMembres'] = groupe.admins.all().count() + groupe.moderators.all().count() + groupe.adherents.all().count()
                    groupes.append(list(g.values()))

            paginator = Paginator(groupes, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            profilGroupes = list(paginator.get_page(page))
            isNumPagesExcessed = False
            previous_page_number = 1
            next_page_number = 1
            if page is None:
                page = 1
                previous_page_number = 1
                next_page_number = 2
            else:
                if int(page) > paginator.num_pages:
                    isNumPagesExcessed = True
                    page = paginator.num_pages
                    previous_page_number = page - 1
                    next_page_number = page
                elif int(page) < 1:
                    page = 1
                    previous_page_number = 1
                    next_page_number = 2
                else:
                    previous_page_number = int(page) - 1
                    next_page_number = int(page) + 1
            context = {
                'statut': True,
                'has_previous': paginator.get_page(page).has_previous(),
                'has_next': paginator.get_page(page).has_next(),
                'previous_page_number': previous_page_number,
                'next_page_number': next_page_number,
                'num_pages': paginator.num_pages,
                'current_page': page,
                'groupes': list(profilGroupes),
                'NumPagesExcessed': isNumPagesExcessed,
                'nbGroupes': len(groupes),
            }
            if context['nbGroupes'] == 0:
                context['msg'] = profil.user.first_name + ' ' + profil.user.last_name + " n'appartient à aucun groupe."
            return JsonResponse(context, safe=False)
        else:
            profilGroupes = [groupe for groupe in Groupe.objects.all() if
                             profil == groupe.creator or profil in groupe.adherents.all() or profil in groupe.admins.all() or profil in groupe.moderators.all()]
            if request.user.profil == Profil.objects.get(id=pk):
                messages.info(request, "C'est votre profil")
                return redirect('SocialMedia:groupes')
            if DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil, statut=3).exists():
                messages.warning(request, "Les groupes concernent un profil bloqué!")
                return redirect('SocialMedia:myprofil')
            if DemandeAmi.objects.filter(recepteur=request.user.profil, emetteur=profil, statut=3).exists():
                messages.warning(request, "Les groupes du profil recherché vous a bloqué!")
                return redirect('SocialMedia:myprofil')
            context['profil'] = profil
            context['poste_actuel'] = Experience.objects.filter(profil=profil, actuel=True).values('poste').values(
                'nom_poste').last()
            context['poste_actuel_renseigne'] = Experience.objects.filter(profil=profil, actuel=True).values(
                'nom_poste').last()
            context['ecole'] = Formation.objects.filter(profil=profil, ecole__isnull=False).values('ecole__nom').last()
            context['ecole_renseignee'] = Formation.objects.filter(profil=profil, ecole__isnull=True).values(
                'nom_ecole').last()
            context['profiles'] = Profil.objects.all().order_by('-id')[:20]
            context['experiences'] = Experience.objects.filter(profil=profil)
            context['formations'] = Formation.objects.filter(profil=profil)
            context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=profil)
            context['is_followed'] = Suivie.objects.filter(followed_profil=profil,
                                                           follower=request.user.profil).exists()
            context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                             Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                             statut=1).exists()
            context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                       statut=0).exists()
            context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                                   statut=0).exists()
            context['sont_ami'] = DemandeAmi.sont_ami(request.user, profil.user)

            page = request.GET.get('page')
            paginator = Paginator(profilGroupes, 12)
            context['profilGroupes'] = paginator.get_page(page)
            context['nbGroupes'] = len(profilGroupes)
            if len(profilGroupes) == 0:
                context['msg'] = profil.user.first_name + ' ' + profil.user.last_name + " n'appartient à aucun groupe."
                return render(request, 'SocialMedia/profil/groupesProfil.html', context)
            return render(request, 'SocialMedia/profil/groupesProfil.html', context)
    except Profil.DoesNotExist:
        messages.error(request, "Le profil recherché n'existe pas!")
        return redirect('SocialMedia:myprofil')
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        context['groupes'] = Groupe.objects.filter(
            id__in=DemandeGroupe.objects.filter(emetteur=profil, reponse=True).values('groupe_recepteur'))
        context['profilGroupes'] = [groupe for groupe in Groupe.objects.all() if
                                    profil == groupe.creator or profil in groupe.adherents.all() or profil in groupe.admins.all() or profil in groupe.moderators.all()]
        if len(context['profilGroupes']) == 0:
            context['msg'] = profil.user.first_name + ' ' + profil.user.last_name + " n'appartient à aucun groupe."
            return render(request, 'SocialMedia/profil/groupesProfil.html', context)
        return render(request, 'SocialMedia/profil/groupesProfil.html', context)
    except Profil.DoesNotExist:
        messages.error(request, "Le profil recherché n'existe pas!")
        return redirect('SocialMedia:myprofil')
    except DemandeGroupe.DoesNotExist:
        context['msg'] = "Le profil ne s'appartient à aucun groupe"
        return render(request, 'SocialMedia/profil/groupesProfil.html', context)


def groupe(request, pk):
    if request.user.is_authenticated:
        context = dict()
        try:
            groupe = Groupe.objects.get(id=pk)
            page = request.GET.get('page', 1)
            statutsSignles = StatutSignales.objects.filter(signal_sender=request.user.profil).values('statut__id')
            statuts = Statut.objects.filter(mur_groupe=groupe, is_group_statut=True).exclude(
                pk__in=statutsSignles).order_by('-date_statut')
            paginator = Paginator(statuts, 2)
            context['statuts'] = paginator.get_page(page)
            context['now'] = now()
            context['groupe'] = groupe
            context['statutForm'] = StatutsForm()
            context['photoform'] = PhotoForm()
            context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
            context['is_request_sent'] = groupe.demandegroupe_set.filter(emetteur=request.user.profil,
                                                                         groupe_recepteur=groupe,
                                                                         reponse=False).exists()
            context['nbMembers'] = (
                    groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(
                user=request.user).count()
            context['is_member'] = False
            if request.user.profil in groupe.admins.all():
                context['is_member'] = True
            if request.user.profil in groupe.moderators.all():
                context['is_member'] = True
            if request.user.profil in groupe.adherents.all():
                context['is_member'] = True
            return render(request, 'SocialMedia/groupe/groupe.html', context)
        except Groupe.DoesNotExist or Profil.DoesNotExist:
            raise Http404
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')


def demandesGroupe(request, pk):
    if request.user.is_authenticated:
        context = dict()
        groupe = Groupe.objects.get(id=pk)
        if request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all():
            formDemande = demandeGroupeForm(request.POST or None)
            if request.method == "POST" and formDemande.is_valid():
                demande = DemandeGroupe.objects.get(id=formDemande.cleaned_data['demande'])
                context['demande'] = demande.id
                if formDemande.cleaned_data['reponse'] == 1:
                    demande.reponse = formDemande.cleaned_data['reponse']
                    demande.save()
                    groupe.adherents.add(demande.emetteur)
                    groupe.save()
                    context['reponse'] = demande.reponse
                    context['message'] = 'demande de {} à été approuvée'.format(
                        demande.emetteur.user.first_name + ' ' + demande.emetteur.user.last_name)
                elif formDemande.cleaned_data['reponse'] == 0:
                    context['message'] = 'demande de {} à été refusée'.format(
                        demande.emetteur.user.first_name + ' ' + demande.emetteur.user.last_name)
                    context['reponse'] = 0
                    demande.delete()
                context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
                context['statut'] = True,
                return JsonResponse(context, safe=False)
            elif request.method == "GET":
                demandesGroupe = groupe.demandegroupe_set.filter(reponse=False).order_by('id')
                paginator = Paginator(demandesGroupe, 12)  # Show 12 Profiles per page
                page = request.GET.get('page')
                context['formDemande'] = formDemande
                context['nbdemandes'] = demandesGroupe.count()
                context['demandesGroupe'] = paginator.get_page(page)
                context['photoform'] = PhotoForm()
                context['groupe'] = groupe
                context['nbMembers'] = (
                        groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(
                    user=request.user).count()
                context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
                context['is_request_sent'] = groupe.demandegroupe_set.filter(emetteur=request.user.profil,
                                                                             groupe_recepteur=groupe,
                                                                             reponse=False).exists()
                return render(request, 'SocialMedia/groupe/demandes_groupe.html', context)
        else:
            messages.error(request,
                           "Vous n'avez pas le droit de valider cette action, s'il s'agit d'une erreur veuiller nous contacter.")
            return redirect(groupe.get_absolute_url())
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')


def demandesGroupeViaAjax(request, pk):
    groupe = Groupe.objects.get(id=pk)
    demandesGroupe = DemandeGroupe.objects.filter(groupe_recepteur=groupe, reponse=False).order_by('id').values()
    paginator = Paginator(demandesGroupe, 12)  # Show 12 Profiles per page
    page = request.GET.get('page')
    demGroupe = list(paginator.get_page(page))
    isNumPagesExcessed = False
    previous_page_number = 1
    next_page_number = 1
    if page is None:
        page = 1
        previous_page_number = 1
        next_page_number = 2
    else:
        if int(page) > paginator.num_pages:
            isNumPagesExcessed = True
            page = paginator.num_pages
            previous_page_number = page - 1
            next_page_number = page
        elif int(page) < 1:
            page = 1
            previous_page_number = 1
            next_page_number = 2
        else:
            previous_page_number = int(page) - 1
            next_page_number = int(page) + 1
    context = {
        'statut': True,
        'has_previous': paginator.get_page(page).has_previous(),
        'has_next': paginator.get_page(page).has_next(),
        'previous_page_number': previous_page_number,
        'next_page_number': next_page_number,
        'num_pages': paginator.num_pages,
        'current_page': page,
        'demandesGroupe': demGroupe,
        'nbdemandes': demandesGroupe.count(),
        'NumPagesExcessed': isNumPagesExcessed,
        'nbMembres': (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().count()
    }
    return JsonResponse(context, safe=False)


def membresGroupe(request, pk):
    if request.user.is_authenticated:
        context = dict()
        groupe = Groupe.objects.get(id=pk)
        formDemande = membresAdminForm(request.POST or None)
        if request.method == "POST" and formDemande.is_valid():
            profil = get_object_or_404(Profil, id=formDemande.cleaned_data['profil'])
            if formDemande.cleaned_data['action'] == 3:
                groupe.admins.add(profil)
                groupe.moderators.remove(profil)
                groupe.adherents.remove(profil)
                groupe.save()
                context['message'] = '{} devient Administrateur.'.format(
                    profil.user.first_name + ' ' + profil.user.last_name)
            elif formDemande.cleaned_data['action'] == 2:
                groupe.moderators.add(profil)
                groupe.admins.remove(profil)
                groupe.adherents.remove(profil)
                groupe.save()
                context['message'] = '{} devient Moderateur.'.format(
                    profil.user.first_name + ' ' + profil.user.last_name)
            elif formDemande.cleaned_data['action'] == 1:
                groupe.admins.remove(profil)
                groupe.moderators.remove(profil)
                groupe.adherents.add(profil)
                groupe.save()
                context['message'] = '{} devenu Adherent.'.format(profil.user.first_name + ' ' + profil.user.last_name)
            elif formDemande.cleaned_data['action'] == 0:
                groupe.admins.remove(profil)
                groupe.moderators.remove(profil)
                groupe.adherents.remove(profil)
                groupe.save()
                context['message'] = '{} à été Banné.'.format(profil.user.first_name + ' ' + profil.user.last_name)
            else:
                context['statut'] = False
                return JsonResponse(context, safe=False)
            groupeMembers = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(
                user=request.user)
            context['statut'] = True
            context['nbMembers'] = groupeMembers.count()
            context['profil'] = profil.id
            return JsonResponse(context, safe=False)
        elif request.method == "GET":
            groupeMembers = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(
                user=request.user)
            paginator = Paginator(groupeMembers, 12)  # Show 12 Profiles per page
            page = request.GET.get('page')
            context['formDemande'] = formDemande
            context['nbMembers'] = groupeMembers.count()
            context['members'] = paginator.get_page(page)
            context['photoform'] = PhotoForm()
            context['groupe'] = groupe
            context['nbdemandes'] = groupe.demandegroupe_set.filter(reponse=False).count()
            context['is_request_sent'] = groupe.demandegroupe_set.filter(emetteur=request.user.profil,
                                                                         groupe_recepteur=groupe,
                                                                         reponse=False).exists()
            return render(request, 'SocialMedia/groupe/membres_groupe.html', context)
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')


def membersGroupeViaAjax(request, pk):
    groupe = Groupe.objects.get(id=pk)
    users_ID = list()
    groupeMembers = dict()
    if "admins" in request.GET:
        groupeMembers = groupe.admins.all().distinct().exclude(user=request.user).values()
    elif "moderators" in request.GET:
        groupeMembers = groupe.moderators.all().distinct().exclude(user=request.user).values()
    elif "adherents" in request.GET:
        groupeMembers = groupe.adherents.all().distinct().exclude(user=request.user).values()
    else:
        groupeMembers = (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(
            user=request.user).values()
    paginator = Paginator(groupeMembers, 12)  # Show 12 Profiles per page
    page = request.GET.get('page')
    memGroupe = paginator.get_page(page)
    isNumPagesExcessed = False
    previous_page_number = 1
    next_page_number = 1
    if page is None:
        page = 1
        previous_page_number = 1
        next_page_number = 2
    else:
        if int(page) > paginator.num_pages:
            isNumPagesExcessed = True
            page = paginator.num_pages
            previous_page_number = page - 1
            next_page_number = page
        elif int(page) < 1:
            page = 1
            previous_page_number = 1
            next_page_number = 2
        else:
            previous_page_number = int(page) - 1
            next_page_number = int(page) + 1
    context = {
        'statut': True,
        'has_previous': paginator.get_page(page).has_previous(),
        'has_next': paginator.get_page(page).has_next(),
        'previous_page_number': previous_page_number,
        'next_page_number': next_page_number,
        'num_pages': paginator.num_pages,
        'current_page': page,
        'membersGroupe': list(memGroupe),
        'nbMembers': groupeMembers.count(),
        'NumPagesExcessed': isNumPagesExcessed,
        'nbMembres': (groupe.admins.all() | groupe.moderators.all() | groupe.adherents.all()).distinct().exclude(
            id=request.user.profil.id).count(),
        'is_admin': groupe.admins.filter(user=request.user).exists()
    }
    return JsonResponse(context, safe=False)


def joinGroupeViaAjax(request, pk):
    if request.user.is_authenticated:
        context = dict()
        if request.method == "POST":
            try:
                print(request.POST.get('userRequestGroupe'))
                if request.POST.get('userRequestGroupe') == "1":
                    print('send request')
                    if DemandeGroupe.objects.filter(emetteur=Profil.objects.get(user=request.user),
                                                    groupe_recepteur=Groupe.objects.get(id=pk), reponse=False).exists():
                        DemandeGroupe.objects.filter(emetteur=Profil.objects.get(user=request.user),
                                                     groupe_recepteur=Groupe.objects.get(id=pk), reponse=False).delete()
                    DemandeGroupe.objects.create(emetteur=Profil.objects.get(user=request.user),
                                                 groupe_recepteur=Groupe.objects.get(id=pk), reponse=False)
                    context['statut'] = True
                    context['msg'] = "Demande envoyée avec succé"
                    return JsonResponse(context, safe=False)
                elif request.POST.get('userRequestGroupe') == "0":
                    print('cancel membership request')
                    groupe = Groupe.objects.get(id=pk)
                    groupe.admins.remove(request.user.profil)
                    groupe.moderators.remove(request.user.profil)
                    groupe.adherents.remove(request.user.profil)
                    groupe.save()
                    DemandeGroupe.objects.filter(emetteur=request.user.profil, groupe_recepteur=groupe).delete()
                    context['statut'] = True
                    context['msg'] = "Vous n'êtes plus memebre de ce groupe"
                    return JsonResponse(context, safe=False)
                elif request.POST.get('userRequestGroupe') == "-1":
                    print('cancel request')
                    DemandeGroupe.objects.get(emetteur=request.user.profil,
                                              groupe_recepteur=Groupe.objects.get(id=pk)).delete()
                    context['statut'] = True
                    context['msg'] = "Demande annulée"
                    return JsonResponse(context, safe=False)
            except Exception as e:
                context['statut'] = False
                context['msg'] = str(e)
                return JsonResponse(context, safe=False)
        else:
            context['statut'] = False
            return JsonResponse(context, safe=False)
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')


def changephotoprofilgroupe(request, pk):
    if request.user.is_authenticated:
        photoform = PhotoForm(data=request.POST, files=request.FILES or None)
        if request.method == "POST":
            if photoform.is_valid():
                photo = photoform.save()
                groupe = Groupe.objects.get(id=pk)
                groupe.photo_profil = photo
                groupe.save()
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
                return JsonResponse(context)
        else:
            return redirect("SocialMedia:myprofil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")


def changephotocouverturegroupe(request, pk):
    if request.user.is_authenticated:
        photoform = PhotoForm(data=request.POST, files=request.FILES or None)
        if request.method == "POST":
            if photoform.is_valid():
                photo = photoform.save()
                groupe = Groupe.objects.get(id=pk)
                groupe.photo_couverture = photo
                groupe.save()
                context = {'status': 'success', 'url': photo.image.url}
                return JsonResponse(context)
            else:
                context = {'status': 'fail', 'photo': 'Veuiller Salectionner Une Image'}
                return JsonResponse(context)
        else:
            return redirect("SocialMedia:myprofil")
    else:
        messages.error(request, "Veuiller Se Connecter!")
        return redirect("SocialMedia:login")


# EndHaytham
# Chipop


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None
    LangueProfil.objects.get(id=id_langue).delete()
    langues = LangueProfil.objects.filter(profil=request.user.profil)
    # return JsonResponse({'messagee': 'La langue a été ajoutée avec succès','langues':serializers.serialize('langues', langues) }, safe=False)
    return render(request, 'SocialMedia/myprofil/informations/liste_langues.html', {'langues': langues})


def generer_form_errors(form):
    message_erreur = ""
    for key, value in form.errors.items():
        message_erreur += key + " " + value.as_text()
    return message_erreur


# Haytham Statut


@login_required
def likeUnlikeStatut(request):
    statut = request.POST.get('statut')
    like = request.POST.get('lk')
    st = Statut.objects.get(id=statut)
    context = dict()
    if like == "1":
        st.likes.add(request.user.profil)
        context['statut'] = True
        context['nblikes'] = st.likes.all().count()
    else:
        st.likes.remove(request.user.profil)
        context['statut'] = True
        context['nblikes'] = st.likes.all().count()
    return JsonResponse(context, safe="False")

@login_required
def addComment(request):
    statutid = request.POST.get('statut')
    commentContent = request.POST.get('cmtContent')
    st = Statut.objects.get(id=statutid)
    comment = Commentaire.objects.create(comment=commentContent, date_commentaire=now(), statut=st,
                                         user=request.user.profil)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        comment.image.add(img)
    return render(request, 'SocialMedia/groupe/comments/commentaire_groupe_ajoute.html',
                  {'comment': comment, 'statutID': st.id, 'NbComments': st.commentaire_set.all().count(),
                   'addedComment': True})

@login_required
def addCommentMyProfil(request):
    statutid = request.POST.get('statut')
    commentContent = request.POST.get('cmtContent')
    st = Statut.objects.get(id=statutid)
    comment = Commentaire.objects.create(comment=commentContent, date_commentaire=now(), statut=st,
                                         user=request.user.profil)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        comment.image.add(img)
    return render(request, 'SocialMedia/myprofil/comments/commentaire_myprofil_ajoute.html',
                  {'comment': comment, 'statutID': st.id, 'NbComments': st.commentaire_set.all().count(),
                   'addedComment': True})

@login_required
def addCommentProfil(request):
    statutid = request.POST.get('statut')
    commentContent = request.POST.get('cmtContent')
    st = Statut.objects.get(id=statutid)
    comment = Commentaire.objects.create(comment=commentContent, date_commentaire=now(), statut=st,
                                         user=request.user.profil)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        comment.image.add(img)
    return render(request, 'SocialMedia/profil/comments/commentaire_profil_ajoute.html',
                  {'comment': comment, 'statutID': st.id, 'NbComments': st.commentaire_set.all().count(),
                   'addedComment': True})


@login_required
def addStatut(request, pk):
    statutContent = request.POST.get('contenu_statut')
    groupe = Groupe.objects.get(id=pk)
    st = Statut.objects.create(date_statut=now(), contenu_statut=statutContent, is_group_statut=True,
                               publisher=request.user.profil, mur_groupe=groupe)
    if 'image' in request.FILES:
        image = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                                profil=request.user.profil)
        image.save()
        st.images.add(image)
    if 'video' in request.FILES:
        video = ReseauSocialFile.objects.create(fichier=request.FILES['video'], date_telechargement=now(),
                                                profil=request.user.profil)
        video.save()
        st.videos.add(video)
    if 'document' in request.FILES:
        document = ReseauSocialFile.objects.create(fichier=request.FILES['document'], date_telechargement=now(),
                                                   profil=request.user.profil)
        document.save()
        st.files.add(document)
    post = render_to_string('SocialMedia/groupe/statuts/statuts_groupe.html',
                            {'statut': st, 'commentID': st.id, 'NbComments': st.commentaire_set.all().count(),
                             'addedStatut': True}, request)
    return JsonResponse(post, safe=False)

def addStatutMyProfil(request):
    statutContent = request.POST.get('contenu_statut')
    st = Statut.objects.create(date_statut=now(), contenu_statut=statutContent, is_profil_statut=True,
                               publisher=request.user.profil, mur_profil=request.user.profil)
    if 'image' in request.FILES:
        image = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                                profil=request.user.profil)
        image.save()
        st.images.add(image)
    if 'video' in request.FILES:
        video = ReseauSocialFile.objects.create(fichier=request.FILES['video'], date_telechargement=now(),
                                                profil=request.user.profil)
        video.save()
        st.videos.add(video)
    if 'document' in request.FILES:
        document = ReseauSocialFile.objects.create(fichier=request.FILES['document'], date_telechargement=now(),
                                                   profil=request.user.profil)
        document.save()
        st.files.add(document)
    post = render_to_string('SocialMedia/myprofil/statuts/statuts_myprofil.html',
                            {'statut': st, 'commentID': st.id, 'NbComments': st.commentaire_set.all().count(),
                             'addedStatut': True}, request)
    return JsonResponse(post, safe=False)

def addStatutProfil(request, pk):
    statutContent = request.POST.get('contenu_statut')
    st = Statut.objects.create(date_statut=now(), contenu_statut=statutContent, is_profil_statut=True,
                               publisher=request.user.profil, mur_profil=Profil.objects.get(id=pk))
    if 'image' in request.FILES:
        image = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                                profil=request.user.profil)
        image.save()
        st.images.add(image)
    if 'video' in request.FILES:
        video = ReseauSocialFile.objects.create(fichier=request.FILES['video'], date_telechargement=now(),
                                                profil=request.user.profil)
        video.save()
        st.videos.add(video)
    if 'document' in request.FILES:
        document = ReseauSocialFile.objects.create(fichier=request.FILES['document'], date_telechargement=now(),
                                                   profil=request.user.profil)
        document.save()
        st.files.add(document)
    post = render_to_string('SocialMedia/profil/statuts/statuts_profil.html',
                            {'statut': st, 'commentID': st.id, 'NbComments': st.commentaire_set.all().count(),
                             'addedStatut': True}, request)
    return JsonResponse(post, safe=False)

@login_required
def addReply(request):
    commentid = request.POST.get('comment')
    replyContent = request.POST.get('replyContent')
    commentaire = Commentaire.objects.get(id=commentid)
    print(commentid)
    print(replyContent)
    print(commentaire)
    rp = Reply.objects.create(commentaire=commentaire, user=request.user.profil, date_reply=now(),
                              replyContent=replyContent)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        rp.image.add(img)
    rep = render_to_string('SocialMedia/groupe/reply/groupe_comment_reply_ajoute.html',
                           {'reply': rp, 'NbReplies': commentaire.reply_set.all().count, 'addedStatut': True}, request)
    return JsonResponse(rep, safe=False)

@login_required
def addReplyMyProfil(request):
    commentid = request.POST.get('comment')
    replyContent = request.POST.get('replyContent')
    commentaire = Commentaire.objects.get(id=commentid)
    print(commentid)
    print(replyContent)
    print(commentaire)
    rp = Reply.objects.create(commentaire=commentaire, user=request.user.profil, date_reply=now(),
                              replyContent=replyContent)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        rp.image.add(img)
    rep = render_to_string('SocialMedia/myprofil/reply/myprofil_comment_reply_ajoute.html',
                           {'reply': rp, 'NbReplies': commentaire.reply_set.all().count, 'addedStatut': True}, request)
    return JsonResponse(rep, safe=False)

@login_required
def addReplyProfil(request):
    commentid = request.POST.get('comment')
    replyContent = request.POST.get('replyContent')
    commentaire = Commentaire.objects.get(id=commentid)
    print(commentid)
    print(replyContent)
    print(commentaire)
    rp = Reply.objects.create(commentaire=commentaire, user=request.user.profil, date_reply=now(),
                              replyContent=replyContent)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        rp.image.add(img)
    rep = render_to_string('SocialMedia/profil/reply/profil_comment_reply_ajoute.html',
                           {'reply': rp, 'NbReplies': commentaire.reply_set.all().count, 'addedStatut': True}, request)
    return JsonResponse(rep, safe=False)


@login_required
def likeUnlikeComment(request):
    comment = request.POST.get('comment')
    like = request.POST.get('lk')
    cm = Commentaire.objects.get(id=comment)
    context = dict()
    if like == "1":
        cm.likes.add(request.user.profil)
        context['statut'] = True
        context['nblikes'] = cm.likes.all().count()
    else:
        cm.likes.remove(request.user.profil)
        context['statut'] = True
        context['nblikes'] = cm.likes.all().count()
    return JsonResponse(context, safe="False")



@login_required
def likeUnlikeReply(request, ):
    reply = request.POST.get('reply')
    like = request.POST.get('lk')
    rp = Reply.objects.get(id=reply)
    context = dict()
    if like == "1":
        rp.likes.add(request.user.profil)
        context['statut'] = True
        context['nblikes'] = rp.likes.all().count()
    else:
        rp.likes.remove(request.user.profil)
        context['statut'] = True
        context['nblikes'] = rp.likes.all().count()
    return JsonResponse(context, safe="False")

def nbsp_Link(value):
    lines = value.split('\r\n')
    values = ""
    for line in lines:
        words = line.split(' ')
        for val in words:
            regex = re.compile(
                r'^((?:http|ftp)s?://)?'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)', re.IGNORECASE)
            v = lower(val)
            if re.match(regex, lower(v)):
                if ("http" not in val):
                    values += "<a target='_blank' href='http://" + val + "'>" + val + "</a>&nbsp"
                else:
                    values += "<a target='_blank' href='" + val + "'>" + val + "</a>&nbsp"
            else:
                values += val + "&nbsp"
        values += "<br />"
    return values

@login_required
def editStatut(request):
    contenuStatut = str(request.POST.get('contenuStatut'))
    statut = Statut.objects.get(id=request.POST.get('statut'))
    statut.contenu_statut = contenuStatut
    statut.save()
    context = dict()
    context['status'] = True
    context['NewContent'] = nbsp_Link(statut.contenu_statut)
    print(context['NewContent'])
    return JsonResponse(context, safe=False)

@login_required
def deleteStatut(request):
    statut = Statut.objects.get(id=int(request.POST.get('statut')))
    statut.delete()
    context = dict()
    context['status'] = True
    return JsonResponse(context, safe=False)

@login_required
def deleteComment(request):
    comment = Commentaire.objects.get(id=int(request.POST.get('comment')))
    comment.delete()
    statut = Statut.objects.get(id=int(request.POST.get('statut')))
    context = dict()
    context['status'] = True
    context['NbComments'] = statut.commentaire_set.all().count()
    return JsonResponse(context, safe=False)

@login_required
def editComment(request):
    if request.method == "GET":
        comment = Commentaire.objects.get(id=int(request.GET.get('comment')))
        modal = render_to_string('SocialMedia/groupe/modals/edit_comment.html', {'comment': comment}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuComment = str(request.POST.get('contenuComment'))
        comment = Commentaire.objects.get(id=request.POST.get('comment'))
        comment.comment = contenuComment
        comment.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(comment.comment)
        print(context['NewContent'])
        return JsonResponse(context, safe=False)

@login_required
def editCommentMyProfil(request):
    if request.method == "GET":
        comment = Commentaire.objects.get(id=int(request.GET.get('comment')))
        modal = render_to_string('SocialMedia/myprofil/modals/edit_comment.html', {'comment': comment}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuComment = str(request.POST.get('contenuComment'))
        comment = Commentaire.objects.get(id=request.POST.get('comment'))
        comment.comment = contenuComment
        comment.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(comment.comment)
        return JsonResponse(context, safe=False)

@login_required
def editCommentProfil(request):
    if request.method == "GET":
        comment = Commentaire.objects.get(id=int(request.GET.get('comment')))
        modal = render_to_string('SocialMedia/profil/modals/edit_comment.html', {'comment': comment}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuComment = str(request.POST.get('contenuComment'))
        comment = Commentaire.objects.get(id=request.POST.get('comment'))
        comment.comment = contenuComment
        comment.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(comment.comment)
        return JsonResponse(context, safe=False)

@login_required
def editReply(request):
    if request.method == "GET":
        reply = Reply.objects.get(id=int(request.GET.get('reply')))
        modal = render_to_string('SocialMedia/groupe/modals/edit_reply.html', {'reply': reply}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuReply = str(request.POST.get('contenuReply'))
        reply = Reply.objects.get(id=int(request.POST.get('reply')))
        reply.replyContent = contenuReply
        reply.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(reply.replyContent)
        return JsonResponse(context, safe=False)

@login_required
def editReplyMyProfil(request):
    if request.method == "GET":
        reply = Reply.objects.get(id=int(request.GET.get('reply')))
        modal = render_to_string('SocialMedia/myprofil/modals/edit_reply.html', {'reply': reply}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuReply = str(request.POST.get('contenuReply'))
        reply = Reply.objects.get(id=int(request.POST.get('reply')))
        reply.replyContent = contenuReply
        reply.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(reply.replyContent)
        return JsonResponse(context, safe=False)

@login_required
def editReplyProfil(request):
    if request.method == "GET":
        reply = Reply.objects.get(id=int(request.GET.get('reply')))
        modal = render_to_string('SocialMedia/profil/modals/edit_reply.html', {'reply': reply}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuReply = str(request.POST.get('contenuReply'))
        reply = Reply.objects.get(id=int(request.POST.get('reply')))
        reply.replyContent = contenuReply
        reply.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(reply.replyContent)
        return JsonResponse(context, safe=False)

@login_required
def deleteReply(request):
    reply = Reply.objects.get(id=int(request.POST.get('reply')))
    reply.delete()
    comment = Commentaire.objects.get(id=int(request.POST.get('commentaire')))
    context = dict()
    context['status'] = True
    context['NbReplies'] = comment.reply_set.all().count()
    return JsonResponse(context, safe=False)

@login_required
def MyProfilStatuts(request):
    if request.user.is_authenticated:
        context = dict()
        try:
            p = Profil.objects.get(user=request.user)
            page = request.GET.get('page', 1)
            statutsSignles = StatutSignales.objects.filter(signal_sender=request.user.profil).values('statut__id')
            statuts = Statut.objects.filter(mur_profil=p, is_profil_statut=True).exclude(
                pk__in=statutsSignles).order_by('-date_statut')
            paginator = Paginator(statuts, 20)
            context['statuts'] = paginator.get_page(page)
            context['now'] = now()
            context['is_first'] = p.is_first_socialmedia
            if context['is_first']:
                p.is_first = False
                p.save()
            context['profiles'] = Profil.objects.all().order_by('-id')[:20]
            context['photoform'] = PhotoForm()
            context['nbdemandes'] = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=0).count()
            context['nom_entreprises'] = Entreprise.noms_entreprises()
            context['nom_postes'] = Poste.noms_postes()
            context['nom_ecoles'] = Ecole.noms_ecoles()
            context['nom_organismes'] = Organisme.noms_organismes()
            context['FormInformations'] = FormInformations()
            context['FormInformationsUser'] = FormInformationsUser()
            context['FormInformationsProfil'] = FormInformationsProfil(user=request.user)
            context['nbGroupes'] = Groupe.objects.filter()
            context['statutForm'] = StatutsForm()
            groupes = list()
            for groupe in Groupe.objects.all():
                print(groupe.admins.all())
                if request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all() or request.user.profil in groupe.adherents.all() or request.user.profil == groupe.creator:
                    g = dict()
                    g['id'] = groupe.id
                    g['photo_profil'] = groupe.photo_profil.image.url
                    g['photo_couverture'] = groupe.photo_couverture.image.url
                    g['statut'] = groupe.statut_groupe
                    g['nom'] = groupe.nom
                    g['description'] = groupe.description
                    g[
                        'nbMembres'] = groupe.admins.all().count() + groupe.moderators.all().count() + groupe.adherents.all().count()
                    groupes.append(list(g.values()))
            context['nbGroupes'] = len(groupes)
            context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if
                                        request.user.profil == groupe.creator or request.user.profil in groupe.adherents.all() or request.user.profil in groupe.admins.all() or request.user.profil in groupe.moderators.all()])

            return render(request, 'SocialMedia/myprofil/statuts.html', context)
        except Groupe.DoesNotExist or Profil.DoesNotExist:
            raise Http404
    else:
        messages.error(request, "Veuiller vous connecter")
        return redirect('main_app:log_in')

@login_required
def ProfilStatuts(request, pk):
    context = dict()
    try:
        if request.user.profil == Profil.objects.get(id=pk):
            return redirect('SocialMedia:myprofil')
        profil = Profil.objects.get(id=pk)

        if not DemandeAmi.sont_ami(request.user, profil.user):
            return redirect('SocialMedia:getProfil', pk=pk)

        if DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                     Q(recepteur=profil) | Q(recepteur=request.user.profil), statut=3).exists():
            messages.warning(request, "Le profil recherché est bloqué!")
            return redirect('SocialMedia:home')
        context['profil'] = profil
        context['poste_actuel'] = Experience.objects.filter(profil=profil, actuel=True).values('poste').values(
            'nom_poste').last()
        context['poste_actuel_renseigne'] = Experience.objects.filter(profil=profil, actuel=True).values(
            'nom_poste').last()
        context['ecole'] = Formation.objects.filter(profil=profil, ecole__isnull=False).values('ecole__nom').last()
        context['ecole_renseignee'] = Formation.objects.filter(profil=profil, ecole__isnull=True).values(
            'nom_ecole').last()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['experiences'] = Experience.objects.filter(profil=profil)
        context['formations'] = Formation.objects.filter(profil=profil)
        context['actionsBenevoles'] = ActionBenevole.objects.filter(profil=profil)
        context['is_followed'] = Suivie.objects.filter(followed_profil=profil,
                                                       follower=request.user.profil).exists()
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                         Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                         statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                   statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        context['nbGroupes'] = len([groupe for groupe in Groupe.objects.all() if
                                    profil == groupe.creator or profil in groupe.adherents.all() or profil in groupe.admins.all() or profil in groupe.moderators.all()])
        context['is_friend'] = DemandeAmi.objects.filter(Q(emetteur=request.user.profil) | Q(emetteur=profil),
                                                         Q(recepteur=request.user.profil) | Q(recepteur=profil),
                                                         statut=1).exists()
        context['is_request_received'] = DemandeAmi.objects.filter(emetteur=profil, recepteur=request.user.profil,
                                                                   statut=0).exists()
        context['is_request_sent'] = DemandeAmi.objects.filter(emetteur=request.user.profil, recepteur=profil,
                                                               statut=0).exists()
        p = Profil.objects.get(id=pk)
        page = request.GET.get('page', 1)
        statutsSignles = StatutSignales.objects.filter(signal_sender=request.user.profil).values('statut__id')
        statuts = Statut.objects.filter(mur_profil=p, is_profil_statut=True).exclude(pk__in=statutsSignles).order_by(
            '-date_statut')
        paginator = Paginator(statuts, 20)
        context['statuts'] = paginator.get_page(page)
        context['now'] = now()
        context['profiles'] = Profil.objects.all().order_by('-id')[:20]
        context['statutForm'] = StatutsForm()
        context['sont_ami'] = DemandeAmi.sont_ami(request.user, profil.user)

        return render(request, 'SocialMedia/profil/statuts.html', context)
    except Profil.DoesNotExist:
        raise Http404

@login_required
def getMoreReplies(request):
    context = dict()
    commentid = request.GET.get('commentId')
    page = int(request.GET.get('page'))
    commentaire = Commentaire.objects.get(id=commentid)
    replySignles = ReplySignales.objects.filter(signal_sender=request.user.profil).values('reply__id')
    replies = commentaire.reply_set.all().exclude(pk__in=replySignles).order_by('-date_reply')
    paginator = Paginator(replies, 2)
    try:
        rpls = paginator.page(page)
    except PageNotAnInteger:
        rpls = paginator.page(1)
    except EmptyPage:
        rpls = paginator.page(paginator.num_pages)
    for r in rpls:
        print(r.replyContent)
        print(r.commentaire)
        print(r.user)
        print(r.date_reply)
    return render(request, 'SocialMedia/groupe/reply/groupe_comment_reply.html',
                  {'replies': rpls, 'commentId': commentaire.id, 'numPages': paginator.num_pages})

@login_required
def getMoreRepliesMyProfil(request):
    context = dict()
    commentid = request.GET.get('commentId')
    page = int(request.GET.get('page'))
    commentaire = Commentaire.objects.get(id=commentid)
    replySignles = ReplySignales.objects.filter(signal_sender=request.user.profil).values('reply__id')
    replies = commentaire.reply_set.all().exclude(pk__in=replySignles).order_by('-date_reply')
    paginator = Paginator(replies, 2)
    try:
        rpls = paginator.page(page)
    except PageNotAnInteger:
        rpls = paginator.page(1)
    except EmptyPage:
        rpls = paginator.page(paginator.num_pages)
    for r in rpls:
        print(r.replyContent)
        print(r.commentaire)
        print(r.user)
        print(r.date_reply)
    return render(request, 'SocialMedia/myprofil/reply/myprofil_comment_reply.html',
                  {'replies': rpls, 'commentId': commentaire.id, 'numPages': paginator.num_pages})

@login_required
def getMoreRepliesProfil(request):
    context = dict()
    commentid = request.GET.get('commentId')
    page = int(request.GET.get('page'))
    commentaire = Commentaire.objects.get(id=commentid)
    replySignles = ReplySignales.objects.filter(signal_sender=request.user.profil).values('reply__id')
    replies = commentaire.reply_set.all().exclude(pk__in=replySignles).order_by('-date_reply')
    paginator = Paginator(replies, 2)
    try:
        rpls = paginator.page(page)
    except PageNotAnInteger:
        rpls = paginator.page(1)
    except EmptyPage:
        rpls = paginator.page(paginator.num_pages)
    return render(request, 'SocialMedia/profil/reply/profil_comment_reply.html',
                  {'replies': rpls, 'commentId': commentaire.id, 'numPages': paginator.num_pages})

@login_required
def getMoreCommentsGroupe(request, pk):
    context = dict()
    statutid = int(request.GET.get('statutid'))
    page = int(request.GET.get('page'))
    print(statutid)
    print(page)
    groupe = Groupe.objects.get(id=pk)
    statut = Statut.objects.get(mur_groupe=groupe, id=statutid)
    commentaireSignles = CommentaireSignales.objects.filter(signal_sender=request.user.profil).values('commentaire__id')
    comments = statut.commentaire_set.all().exclude(pk__in=commentaireSignles).order_by('-date_commentaire')
    paginator = Paginator(comments, 2)
    try:
        cmts = paginator.page(page)
    except PageNotAnInteger:
        cmts = paginator.page(1)
    except EmptyPage:
        cmts = paginator.page(paginator.num_pages)
    return render(request, 'SocialMedia/groupe/comments/commentaire_groupe.html',
                  {'comments': cmts, 'statutid': statut.id, 'numPages': paginator.num_pages})

@login_required
def getMoreCommentsMyProfil(request):
    statutid = int(request.GET.get('statutid'))
    page = int(request.GET.get('page'))
    print(statutid)
    print(page)
    statut = Statut.objects.get(mur_profil=request.user.profil, id=statutid)
    commentaireSignles = CommentaireSignales.objects.filter(signal_sender=request.user.profil).values('commentaire__id')
    comments = statut.commentaire_set.all().exclude(pk__in=commentaireSignles).order_by('-date_commentaire')
    paginator = Paginator(comments, 2)
    try:
        cmts = paginator.page(page)
    except PageNotAnInteger:
        cmts = paginator.page(1)
    except EmptyPage:
        cmts = paginator.page(paginator.num_pages)
    return render(request, 'SocialMedia/myprofil/comments/commentaire_myprofil.html',
                  {'comments': cmts, 'statutid': statut.id, 'numPages': paginator.num_pages})

@login_required
def getMoreCommentsProfil(request, pk):
    context = dict()
    statutid = int(request.GET.get('statutid'))
    page = int(request.GET.get('page'))
    print(statutid)
    print(page)
    statut = Statut.objects.get(mur_profil=Profil.objects.get(id=pk), id=statutid)
    commentaireSignles = CommentaireSignales.objects.filter(signal_sender=request.user.profil).values('commentaire__id')
    comments = statut.commentaire_set.all().exclude(pk__in=commentaireSignles).order_by('-date_commentaire')
    paginator = Paginator(comments, 2)
    try:
        cmts = paginator.page(page)
    except PageNotAnInteger:
        cmts = paginator.page(1)
    except EmptyPage:
        cmts = paginator.page(paginator.num_pages)
    return render(request, 'SocialMedia/profil/comments/commentaire_profil.html',
                  {'comments': cmts, 'statutid': statut.id, 'numPages': paginator.num_pages})

@login_required
def getStatutLikers(request):
    type = request.GET.get('type')
    data = request.GET.get('data')
    print(type)
    print(data)
    if type == "statut":
        statut = Statut.objects.get(id=int(data))
        likers = statut.likes.all()
    elif type == "comment":
        comment = Commentaire.objects.get(id=int(data))
        likers = comment.likes.all()
    else:
        reply = Reply.objects.get(id=int(data))
        likers = reply.likes.all()
    md = render_to_string('SocialMedia/PopUps/likers.html', {'likers': likers}, request)
    return JsonResponse(md, safe=False)

@login_required()
def signalerStatut(request):
    if request.method == "POST":
        statut = request.POST.get('statut')
        st = Statut.objects.get(id=statut)
        StatutSignales.objects.create(statut=st, signal_sender=request.user.profil)
        context = dict()
        context['signale'] = True
        return JsonResponse(context, safe=False)

@login_required()
def signalerCommentaire(request):
    if request.method == "POST":
        comment = request.POST.get('comment')
        cm = Commentaire.objects.get(id=comment)
        CommentaireSignales.objects.create(commentaire=cm, signal_sender=request.user.profil)
        context = dict()
        context['signale'] = True
        return JsonResponse(context, safe=False)

@login_required()
def signalerReply(request):
    if request.method == "POST":
        reply = request.POST.get('reply')
        rp = Reply.objects.get(id=reply)
        ReplySignales.objects.create(reply=rp, signal_sender=request.user.profil)
        context = dict()
        context['signale'] = True
        return JsonResponse(context, safe=False)

@login_required
def getStatut(request, pk):
    context = dict()
    statutsSignles = StatutSignales.objects.filter(signal_sender=request.user.profil)
    statut = get_object_or_404(Statut, id=pk)
    for st in statutsSignles:
        if statut == st.statut:
            context['signale'] = True
            return render(request, 'SocialMedia/statut/statut.html', context)
    context['mes_pages_entreprises'] = PageEntreprise.objects.filter(
        Q(moderateurs__in=[request.user.profil]) | Q(administrateurs__in=[request.user.profil]))
    context['statut'] = statut
    return render(request, 'SocialMedia/statut/statut.html', context)

@login_required
def editReplyStatut(request):
    if request.method == "GET":
        reply = Reply.objects.get(id=int(request.GET.get('reply')))
        modal = render_to_string('SocialMedia/statut/modals/edit_reply.html', {'reply': reply}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuReply = str(request.POST.get('contenuReply'))
        reply = Reply.objects.get(id=int(request.POST.get('reply')))
        reply.replyContent = contenuReply
        reply.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(reply.replyContent)
        return JsonResponse(context, safe=False)

@login_required
def editReplyAcceuil(request):
    if request.method == "GET":
        reply = Reply.objects.get(id=int(request.GET.get('reply')))
        modal = render_to_string('SocialMedia/acceuil/modals/edit_reply.html', {'reply': reply}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuReply = str(request.POST.get('contenuReply'))
        reply = Reply.objects.get(id=int(request.POST.get('reply')))
        reply.replyContent = contenuReply
        reply.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(reply.replyContent)
        return JsonResponse(context, safe=False)

@login_required
def addCommentStatut(request):
    statutid = request.POST.get('statut')
    commentContent = request.POST.get('cmtContent')
    st = Statut.objects.get(id=statutid)
    comment = Commentaire.objects.create(comment=commentContent, date_commentaire=now(), statut=st,
                                         user=request.user.profil)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        comment.image.add(img)
    return render(request, 'SocialMedia/statut/comments/commentaire_statut_ajoute.html',
                  {'comment': comment, 'statutID': st.id, 'NbComments': st.commentaire_set.all().count(),
                   'addedComment': True})

@login_required
def addCommentAcceuil(request):
    statutid = request.POST.get('statut')
    commentContent = request.POST.get('cmtContent')
    st = Statut.objects.get(id=statutid)
    comment = Commentaire.objects.create(comment=commentContent, date_commentaire=now(), statut=st,
                                         user=request.user.profil)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        comment.image.add(img)
    return render(request, 'SocialMedia/acceuil/comments/commentaire_statut_ajoute.html',
                  {'comment': comment, 'statutID': st.id, 'NbComments': st.commentaire_set.all().count(),
                   'addedComment': True})

@login_required
def getMoreRepliesStatut(request):
    context = dict()
    commentid = request.GET.get('commentId')
    page = int(request.GET.get('page'))
    commentaire = Commentaire.objects.get(id=commentid)
    replySignles = ReplySignales.objects.filter(signal_sender=request.user.profil).values('reply__id')
    replies = commentaire.reply_set.all().exclude(pk__in=replySignles).order_by('-date_reply')
    paginator = Paginator(replies, 2)
    try:
        rpls = paginator.page(page)
    except PageNotAnInteger:
        rpls = paginator.page(1)
    except EmptyPage:
        rpls = paginator.page(paginator.num_pages)
    return render(request, 'SocialMedia/statut/reply/statut_reply.html',
                  {'replies': rpls, 'commentId': commentaire.id, 'numPages': paginator.num_pages})

@login_required
def getMoreRepliesAcceuil(request):
    context = dict()
    commentid = request.GET.get('commentId')
    page = int(request.GET.get('page'))
    commentaire = Commentaire.objects.get(id=commentid)
    replySignles = ReplySignales.objects.filter(signal_sender=request.user.profil).values('reply__id')
    replies = commentaire.reply_set.all().exclude(pk__in=replySignles).order_by('-date_reply')
    paginator = Paginator(replies, 2)
    try:
        rpls = paginator.page(page)
    except PageNotAnInteger:
        rpls = paginator.page(1)
    except EmptyPage:
        rpls = paginator.page(paginator.num_pages)
    return render(request, 'SocialMedia/acceuil/reply/statut_reply.html',
                  {'replies': rpls, 'commentId': commentaire.id, 'numPages': paginator.num_pages})

@login_required
def addReplyStatut(request):
    commentid = request.POST.get('comment')
    replyContent = request.POST.get('replyContent')
    commentaire = Commentaire.objects.get(id=commentid)
    rp = Reply.objects.create(commentaire=commentaire, user=request.user.profil, date_reply=now(),
                              replyContent=replyContent)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        rp.image.add(img)
    rep = render_to_string('SocialMedia/statut/reply/statut_reply_ajoute.html',
                           {'reply': rp, 'NbReplies': commentaire.reply_set.all().count, 'addedStatut': True}, request)
    return JsonResponse(rep, safe=False)

@login_required
def addReplyAcceuil(request):
    commentid = request.POST.get('comment')
    replyContent = request.POST.get('replyContent')
    commentaire = Commentaire.objects.get(id=commentid)
    rp = Reply.objects.create(commentaire=commentaire, user=request.user.profil, date_reply=now(),
                              replyContent=replyContent)
    if 'image' in request.FILES:
        img = ReseauSocialFile.objects.create(fichier=request.FILES['image'], date_telechargement=now(),
                                              profil=request.user.profil)
        img.save()
        rp.image.add(img)
    rep = render_to_string('SocialMedia/acceuil/reply/statut_reply_ajoute.html',
                           {'reply': rp, 'NbReplies': commentaire.reply_set.all().count, 'addedStatut': True}, request)
    return JsonResponse(rep, safe=False)

@login_required
def editCommentStatut(request):
    if request.method == "GET":
        comment = Commentaire.objects.get(id=int(request.GET.get('comment')))
        modal = render_to_string('SocialMedia/statut/modals/edit_comment.html', {'comment': comment}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuComment = str(request.POST.get('contenuComment'))
        comment = Commentaire.objects.get(id=request.POST.get('comment'))
        comment.comment = contenuComment
        comment.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(comment.comment)
        print(context['NewContent'])
        return JsonResponse(context, safe=False)

@login_required
def editCommentAcceuil(request):
    if request.method == "GET":
        comment = Commentaire.objects.get(id=int(request.GET.get('comment')))
        modal = render_to_string('SocialMedia/acceuil/modals/edit_comment.html', {'comment': comment}, request)
        return JsonResponse(modal, safe=False)
    else:
        contenuComment = str(request.POST.get('contenuComment'))
        comment = Commentaire.objects.get(id=request.POST.get('comment'))
        comment.comment = contenuComment
        comment.save()
        context = dict()
        context['status'] = True
        context['NewContent'] = nbsp_Link(comment.comment)
        print(context['NewContent'])
        return JsonResponse(context, safe=False)

@login_required
def getMoreCommentsStatut(request):
    statutid = int(request.GET.get('statutid'))
    page = int(request.GET.get('page'))
    statut = Statut.objects.get(id=statutid)
    commentaireSignles = CommentaireSignales.objects.filter(signal_sender=request.user.profil).values('commentaire__id')
    comments = statut.commentaire_set.all().exclude(pk__in=commentaireSignles).order_by('-date_commentaire')
    paginator = Paginator(comments, 2)
    try:
        cmts = paginator.page(page)
    except PageNotAnInteger:
        cmts = paginator.page(1)
    except EmptyPage:
        cmts = paginator.page(paginator.num_pages)
    return render(request, 'SocialMedia/statut/comments/commentaire_statut.html',
                  {'comments': cmts, 'statutid': statut.id, 'numPages': paginator.num_pages})

@login_required
def getMoreCommentsAcceuil(request):
    statutid = int(request.GET.get('statutid'))
    page = int(request.GET.get('page'))
    statut = Statut.objects.get(id=statutid)
    commentaireSignles = CommentaireSignales.objects.filter(signal_sender=request.user.profil).values('commentaire__id')
    comments = statut.commentaire_set.all().exclude(pk__in=commentaireSignles).order_by('-date_commentaire')
    paginator = Paginator(comments, 2)
    try:
        cmts = paginator.page(page)
    except PageNotAnInteger:
        cmts = paginator.page(1)
    except EmptyPage:
        cmts = paginator.page(paginator.num_pages)
    return render(request, 'SocialMedia/acceuil/comments/commentaire_statut.html',
                  {'comments': cmts, 'statutid': statut.id, 'numPages': paginator.num_pages})


@login_required
def shareStatut(request):
    if request.method == "GET":
        statut = Statut.objects.get(id=int(request.GET.get('statut')))
        modal = render_to_string('SocialMedia/statut/modals/share_statut.html', {'statut': statut}, request)
        return JsonResponse(modal, safe=False)
    else:
        statut = Statut.objects.get(id=request.POST.get('statut'))
        st = Statut.objects.create(date_statut=now(),is_shared=True, original_statut_id=statut.pk, contenu_statut=statut.contenu_statut, is_profil_statut=True,
                                   publisher=request.user.profil, mur_profil=request.user.profil)
        for image in statut.images.all():
            st.images.add(image)
        for video in statut.videos.all():
            st.images.add(video)
        for file in statut.files.all():
            st.images.add(file)
        context = dict()
        context['status'] = True
        return JsonResponse(context, safe=False)

@login_required
def notifications(request):
    context = dict()
    friendsAccept = DemandeAmi.objects.filter(recepteur=request.user.profil, statut=1).values('emetteur')
    friendsSend = DemandeAmi.objects.filter(emetteur=request.user.profil, statut=1).values('recepteur')
    context['amis'] = friendsAccept.count() + friendsSend.count()
    notifications = Notification.objects.filter(profil_to_notify=request.user.profil)
    context['notifications'] = tuple(notifications)
    for notification in Notification.objects.filter(profil_to_notify=request.user.profil):
            if not notification.is_read:
                notification.is_read=True
                notification.read_date=now()
                notification.save()
    return render(request, 'SocialMedia/notifications/notifications.html', context)

@login_required
def deleteNotification(request):
    context = dict()
    notificationID = request.POST.get('notification')
    notification = Notification.objects.get(id=notificationID)
    notification.delete()
    context['status'] = True
    return JsonResponse(context, safe=False)




