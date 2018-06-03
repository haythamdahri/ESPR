from django.db import models
from django.contrib.auth.models import User
from django_markdown.models import MarkdownField
from main_app.models import *
from ckeditor.fields import RichTextField  
from ckeditor_uploader.fields import RichTextUploadingField
import datetime



# Create your models here.
class Tag(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    date = models.DateTimeField(default=datetime.datetime.today(), blank=True)
    def __str__(self):
        return self.slug

    class Meta:
        ordering = ('slug',)


###################################################################################

# class Profil(models.Model):
#     user = models.OneToOneField(User, on_delete=True)
#     points = models.IntegerField(default=0)

#     website = models.URLField(blank=True)
#     picture = models.ImageField(upload_to='qa/static/profile_images', blank=True)
#     date_naissance = models.DateField()
#     # entreprise = models.ForeignKey(Entreprise,blank=True,null=True,  on_delete=models.CASCADE)
#     # photo_profil = models.OneToOneField(Image, blank=True,null=True, on_delete=models.CASCADE, related_name="profil_photo")
#     # photo_couverture = models.OneToOneField(Image, blank=True,null=True, on_delete=models.CASCADE, related_name="photo_cover")
#     facebook = models.CharField(max_length=300, blank=True, null=True, default="")
#     youtube = models.CharField(max_length=300, blank=True, null=True, default="")
#     instagram = models.CharField(max_length=300, blank=True, null=True, default="")
#     linkedin = models.CharField(max_length=300, blank=True, null=True, default="")
#     tel = models.CharField(max_length=300, blank=True, null=True, default="")
#     ville = models.CharField(max_length=300, blank=True, null=True, default="")
#     pays = models.CharField(max_length=300, blank=True, null=True, default="")
#     fonction = models.CharField(max_length=300, blank=True, null=True, default="")
#     service = models.CharField(max_length=300, blank=True, null=True, default="")

#     def __str__(self):
#         return self.user.username


###################################################################################


class Categorie(models.Model):
    title_categorie = models.CharField(max_length=100)
    description_categorie = models.CharField(max_length=200)


    def __str__(self):
        return self.title_categorie


###################################################################################

class Question(models.Model):
    # question_text = models.CharField(max_length=200)
    question_text = RichTextUploadingField ()
    question_title = models.CharField(max_length=200)
    # question_text = MarkdownField()
    pub_date = models.DateTimeField('date published')
    tags = models.ManyToManyField(Tag)
    reward = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    user_data = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE,null=True,blank=True)
    type_pub = models.CharField(max_length=200 , default='question')
    user_update = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE,  related_name="update_profil", blank=True, null=True )
    update_date = models.DateTimeField('date update', blank=True, null=True)


    def __str__(self):
        return self.question_text

    @staticmethod
    def noms_questions():
        noms_questions = ""
        for question in Question.objects.all():
            noms_questions += question.question_title + ","
        return noms_questions[:-1]


###################################################################################

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE ,null=True,blank=True)
    answer_text = RichTextUploadingField()
    votes = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    user_data = models.ForeignKey('main_app.Profil', on_delete=True)

    def __str__(self):
        return self.answer_text


###################################################################################

class Voter(models.Model):
    user = models.ForeignKey('main_app.Profil', on_delete=True)
    answer = models.ForeignKey(Answer, on_delete=True)


###################################################################################

class QVoter(models.Model):
    user = models.ForeignKey('main_app.Profil', on_delete=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


###################################################################################

class Comment(models.Model):
    answer = models.ForeignKey(Answer, on_delete=True)
    comment_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    user_data = models.ForeignKey('main_app.Profil', on_delete=True)

    def __str__(self):
        return self.comment_text

###################################################################################

class Level(models.Model):
    libelle = models.CharField(max_length=200)

    def __str__(self):
        return self.libelle

###################################################################################

class Blog_qa(models.Model):
    # question_text = models.CharField(max_length=200)
    blog_text = RichTextUploadingField ()
    blog_title = models.CharField(max_length=200, blank=True, null=True)
    # question_text = MarkdownField()
    pub_date = models.DateTimeField('date published', blank=True, null=True)
    tags = models.ManyToManyField(Tag , blank=True, null=True)
    reward = models.IntegerField(default=0 , blank=True, null=True)
    views = models.IntegerField(default=0 , blank=True, null=True)
    user_data = models.ForeignKey('main_app.Profil', on_delete=True , blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=True,null=True,blank=True)
    user_update = models.ForeignKey('main_app.Profil', on_delete=True,  related_name="update_blog", blank=True, null=True )
    update_date = models.DateTimeField('date update', blank=True, null=True)
    photo =  models.ForeignKey('main_app.Image', on_delete=True , blank=True, null=True)


    def __str__(self):
        return self.blog_title


###################################################################################

class Answer_blog(models.Model):
    blog = models.ForeignKey(Blog_qa, on_delete=True ,null=True,blank=True)
    answer_text = RichTextUploadingField()
    votes = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    user_data = models.ForeignKey('main_app.Profil', on_delete=True)

    def __str__(self):
        return self.answer_text


###################################################################################

class blog_Voter(models.Model):
    user = models.ForeignKey('main_app.Profil', on_delete=True)
    blog = models.ForeignKey(Blog_qa, on_delete=True , related_name="voteblog")


###################################################################################