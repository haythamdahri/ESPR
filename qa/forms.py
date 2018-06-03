from qa.models import *
from django.contrib.auth.models import User
from django import forms
from django_markdown.fields import MarkdownFormField
from django_markdown.widgets import MarkdownWidget
from markdownx.fields import MarkdownxFormField
from ckeditor_uploader.fields import RichTextUploadingField
from django_select2.forms import ModelSelect2MultipleWidget , Select2MultipleWidget
from easy_select2 import select2_modelform , Select2

class QuestionForm(forms.ModelForm):
    categorie = forms.ModelChoiceField(queryset=Categorie.objects.all(), widget=Select2(select2attrs={'width': '100%'}))
    class Meta:
        model = Question
        fields = ['question_text']
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer_text']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = '__all__'


class blogForm(forms.ModelForm):
    class Meta:
        model = Blog_qa
        fields = ['blog_text']        



class AnswerBlogForm(forms.ModelForm):
    class Meta:
        model = Answer_blog
        fields = ['answer_text']