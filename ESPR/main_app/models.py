from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Image(models.Model):
    image = models.ImageField(default="")

    def __str__(self):
        return str(self.image)


class TypeEntreprise(models.Model):
    types = (('publique', 'publique'), ('prive', 'prive'))
    type = models.CharField(max_length=255, choices=types)

class Entreprise(models.Model):
    types = (('Petite entreprise', 'Petite entreprise'), ('Grande entreprise', 'Grande entreprise'), ('Très petite entreprise', 'Très petite entreprise'), ('Moyenne entreprise', 'Moyenne entreprise'))
    secteurs = (('Publique', 'Publique'), ('Prive', 'Privé'))
    nom = models.CharField(max_length=300, null=True, blank=False,unique=True)
    activite = models.CharField(max_length=255, null=True, blank=False)
    secteurActivite = models.CharField(choices=secteurs, null=True, blank=False, max_length=255)
    capitale = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)
    pays = models.CharField(max_length=255, blank=True, null=False)
    ville = models.CharField(max_length=255, null=True, blank=False)
    codePostal = models.IntegerField(null=True)
    telephone = models.IntegerField(null=True)
    typeEntreprise = models.CharField(max_length=255, choices=types)
    raison_social = models.CharField(max_length=255, blank=False, null=True)
    registre_commerce = models.CharField(max_length=255, blank=False, null=True)
    fax = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    email_entreprise = models.EmailField(null=True)
    adresse_Entreprise = models.CharField(max_length=255, blank=False, null=True)
    logo = models.FileField(upload_to="", null=True, blank=False)

    @staticmethod
    def noms_entreprises():
        noms_entreprises = ""
        for entreprise in Entreprise.objects.all():
            noms_entreprises += entreprise.nom + ","
        return noms_entreprises[:-1]

    def __str__(self):
        return self.nom


class Profil(models.Model):
    GENRE_CHOICES = [('homme', 'Homme'),
                     ('femme', 'Femme')]
    date_naissance = models.DateField(null=True, blank=True)
    website = models.CharField(max_length=300, default="", null=True, blank=True)
    entreprise = models.ForeignKey(Entreprise, blank=True, null=True, on_delete=models.CASCADE)
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    photo_profil = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE,
                                     related_name="profil_photo")
    photo_couverture = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE,
                                         related_name="photo_cover")
    facebook = models.CharField(max_length=300, blank=True, null=True, default="")
    youtube = models.CharField(max_length=300, blank=True, null=True, default="")
    instagram = models.CharField(max_length=300, blank=True, null=True, default="")
    linkedin = models.CharField(max_length=300, blank=True, null=True, default="")
    twitter = models.CharField(max_length=300, blank=True, null=True, default="")
    tel = models.CharField(max_length=300, blank=True, null=True, default="")
    ville = models.CharField(max_length=300, blank=True, null=True, default="")
    pays = models.CharField(max_length=300, blank=True, null=True, default="")
    fonction = models.CharField(max_length=300, blank=True, null=True, default="")
    service = models.CharField(max_length=300, blank=True, null=True, default="")
    token_email = models.CharField(max_length=300, blank=True, null=True, default="")
    token_email_expiration = models.DateTimeField(blank=True, null=True)
    civilité = models.CharField(max_length=255, blank=False, null=False)
    adresse_profile = models.CharField(max_length=255, blank=False, null=False)
    is_first_socialmedia = models.BooleanField(default=True)
    is_first_appoffre = models.BooleanField(default=True)
    genre = models.CharField(u'Genre', choices=GENRE_CHOICES, blank=False, default='homme', max_length=20)
    formation_profil = models.ForeignKey('SocialMedia.Formation', on_delete=models.CASCADE, blank=True, null=True,
                                         related_name="formation_profil")
    experience_profil = models.ForeignKey('SocialMedia.Experience', on_delete=models.CASCADE, blank=True, null=True,
                                          related_name="experience_profil")
    resume = models.CharField(max_length=300, blank=True, null=True, default="")
    is_professional = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    mylevel = models.ForeignKey('qa.Level', on_delete=models.CASCADE,blank=True, null=True , default=1,  related_name="level_profil")


    def __str__(self):
        return self.user.username


class Contact(models.Model):
    full_name = models.CharField(max_length=300)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.full_name