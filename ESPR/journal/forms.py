from django import forms
from .models import Image, ImageNews

from captcha.fields import ReCaptchaField
from ckeditor.widgets import CKEditorWidget


class JournalistImageUploadForm(forms.Form):
    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'class': 'inputfile inputfile-1',
                'accept': 'image/*'
            }
        )
    )


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        max_length=40,
        widget=forms.EmailInput(
            attrs={
                'class': 'input',
                'placeholder': 'Email:*'}
        ))


class ReplyForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'input',
                'placeholder': 'Nom complet:*'
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'input',
                'placeholder': 'Email:*'
            }
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'input',
                'placeholder': 'Commentaire:*'
            }
        )
    )


class SignalForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'class': 'input',
                'placeholder': 'Email:* '
            }
        )
    )
    motif = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'input',
                'placeholder': 'Motif:* (max 255)'
            }
        )
    )


class JournalistProfileForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Username'
            }
        )
    )
    telephone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Telephone'
            }
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Prénom'
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Nom'
            }
        )
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Website'
            }
        )
    )
    facebook = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Facebook'
            }
        )
    )
    twitter = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Twitter'
            }
        )
    )
    youtube = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Youtube'
            }
        )
    )
    instagram = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Instagram'
            }
        )
    )
    google_plus = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'Google+'
            }
        )
    )
    linkedin = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control border-input',
                'placeholder': 'LinkedIn'
            }
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': '5',
                'class': 'form-control border-input',
                'placeholder': 'Ici vous pouvez écrire votre description'
            }
        )
    )


class JournalistImageImport(forms.ModelForm):
    class Meta:
        model = ImageNews
        fields = ('image', )


class JournalistImagePrimaryImport(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image', )


class JournalistCreateArticle(forms.Form):
    title = forms.CharField(
        max_length=255,
        widget=forms.Textarea(
            attrs={
                'rows': '2',
                'class': 'form-control',
                'placeholder': 'Titre'
            }
        )
    )

    small_title = forms.CharField(
        max_length=155,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Titre réduit'
            }
        )
    )

    content = forms.CharField(
        widget=CKEditorWidget()
    )
    resume = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': '5',
                'class': 'form-control',
                'placeholder': 'Résumé de l\'article'
            }
        )
    )

    category = forms.CharField(
        widget=forms.HiddenInput()
    )

    comment_enable = forms.CharField(
        widget=forms.HiddenInput()
    )

    share_enable = forms.CharField(
        widget=forms.HiddenInput()
    )


class JournalistCreateVideo(forms.Form):
    title = forms.CharField(
        max_length=255,
        widget=forms.Textarea(
            attrs={
                'rows': '2',
                'class': 'form-control',
                'placeholder': 'Titre'
            }
        )
    )

    small_title = forms.CharField(
        max_length=155,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Titre réduit'
            }
        )
    )

    url = forms.URLField(
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Lien du vidéo'
            }
        )
    )

    content = forms.CharField(
        widget=CKEditorWidget()
    )

    resume = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': '5',
                'class': 'form-control',
                'placeholder': 'Résumé de l\'article'
            }
        )
    )

    category = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Résumé de l\'article'
            }
        )
    )

    comment_enable = forms.CharField(
        widget=forms.HiddenInput()
    )

    share_enable = forms.CharField(
        widget=forms.HiddenInput()
    )


class JournalistAddTagForm(forms.Form):
    name = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nom du Tag'
            }
        )
    )

    color = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Couleur du Tag'
            }
        )
    )

    description = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.Textarea(
            attrs={
                'rows': '3',
                'class': 'form-control',
                'placeholder': 'Description du Tag (non requis)'
            }
        )
    )


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nom Complet'
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }
        )
    )

    website = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Website'
            }
        )
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': '5',
                'class': 'form-control',
                'placeholder': 'Message'
            }
        )
    )

    captcha = ReCaptchaField(
        public_key='6Le6VFoUAAAAAAavNsXOmqwQGhrzP9fBORD70McJ',
        private_key='6Le6VFoUAAAAAEToKNwZCgaz_56ITAj1sDWec1Ij'
    )


class JoinForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }
        )
    )

    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }
        )
    )

    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }
        )
    )

    website = forms.URLField(
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Website (non requis)'
            }
        )
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': '10',
                'class': 'form-control',
                'placeholder': 'Message de motivation'
            }
        )
    )

    captcha = ReCaptchaField(
        public_key='6Le6VFoUAAAAAAavNsXOmqwQGhrzP9fBORD70McJ',
        private_key='6Le6VFoUAAAAAEToKNwZCgaz_56ITAj1sDWec1Ij'
    )
