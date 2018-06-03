from django.shortcuts import render
from .forms import RegistrationCours
from django.contrib import messages
from ELearning import models,forms
from .models import Formation,Courses,Theme,Lessons,Exam
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets
from ELearning.models import Question, Exam
from ELearning.serializer import QuestionSerialzer, ExamSerializer
# Create your views here.
def index(request):
    return render(request, 'ELearning/index-3.html')

def index_1(request):
    return render(request, 'ELearning/index-1.html')

def index_2(request):
    return render(request, 'ELearning/index-2.html')

def about(request):
    context={
    'themes': Theme.objects.all().order_by('id'),}
    return render(request, 'ELearning/about.html', context)

def prof(request):
    context = {
        'themes': Theme.objects.all().order_by('id'), }
    return render(request, 'ELearning/formateur.html', context)

def dash(request):
    context = {
        'formateur': User.objects.all().order_by('id'),
    }
    return render(request,'index.html',context)


def formation_add(request,formateur_id):
    formations = models.Formation.objects.filter(formateur_id=formateur_id)
    formateur = models.User.objects.get(id=formateur_id)

    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        if libelle and Formation.objects.filter(libelle=libelle).exists():
            messages.info(request, "Cette formation existe déjà")
            return lister_formation(request,formateur_id)
    form_data = forms.RegistrationFormation(request.POST or None,request.FILES)

    if form_data.is_valid():
        formation = models.Formation()
        formation.libelle = form_data.cleaned_data['libelle']
        formation.description = form_data.cleaned_data['description']
        formation.objectifs=form_data.cleaned_data['objectifs']
        formation.date_creation = form_data.cleaned_data['date_creation']
        formation.formation_picture=form_data.cleaned_data['formation_picture']
        formation.formateur_id = formateur
        formation.save()

        messages.success(request, "Formation créé avec succées")
    context={
            'formations':formations,
             'formateurs':formateur,
              'form':form_data,

        }
    return render(request, 'ELearning/Formation.html', context)

def lister_formation(request,formateur_id):

    context = {
        'formations' : Formation.objects.filter(formateur_id=formateur_id),
         'formateurs' :models.User.objects.get(id=formateur_id)


    }
    return render(request, 'ELearning/liste_form.html', context)


def formation(request,id,formateur_id):
    context={
        'f':Formation.objects.get(id=id),
        'formateurs' : models.User.objects.get(id=formateur_id)
    }
    return render(request, 'ELearning/modifie_formation.html', context)



def modifier_form(request,id,formateur_id):
    objectFormation = Formation.objects.filter(id=id)

    t=request.GET.get('titreForm')
    de=request.GET.get('descripForm')
    o=request.GET.get('objecForm')
    d=request.GET.get('dateForm')
    i=request.GET.get('photoForm')


    for pg in objectFormation:

        pg.libelle=t
        pg.description=de
        pg.objectifs=o
        pg.date_creation=d
        pg.formation_picture='Formation_Picture/'+i

        pg.save()
        messages.success(request, "Ligne modifiée avec succées")


    return formation(request,id,formateur_id)

def supprimer_form(request,id,formateur_id):
    objetFormation = Formation.objects.get(id=id)


    objetFormation.delete()
    messages.success(request, "Ligne supprimée avec succées")
    return lister_formation(request,formateur_id)

def lister_theme(request,formateur_id):

    context = {
        'themes' : Theme.objects.filter(formateur_id=formateur_id),
        'formateurs': models.User.objects.get(id=formateur_id)

    }
    return render(request, 'ELearning/liste_theme.html', context)
def theme_add(request,formation_id,formateur_id):
    themes = models.Theme.objects.filter(formation_id=formation_id)
    formations = models.Formation.objects.get(id=formation_id)
    formateur = models.User.objects.get(id=formateur_id)
    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        if libelle and Theme.objects.filter(libelle=libelle).exists():
            messages.info(request, "Ce thème existe déjà")
            return lister_theme(request,formateur_id)


    form_data = forms.RegistrationTheme(request.POST or None,request.FILES)

    if form_data.is_valid():
        theme = models.Theme()
        theme.libelle = form_data.cleaned_data['libelle']
        theme.description = form_data.cleaned_data['description']
        theme.but=form_data.cleaned_data['but']
        theme.contenu=form_data.cleaned_data['contenu']
        theme.theme_picture=form_data.cleaned_data['theme_picture']
        theme.formation_id = formations
        theme.formateur_id=formateur
        theme.save()
        messages.success(request, "Thème créé avec succées")



    context={
            'formations':formations,
            'formateurs':formateur,
            'themes':themes,
            'form':form_data,

        }
    return render(request, 'ELearning/Theme.html', context)



def theme(request,id,formateur_id):
    context={
        't':Theme.objects.get(id=id),
        'formateurs' : models.User.objects.get(id=formateur_id)
    }
    return render(request, 'ELearning/modifie_theme.html', context)

def modifier_theme(request,id,formateur_id):
    objectTheme = Theme.objects.filter(id=id)
    t=request.GET.get('titreTheme')
    de=request.GET.get('descripTheme')
    b = request.GET.get('butTheme')
    c = request.GET.get('conTheme')
    i = request.GET.get('photoTheme')

    for pg in objectTheme:

        pg.libelle=t
        pg.description=de
        pg.but=b
        pg.contenu=c
        pg.theme_picture='Theme_Picture/'+i
        pg.save()
        messages.success(request, "Ligne modifiée avec succées")

    return theme(request, id, formateur_id)
def supprimer_theme(request,id,formateur_id):
    objetTheme = Theme.objects.get(id=id)


    objetTheme.delete()
    messages.success(request, "Ligne supprimée avec succées")
    return lister_theme(request,formateur_id)


def lister_cours_prof(request,formateur_id):

    context = {
        'Cours' : Courses.objects.filter(formateur_id=formateur_id),
        'formateurs': models.User.objects.get(id=formateur_id)
    }
    return render(request, 'ELearning/courses.html', context)

def cours_add(request,theme_id,formateur_id):
    courses = models.Courses.objects.filter(theme_id=theme_id)
    themes = models.Theme.objects.get(id=theme_id)
    formateur = models.User.objects.get(id=formateur_id)

    if request.method == 'POST':
        course_title = request.POST.get('course_title')
        video_url=request.POST.get('video_url')
        video_url=video_url.split("v=")
        video_url=video_url[1].split("&")
        video_url=video_url[0]
        lien="https://www.youtube.com/embed/"+video_url

        if course_title and Courses.objects.filter(course_title=course_title).exists():
            messages.info(request, "Ce cours existe déjà")
            return lister_cours_prof(request,formateur_id)


        form_data = RegistrationCours(request.POST or None,request.FILES)


        if form_data.is_valid():



         course = models.Courses()
         course.course_title = form_data.cleaned_data['course_title']
         course.course_price = form_data.cleaned_data['course_price']
         course.course_start = form_data.cleaned_data['course_start']
         course.course_expire = form_data.cleaned_data['course_expire']
         course.course_description=form_data.cleaned_data['course_description']
         course.course_resume = form_data.cleaned_data['course_resume']
         course.course_picture= form_data.cleaned_data['course_picture']
         course.video_url=lien
         course.video_name=form_data.cleaned_data['video_name']
         course.formateur_id=formateur
         course.theme_id=themes
         course.save()
         messages.success(request, "Cours ajouté avec succées")


    else:
        form_data = RegistrationCours()
    context={
              'cours':courses,
              'themes':themes,
              'form':form_data,
              'formateurs':formateur


        }
    return render(request, 'ELearning/add-listing.html', context)




def cours(request,id,formateur_id):
    context={
        'c':Courses.objects.get(id=id),
        'formateurs' : models.User.objects.get(id=formateur_id)
    }
    return render(request, 'ELearning/modifie_cours.html', context)
def modifier_cours(request,id,formateur_id):
    objectCours = Courses.objects.filter(id=id)
    t=request.GET.get('titreCours')
    p=request.GET.get('prixCours')
    dd = request.GET.get('dateDebutCours')
    df = request.GET.get('dateFinCours')
    r=request.GET.get('resumeCours')
    d=request.GET.get('descripCours')
    o=request.GET.get('objCours')

    for pg in objectCours:

        pg.course_title=t
        pg.course_price=p
        pg.course_start=dd
        pg.course_expire=df
        pg.course_resume=r
        pg.course_description=d
        pg.course_goal=o
        pg.save()
        messages.success(request, "Ligne modifiée avec succées")

    return cours(request, id, formateur_id)

def supprimer_cours(request,id,formateur_id):
    objetCours = Courses.objects.get(id=id)


    objetCours.delete()
    messages.success(request, "Ligne supprimée avec succées")
    return lister_cours_prof(request,formateur_id)

def lister_leçons(request,formateur_id):

    context = {
        'lessons' : Lessons.objects.filter(formateur_id=formateur_id),
        'formateurs': models.User.objects.get(id=formateur_id)
    }
    return render(request, 'ELearning/liste_leçons.html', context)

def leçon_add(request,course_id,formateur_id):
    lessons = models.Lessons.objects.filter(course_id=course_id)
    cours = models.Courses.objects.get(id=course_id)
    formateur = models.User.objects.get(id=formateur_id)
    if request.method == 'POST':
        lesson_title = request.POST.get('lesson_title')
        if lesson_title and Lessons.objects.filter(lesson_title=lesson_title).exists():
            messages.info(request, "Cette leçon existe déjà")
            return lister_leçons(request, formateur_id)

        form_data = forms.RegistrationLecon(request.POST or None,request.FILES)

        if form_data.is_valid():
         lesson = models.Lessons()
         lesson.lesson_title = form_data.cleaned_data['lesson_title']
         lesson.lesson_duration = form_data.cleaned_data['lesson_duration']
         lesson.lesson_file = form_data.cleaned_data['lesson_file']
         lesson.file_name = form_data.cleaned_data['file_name']
         lesson.lesson_description = form_data.cleaned_data['lesson_description']
         lesson.lesson_resume = form_data.cleaned_data['lesson_resume']
         lesson.lesson_goal = form_data.cleaned_data['lesson_goal']
         lesson.lesson_video = form_data.cleaned_data['lesson_video']
         lesson.lesson_video_name=form_data.cleaned_data['lesson_video_name']
         lesson.file_format=form_data.cleaned_data['file_format']
         lesson.lesson_video_format = form_data.cleaned_data['lesson_video_format']
         lesson.course_id=cours
         lesson.formateur_id=formateur
         lesson.save()
         messages.success(request, ('Leçon ajoutée avec succès'))

    else:
        form_data=forms.RegistrationLecon()
    context={
              'cours':cours,
              'formateurs':formateur,
             'lessons':lessons,
              'form':form_data,

        }
    return render(request, 'ELearning/add-leçon.html', context)

def leçons(request,id,formateur_id):
    context={
        'l':Lessons.objects.get(id=id),
        'formateurs' : models.User.objects.get(id=formateur_id)
    }
    return render(request, 'ELearning/modifie_leçon.html', context)

def modifier_leçon(request,id,formateur_id):
    objectLeçons = Lessons.objects.filter(id=id)
    t=request.GET.get('titreLeçon')
    dd = request.GET.get('dureeLeçon')
    r=request.GET.get('resumeLeçon')
    d=request.GET.get('descripLeçon')
    o=request.GET.get('objLeçon')

    for pg in objectLeçons:

        pg.lesson_title=t
        pg.lesson_duration=dd
        pg.lesson_resume=r
        pg.lesson_description=d
        pg.lesson_goal=o
        pg.save()
        messages.success(request, "Ligne modifiée avec succées")

    return leçons(request, id, formateur_id)
def supprimer_leçon(request,id,formateur_id):
    objetLeçon = Lessons.objects.get(id=id)


    objetLeçon.delete()
    messages.success(request, "Ligne supprimée avec succées")
    return lister_leçons(request,formateur_id)
def lister_cours(request):

    context = {
        'cours' : Courses.objects.all().order_by('id'),
        'themes': Theme.objects.all().order_by('id'),
    }
    return render(request, 'ELearning/index-3.html', context)

def lister_cours_1(request):

    context = {
        'cours' : Courses.objects.all().order_by('id'),
        'themes': Theme.objects.all().order_by('id'),
    }
    return render(request, 'ELearning/index-1.html', context)

def lister_cours_2(request):

    context = {
        'themes':Theme.objects.all().order_by('id'),
        'cours' : Courses.objects.all().order_by('id')
    }
    return render(request, 'ELearning/index-2.html', context)

def lister_cours_3(request,theme_id):

    context = {
        'cours' : Courses.objects.filter(theme_id=theme_id),
        'themes': Theme.objects.all().order_by('id'),

    }
    return render(request, 'ELearning/courses-list.html', context)


def detail_cours(request,id):

    context ={
        'c':Courses.objects.get(id=id),
        'l': Lessons.objects.filter(course_id=id),
        'themes': Theme.objects.all().order_by('id'),

    }
    return render(request, 'ELearning/course-detail.html', context)

def lister_cours_4(request):

    context = {
        'cours' : Courses.objects.all(),
        'themes': Theme.objects.all().order_by('id'),
    }
    return render(request, 'ELearning/courses-list.html', context)



