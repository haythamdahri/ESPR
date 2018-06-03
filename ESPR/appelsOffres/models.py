from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class fonction(models.Model):
    id = models.AutoField(primary_key=True)
    fonction = models.CharField(max_length=70)

    def __str__(self):
        return self.fonction

class service(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.CharField(max_length=70)

    def __str__(self):
        return self.service

class Lot(models.Model):
    id=models.AutoField(primary_key=True)
    titre = models.CharField(max_length=100, null=True)
    categorie = models.CharField(max_length=100, null=True)
    description = models.TextField()
    estimation = models.FloatField()
    cautionProvisoire = models.FloatField()
    qualifications = models.CharField(max_length=255, null=True)
    Agrements = models.CharField(max_length=255, null=True)
    echantillons = models.TextField()
    visiteLieux = models.TextField()
    variante = models.CharField(max_length=100)
    reservePME = models.CharField(max_length=100)
    cahierDeCharge = models.FileField(upload_to='appelsOffres/')
    user = models.ForeignKey(User, on_delete= models.CASCADE, unique=False)

    def __str__(self):
        return self.titre

class assoDevis(models.Model):
    id = models.AutoField(primary_key=True)
    TVA = models.IntegerField(null=True)
    description = models.CharField(max_length=255, null=True)
    quantite = models.IntegerField(null=True)
    prixUTH = models.FloatField(null=True)
    devisFile = models.FileField(upload_to='appelsOffres/devis', null=True)

    def quantitePrix(self):
        return (self.quantite*self.prixUTH)

    def quantitePrixTVA(self):
        p = (self.quantite*self.prixUTH) + (self.quantite*self.prixUTH)*self.TVA/100
        return p

class Devis(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False, null=True)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, unique=False, null=True)
    ifFile = models.BooleanField(default=False)
    ifForm = models.BooleanField(default=False)
    devisAss = models.ManyToManyField(assoDevis)


class Annonce(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    datePub = models.DateTimeField(default=datetime.now(), null=True)
    dateDelai = models.DateTimeField(null=True)
    statusAnnonce = models.BooleanField(default=True)
    valid = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    lot = models.ManyToManyField(Lot)
    devis = models.ManyToManyField(Devis)
    nbVue = models.IntegerField(null=True)

    def display_lot(self):
        return self.lot.iterator().__iter__()

    def __str__(self):
        return self.titre


class ImageScrol(models.Model):
    id = models.AutoField(primary_key=True)
    imageScrol = models.ImageField(upload_to='appelsOffres')

class categorie(models.Model):
    id = models.AutoField(primary_key=True)
    categorie = models.CharField(max_length=100)

    def __str__(self):
        return self.categorie

class Favoris(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, unique=False, on_delete=False)
    annonce = models.ForeignKey(Annonce, unique=False, on_delete=False)

    def listAnnonce(self):
        return self.objects







