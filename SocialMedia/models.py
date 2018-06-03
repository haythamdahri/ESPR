from django.db import models
from django.contrib.auth.models import User
import os.path
from django.urls import reverse
from itertools import chain
from django.db.models import Max
from django.utils.timezone import now


class Groupe(models.Model):
    statuts = (('publique', 'publique'), ('prive', 'privé'))
    nom = models.CharField(max_length=255)
    date_creation = models.DateField()
    statut_groupe = models.CharField(choices=statuts, max_length=255, null=False, blank=False)
    have_image = models.BooleanField(default=False)
    description = models.TextField(default="")
    photo_profil = models.ForeignKey('main_app.Image', on_delete=models.CASCADE, related_name="groupe_photo")
    photo_couverture = models.ForeignKey('main_app.Image', on_delete=models.CASCADE, related_name="profil_cover")
    admins = models.ManyToManyField('main_app.Profil', related_name="admin")
    moderators = models.ManyToManyField('main_app.Profil', related_name="moderateur")
    creator = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="createur")
    adherents = models.ManyToManyField('main_app.Profil', related_name="adherent")

    def __str__(self):
        return "Groupe: " + self.nom + "\b\bCree Par: " + self.creator.user.username

    def get_absolute_url(self):
        return reverse('SocialMedia:groupe', args=[str(self.id)])


class DemandeGroupe(models.Model):
    emetteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    groupe_recepteur = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    reponse = models.BooleanField()

    def __str__(self):
        return self.emetteur.user.username + " à demandé de rejoidre le groupe " + self.groupe_recepteur.nom


def generate_path(instance, filename):
    extension = os.path.splitext(filename)[1][1:]
    if extension in VALID_IMAGE_EXTENSIONS:
        path = 'SocialMedia/Image/'
    else:
        path = 'SocialMedia/Fichier/'

    return os.path.join(path, instance.fichier.name)


class ReseauSocialFile(models.Model):
    fichier = models.FileField(upload_to=generate_path)
    date_telechargement = models.DateTimeField()
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="FileOwner")

    def str(self):
        return self.fichier.name


class Statut(models.Model):
    is_shared = models.BooleanField(default=False)
    original_statut_id = models.IntegerField(null=True, blank=True)
    date_statut = models.DateTimeField()
    contenu_statut = models.CharField(max_length=6000)
    is_group_statut = models.BooleanField(default=False)
    is_profil_statut = models.BooleanField(default=False)
    publisher = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="pub")
    mur_profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="statut_mur_profil")
    mur_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True)
    images = models.ManyToManyField(ReseauSocialFile, related_name="images", blank=True, null=True)
    videos = models.ManyToManyField(ReseauSocialFile, related_name="videos", blank=True, null=True)
    files = models.ManyToManyField(ReseauSocialFile, related_name="files", blank=True, null=True)
    likes = models.ManyToManyField('main_app.Profil', blank=True, null=True)

    def __str__(self):
        return self.publisher.user.username + " a publié un statut"

    def get_absolute_url(self):
        return reverse('SocialMedia:Statut', args=[str(self.id)])


class Commentaire(models.Model):
    comment = models.CharField(null=False, blank=False, max_length=6000)
    date_commentaire = models.DateField()
    statut = models.ForeignKey(Statut, on_delete=models.CASCADE)
    user = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="commented_user")
    image = models.ManyToManyField(ReseauSocialFile, null=True, blank=True)
    likes = models.ManyToManyField('main_app.Profil', null=True, blank=True)



class DemandeAmi(models.Model):
    demandes = ((0, 'En Cours'), (1, 'Acceptée'), (2, 'Refusée'), (3, 'Bloquée'))
    emetteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="sender")
    recepteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="receiver")
    statut = models.IntegerField(null=False, blank=False, choices=demandes)


    @staticmethod
    def sont_ami(user1, user2):
        demande_acceptee = get_object_or_none(DemandeAmi, emetteur=user1.profil, recepteur=user2.profil, statut=1)
        demande_acceptee2 = get_object_or_none(DemandeAmi, emetteur=user2.profil, recepteur=user1.profil, statut=1)

        if demande_acceptee is not None or demande_acceptee2 is not None:
            return True
        return False

    def __str__(self):
        return self.demandes[self.statut][1]


class Suivie(models.Model):
    follower = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="suiveur")
    followed_profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="suive")

    class Meta:
        unique_together = ('follower', 'followed_profil',)

    def __str__(self):
        return self.follower.user.username + " suit " + self.followed_profil.user.username


class Conversation(models.Model):
    start_date = models.DateTimeField(blank=False)
    participants = models.ManyToManyField(User)

    def __str__(self):
        show = ""
        for user in self.participants.all():
            show += " || Participant Username: " + user.username
        return show


class Responseconversation(models.Model):
    message = models.CharField(max_length=6000)
    message_date = models.DateTimeField(blank=False)
    is_image = models.BooleanField(default=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    image = models.ForeignKey('main_app.Image', on_delete=models.CASCADE, blank=True, null=True)
    user_responsed = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return "Response Of: " + self.user_responsed.username


VALID_IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
]


class Poste(models.Model):
    nom_poste = models.CharField(max_length=300)

    @staticmethod
    def noms_postes():
        noms_postes = ""
        for poste in Poste.objects.all():
            noms_postes += poste.nom_poste + ","
        return noms_postes[:-1]

    def __str__(self):
        return self.nom_poste


class PageEntreprise(models.Model):
    entreprise = models.OneToOneField("main_app.Entreprise", blank=False, null=True, on_delete=models.CASCADE)
    presentation_entreprise = models.CharField(max_length=3000, blank=False, null=True)
    siege_social = models.CharField(max_length=255, blank=False, null=True)
    annee_creation = models.IntegerField(null=True, blank=False)
    specialisation = models.CharField(max_length=255, blank=False, null=True)
    abonnees = models.ManyToManyField('main_app.Profil', related_name="abonnees", blank=True)
    administrateurs = models.ManyToManyField('main_app.Profil', related_name="administrateurs", blank=True)
    moderateurs = models.ManyToManyField('main_app.Profil', related_name="moderateurs", blank=True)
    img_couverture = models.ImageField(upload_to="",null=True,blank=True)

    def is_administrateur(self,user):
        if user.profil not in self.administrateurs.all():
            return False
        return True

    def is_moderateur(self,user):
        if user.profil not in self.moderateurs.all():
            return False
        return True


    def __str__(self):
        return self.entreprise.nom

    def get_absolute_url(self):
        return reverse('SocialMedia:page_entreprise', args=[str(self.entreprise_id)])


class OffreEmploi(models.Model):
    TYPES_EMPLOI = (('plein', 'Plein temps'), ('partiel', 'Temps partiel'))
    TYPES_CONTRAT = (('cdi', 'CDI'), ('cdd', 'CDD'))

    tel = models.IntegerField()
    email = models.EmailField()
    pays = models.CharField(max_length=300)
    ville = models.CharField(max_length=300)
    diplome_requis = models.CharField(max_length=300)
    type_contrat = models.CharField(max_length=300,choices=TYPES_CONTRAT)
    description_poste = models.TextField()
    profil_recherche = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    en_cours = models.BooleanField(default=True)
    date_fin = models.DateField(null=True,default=None,blank=True)
    type_emploi = models.CharField(max_length=300, choices=TYPES_EMPLOI)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE,
                              related_name="poste_recherche",null=True)
    nom_poste = models.CharField(max_length=300)
    page_entreprise = models.ForeignKey(PageEntreprise, on_delete=models.CASCADE)
    profil_publicateur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE,
                                           related_name="profil_publicateur")
    profil_postulants = models.ManyToManyField('main_app.Profil', related_name="profil_postulants", blank=True)
    fichier_joint = models.FileField(null=True,blank=True)

    def __str__(self):
        return self.page_entreprise.entreprise.nom + " propose un poste d'un " + self.poste.nom_poste



class Experience(models.Model):
    entreprise = models.ForeignKey('main_app.Entreprise', on_delete=models.CASCADE, null=True, blank=True)
    nom_entreprise = models.CharField(max_length=300)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE, null=True, blank=True)
    nom_poste = models.CharField(max_length=300)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    actuel = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    lieu = models.CharField(max_length=300, null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)

    def regler_date(self):
        self.date_debut = self.date_debut.replace(day=1)
        self.date_fin = self.date_fin.replace(day=1)

    @staticmethod
    def get_user_experiences(user):
        exp = Experience.objects.filter(profil=user.profil).exclude(date_fin=None).order_by(
            '-date_fin')  # Experiences passées
        exp2 = Experience.objects.filter(profil=user.profil, date_fin=None)  # Experience actuelle
        return list(chain(exp2, exp))

    def __str__(self):
        return self.nom_poste + " à " + self.nom_entreprise


class Ecole(models.Model):
    nom = models.CharField(max_length=300)
    logo = models.ImageField(upload_to="SocialMedia/Image/")

    @staticmethod
    def noms_ecoles():
        noms_ecoles = ""
        for ecole in Ecole.objects.all():
            noms_ecoles += ecole.nom + ","

        return noms_ecoles[:-1]

    def __str__(self):
        return self.nom


class Formation(models.Model):
    titre_formation = models.CharField(max_length=300)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, null=True, blank=True)
    nom_ecole = models.CharField(max_length=300)
    domaine = models.CharField(max_length=300, null=True, blank=True)
    activite_et_associations = models.TextField(null=True, blank=True)
    annee_debut = models.DateField()
    annee_fin = models.DateField()
    description = models.TextField(null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)

    @staticmethod
    def get_last_formation(user):
        max_annee_fin = Formation.objects.filter(profil=user.profil).aggregate(Max('annee_fin'))['annee_fin__max']
        return Formation.objects.filter(profil=user.profil, annee_fin=max_annee_fin).first()

    def regler_date(self):
        self.date_debut = self.annee_debut.replace(day=1)
        self.date_fin = self.annee_fin.replace(day=1)
        self.date_fin = self.annee_debut.replace(month=1)
        self.date_fin = self.annee_fin.replace(month=1)

    @staticmethod
    def get_user_formations(user):
        return Formation.objects.filter(profil=user.profil).order_by('-annee_fin')  # Formations passées

    def __str__(self):
        return self.titre_formation + " à " + self.nom_ecole


class Organisme(models.Model):
    nom = models.CharField(max_length=300)
    logo = models.ImageField(upload_to="SocialMedia/Image/")

    @staticmethod
    def noms_organismes():
        noms_organismes = ""
        for organisme in Organisme.objects.all():
            noms_organismes += organisme.nom + ","

        return noms_organismes[:-1]

    def __str__(self):
        return self.nom


class ActionBenevole(models.Model):
    organisme = models.ForeignKey(Organisme, on_delete=models.CASCADE, null=True, blank=True)
    nom_organisme = models.CharField(max_length=300)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE, null=True, blank=True)
    nom_poste = models.CharField(max_length=300)
    cause = models.TextField(null=True, blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    description = models.TextField(null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)

    @staticmethod
    def get_user_benevolats(user):
        return ActionBenevole.objects.filter(profil=user.profil).order_by('-date_fin')  # Benevolats passés

    def regler_date(self):
        self.date_debut = self.date_debut.replace(day=1)
        self.date_fin = self.date_fin.replace(day=1)

    def __str__(self):
        return self.profil.user.first_name + " " + self.profil.user.last_name + " fait  " + self.nom_poste + " à " + self.nom_organisme


class Langue(models.Model):
    nom = models.CharField(max_length=300)

    def __str__(self):
        return self.nom


class NiveauLangue(models.Model):
    niveau = models.CharField(max_length=300)

    def __str__(self):
        return self.niveau


class LangueProfil(models.Model):
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, null=True, blank=True)
    langue = models.ForeignKey(Langue, on_delete=models.CASCADE)
    niveau = models.ForeignKey(NiveauLangue, on_delete=models.CASCADE)


class Reply(models.Model):
    replyContent = models.CharField(max_length=6000)
    commentaire = models.ForeignKey(Commentaire, on_delete=models.CASCADE)
    image = models.ManyToManyField(ReseauSocialFile, null=True, blank=True)
    user = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name='publisher')
    date_reply = models.DateTimeField()
    likes = models.ManyToManyField('main_app.Profil', related_name='likedBy', null=True, blank=True)


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


class StatutSignales(models.Model):
    statut = models.ForeignKey(Statut, on_delete=models.CASCADE)
    signal_sender = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    data_signale = models.DateTimeField(default=now)


class CommentaireSignales(models.Model):
    commentaire = models.ForeignKey(Commentaire, on_delete=models.CASCADE)
    signal_sender = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    data_signale = models.DateTimeField(default=now)


class ReplySignales(models.Model):
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE)
    signal_sender = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    data_signale = models.DateTimeField(default=now)


class Notification(models.Model):
    types = ((0, 'statut'),
             (1, 'groupe'),
             (2, 'profil'),
             (3, 'offreEmploi'),
             (4, 'entreprise'),
             (5, 'demande'))
    statut = models.ForeignKey(Statut, on_delete=models.CASCADE, null=True, blank=True)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', related_name='profil', on_delete=models.CASCADE, null=True,
                               blank=True)
    offreEmploi = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE, null=True, blank=True)
    entreprise = models.ForeignKey(PageEntreprise, on_delete=models.CASCADE, null=True, blank=True)
    type = models.IntegerField(choices=types, null=True, blank=True)
    message = models.CharField(max_length=1000)
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)
    date_notification = models.DateTimeField(default=now)
    profil_to_notify = models.ForeignKey('main_app.Profil', related_name='profil_to_notify', null=True, blank=True,
                                         on_delete=models.CASCADE)

    def __str__(self):
        return self.profil_to_notify.user.username+": "+self.message
