from django import forms

class RegistrationFormation(forms.Form):
    libelle=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Titre Formation'}))
    description=forms.CharField(required=True,widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Description'}))
    objectifs = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Objectifs'}))
    date_creation=forms.DateField(required=True,widget=forms.DateInput(attrs={'class': 'form-control','placeholder': 'YYYY-MM-DD'}))
    formation_picture = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'dropzone'}))

class RegistrationTheme(forms.Form):
    libelle=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Titre Thème'}))
    description=forms.CharField(required=True,widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Description'}))
    but=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Intérêt',}))
    contenu=forms.CharField(required=True,widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Contenu',}))
    theme_picture = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'dropzone'}))

class RegistrationCours(forms.Form):
    course_title = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Titre Cours'}))
    course_price = forms.FloatField(required=True,widget=forms.NumberInput(attrs={'class':'form-control ','placeholder':'Coût'}))
    course_start = forms.DateField(required=True,widget=forms.DateInput(attrs={'class':'form-control date-pick','placeholder':'YYYY-MM-DD'}))
    course_expire = forms.DateField(required=True,widget=forms.DateInput(attrs={'class':'form-control date-pick','placeholder':'YYYY-MM-DD'}))
    course_description = forms.CharField(required=True,widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Description'}))
    course_goal = forms.CharField(required=True,widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Objectifs'}))
    course_resume = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Résumé'}))
    course_picture = forms.ImageField(required=True,widget=forms.FileInput(attrs={'class':'dropzone'}))
    video_url = forms.URLField(required=True,widget=forms.URLInput(attrs={'class':'form-control','placeholder':'URL'}))
    video_name = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom de video'}))


class RegistrationLecon(forms.Form):
    lesson_title=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Titre leçon'}))
    lesson_duration=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Durée:hh:mm:ss'}))
    lesson_description = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}))
    lesson_goal = forms.CharField(required=True,widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Objectifs'}))
    lesson_resume = forms.CharField(required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Résumé'}))
    lesson_file=forms.FileField(required=True,widget=forms.FileInput(attrs={'class':'form-control'}))
    file_format=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Ex:pdf,word..'}))
    file_name= forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du document'}))
    lesson_video=forms.FileField(required=True,widget=forms.FileInput(attrs={'class':'form-control'}))
    lesson_video_name = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom de video'}))
    lesson_video_format=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Ex:mp4'}))


