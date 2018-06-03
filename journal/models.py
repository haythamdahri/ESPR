import time
import os
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.deconstruct import deconstructible

from ckeditor.fields import RichTextField

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


# For rename the file before save
@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        # eg: filename = 'my uploaded file.jpg'
        ext = filename.split('.')[-1]  # eg: 'jpg'
        uid = uuid.uuid4().hex[:10]  # eg: '567ae32f97'

        # eg: 'my-uploaded-file'
        new_name = '-'.join(filename.replace('.%s' % ext, '').split())

        # eg: 'my-uploaded-file_64c942aa64.jpg'
        renamed_filename = '%(new_name)s_%(uid)s.%(ext)s' % {'new_name': new_name, 'uid': uid, 'ext': ext}

        # eg: 'images/2017/01/29/my-uploaded-file_64c942aa64.jpg'
        return os.path.join(self.path, renamed_filename)


class Image(models.Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    image_path = time.strftime('images/%Y/%m/%d')
    image = models.ImageField(upload_to=PathAndRename(image_path))
    date_publication = models.DateTimeField(auto_now_add=True)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(262, 175)],
        format='JPEG',
        options={'quality': 100})
    image_video = ImageSpecField(
        source='image',
        processors=[ResizeToFill(600, 600)],
        format='JPEG',
        options={'quality': 100})

    def __str__(self):
        return self.image.name


class Journalist(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    tel = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, null=True)
    active = models.BooleanField(default=True)
    link = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    google = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    profile_picture = models.ForeignKey(Image, default=60, on_delete=models.SET(60))

    def __str__(self):
        return self.first_name.capitalize() + ' ' + self.last_name.upper()

    @staticmethod
    def email_list():
        return Journalist.objects.filter(active=True).values_list('email', flat=True)


class Category(models.Model):
    name = models.CharField(max_length=20)
    displayed_text = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=30, default='#37474F')
    icon = models.CharField(max_length=30, null=True, blank=True)
    tab_home = models.CharField(max_length=50, default='tab1')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.TextField(max_length=30, default='#37474F')

    def __str__(self):
        return self.name

    def news_count(self):
        return self.news_set.count()


class News(models.Model):
    title = models.CharField(max_length=255)
    small_title = models.CharField(null=True, blank=True, max_length=255)
    content = RichTextField(default='null')
    date_publication = models.DateTimeField(auto_now_add=True)
    view_number = models.IntegerField(default=0)
    resume = models.TextField(blank=True, null=True)
    comment_enable = models.BooleanField(default=True, verbose_name='comment')
    share_enable = models.BooleanField(default=True, verbose_name='share')
    journalist = models.ForeignKey(Journalist, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE)
    primary_image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True)
    tag = models.ManyToManyField(Tag)
    active = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def add_view(self):
        self.view_number += 1
        self.save()

    def sorted_comment(self):
        return self.comment_set.all().order_by('-number_like')

    class Meta:
        verbose_name_plural = 'Articles'


class Video(News):
    video_url = models.URLField()
    data_merge = models.IntegerField(default=2)
    team_selection = models.BooleanField(default=False)


class ImageNews(Image):
    article = models.ForeignKey(News, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Articles Images'


class AbstractComment(models.Model):
    full_name = models.CharField(max_length=50)
    date_publication = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    message = models.TextField()
    number_like = models.IntegerField(default=0)

    def like(self):
        self.number_like += 1
        self.save()

    def dislike(self):
        self.number_like -= 1
        self.save()

    def __str__(self):
        return self.full_name

    class Meta:
        abstract = True


class Comment(AbstractComment):
    news = models.ForeignKey(News, on_delete=models.CASCADE)


class Answer(AbstractComment):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)


class Signal(models.Model):
    email = models.EmailField()
    cause = models.TextField()
    date_send = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email + '' + str(self.date_send.date())

    class Meta:
        abstract = True


class SignalComment(Signal):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    @staticmethod
    def type():
        return 'comment'


class SignalAnswer(Signal):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    @staticmethod
    def type():
        return 'answer'


class Newsletter(models.Model):
    email = models.EmailField(primary_key=True)
    register_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class CommentFilter(models.Model):
    word = models.CharField(max_length=50)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name_plural = 'CommentsFilter'


class ContactMessage(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=155)
    website = models.URLField(null=True, blank=True)
    date_send = models.DateTimeField(auto_now_add=True, null=True)
    message = models.TextField()
    open = models.BooleanField(default=False)


class Supervisor(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.email

    @staticmethod
    def email_list():
        return Supervisor.objects.filter(active=True).values_list('email', flat=True)


class JoinMessage(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    website = models.URLField(null=True, blank=True)
    date_send = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name.capitalize() + ' ' + self.last_name.upper()
