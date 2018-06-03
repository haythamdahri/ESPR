from django import forms
from .models import *
from main_app.models import *
from django.contrib.auth.models import User
from datetime import datetime


class PhotoForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Image
        fields = '__all__'


class demandeForm(forms.Form):
    demande = forms.IntegerField(widget=forms.HiddenInput)
    statut = forms.IntegerField(widget=forms.HiddenInput)


class demandeGroupeForm(forms.Form):
    demande = forms.IntegerField(widget=forms.HiddenInput)
    reponse = forms.IntegerField(widget=forms.HiddenInput)


class UserExperienceEdit(forms.Form):
    poste = forms.ModelChoiceField(queryset=Poste.objects.all())
    entreprise = forms.ModelChoiceField(queryset=Entreprise.objects.all())
    dateDebut = forms.DateField()
    dateFin = forms.DateField()
    description = forms.CharField(widget=forms.Textarea)


class StatutsForm(forms.Form):
    contenu_statut = forms.CharField(widget=forms.Textarea(attrs={'rows':'1'}))

class membresAdminForm(forms.Form):
    profil = forms.IntegerField(widget=forms.HiddenInput)
    action = forms.IntegerField(widget=forms.HiddenInput)


class FormAjouterLangue(forms.ModelForm):
    class Meta:
        model = LangueProfil
        fields = ['langue', 'niveau']


class FormExperience(forms.ModelForm):
    actuel = models.BooleanField("Ceci est mon poste actuel")
    date_debut = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))
    date_fin = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))

    class Meta:
        model = Experience
        fields = ['nom_entreprise', 'nom_poste', 'date_debut', 'date_fin', 'actuel', 'description', 'lieu']


class FormFormation(forms.ModelForm):
    annee_debut = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))
    annee_fin = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))

    class Meta:
        model = Formation
        fields = ['nom_ecole', 'titre_formation', 'domaine', 'annee_debut', 'annee_fin', 'activite_et_associations',
                  'description']


class FormBenevolat(forms.ModelForm):
    date_debut = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))
    date_fin = forms.DateField(widget=forms.SelectDateWidget(years=range(datetime.now().year + 10, 1970, -1)))

    class Meta:
        model = ActionBenevole
        fields = ['nom_organisme', 'nom_poste', 'cause', 'date_debut', 'date_fin', 'description']


class FormInformations(forms.ModelForm):
    date_naissance = forms.DateField(required=True,
                                     widget=forms.SelectDateWidget(years=range(datetime.now().year, 1940, -1)))

    class Meta:
        model = Profil
        fields = ['date_naissance', 'website', 'tel', 'facebook', 'youtube', 'instagram', 'linkedin', 'twitter']


class FormInformationsProfil(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['formation_profil', 'experience_profil', 'resume', 'ville', 'pays']

    def __init__(self, user, *args, **kwargs):
        super(FormInformationsProfil, self).__init__(*args, **kwargs)

        self.fields['formation_profil'].queryset = Formation.objects.filter(profil=user.profil)
        self.fields['experience_profil'].queryset = Experience.objects.filter(profil=user.profil)


class FormInformationsUser(forms.ModelForm):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=100)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class FormCreerEntreprise(forms.ModelForm):
    presentation_entreprise = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Entreprise
        fields = ['nom', "typeEntreprise", 'logo']


class FormCreerPageEntreprise(forms.ModelForm):
    presentation_entreprise = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = PageEntreprise
        fields = ['presentation_entreprise', 'siege_social', 'annee_creation', 'specialisation', 'img_couverture']

class FormCreerGroupe(forms.ModelForm):
    class Meta:
        model = Groupe
        fields = ['nom', 'statut_groupe','description']

class FormPhotosGroupe(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']


class FormModifierEntreprise(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['nom', "typeEntreprise", ]


class FormModifierPageEntreprise(forms.ModelForm):
    presentation_entreprise = forms.CharField(widget=forms.Textarea, required=True)
    class Meta:
        model = PageEntreprise
        fields = ['presentation_entreprise', 'siege_social', 'annee_creation', 'specialisation', ]


class FormCreerOffreEmploi(forms.ModelForm):
    class Meta:
        model = OffreEmploi
        fields = ['tel', 'email', 'pays', 'ville', 'diplome_requis', 'type_contrat', 'description_poste',
                  'profil_recherche', 'type_emploi', 'nom_poste', 'fichier_joint']


class FormModifierOffreEmploi(forms.ModelForm):
    class Meta:
        model = OffreEmploi
        fields = ['tel', 'email', 'pays', 'ville', 'diplome_requis', 'type_contrat', 'description_poste',
                  'profil_recherche', 'type_emploi', 'nom_poste', 'fichier_joint', 'en_cours']


class FormPhotoProfilEntreprise(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['logo']


class FormPhotoCouvertureEntreprise(forms.ModelForm):
    class Meta:
        model = PageEntreprise
        fields = ['img_couverture']

#Haytham Forms
#Statut

class StatutsForm(forms.Form):
    contenu_statut = forms.CharField(widget=forms.Textarea(attrs={'rows':'1'}))
    image = forms.ImageField()
    video = forms.FileField()
    document = forms.FileField()


