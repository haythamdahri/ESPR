from django.db import models
from django.contrib.auth.models import User




# Create your models here.
class Formation(models.Model):
    formateur_id = models.ForeignKey(User,on_delete=models.CASCADE)
    libelle=models.CharField(max_length=255,blank=True,null=True)
    description=models.TextField(max_length=1000,blank=True,null=True)
    date_creation=models.DateField(blank=True,null=True)
    objectifs=models.TextField(max_length=1000,blank=True,null=True)
    formation_picture=models.ImageField(upload_to='Formation_Picture', blank=True, null=True)

class Theme(models.Model):
    formateur_id = models.ForeignKey(User, on_delete=models.CASCADE)
    formation_id=models.ForeignKey(Formation,on_delete=models.CASCADE)
    libelle=models.CharField(max_length=255,blank=True,null=True)
    description=models.CharField(max_length=1000,blank=True,null=True)
    but=models.CharField(max_length=1000,blank=True,null=True)
    contenu=models.CharField(max_length=1000,blank=True,null=True)
    theme_picture = models.ImageField(upload_to='Theme_Picture', blank=True, null=True)


class Courses(models.Model):
    formateur_id = models.ForeignKey(User, on_delete=models.CASCADE)
    theme_id=models.ForeignKey(Theme,on_delete=models.CASCADE)
    course_title=models.CharField(max_length=255,blank=True,null=True,default='')
    course_price=models.FloatField(max_length=255,blank=True,null=True,default='')
    course_start=models.DateField(blank=True,null=True,default='')
    course_expire=models.DateField(blank=True,null=True,default='')
    course_description=models.TextField(blank=True,null=True,default='')
    course_goal = models.TextField(blank=True,null=True,default='')
    course_resume=models.CharField(max_length=255,blank=True,null=True,default='')
    course_picture=models.ImageField(upload_to='Course_Picture',blank=True,null=True)
    video_url=models.URLField(blank=True,null=True)
    video_name=models.CharField(max_length=255,blank=True,null=True,default='')


    def __str__(self):
        return self.course_title

class Lessons(models.Model):
    formateur_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id=models.ForeignKey(Courses,on_delete=models.CASCADE)
    lesson_title=models.CharField(max_length=255,blank=True,null=True)
    lesson_description = models.TextField(blank=True, null=True, default='')
    lesson_goal = models.TextField(blank=True, null=True, default='')
    lesson_resume = models.CharField(max_length=255, blank=True, null=True, default='')
    lesson_duration = models.CharField(max_length=255,blank=True, null=True, default='')
    lesson_file = models.FileField(upload_to='Files', blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_format=models.CharField(max_length=255, blank=True, null=True, default='')
    lesson_video=models.FileField(upload_to='Files',blank=True,null=True)
    lesson_video_name = models.CharField(max_length=255, blank=True, null=True, default='')
    lesson_video_format=models.CharField(max_length=255, blank=True, null=True, default='')



class Exam(models.Model):

    name = models.CharField(max_length=100,default="")



    def __unicode__(self):
        return self.name
class Question(models.Model):
    question = models.TextField(max_length=200,default="")
    option1 = models.CharField(max_length=50,default="")
    option2 = models.CharField(max_length=50, default="")
    option3 = models.CharField(max_length=50, default="")
    option4 = models.CharField(max_length=50, default="")
    answer = models.CharField(max_length=50, default="")
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE)

    def __unicode__(self):
        return self.question
