# Generated by Django 2.0.5 on 2018-06-02 17:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Courses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_title', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('course_price', models.FloatField(blank=True, default='', max_length=255, null=True)),
                ('course_start', models.DateField(blank=True, default='', null=True)),
                ('course_expire', models.DateField(blank=True, default='', null=True)),
                ('course_description', models.TextField(blank=True, default='', null=True)),
                ('course_goal', models.TextField(blank=True, default='', null=True)),
                ('course_resume', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('course_picture', models.ImageField(blank=True, null=True, upload_to='Course_Picture')),
                ('video_url', models.URLField(blank=True, null=True)),
                ('video_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('formateur_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Formation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('date_creation', models.DateField(blank=True, null=True)),
                ('objectifs', models.TextField(blank=True, max_length=1000, null=True)),
                ('formation_picture', models.ImageField(blank=True, null=True, upload_to='Formation_Picture')),
                ('formateur_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Lessons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_title', models.CharField(blank=True, max_length=255, null=True)),
                ('lesson_description', models.TextField(blank=True, default='', null=True)),
                ('lesson_goal', models.TextField(blank=True, default='', null=True)),
                ('lesson_resume', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('lesson_duration', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('lesson_file', models.FileField(blank=True, null=True, upload_to='Files')),
                ('file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('file_format', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('lesson_video', models.FileField(blank=True, null=True, upload_to='Files')),
                ('lesson_video_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('lesson_video_format', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ELearning.Courses')),
                ('formateur_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(default='', max_length=200)),
                ('option1', models.CharField(default='', max_length=50)),
                ('option2', models.CharField(default='', max_length=50)),
                ('option3', models.CharField(default='', max_length=50)),
                ('option4', models.CharField(default='', max_length=50)),
                ('answer', models.CharField(default='', max_length=50)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ELearning.Exam')),
            ],
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('but', models.CharField(blank=True, max_length=1000, null=True)),
                ('contenu', models.CharField(blank=True, max_length=1000, null=True)),
                ('theme_picture', models.ImageField(blank=True, null=True, upload_to='Theme_Picture')),
                ('formateur_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('formation_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ELearning.Formation')),
            ],
        ),
        migrations.AddField(
            model_name='courses',
            name='theme_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ELearning.Theme'),
        ),
    ]
