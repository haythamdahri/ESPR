from datetime import datetime
from django.core.files.storage import FileSystemStorage


import locale

from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render



# Create your views here.
from django.utils.datastructures import MultiValueDictKeyError

from main_app import models
from main_app.models import Entreprise
from main_app.models import Profil
from . import models

def devenirPro(request):
    if request.user.is_authenticated:
        fonction = models.fonction.objects.all()
        service = models.service.objects.all()
        message = messages.get_messages(request)

        context = {
            "fonct": fonction,
            "service": service,
            "message": messages,
        }
        return render(request, "appelsOffres/register.html", context)
    else:
        return render(request, "appelsOffres/index.html")

def index(request):
    if request.user.is_authenticated:
        if request.user.profil.is_first_appoffre :

            return render(request,"appelsOffres/index.html" )
        else:
            message = messages.get_messages(request)
            user = request.user
            profil = Profil.objects.get(user=user)
            entreprise = Entreprise.objects.get(id=profil.entreprise.id)

            maintenant = datetime.now().astimezone()

            d = maintenant.day
            m = maintenant.month
            a = maintenant.year

            duree = datetime(2018, 5, 15) - datetime(a,m,d)


            locale.setlocale(locale.LC_TIME, '')
            #dateA = timezone.localdate()

            dateA = datetime(2018, 5, 6, 22, 10, 11)

            #dateA = timezone.localtime()

            images = models.ImageScrol.objects.all()

            annonces_list = models.Annonce.objects.exclude(user=user).order_by('id').reverse()
            page = request.GET.get('page', 1)
            paginator = Paginator(annonces_list, 3)
            try:
                an = paginator.page(page)
            except PageNotAnInteger:
                an = paginator.page(1)
            except EmptyPage:
                an = paginator.page(paginator.num_pages)

            categorie = models.categorie.objects.all()
            fav = models.Favoris.objects.filter(user=user)

            context = {
                "user": user,
                "profile":profil,
                "entreprise":entreprise,
                "message": messages,
                "mnt":maintenant,
                "date":dateA,
                "images":images,
                "annonces":annonces_list,
                "an":an,
                "categorie":categorie,
                "fav":fav,
            }
            return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)

    else :
        return render(request,"appelsOffres/index.html" )

def log_in(request):
    return HttpResponseRedirect('/main/login')

def register(request):
    return HttpResponseRedirect('/main/signup')

def aplofr(request):
    annonces_list = models.Annonce.objects.all().order_by('id').reverse()
    page = request.GET.get('page', 1)
    paginator = Paginator(annonces_list, 3)
    try:
        an = paginator.page(page)
    except PageNotAnInteger:
        an = paginator.page(1)
    except EmptyPage:
        an = paginator.page(paginator.num_pages)

    context = {
        "annonces": annonces_list,
        "an": an,
    }
    return render(request, 'appelsOffres/aplofr.html', context)

def aboutus(request):
    return render(request, "appelsOffres/aboutus.html")

def inscriptionaa(request):
    if request.method == "POST":

        fonction = request.POST.get('fonction')
        service = request.POST.get('service')
        paysProfile = request.POST.get('paysProfile')
        villeProfile = request.POST.get('villeProfile')
        telephone = request.POST.get('telephone')
        civilité = request.POST.get('civilite')
        adresseProfile = request.POST.get('adresseProfile')

        RaisonSociale = request.POST.get('RaisonSociale')
        nrc = request.POST.get('nrc')
        activite = request.POST.get('activite')
        Secteur = request.POST.get('Secteur')
        paysEntreprise = request.POST.get('paysEntreprise')
        villeEntreprise = request.POST.get('villeEntreprise')
        emailEntreprise = request.POST.get('emailEntreprise')
        telephoneEntreprise = request.POST.get('telephoneEntreprise')
        adresseEntreprise = request.POST.get('adresseEntreprise')

        entreprise = Entreprise()
        entreprise.raison_social = RaisonSociale
        entreprise.registre_commerce = nrc
        entreprise.activite = activite
        entreprise.secteurActivite = Secteur
        entreprise.pays = paysEntreprise
        entreprise.ville = villeEntreprise
        entreprise.email_entreprise = emailEntreprise
        entreprise.telephone = telephoneEntreprise
        entreprise.adresse_Entreprise = adresseEntreprise
        entreprise.save()

        user = request.user

        profile = Profil.objects.get(user=user)
        profile.entreprise = entreprise
        profile.fonction =fonction
        profile.service = service
        profile.civilité = civilité
        profile.pays = paysProfile
        profile.ville = villeProfile
        profile.tel = telephone
        profile.adresse_profile = adresseProfile
        profile.is_first_appoffre = False
        profile.save()



        messages.success(request,"Vous avez terminé la partie d'inscription !! Merci.")
        return HttpResponseRedirect('/appelsOffres')

    else:
        return HttpResponseRedirect('/appelsOffres/')

def nouvelleAnnonce(request):
    if request.user.is_authenticated:
        user = request.user
        lot = models.Lot.objects.filter(user=user)
        context = {
            "user":user,
            "lot":lot,
        }
        return render(request, "appelsOffres/Authentifier/NouvelleAnnonce.html", context)
    else:
        return render(request, "appelsOffres/index.html")

def MesAnnonces(request):
    if request.user.is_authenticated:
        user = request.user

        annonces_nb = models.Annonce.objects.filter(user=user).order_by('datePub').reverse().count()

        if annonces_nb == 0:
            messages.warning(request, "Aucune annonce trouver, si vous etes interesser vous pouvez ajouter une nouvelle annonce, Merci")
            return nouvelleAnnonce(request)


        annonces_list = models.Annonce.objects.filter(user=user).order_by('datePub').reverse()
        page = request.GET.get('page', 1)

        paginator = Paginator(annonces_list, 5)
        try:
            annonces = paginator.page(page)
        except PageNotAnInteger:
            annonces = paginator.page(1)
        except EmptyPage:
            annonces = paginator.page(paginator.num_pages)

        context = {
            "user": user,
            "annonces":annonces,
        }
        return render(request, "appelsOffres/Authentifier/MesAnnonces.html", context)
    else:
        return render(request, "appelsOffres/index.html")

def NouveauProjet(request):
    if request.user.is_authenticated:
        user = request.user

        categorie = models.categorie.objects.all()

        context = {
            "user": user,
            "categorie":categorie,
        }
        return render(request, "appelsOffres/Authentifier/NouveauProjet.html", context)
    else:
        return render(request, "appelsOffres/index.html")

def MesProjets(request):
    if request.user.is_authenticated:
        user = request.user

        lot_nb = models.Lot.objects.filter(user=user).count()

        if lot_nb == 0:
            messages.warning(request,"Aucune Lot trouver, si vous etes interesser vous pouvez ajouter un nouveau lot, Merci")
            return NouveauProjet(request)

        lot_list = models.Lot.objects.filter(user=user)
        page = request.GET.get('page', 1)

        paginator = Paginator(lot_list,5)
        try:
            lot = paginator.page(page)
        except PageNotAnInteger:
            lot = paginator.page(1)
        except EmptyPage:
            lot = paginator.page(paginator.num_pages)

        context = {
            "user": user,
            "lot":lot,
        }
        return render(request, "appelsOffres/Authentifier/MesProjets.html", context)
    else:
        return render(request, "appelsOffres/index.html")

def MonProfile(request):
    if request.user.is_authenticated:
        user = request.user
        context = {
            "user": user,
        }
        return render(request, "appelsOffres/Authentifier/MonProfile.html", context)

    else:
        return render(request, "appelsOffres/index.html")

def changePassword(request, id):

    user = User.objects.filter(id=id)
    nouveauPassword = request.POST.get('nouveauPassword')

    for it in user:
        it.set_password(nouveauPassword)
        it.save()

    messages.success(request, "Votre mot de passe a été changer, Merci !")
    return log_in(request)

def deleteProfile(request, iduser, identreprise):

    user = User.objects.get(id=iduser)

    entreprise = Entreprise.objects.get(id=identreprise)

    user.delete()
    entreprise.delete()

    return HttpResponseRedirect('/appelsOffres')

def updateprofile(request):
    if request.user.is_authenticated:
        fonction = models.fonction.objects.all()
        service = models.service.objects.all()

        user = request.user
        context = {
            "fonction":fonction,
            "service":service,
            "user": user,
        }
        return render(request, "appelsOffres/Authentifier/updateProfile.html", context)
    else :
        return render(request, "appelsOffres/index.html")

def update(request):

    emailuser = request.POST.get('emailuser')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    telephoneProfile = request.POST.get('telephoneProfile')
    civilite = request.POST.get('civilite')
    fonction = request.POST.get('fonction')
    service = request.POST.get('service')
    paysProfile = request.POST.get('paysProfile')
    villeProfile = request.POST.get('villeProfile')
    adresse_profile = request.POST.get('adresse_profile')

    RaisonSociale = request.POST.get('RaisonSociale')
    nrc = request.POST.get('nrc')
    activite = request.POST.get('activite')
    Secteur = request.POST.get('Secteur')
    telephoneEntreprise = request.POST.get('telephoneEntreprise')
    paysEntreprise = request.POST.get('paysEntreprise')
    villeEntreprise = request.POST.get('villeEntreprise')
    adresseEntreprise = request.POST.get('adresseEntreprise')

    user= request.user
    mail = user.email
    profil = Profil.objects.get(user=user)
    entreprise = Entreprise.objects.get(raison_social=profil.entreprise)


    if mail != emailuser:
        nblign = User.objects.filter(email=emailuser).count()
        if (nblign == 1):
            messages.warning(request,"Attenton ! cet email est deja exsiste")
            return HttpResponseRedirect("/appelsOffres/updateProfile")
        else:
            if (emailuser == ""):
                emailuser = user.email
            if (firstname == ""):
                firstname = user.first_name
            if (lastname == ""):
                lastname = user.last_name
            if (telephoneProfile == ""):
                telephoneProfile = profil.tel
            if (civilite == None):
                civilite = profil.civilité
            if (fonction == ""):
                fonction = profil.fonction
            if (service == ""):
                service = profil.service
            if (paysProfile == ""):
                paysProfile = profil.pays
            if (villeProfile == ""):
                villeProfile = profil.ville
            if (adresse_profile == ""):
                adresse_profile = profil.adresse_profile

            if (RaisonSociale == ""):
                RaisonSociale = entreprise.raison_social
            if (nrc == ""):
                nre = entreprise.registre_commerce
            if (activite == ""):
                activite = entreprise.activite
            if (Secteur == ""):
                Secteur = entreprise.secteurActivite
            if (telephoneEntreprise == ""):
                telephoneEntreprise = entreprise.telephone
            if (paysEntreprise == ""):
                paysEntreprise = entreprise.pays
            if (villeEntreprise == ""):
                villeEntreprise = entreprise.ville
            if (adresseEntreprise == ""):
                adresseEntreprise = entreprise.adresse_Entreprise

            user.email = emailuser
            user.first_name = firstname
            user.last_name = lastname
            user.save()

            profil.tel = telephoneProfile
            profil.civilité = civilite
            profil.fonction = fonction
            profil.service = service
            profil.pays = paysProfile
            profil.ville = villeProfile
            profil.adresse_profile = adresse_profile
            profil.save()

            entreprise.raison_social = RaisonSociale
            entreprise.registre_commerce = nrc
            entreprise.activite = activite
            entreprise.secteurActivite = Secteur
            entreprise.telephone = telephoneEntreprise
            entreprise.pays = paysEntreprise
            entreprise.ville = villeEntreprise
            entreprise.adresse_Entreprise = adresseEntreprise
            entreprise.save()

            context = {
                "emailuser": emailuser,
                "firstname": firstname,
                "lastname": lastname,
                "telephoneProfile": telephoneProfile,
                "civilite": civilite,
                "fonction": fonction,
                "service": service,
                "paysProfile": paysProfile,
                "villeProfile": villeProfile,
                "adresseProfile": adresse_profile,
                "RaisonSociale": RaisonSociale,
                "nrc": nrc,
                "activite": activite,
                "Secteur": Secteur,
                "telephoneEntreprise": telephoneEntreprise,
                "paysEntreprise": paysEntreprise,
                "villeEntreprise": villeEntreprise,
                "adresseEntreprise": adresseEntreprise,
            }

            messages.success(request, "Votre profil a été modifier, Merci")
            return MonProfile(request)

    else:
        if (emailuser == ""):
            emailuser = user.email
        if (firstname == ""):
            firstname = user.first_name
        if (lastname == ""):
            lastname = user.last_name
        if (telephoneProfile == ""):
            telephoneProfile = profil.tel
        if (civilite == None):
            civilite = profil.civilité
        if (fonction == ""):
            fonction = profil.fonction
        if (service == ""):
            service = profil.service
        if (paysProfile == ""):
            paysProfile = profil.pays
        if (villeProfile == ""):
            villeProfile = profil.ville
        if (adresse_profile == ""):
            adresse_profile = profil.adresse_profile

        if (RaisonSociale == ""):
            RaisonSociale = entreprise.raison_social
        if (nrc == ""):
            nre = entreprise.registre_commerce
        if (activite == ""):
            activite = entreprise.activite
        if (Secteur == ""):
            Secteur = entreprise.secteurActivite
        if (telephoneEntreprise == ""):
            telephoneEntreprise = entreprise.telephone
        if (paysEntreprise == ""):
            paysEntreprise = entreprise.pays
        if (villeEntreprise == ""):
            villeEntreprise = entreprise.ville
        if (adresseEntreprise == ""):
            adresseEntreprise = entreprise.adresse_Entreprise



        user.email = emailuser
        user.first_name = firstname
        user.last_name = lastname
        user.save()

        profil.tel = telephoneProfile
        profil.civilité = civilite
        profil.fonction = fonction
        profil.service = service
        profil.pays = paysProfile
        profil.ville = villeProfile
        profil.adresse_profile = adresse_profile
        profil.save()

        entreprise.raison_social = RaisonSociale
        entreprise.registre_commerce = nrc
        entreprise.activite = activite
        entreprise.secteurActivite = Secteur
        entreprise.telephone = telephoneEntreprise
        entreprise.pays = paysEntreprise
        entreprise.ville = villeEntreprise
        entreprise.adresse_Entreprise = adresseEntreprise
        entreprise.save()


        context = {
            "emailuser":emailuser,
            "firstname":firstname,
            "lastname":lastname,
            "telephoneProfile":telephoneProfile,
            "civilite":civilite,
            "fonction":fonction,
            "service":service,
            "paysProfile":paysProfile,
            "villeProfile":villeProfile,
            "adresseProfile":adresse_profile,
            "RaisonSociale":RaisonSociale,
            "nrc":nrc,
            "activite":activite,
            "Secteur":Secteur,
            "telephoneEntreprise":telephoneEntreprise,
            "paysEntreprise":paysEntreprise,
            "villeEntreprise":villeEntreprise,
            "adresseEntreprise":adresseEntreprise,
        }

        messages.success(request,"Votre profil a été modifier, Merci")
        return MonProfile(request)

def addLot(request):

    if request.method == "POST" :
        user = request.user

        titre = request.POST.get('titre')
        categorie = request.POST.get('categorie')
        description = request.POST.get('description')
        estimation = request.POST.get('estimation')
        caution = request.POST.get('caution')
        qualification = request.POST.get('qualification')
        agrement = request.POST.get('agrement')
        echantillons = request.POST.get('echantillons')
        visitLieux = request.POST.get('visitLieux')
        variante = request.POST.get('variante')
        reservePME = request.POST.get('reservePME')
        cdc = request.FILES.get('CDCFILE')

        lot = models.Lot()

        lot.titre = titre
        lot.categorie = categorie
        lot.description = description
        lot.estimation =  estimation
        lot.cautionProvisoire = caution
        lot.qualifications = qualification
        lot.Agrements = agrement
        lot.echantillons = echantillons
        lot.visiteLieux = visitLieux
        lot.variante = variante
        lot.reservePME = reservePME
        lot.cahierDeCharge = cdc
        lot.user = user

        lot.save()

        messages.success(request, 'Votre Lot a été créer avec success, Merci ! ')

        return render(request, 'appelsOffres/Authentifier/NosAppeleOffreAuth.html')

    else:

        messages.warning(request, 'Error ... ! ')
        return NouveauProjet(request)

def detailLot(request, idlot):

    lot = models.Lot.objects.filter(id=idlot)

    context = {
        "lot":lot,
    }

    return render(request, "appelsOffres/Authentifier/detailLot.html", context)

def deleteLot(request, idlot):

    lot = models.Lot.objects.filter(id=idlot)

    lot.delete()

    return HttpResponseRedirect('/appelsOffres/MesProjets')

def updateLot(request,idlot):
    lot = models.Lot.objects.filter(id=idlot)
    categorie = models.categorie.objects.all()

    context = {
        "lot":lot,
        "categorie":categorie,
    }

    return render(request, "appelsOffres/Authentifier/updateLot.html", context)

def updateLOT(request, idlot):

    if request.method == "POST":

        titre = request.POST.get('titre')
        categorie = request.POST.get('categorie')
        description = request.POST.get('description')
        qualification = request.POST.get('qualification')
        agrement = request.POST.get('agrement')
        echantillons = request.POST.get('echantillons')
        visitLieux = request.POST.get('visitLieux')
        variante = request.POST.get('variante')
        reservePME = request.POST.get('reservePME')
        cdc = request.FILES.get('CDCFILE')

        lot = models.Lot.objects.filter(id=idlot)

        for it in lot:
            rtitre = it.titre
            rcategorie = it.categorie
            rdescription = it.description
            restimation = it.estimation
            rcaution = it.cautionProvisoire
            rqualification = it.qualifications
            ragrement = it.Agrements
            rechantillons = it.echantillons
            rvisitLieux = it.visiteLieux
            rvariante = it.variante
            rreservePME = it.reservePME
            rcdc = it.cahierDeCharge

        if titre == "":
            titre = rtitre
        if categorie == "":
            categorie = rcategorie
        if description == "":
            description = rdescription
        if qualification == "":
            qualification = rqualification
        if agrement == "":
            agrement = ragrement
        if echantillons == "":
            echantillons = rechantillons
        if visitLieux == "":
            visitLieux = rvisitLieux
        if variante == "":
            variante = rvariante
        if reservePME == "":
            reservePME == rreservePME
        if cdc == None:
            cdc = rcdc


        for item in lot:
            it.titre = titre
            it.categorie = categorie
            it.description = description
            it.qualifications = qualification
            it.Agrements = agrement
            it.echantillons = echantillons
            it.visiteLieux = visitLieux
            it.variante = variante
            it.reservePME = reservePME
            it.cahierDeCharge = cdc
            it.save()

        messages.success(request,"votre modification a été effectuer, Merci "+titre)

    return MesProjets(request)

def addAnnonce(request):

    user = request.user

    messa =""

    if request.method == "POST":
        titre = request.POST.get('titre')
        time = request.POST.get('time')
        status = request.POST.get('Status')
        lots = request.POST.getlist('lots')
        description = request.POST.get('description')


        myDate = datetime.now()
        timeNow = myDate.strftime("%Y-%m-%d")


        annonce = models.Annonce()

        annonce.titre = titre
        annonce.description = description
        annonce.datePub = timeNow
        annonce.dateDelai = time

        if(status == "ouvert"):
            annonce.statusAnnonce == True

        else:
            annonce.statusAnnonce == False

        annonce.user = user
        annonce.nbVue = 0

        annonce.save()


        for it in lots :
            l = models.Lot.objects.filter(titre=it)
            for i in l:
                annonce.lot.add(i.id)
                annonce.save()

        '''
        timeDate = datetime.strptime(time,"%Y-%m-%d").date()
        y = timeDate.year
        m = timeDate.month
        d = timeDate.day

        a = myDate.year
        m1 = myDate.month
        j = myDate.day


        ne = datetime(y,m,d) - datetime(a,m1,j)

        if (ne.days == 0 ) :
            messa = " aaaaaaaaaa "

        '''

    messages.success(request,"votre annonce a été publier, Merci ! ")

    return MesAnnonces(request)

def detailAnnonce(request,idannonce):

    user = request.user

    annonces = models.Annonce.objects.filter(id=idannonce)

    for it in annonces:
        if it.user != user:
            nb = it.nbVue
            it.nbVue = nb + 1
            it.save()


    context = {
        "user": user,
        "annonces": annonces,
    }

    return render(request, "appelsOffres/Authentifier/detailAnnonce.html", context)

def searchMotCle(request):
    user = request.user
    
    if request.method == "POST":

        message = messages.get_messages(request)
        user = request.user
        profil = Profil.objects.get(user=user)
        entreprise = Entreprise.objects.get(id=profil.entreprise.id)

        maintenant = datetime.now().astimezone()

        d = maintenant.day
        m = maintenant.month
        a = maintenant.year

        duree = datetime(2018, 5, 15) - datetime(a, m, d)

        locale.setlocale(locale.LC_TIME, '')
        # dateA = timezone.localdate()

        dateA = datetime(2018, 5, 6, 22, 10, 11)

        # dateA = timezone.localtime()

        images = models.ImageScrol.objects.all()
        
        motcle = request.POST.get("motcle")

        nbAnnonce = models.Annonce.objects.filter(titre__contains=motcle).exclude(user=user).order_by('id').reverse().count()

        if nbAnnonce == 0:
            messages.warning(request,"Aucun annonce ne correspond aux termes de recherche spécifiés : " + motcle )
            annonces_list = models.Annonce.objects.exclude(user=user).order_by(
                'id').reverse()
            page = request.GET.get('page', 1)
            paginator = Paginator(annonces_list, 10)
            try:
                an = paginator.page(page)
            except PageNotAnInteger:
                an = paginator.page(1)
            except EmptyPage:
                an = paginator.page(paginator.num_pages)

            categorie = models.categorie.objects.all()

            context = {
                "user": user,
                "profile": profil,
                "entreprise": entreprise,
                "message": messages,
                "mnt": maintenant,
                "date": dateA,
                "images": images,
                "annonces": annonces_list,
                "an": an,
                "categorie": categorie,
            }
            return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)


        annonces_list = models.Annonce.objects.filter(titre__contains=motcle).exclude(user=user).order_by('id').reverse()
        page = request.GET.get('page', 1)
        paginator = Paginator(annonces_list, 10)
        try:
            an = paginator.page(page)
        except PageNotAnInteger:
            an = paginator.page(1)
        except EmptyPage:
            an = paginator.page(paginator.num_pages)

        categorie = models.categorie.objects.all()

        context = {
            "user": user,
            "profile": profil,
            "entreprise": entreprise,
            "message": messages,
            "mnt": maintenant,
            "date": dateA,
            "images": images,
            "annonces": annonces_list,
            "an": an,
            "categorie": categorie,
        }
        return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)

    else:
        return render(request, "appelsOffres/index.html")

def searchcategorie(request, cat ):
    user = request.user

    profil = Profil.objects.get(user=user)
    entreprise = Entreprise.objects.get(id=profil.entreprise.id)

    maintenant = datetime.now().astimezone()

    d = maintenant.day
    m = maintenant.month
    a = maintenant.year

    duree = datetime(2018, 5, 15) - datetime(a, m, d)

    locale.setlocale(locale.LC_TIME, '')
    # dateA = timezone.localdate()

    dateA = datetime(2018, 5, 6, 22, 10, 11)

    # dateA = timezone.localtime()

    images = models.ImageScrol.objects.all()

    nbAnnonce = models.Annonce.objects.filter(lot__categorie=cat).exclude(user=user).order_by('id').reverse().count()

    if nbAnnonce == 0:
        messages.warning(request, "Aucun annonce ne correspond a cette catégorie : " + cat )
        annonces_list = models.Annonce.objects.exclude(user=user).order_by(
            'id').reverse()
        page = request.GET.get('page', 1)
        paginator = Paginator(annonces_list, 10)
        try:
            an = paginator.page(page)
        except PageNotAnInteger:
            an = paginator.page(1)
        except EmptyPage:
            an = paginator.page(paginator.num_pages)

        categorie = models.categorie.objects.all()

        context = {
            "user": user,
            "profile": profil,
            "entreprise": entreprise,
            "message": messages,
            "mnt": maintenant,
            "date": dateA,
            "images": images,
            "annonces": annonces_list,
            "an": an,
            "categorie": categorie,
        }
        return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)

    annonces_list = models.Annonce.objects.filter(lot__categorie=cat).exclude(user=user).order_by('id').reverse()
    page = request.GET.get('page', 1)
    paginator = Paginator(annonces_list, 10)
    try:
        an = paginator.page(page)
    except PageNotAnInteger:
        an = paginator.page(1)
    except EmptyPage:
        an = paginator.page(paginator.num_pages)

    categorie = models.categorie.objects.all()

    context = {
        "user": user,
        "profile": profil,
        "entreprise": entreprise,
        "message": messages,
        "mnt": maintenant,
        "date": dateA,
        "images": images,
        "annonces": annonces_list,
        "an": an,
        "categorie": categorie,
    }
    return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)

def deleteAnnonce(request, idannonce):
    Annonce = models.Annonce.objects.filter(id=idannonce)
    messages.success(request,"Votre Annonce a été supprimer, Merci!")

    Annonce.delete()

    return HttpResponseRedirect('/appelsOffres/MesAnnonces')

def updateAnnonce(request, idannonce):
    user = request.user
    annonce = models.Annonce.objects.filter(id=idannonce)

    lot = models.Lot.objects.filter(user=user)

    context = {
        "annonce":annonce,
        "lot":lot,
    }

    return render(request, "appelsOffres/Authentifier/updateAnnonce.html", context)

def updateANNONCE(request, idannonce):
    user = request.user

    titre = request.POST.get('titre')
    lots = request.POST.getlist('lots')
    description = request.POST.get('description')


    annonce = models.Annonce.objects.filter(id=idannonce)

    for item in annonce:
        item.titre = titre
        item.description = description
        item.lot.clear()
        item.save()

    for it in lots:
        l = models.Lot.objects.filter(titre=it)
        for i in l:
            item.lot.add(i.id)
            item.save()

    messages.success(request, "Modification a été effectuer, Merci ! ")

    return detailAnnonce(request, idannonce)

def addfavori(request, idannonce):
    user = request.user

    f = models.Favoris.objects.filter(user=user, annonce__id=idannonce).count()

    if f == 0:
        fav = models.Favoris()

        fav.user = user
        fav.annonce = models.Annonce.objects.get(id=idannonce)
        fav.save()

        messages.success(request,'Ajouter au favoris, Merci !')
    else:
        messages.warning(request, 'vous avez deja ajouter cette annonce au favorie')

    return index(request)

def MESFAVORIS(request):

    user = request.user


    fav_list = models.Favoris.objects.filter(user=user)
    page = request.GET.get('page', 1)
    paginator = Paginator(fav_list, 10)
    try:
        fav = paginator.page(page)
    except PageNotAnInteger:
        fav = paginator.page(1)
    except EmptyPage:
        fav = paginator.page(paginator.num_pages)


    context = {
        "fav":fav,
    }

    return render(request, "appelsOffres/Authentifier/MESFAVORIS.html", context)

def deleteFavorie(request, idFav):

    fa = models.Favoris.objects.filter(id=idFav)
    fa.delete()

    messages.success(request, "L'annonce a été retirer, Merci!")

    return MESFAVORIS(request)

def addDevis(request, idannonce, idlot):
    user = request.user
    annonce = models.Annonce.objects.get(id=idannonce)
    lot = models.Lot.objects.get(id=idlot)

    description = list(request.POST.getlist('description'))
    quantites = request.POST.getlist('quantite')
    puHT = request.POST.getlist('puHT')

    nb = range(len(description))

    devis = models.Devis()
    devis.user = user
    devis.lot = lot
    devis.ifForm = True
    devis.save()

    annonce.devis.add(devis)

    for i in nb:
        devisA = models.assoDevis()
        devisA.description = description[i]
        devisA.quantite = quantites[i]
        devisA.prixUTH = puHT[i]
        devisA.TVA = request.POST.get('tva')
        devisA.save()
        devis.devisAss.add(devisA)

    send_mail(
        'Devis Annonces',
        'vous avez recu une nouvelle reponse devis a votre annonce : /n'
        '' + annonce.titre + " Lot : " + lot.titre,
        user.email,
        ['soufianeaitmbarek@hotmail.com'],
        fail_silently=False,
    )


    context = {
        "description":description,
        "quantite":quantites,
        "puHT":puHT,
        "nb":nb,
    }

    messages.success(request, 'Votre devis a été envoyer avec succes')
    return index(request)

def searchDate(request):

    if request.method == "POST":

        user = request.user
        profil = Profil.objects.get(user=user)

        datD = request.POST.get('datepubdebut')
        datF = request.POST.get('datepubFin')

        annonces_nb = models.Annonce.objects.filter(datePub__gte=datD, datePub__lte=datF).exclude(user=user).order_by('id').reverse().count()

        if annonces_nb == 0:
            messages.warning(request,"Aucun annonce ne correspond a cette date")
            return index(request)


        annonces_list = models.Annonce.objects.filter(datePub__gte=datD, datePub__lte=datF).exclude(user=user).order_by('id').reverse()

        page = request.GET.get('page', 1)
        paginator = Paginator(annonces_list, 5)
        try:
            an = paginator.page(page)
        except PageNotAnInteger:
            an = paginator.page(1)
        except EmptyPage:
            an = paginator.page(paginator.num_pages)

        categorie = models.categorie.objects.all()

        context = {
            "user": user,
            "profile": profil,
            "message": messages,
            "annonces": annonces_list,
            "an": an,
            "categorie": categorie,
        }
        return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)

    else:
        return index(request)

def searchDatePrecise(request):
    if request.method == "POST":

        user = request.user
        profil = Profil.objects.get(user=user)

        dat = request.POST.get('datepub')


        annonces_nb = models.Annonce.objects.filter(datePub=dat).exclude(user=user).order_by('id').reverse().count()

        if annonces_nb == 0:
            messages.warning(request,"Aucun annonce ne correspond a cette date")
            return index(request)


        annonces_list = models.Annonce.objects.filter(datePub=dat).exclude(user=user).order_by('id').reverse()

        page = request.GET.get('page', 1)
        paginator = Paginator(annonces_list, 5)
        try:
            an = paginator.page(page)
        except PageNotAnInteger:
            an = paginator.page(1)
        except EmptyPage:
            an = paginator.page(paginator.num_pages)

        categorie = models.categorie.objects.all()

        context = {
            "user": user,
            "profile": profil,
            "message": messages,
            "annonces": annonces_list,
            "an": an,
            "categorie": categorie,
        }
        return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)

    else:
        return index(request)


def searchDateLimite(request):

    if request.method == "POST":

        user = request.user
        profil = Profil.objects.get(user=user)

        datD = request.POST.get('dateLimitedebut')
        datF = request.POST.get('dateLimiteFin')

        annonces_nb = models.Annonce.objects.filter(dateDelai__gte=datD, dateDelai__lte=datF).exclude(user=user).order_by('id').reverse().count()

        if annonces_nb == 0:
            messages.warning(request,"Aucun annonce ne correspond a cette date")
            return index(request)


        annonces_list = models.Annonce.objects.filter(dateDelai__gte=datD, dateDelai__lte=datF).exclude(user=user).order_by('id').reverse()

        page = request.GET.get('page', 1)
        paginator = Paginator(annonces_list, 5)
        try:
            an = paginator.page(page)
        except PageNotAnInteger:
            an = paginator.page(1)
        except EmptyPage:
            an = paginator.page(paginator.num_pages)

        categorie = models.categorie.objects.all()

        context = {
            "user": user,
            "profile": profil,
            "message": messages,
            "annonces": annonces_list,
            "an": an,
            "categorie": categorie,
        }
        return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)

    else:
        return index(request)

def searchDateLimitePrecise(request):
    if request.method == "POST":

        user = request.user
        profil = Profil.objects.get(user=user)

        dat = request.POST.get('dateLimite')


        annonces_nb = models.Annonce.objects.filter(dateDelai=dat).exclude(user=user).order_by('id').reverse().count()

        if annonces_nb == 0:
            messages.warning(request,"Aucun annonce ne correspond a cette date")
            return index(request)


        annonces_list = models.Annonce.objects.filter(dateDelai=dat).exclude(user=user).order_by('id').reverse()

        page = request.GET.get('page', 1)
        paginator = Paginator(annonces_list, 5)
        try:
            an = paginator.page(page)
        except PageNotAnInteger:
            an = paginator.page(1)
        except EmptyPage:
            an = paginator.page(paginator.num_pages)

        categorie = models.categorie.objects.all()

        context = {
            "user": user,
            "profile": profil,
            "message": messages,
            "annonces": annonces_list,
            "an": an,
            "categorie": categorie,
        }
        return render(request, "appelsOffres/Authentifier/NosAppeleOffreAuth.html", context)

    else:
        return index(request)

def EnvoieDevisFichier(request, idannonce, idlot):
    user = request.user
    annonce = models.Annonce.objects.get(id=idannonce)
    lot = models.Lot.objects.get(id=idlot)

    devisss = models.assoDevis()
    devisss.devisFile = request.FILES.get('devis')
    devisss.save()

    devis = models.Devis()
    devis.user = user
    devis.lot = lot
    devis.ifFile = True
    devis.save()

    devis.devisAss.add(devisss)
    annonce.devis.add(devis)


    send_mail(
        'Devis Annonces',
        'vous avez recu une nouvelle reponse devis a votre annonce : '
        '' + annonce.titre + " Lot : " + lot.titre ,
        user.email,
        ['soufianeaitmbarek@hotmail.com'],
        fail_silently=False,
    )


    messages.success(request, 'Votre devis a été envoyer avec succes')
    return index(request)

def voirReponse(request, idannonce):

    user = request.user
    annonce = models.Annonce.objects.filter(id=idannonce)

    context = {
        "annonce":annonce,
    }

    return render(request, "appelsOffres/Authentifier/voirReponse.html", context)