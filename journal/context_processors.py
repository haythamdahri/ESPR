from django.db.models import Count

from journal.models import Category, Video, News, Comment, Journalist, Supervisor, Tag
from journal.forms import NewsletterForm
# import requests


def global_var(request):
    # Weather
    # url = 'http://api.openweathermap.org/data/2.5/weather?q=Rabat&units=metric&appid=91d3852842a30e80531df63b131af6d4'
    # r = requests.get(url).json()
    # weather = {
    #    'city': 'Casablanca',
    #    'temperature': r['main']['temp'],
    #    'description': r['weather'][0]['description'],
    #    'icon': r['weather'][0]['icon'],
    # }

    # TOP_READ
    video_id = Video.objects.filter(active=True, approved=True).values_list('id', flat=True)
    top_read = News.objects.filter(active=True, approved=True).exclude(id__in=video_id).order_by('-view_number', 'id')[:7]

    # TOP COMMENTS
    top_comment = Comment.objects.all().order_by('-number_like', '-date_publication')[:4]

    # TOP TAGS
    top_tags = Tag.objects.all().annotate(count=Count('news')).order_by('-count', '-id')[:11]

    # LAST ADDED ARTICLE FOR 404 PAGE
    last_article = News.objects.all().exclude(id__in=video_id).filter(active=True, approved=True).order_by('-id')[:6]

    # IS JOURNALIST
    check = False
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            check = True

    # IS SUPERVISOR
    check_s = False
    if request.user.is_authenticated:
        user = request.user
        if user.email in Supervisor.email_list():
            check_s = True

    context = {
        'cats': Category.objects.all().order_by('id'),
        # 'weather': weather,
        'topRead': top_read,
        'topComment': top_comment,
        'top_tags': top_tags,
        'newsletterForm': NewsletterForm(),
        'is_journalist': check,
        'is_supervisor': check_s,
        'last_article': last_article
    }

    return context
