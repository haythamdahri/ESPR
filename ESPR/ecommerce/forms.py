from django import forms
from captcha.fields import ReCaptchaField
from .models import CommerceSCategory, Brand, CommerceImage
from ckeditor.widgets import CKEditorWidget

BOOL_CHOICES = [
    ('yes', 'Oui'),
    ('no', 'Non'),
]


class AddProductForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }
        )
    )
    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'class': 'inputfile inputfile-1',
                'accept': 'image/*',
                'style': 'display:none',
                'onchange': "$('#upload-file-info').html(this.files[0].name)"
            }
        )
    )
    price = forms.DecimalField(
        max_digits=15,
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Prix du produit'
            }
        )
    )
    category = forms.ModelChoiceField(
        queryset=CommerceSCategory.objects.all().order_by('name'),
        widget=forms.Select(
            attrs={
                'class': 'selectpicker form-control',
                'title': 'Sélectionnez une catégorie'
            }
        )
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    min_quantity = forms.IntegerField(
        initial=1,
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    unit = forms.CharField(
        max_length=200,
        initial='Pièce',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    professional = forms.CharField(
        widget=forms.RadioSelect(
            choices=BOOL_CHOICES
        )
    )
    packaging = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Emballage du produit'
            }
        )
    )
    delivery = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Livraison du produit'
            }
        )
    )
    description = forms.CharField(
        widget=CKEditorWidget()
    )
    old_price = forms.DecimalField(
        max_digits=15,
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ancien prix'
            }
        )
    )


class ProductImageImport(forms.ModelForm):
    class Meta:
        model = CommerceImage
        fields = ('image', )


class AddProductStockForm(forms.Form):
    quantity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Quantité'
            }
        )
    )
    price_sup = forms.DecimalField(
        initial=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Différence de prix en DH',
                'style': 'padding-right: 40px;'
            }
        )
    )
    color = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Couleur du produit'
            }
        )
    )


class AddProductSpecificationForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Titre du Spécification'
            }
        )
    )
    content = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                'row': '5',
                'class': 'form-control',
                'placeholder': 'Contenu du Spécification'
            }
        )
    )


class AddProductDetailForm(forms.Form):
    name = forms.CharField(
        max_length=250,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Titre du Détail'
            }
        )
    )
    value = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'row': '5',
                'class': 'form-control',
                'placeholder': 'Contenu du Détail'
            }
        )
    )


class StoreForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }
        )
    )
    image_profile = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'style': 'display:none',
                'onchange': "$('#upload-file-label-p').html(this.files[0].name)"
            }
        )
    )
    image_cover = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
                'style': 'display:none',
                'onchange': "$('#upload-file-label-c').html(this.files[0].name)"
            }
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': '5',
                'class': 'form-control',
                'placeholder': 'Description'
            }
        )
    )
    address = forms.CharField(
        max_length=300,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Adresse'
            }
        )
    )
    tel = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }
        )
    )
    captcha = ReCaptchaField(
        public_key='6Le6VFoUAAAAAAavNsXOmqwQGhrzP9fBORD70McJ',
        private_key='6Le6VFoUAAAAAEToKNwZCgaz_56ITAj1sDWec1Ij'
    )


class UpdateProductForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }
        )
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'inputfile inputfile-1',
                'accept': 'image/*',
                'style': 'display:none',
                'onchange': "$('#upload-file-info').html(this.files[0].name)"
            }
        )
    )
    price = forms.DecimalField(
        max_digits=15,
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Prix du produit'
            }
        )
    )
    category = forms.ModelChoiceField(
        queryset=CommerceSCategory.objects.all().order_by('name'),
        widget=forms.Select(
            attrs={
                'class': 'selectpicker form-control',
                'title': 'Sélectionnez une catégorie'
            }
        )
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    min_quantity = forms.IntegerField(
        initial=1,
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    unit = forms.CharField(
        max_length=200,
        initial='Pièce',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    professional = forms.CharField(
        widget=forms.RadioSelect(
            choices=BOOL_CHOICES
        )
    )
    packaging = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Emballage du produit'
            }
        )
    )
    delivery = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Livraison du produit'
            }
        )
    )
    description = forms.CharField(
        widget=CKEditorWidget()
    )
    old_price = forms.DecimalField(
        max_digits=15,
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ancien prix'
            }
        )
    )
