import re
from operator import attrgetter

from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Value, CharField
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.views.decorators.http import require_POST

from datetime import timedelta, datetime
from itertools import chain

from .models import Category, Image, News, Video, Comment, Tag, Answer, Newsletter, JoinMessage, \
    CommentFilter, Journalist, ImageNews, SignalComment, SignalAnswer, ContactMessage, Supervisor
from .forms import ReplyForm, SignalForm, JournalistProfileForm, JournalistAddTagForm, \
    JournalistImageUploadForm, JournalistImageImport, JournalistImagePrimaryImport, JournalistCreateArticle, \
    JournalistCreateVideo, ContactForm, JoinForm

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


#####################################################
#            PUBLIC PAGE REQUEST VIEW               #
#####################################################


# ## HOME PAGE ## #
def index(request):
    # VIDEO ID
    video_id = Video.objects.all().values_list('id', flat=True)

    # CAROUSEL
    cat = Category.objects.get(id=1)
    new_car = News.objects.all().exclude(id__in=video_id).filter(active=True, category=cat, approved=True).order_by(
        '-id')[:5]

    # TRENDING NOW
    trending_now = News.objects.all().exclude(id__in=video_id).filter(active=True, category=cat,
                                                                      approved=True).order_by('-id')[:10]

    # TRENDING : Get last week post ordering by view number and id
    # one_week_ago = datetime.today() - timedelta(days=7)
    one_week_ago = datetime.today() - timedelta(days=90)
    #   T All
    trending = News.objects.filter(date_publication__gte=one_week_ago).filter(active=True, approved=True).exclude(
        id__in=video_id).order_by('-view_number', '-id')[:10]
    #   T1
    t_category = Category.objects.get(id=2)
    t1 = News.objects.filter(category=t_category, date_publication__gte=one_week_ago).filter(
        active=True, approved=True).exclude(id__in=video_id).order_by('-view_number')[:8]
    #   T2
    t_category = Category.objects.get(id=3)
    t2 = News.objects.filter(category=t_category, date_publication__gte=one_week_ago, active=True,
                             approved=True).exclude(
        id__in=video_id).order_by('-view_number')[:8]
    #   T3
    t_category = Category.objects.get(id=4)
    t3 = News.objects.filter(category=t_category, date_publication__gte=one_week_ago, active=True,
                             approved=True).exclude(
        id__in=video_id).order_by('-view_number')[:8]
    #   T4
    t_category = Category.objects.get(id=5)
    t4 = News.objects.filter(category=t_category, date_publication__gte=one_week_ago, active=True,
                             approved=True).exclude(
        id__in=video_id).order_by('-view_number')[:8]
    #   T5
    t_category = Category.objects.get(id=8)
    t5 = News.objects.filter(category=t_category, date_publication__gte=one_week_ago, active=True,
                             approved=True).exclude(id__in=video_id).order_by('-view_number')[:8]

    # LAST ADD
    #   col_1
    l_category = Category.objects.get(id=2)
    last_inter = News.objects.filter(category=l_category, active=True, approved=True).exclude(
        id__in=video_id).order_by('-id')[:3]
    #   col_2
    l_category = Category.objects.get(id=3)
    last_eco = News.objects.filter(category=l_category, active=True, approved=True).exclude(
        id__in=video_id).order_by('-id')[:3]
    #   col_3
    l_category = Category.objects.get(id=8)
    last_news = News.objects.filter(category=l_category, active=True, approved=True).exclude(
        id__in=video_id).order_by('-id')[:5]

    # TOP VIDEO
    top_video = Video.objects.filter(active=True, approved=True).order_by('-view_number', '-id')[:5]

    # LAST ADD
    #   LAST ADD NEWS
    last_add = News.objects.all().exclude(id__in=video_id).filter(active=True, approved=True).order_by(
        '-date_publication')
    page = request.GET.get('page', 1)
    paginator = Paginator(last_add, 4)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    #   LAST ADD VIDEO
    last_add_video = Video.objects.filter(active=True).order_by('-date_publication')[:4]
    #   LAST ADD COMMENT
    last_add_comment = Comment.objects.all().order_by('-date_publication')[:3]
    #   LAST ADD IMAGE
    last_add_image = Image.objects.all().order_by('-date_publication')[:6]

    context = {
        'newscar': new_car,
        'trending_now': trending_now,
        'tendance': trending,
        't1': t1,
        't2': t2,
        't3': t3,
        't4': t4,
        't5': t5,
        'lastEco': last_eco,
        'lastInter': last_inter,
        'lastNews': last_news,
        'topVideo': top_video,
        'lastAdd': articles,
        'lastAddVideo': last_add_video,
        'lastAddComment': last_add_comment,
        'lastAddImage': last_add_image,
    }
    return render(request, 'journal/index.html', context)


# ## ABOUT PAGE ## #
def about(request):
    nbr_articles = News.objects.all().count()
    nbr_comments = Comment.objects.all().count() + Answer.objects.all().count()
    nbr_views = 0
    for n in News.objects.all():
        nbr_views += n.view_number

    context = {
        'nbr_articles': nbr_articles,
        'nbr_comments': nbr_comments,
        'nbr_views': nbr_views
    }

    return render(request, 'journal/about.html', context)


# ## CONTACT PAGE ## #
def contact(request):
    contact_form = ContactForm()
    created = False

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            cd = contact_form.cleaned_data
            ContactMessage.objects.create(
                name=cd['email'],
                email=cd['email'],
                website=cd['website'],
                message=cd['message']
            )
            created = True
        else:
            contact_form.fields['email'].widget.attrs['hidden'] = 'true'
            contact_form.fields['email'].widget.attrs['class'] = ''
            contact_form.fields['name'].widget.attrs['hidden'] = 'true'
            contact_form.fields['name'].widget.attrs['class'] = ''

    if request.user.is_authenticated:
        contact_form.fields['email'].widget.attrs['hidden'] = 'true'
        contact_form.fields['email'].widget.attrs['class'] = ''
        contact_form.fields['email'].widget.attrs['value'] = request.user.email
        contact_form.fields['name'].widget.attrs['hidden'] = 'true'
        contact_form.fields['name'].widget.attrs['class'] = ''
        contact_form.fields['name'].widget.attrs['value'] = request.user

    context = {
        'form': contact_form,
        'created': created
    }
    return render(request, 'journal/contact.html', context)


# ## PRIVACY PAGE ## #
def privacy(request):
    return render(request, 'journal/privacy.html')


# ## SELECTED ARTICLE SHOW PAGE ## #
def article_show(request, category_name, post):
    # TRENDING NOW
    video_id = Video.objects.all().values_list('id', flat=True)
    cat = get_object_or_404(Category, name=category_name)
    trending_now = News.objects.all().exclude(id__in=video_id).filter(active=True, category=cat,
                                                                      approved=True).order_by('-id')[:10]

    # GET INFORMATION
    article = get_object_or_404(News, id=post)
    if article.active is False:
        return redirect('index')
    if article.category != cat:
        return redirect('index')
    if not article.approved:
        if not request.user.is_authenticated:
            raise Http404
        else:
            if not is_supervisor(request):
                raise Http404
    article.add_view()

    # ARTICLE TAGS
    tags = Tag.objects.filter(news=article)

    # MORE FROM AUTHOR
    more_article = News.objects.filter(journalist=article.journalist, category=article.category, active=True,
                                       approved=True).exclude(
        id=article.id).order_by('-date_publication')[:4]
    if more_article.count() < 4:
        article_id = more_article.values_list('id', flat=True)
        number = 4 - more_article.count()
        added_article = News.objects.filter(journalist=article.journalist, active=True, approved=True).exclude(
            id=article.id).exclude(
            id__in=article_id)
        added_article = added_article.order_by('-date_publication')[:number]
        more_article = list(chain(more_article, added_article))

    # DYNAMIC COMMENT FORM
    reply_form = ReplyForm()
    signal_form = SignalForm()
    if request.user.is_authenticated:
        reply_form.fields['email'].widget.attrs['hidden'] = 'true'
        reply_form.fields['email'].widget.attrs['value'] = request.user.email
        reply_form.fields['name'].widget.attrs['hidden'] = 'true'
        reply_form.fields['name'].widget.attrs['value'] = request.user
        signal_form.fields['email'].widget.attrs['hidden'] = 'true'
        signal_form.fields['email'].widget.attrs['value'] = request.user.email

    # CHECK IF USER CONNECTED AND IF HE IS THE JOURNALIST OF THIS ARTICLE
    self_article = False
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            j = get_object_or_404(Journalist, email=user.email)
            if article.journalist == j:
                self_article = True

    context = {
        'article': article,
        'signal_form': signal_form,
        'tags': tags,
        'reply_form': reply_form,
        'more_article': more_article,
        'navActive': '#nav' + article.category.name,
        'self_article': self_article,
        'trending_now': trending_now
    }
    return render(request, 'journal/post.html', context)


# ## ARTICLE CATEGORY PAGE ## #
def category(request, category_name):
    # VIDEO ID
    video_id = Video.objects.all().values_list('id', flat=True)

    cat = get_object_or_404(Category, name=category_name)

    news_filter = request.GET.get('filter', '-date_publication')

    news = News.objects.filter(category=cat, active=True, approved=True).annotate(
        comment_number=Count('comment')).exclude(
        id__in=video_id)

    # LAST FIVE
    last_five = news.order_by(news_filter, '-id')[:5]

    # OTHER ARTICLE
    last_five_id = last_five.values_list('id', flat=True)
    # other = news.exclude(id__in=lastFiveId).order_by(news_filter)
    # for test
    other = News.objects.filter(active=True, approved=True).exclude(id__in=last_five_id).exclude(
        id__in=video_id).order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(other, 8)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    context = {
        'last_five': last_five,
        'category': cat,
        'articles': articles,
        'navActive': '#nav' + cat.name,
        'filter': news_filter
    }
    return render(request, 'journal/category.html', context)


# ## TAG PAGE ## #
def tag(request, tag_name):
    selected_tag = get_object_or_404(Tag, name=tag_name)

    # VIDEO ID
    video_id = Video.objects.all().values_list('id', flat=True)

    news_filter = request.GET.get('filter', '-date_publication')

    news = News.objects.filter(tag=selected_tag, active=True, approved=True).annotate(
        comment_number=Count('comment')).exclude(
        id__in=video_id)

    count = news.count()

    # LAST FIVE
    last_five = news.order_by(news_filter, '-id')[:5]

    # OTHER ARTICLE
    last_five_id = last_five.values_list('id', flat=True)
    # other = news.exclude(id__in=lastFiveId).order_by(news_filter)
    # for test
    other = News.objects.filter(active=True, approved=True).exclude(id__in=last_five_id).exclude(
        id__in=video_id).order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(other, 8)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    context = {
        'tag': selected_tag,
        'last_five': last_five,
        'articles': articles,
        'filter': news_filter,
        'count': count
    }

    return render(request, 'journal/tag.html', context)


# ## LAST ADDED ARTICLE PAGE ## #
def last_articles(request):
    # VIDEO ID
    video_id = Video.objects.all().values_list('id', flat=True)

    # FILTER
    news_filter = request.GET.get('filter', '-date_publication')
    news = News.objects.filter(active=True, approved=True).annotate(comment_number=Count('comment')).exclude(
        id__in=video_id)

    # ARTICLES
    articles = news.order_by(news_filter)
    page = request.GET.get('page', 1)
    paginator = Paginator(articles, 15)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    context = {
        'articles': articles,
        'filter': news_filter
    }
    return render(request, 'journal/lastArticles.html', context)


# ## AUTHOR PAGE ## #
def author(request, selected_author_id):
    # AUTHOR
    aut = get_object_or_404(Journalist, id=selected_author_id)

    # COMMENT NUMBER
    number = Comment.objects.filter(email=aut.email).count()

    # ARTICLES
    video_id = Video.objects.all().values_list('id', flat=True)
    articles = aut.news_set.filter(active=True, approved=True).order_by('-date_publication').exclude(id__in=video_id)

    for a in articles:
        if isinstance(a, Video):
            print('Video')

    page = request.GET.get('page', 1)
    paginator = Paginator(articles, 14)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    # OTHER AUTHOR
    authors = Journalist.objects.annotate(news_count=Count('news')).order_by('-news_count')[:5]

    context = {
        'author': aut,
        'articles': articles,
        'comment_number': number,
        'authors': authors

    }
    return render(request, 'journal/author.html', context)


# ## ALL VIDEO PAGE ## #
def videos(request):
    # VIDEO SELECTION
    video_selection = Video.objects.filter(active=True, approved=True, team_selection=True).order_by(
        '-date_publication')[:5]

    # OTHER VIDEO
    other_video = Video.objects.filter(active=True, approved=True).order_by('-date_publication')
    page = request.GET.get('page', 1)
    paginator = Paginator(other_video, 10)
    try:
        other_video = paginator.page(page)
    except PageNotAnInteger:
        other_video = paginator.page(1)
    except EmptyPage:
        other_video = paginator.page(paginator.num_pages)

    context = {
        'video_selection': video_selection,
        'other_video': other_video
    }

    return render(request, 'journal/video.html', context)


# ## SELECTED VIDEO SHOW PAGE ## #
def video_show(request, selected_video_id):
    # VIDEO
    selected_video = get_object_or_404(Video, id=selected_video_id)
    selected_video.add_view()

    # VIDEO TAGS
    tags = Tag.objects.filter(news=selected_video)

    # MORE FROM AUTHOR
    more_video = Video.objects.filter(active=True, approved=True, journalist=selected_video.journalist,
                                      category=selected_video.category).exclude(
        id=selected_video.id).order_by('-date_publication')[:4]
    if more_video.count() < 4:
        video_id = more_video.values_list('id', flat=True)
        number = 4 - more_video.count()
        added_video = Video.objects.filter(active=True, approved=True, journalist=selected_video.journalist).exclude(
            id__in=video_id).order_by('-date_publication')[:number]
        more_video = list(chain(more_video, added_video))

    # LAST ADD VIDEO
    last_add_video = Video.objects.filter(active=True, approved=True).order_by('-date_publication')[:4]

    # DYNAMIC COMMENT FORM
    reply_form = ReplyForm()
    signal_form = SignalForm()
    if request.user.is_authenticated:
        reply_form.fields['email'].widget.attrs['hidden'] = 'true'
        reply_form.fields['email'].widget.attrs['value'] = request.user.email
        reply_form.fields['name'].widget.attrs['hidden'] = 'true'
        reply_form.fields['name'].widget.attrs['value'] = request.user
        signal_form.fields['email'].widget.attrs['hidden'] = 'true'
        signal_form.fields['email'].widget.attrs['value'] = request.user.email

    # CHECK IF USER CONNECTED AND IF HE IS THE JOURNALIST OF THIS ARTICLE
    self_video = False
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            j = get_object_or_404(Journalist, email=user.email)
            if selected_video.journalist == j:
                self_video = True

    context = {
        'video': selected_video,
        'tags': tags,
        'more_video': more_video,
        'lastAddVideo': last_add_video,
        'signalForm': signal_form,
        'replyForm': reply_form,
        'self_video': self_video
    }

    return render(request, 'journal/video_view.html', context)


# ## NEWS SEARCH PAGE ## #
def search(request):
    qs = News.objects.filter(active=True, approved=True)
    keywords = request.GET.get('q')
    if keywords:
        query = SearchQuery(keywords)
        title_vector = SearchVector('title', weight='A')
        resume_vector = SearchVector('resume', weight='B')
        content_vector = SearchVector('content', weight='C')
        vectors = title_vector + content_vector + resume_vector
        qs = qs.annotate(search=vectors).filter(search=query)
        qs = qs.annotate(rank=SearchRank(vectors, query)).order_by('-rank', '-view_number')
    else:
        return redirect('index')

    count = qs.all().count

    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 7)
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)

    context = {
        'article_result': qs,
        'search': keywords,
        'count': count
    }

    return render(request, 'journal/search.html', context)


def article_print(request, article_id):
    if article_id in Video.objects.all().values_list('id', flat=True):
        return redirect('index')
    article = get_object_or_404(News, id=article_id)
    if article.active is False:
        return redirect('index')
    if not article.approved:
        if not request.user.is_authenticated:
            raise Http404
        else:
            if not is_supervisor(request):
                raise Http404

    return render(request, 'journal/print_article.html', {'article': article})


def join_us(request):
    form = JoinForm()
    sended = False
    if request.method == 'POST':
        form = JoinForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            JoinMessage.objects.create(
                email=cd['email'],
                first_name=cd['first_name'],
                last_name=cd['last_name'],
                website=cd['website'],
                message=cd['message']
            )
            sended = True
        else:
            form.fields['email'].widget.attrs['hidden'] = 'true'
            form.fields['first_name'].widget.attrs['hidden'] = 'true'
            form.fields['last_name'].widget.attrs['hidden'] = 'true'
            form.fields['email'].widget.attrs['class'] = ''
            form.fields['first_name'].widget.attrs['class'] = ''
            form.fields['last_name'].widget.attrs['class'] = ''
    else:
        if request.user.is_authenticated:
            user = request.user
            form = JoinForm(initial={
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            })
            form.fields['email'].widget.attrs['hidden'] = 'true'
            form.fields['first_name'].widget.attrs['hidden'] = 'true'
            form.fields['last_name'].widget.attrs['hidden'] = 'true'
            form.fields['email'].widget.attrs['class'] = ''
            form.fields['first_name'].widget.attrs['class'] = ''
            form.fields['last_name'].widget.attrs['class'] = ''

    context = {
        'form': form,
        'sended': sended
    }
    return render(request, 'journal/join_us.html', context)


#####################################################
#               AJAX REQUEST VIEW                   #
#####################################################


# ## NEWSLETTER SUBSCRIBE FUNCTION ## #
def subscribe(request):
    email = request.GET.get('email', None)
    if email is None:
        return redirect('index')
    data = {
        'is_taken': Newsletter.objects.filter(email=email).exists()
    }
    if data['is_taken']:
        data['message'] = 'Vous êtes déjà inscrit'
    else:
        registration = Newsletter(email=email)
        registration.save()
        data['message'] = 'Inscription effectué'
    return JsonResponse(data)


# ## COMMENT ARTICLE FUNCTION ## #
def find_word(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def comment(request, post):
    name = request.GET.get('name', None)
    email = request.GET.get('email', None)
    message = request.GET.get('message', None)

    comment_verify = True
    if(name is None) or (name == ''):
        comment_verify = False
    if (email is None) or (email == ''):
        comment_verify = False
    if (message is None) or (message == ''):
        comment_verify = False
    if not comment_verify:
        message = 'Veuillez entrer des données valides'
        data = {
            'message': message,
            'accept': comment_verify
        }
        return JsonResponse(data)

    for c_filter in CommentFilter.objects.all():
        # if c_filter.word in str(message):
        if find_word(c_filter)(str(message)):
            message = 'Commentaire inapproprié, veuillez vérifier les mots utilisés dans votre commentaire'
            comment_verify = False
            print(str(comment_verify))
            data = {
                'message': message,
                'accept': comment_verify
            }
            return JsonResponse(data)

    c = News.objects.get(id=post).comment_set.create(full_name=name, email=email, message=message)
    data = {
        'accept': comment_verify,
        'message': 'Commentaire ajouté',
        'name': name,
        'comment': message,
        'date': c.date_publication
    }
    return JsonResponse(data)


# ## LIKE AND DISLIKE COMMENT FUNCTION ## #
def like(request, selected_comment):
    comment_type = request.GET.get('type', None)
    method = request.GET.get('method', None)
    c = Comment()
    if comment_type == 'answer':
        c = Answer.objects.get(id=selected_comment)
    elif comment_type == 'comment':
        c = Comment.objects.get(id=selected_comment)
    if method == 'like':
        c.like()
    elif method == 'dislike':
        c.dislike()
    data = {
        'nombre': str(c.number_like),
        'id': '#numberLike' + str(c.id),
        'div': '#divComment' + str(c.id)
    }
    return JsonResponse(data)


# ## SIGNAL COMMENT AND REPLY FUNCTION ## #
def signal(request, selected_comment):
    comment_type = request.GET.get('type', None)
    email = request.GET.get('email', None)
    motif = request.GET.get('motif', None)
    if comment_type == 'answer':
        Answer.objects.get(id=selected_comment).signalanswer_set.create(email=email, cause=motif)
    elif comment_type == 'comment':
        Comment.objects.get(id=selected_comment).signalcomment_set.create(email=email, cause=motif)
    data = {
        'message': 'Merci pour votre avertissement, nous allons consulter votre signal le plus tot possible',
        'formButton': '#formButtonSignaler' + str(selected_comment),
        'formSignaler': '#signalForm' + str(selected_comment),
        'paragraphe': '#messageSignal' + str(selected_comment)
    }
    return JsonResponse(data)


# ## COMMENT REPLY FUNCTION ## #
def reply(request, selected_comment):
    email = request.GET.get('email', None)
    name = request.GET.get('name', None)
    message = request.GET.get('message', None)

    comment_verify = True
    for c_filter in CommentFilter.objects.all():
        if c_filter.word in str(message):
            message = 'Réponse inapproprié, veuillez vérifier les mots utilisés dans votre réponse'
            comment_verify = False
            print(str(comment_verify))
            data = {
                'message': message,
                'accept': comment_verify
            }
            return JsonResponse(data)

    Comment.objects.get(id=selected_comment).answer_set.create(email=email, full_name=name, message=message)
    data = {
        'accept': comment_verify,
        # 'formRepondre': '#repondreForm' + str(selected_comment), # For AJAX
        # 'formButtonRepondre': '#formButtonRepondre' + str(selected_comment) # For AJAX
    }
    return JsonResponse(data)


#####################################################
#            JOURNALIST MANAGEMENT VIEW             #
#####################################################

# ## JOURNALIST HOME PAGE ## #
def journalist(request):
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # VIDEO ID
            video_id = Video.objects.all().values_list('id', flat=True)

            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)

            # STATISTIC
            # ## COMMENT COUNT
            number_comment = 0

            # ## NEWS COUNT
            # ## NEWS VIEW SUM
            number_news = 0
            news_views_sum = 0
            for n in News.objects.exclude(id__in=video_id).filter(journalist=j, approved=True, active=True):
                number_news += 1
                news_views_sum += n.view_number
                number_comment += n.comment_set.count()

            # ## VIDEO COUNT
            # ## VIDEO VIEW SUM
            number_video = 0
            video_views_sum = 0
            for v in Video.objects.filter(journalist=j, active=True, approved=True):
                number_video += 1
                video_views_sum += v.view_number
                number_comment += v.comment_set.count()

            # ## SELF COMMENT COUNT
            self_comment_count = Comment.objects.filter(email=j.email).count()

            statistic = {
                'number_comment': number_comment,
                'number_news': number_news,
                'news_views_sum': news_views_sum,
                'number_video': number_video,
                'video_views_sum': video_views_sum,
                'self_comment_count': self_comment_count
            }

            # TOP ARTICLE
            top_article = News.objects.exclude(id__in=video_id).filter(journalist=j, active=True,
                                                                       approved=True).order_by(
                '-view_number').first()

            # TOP VIDEO
            top_video = Video.objects.filter(journalist=j, active=True, approved=True).order_by('-view_number').first()

            context = {
                'journalist': j,
                'statistic': statistic,
                'top_article': top_article,
                'top_video': top_video
            }
            return render(request, 'journal/journalist/journalist.html', context)

    return redirect('index')


# ## JOURNALIST PROFILE PAGE ## #
def journalist_profile(request):
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():

            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)

            form = JournalistProfileForm()
            message = 'null'
            message_image = 'null'

            if request.method == 'POST':

                if request.POST['method'] == 'image':
                    form_image = JournalistImageUploadForm(request.POST, request.FILES)
                    if form_image.is_valid():
                        img = Image(image=form_image.cleaned_data['image'], description='Profile image')
                        img.save()
                        j.profile_picture = img
                        j.save()
                        message_image = 'success'
                    else:
                        message_image = 'failed'

                else:
                    form = JournalistProfileForm(request.POST)

                    if form.is_valid():
                        cd = form.cleaned_data
                        user.username = cd['username']
                        user.save()

                        j.first_name = cd['first_name']
                        j.last_name = cd['last_name']
                        j.tel = cd['telephone']
                        j.link = cd['website']
                        j.facebook = cd['facebook']
                        j.twitter = cd['twitter']
                        j.instagram = cd['instagram']
                        j.youtube = cd['youtube']
                        j.google = cd['google_plus']
                        j.linkedin = cd['linkedin']
                        j.description = cd['description']
                        j.save()

                        message = 'Informations modifiées avec succès'

            # INFO
            number_comment = 0
            sum_views = 0
            for n in News.objects.filter(journalist=j, active=True, approved=True):
                sum_views += n.view_number
                number_comment += n.comment_set.count()

            # FORM
            form.fields['username'].widget.attrs['value'] = user.username
            form.fields['telephone'].widget.attrs['value'] = j.tel
            form.fields['first_name'].widget.attrs['value'] = j.first_name
            form.fields['last_name'].widget.attrs['value'] = j.last_name
            form.fields['website'].widget.attrs['value'] = j.link
            form.fields['facebook'].widget.attrs['value'] = j.facebook
            form.fields['twitter'].widget.attrs['value'] = j.twitter
            form.fields['instagram'].widget.attrs['value'] = j.instagram
            form.fields['youtube'].widget.attrs['value'] = j.youtube
            form.fields['google_plus'].widget.attrs['value'] = j.google
            form.fields['linkedin'].widget.attrs['value'] = j.linkedin

            context = {
                'journalist': j,
                'form': form,
                'sum_views': sum_views,
                'number_comment': number_comment,
                'message': message,
                'form_image': JournalistImageUploadForm,
                'message_image': message_image
            }
            return render(request, 'journal/journalist/journalist-profile.html', context)

    return redirect('index')


# ## JOURNALIST ARTICLES PAGE ## #
def journalist_articles(request):
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)

            if request.method == 'POST':
                article_id = request.POST['article']
                article = get_object_or_404(News, id=article_id)
                if article.journalist == j:
                    article.active = False
                    article.save()

            # JOURNALIST ARTICLES
            video_id = Video.objects.all().values_list('id', flat=True)
            j_articles = j.news_set.filter(active=True, approved=True).exclude(id__in=video_id).order_by(
                '-date_publication')

            # SEARCH
            search_get = False
            keywords = request.GET.get('q')
            if keywords:
                search_get = True
                query = SearchQuery(keywords)
                title_vector = SearchVector('title', weight='A')
                resume_vector = SearchVector('resume', weight='B')
                content_vector = SearchVector('content', weight='C')
                vectors = title_vector + content_vector + resume_vector
                j_articles = j_articles.annotate(search=vectors).filter(search=query)
                j_articles = j_articles.annotate(rank=SearchRank(vectors, query)).order_by('-rank', '-view_number')

            count = j_articles.count()

            # PAGINATOR
            page = request.GET.get('page', 1)
            paginator = Paginator(j_articles, 20)
            try:
                j_articles = paginator.page(page)
            except PageNotAnInteger:
                j_articles = paginator.page(1)
            except EmptyPage:
                j_articles = paginator.page(paginator.num_pages)

            # CHECK IF REDIRECT FROM CREATE ARTICLE
            created = request.session.get('created', '0')
            if created == '1':
                del request.session['created']

            # CHECK IF REDIRECT FROM CREATE UPDATE
            updated = request.session.get('updated', '0')
            if updated == '1':
                del request.session['updated']

            context = {
                'journalist': j,
                'count': count,
                'articles': j_articles,
                'search': search_get,
                'keywords': keywords,
                'created': created,
                'updated': updated
            }

            return render(request, 'journal/journalist/journalist_articles.html', context)

    return redirect('index')


# ## JOURNALIST CREATE ARTICLE PAGE ## #
def journalist_create_article(request):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY ARTICLE OR CREATE NEW ONE
    article_id = request.session.get('article', None)
    has_image = 0
    if article_id is None:
        article = News.objects.create(title='Session Article', journalist=j, active=False)
        request.session['article'] = article.id
    else:
        article = News.objects.get(id=article_id)
        if article.primary_image is not None:
            has_image = 1

    form = JournalistCreateArticle()

    # CREATING ARTICLE
    if request.method == 'POST':
        if article.primary_image is None:
            has_image = 0
        else:
            form = JournalistCreateArticle(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                article.title = cd['title']
                article.small_title = cd['small_title']
                article.category = get_object_or_404(Category, id=cd['category'])
                article.resume = cd['resume']
                article.content = cd['content']
                if cd['comment_enable'] == 'no':
                    article.comment_enable = False
                if cd['share_enable'] == 'no':
                    article.share_enable = False
                tags = request.POST.getlist('tags')
                for t in tags:
                    article.tag.add(get_object_or_404(Tag, id=t))
                article.active = True
                article.save()

                del request.session['article']
                request.session['created'] = '1'

                return redirect('journalist_articles')

    photos_list = ImageNews.objects.filter(article=article)
    context = {
        'tags': Tag.objects.all().order_by('name'),
        'photos': photos_list,
        'form': form,
        'has_image': has_image,
        'form_tag': JournalistAddTagForm,
        'image': article.primary_image
    }
    return render(request, 'journal/journalist/journalist_add_article.html', context)


# ## JOURNALIST CANCEL CREATE ARTICLE REDIRECT ## #
def journalist_cancel_article(request):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY ARTICLE AND DELETE IT
    article_id = request.session.get('article', None)
    if article_id is not None:
        article = News.objects.get(id=article_id)
        if article.journalist == j:
            ImageNews.objects.filter(article=article).delete()
            article.delete()
            del request.session['article']

    return redirect('journalist_articles')


# ## JOURNALIST UPDATE ARTICLE PAGE ## #
def journalist_update_article(request, article_id):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET ARTICLE
    article = get_object_or_404(News, id=article_id, active=True)
    if article.journalist != j:
        return redirect('journalist_articles')

    # UPDATING ARTICLE
    if request.method == 'POST':
        form = JournalistCreateArticle(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            article.title = cd['title']
            article.small_title = cd['small_title']
            article.category = get_object_or_404(Category, id=cd['category'])
            article.resume = cd['resume']
            article.content = cd['content']
            if cd['comment_enable'] == 'no':
                article.comment_enable = False
            else:
                article.comment_enable = True
            if cd['share_enable'] == 'no':
                article.share_enable = False
            else:
                article.share_enable = True
            tags = request.POST.getlist('tags')
            for t in tags:
                article.tag.add(get_object_or_404(Tag, id=t))
            article.active = True
            article.approved = False
            article.save()

            request.session['updated'] = '1'

            return redirect('journalist_articles')

    else:
        form = JournalistCreateArticle(initial={
            'title': article.title,
            'small_title': article.small_title,
            'resume': article.resume,
            'content': article.content
        })

    context = {
        'article': article,
        'tags': Tag.objects.all().order_by('name'),
        'selected_tags': Tag.objects.filter(news=article),
        'form': form,
        'form_tag': JournalistAddTagForm
    }

    return render(request, 'journal/journalist/journalist_update_article.html', context)


def journalist_video(request):
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)

            if request.method == 'POST':
                video_id = request.POST['video']
                video = get_object_or_404(Video, id=video_id)
                if video.journalist == j:
                    video.active = False
                    video.save()

            # JOURNALIST VIDEOS
            j_videos = Video.objects.filter(active=True, approved=True, journalist=j).order_by('-date_publication')

            # SEARCH
            search_get = False
            keywords = request.GET.get('q')
            if keywords:
                search_get = True
                query = SearchQuery(keywords)
                title_vector = SearchVector('title', weight='A')
                resume_vector = SearchVector('resume', weight='B')
                content_vector = SearchVector('content', weight='C')
                vectors = title_vector + content_vector + resume_vector
                j_videos = j_videos.annotate(search=vectors).filter(search=query)
                j_videos = j_videos.annotate(rank=SearchRank(vectors, query)).order_by('-rank', '-view_number')

            count = j_videos.count()

            # PAGINATOR
            page = request.GET.get('page', 1)
            paginator = Paginator(j_videos, 20)
            try:
                j_videos = paginator.page(page)
            except PageNotAnInteger:
                j_videos = paginator.page(1)
            except EmptyPage:
                j_videos = paginator.page(paginator.num_pages)

            # CHECK IF REDIRECT FROM CREATE VIDEO
            created = request.session.get('created', '0')
            if created == '1':
                del request.session['created']

            # CHECK IF REDIRECT FROM UPDATE VIDEO
            updated = request.session.get('updated', '0')
            if updated == '1':
                del request.session['updated']

            context = {
                'journalist': j,
                'count': count,
                'videos': j_videos,
                'search': search_get,
                'keywords': keywords,
                'created': created,
                'updated': updated
            }

            return render(request, 'journal/journalist/journalist_videos.html', context)

    return redirect('index')


# ## JOURNALIST CREATE VIDEO PAGE ## #
def journalist_create_video(request):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY VIDEO OR CREATE NEW ONE
    video_id = request.session.get('video', None)
    has_image = 0
    if video_id is None:
        video = Video.objects.create(title='Session Video', journalist=j, active=False)
        request.session['video'] = video.id
    else:
        video = Video.objects.get(id=video_id)
        if video.primary_image is not None:
            has_image = 1

    form = JournalistCreateVideo()

    # CREATING VIDEO
    if request.method == 'POST':
        if video.primary_image is None:
            has_image = 0
        else:
            form = JournalistCreateVideo(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                video.title = cd['title']
                video.small_title = cd['small_title']
                video.category = get_object_or_404(Category, id=cd['category'])
                video.resume = cd['resume']
                video.content = cd['content']
                video.video_url = cd['url']
                if cd['comment_enable'] == 'no':
                    video.comment_enable = False
                if cd['share_enable'] == 'no':
                    video.share_enable = False
                tags = request.POST.getlist('tags')
                for t in tags:
                    video.tag.add(get_object_or_404(Tag, id=t))
                video.active = True
                video.save()

                del request.session['video']
                request.session['created'] = '1'

                return redirect('journalist_videos')

            else:
                print(form.errors)

    context = {
        'tags': Tag.objects.all().order_by('name'),
        'form': form,
        'has_image': has_image,
        'form_tag': JournalistAddTagForm,
        'image': video.primary_image
    }
    return render(request, 'journal/journalist/journalist_add_video.html', context)


# ## JOURNALIST CANCEL CREATE VIDEO REDIRECT ## #
def journalist_cancel_video(request):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY VIDEO AND DELETE IT
    video_id = request.session.get('video', None)
    if video_id is not None:
        video = Video.objects.get(id=video_id)
        if video.journalist == j:
            ImageNews.objects.filter(article=video).delete()
            video.delete()
            del request.session['video']

    return redirect('journalist_videos')


# ## JOURNALIST UPDATE VIDEO PAGE ## #
def journalist_update_video(request, video_id):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET VIDEO
    video = get_object_or_404(Video, id=video_id, active=True)
    if video.journalist != j:
        return redirect('journalist_videos')

    # UPDATING VIDEO
    if request.method == 'POST':
        form = JournalistCreateVideo(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            video.title = cd['title']
            video.small_title = cd['small_title']
            video.category = get_object_or_404(Category, id=cd['category'])
            video.resume = cd['resume']
            video.content = cd['content']
            video.video_url = cd['url']
            if cd['comment_enable'] == 'no':
                video.comment_enable = False
            else:
                video.comment_enable = True
            if cd['share_enable'] == 'no':
                video.share_enable = False
            else:
                video.share_enable = True
            tags = request.POST.getlist('tags')
            for t in tags:
                video.tag.add(get_object_or_404(Tag, id=t))
            video.active = True
            video.approved = False
            video.save()

            request.session['updated'] = '1'

            return redirect('journalist_videos')

    else:
        form = JournalistCreateVideo(initial={
            'title': video.title,
            'small_title': video.small_title,
            'resume': video.resume,
            'content': video.content,
            'url': video.video_url
        })

    context = {
        'video': video,
        'tags': Tag.objects.all().order_by('name'),
        'selected_tags': Tag.objects.filter(news=video),
        'form': form,
        'form_tag': JournalistAddTagForm
    }

    return render(request, 'journal/journalist/journalist_update_video.html', context)


# ## JOURNALIST SIGNALS PAGE ## #
def journalist_signals(request):
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)

            # DELETE COMMENT OR ANSWER
            if request.method == 'POST':
                if request.POST['method'] == 'comment':
                    comment_id = request.POST['comment']
                    if Comment.objects.filter(id=comment_id).exists():
                        c = Comment.objects.get(id=comment_id)
                        if c.news.journalist == j:
                            c.delete()
                            return redirect('journalist_signals')
                    elif Answer.objects.filter(id=comment_id).exists():
                        a = Answer.objects.get(id=comment_id)
                        if a.comment.news.journalist == j:
                            a.delete()
                            return redirect('journalist_signals')
                    else:
                        return redirect('journalist')
                elif request.POST['method'] == 'signal':
                    signal_id = request.POST['signal']
                    if SignalComment.objects.filter(id=signal_id).exists():
                        c = SignalComment.objects.get(id=signal_id)
                        if c.comment.news.journalist == j:
                            c.delete()
                            return redirect('journalist_signals')
                    elif SignalAnswer.objects.filter(id=signal_id).exists():
                        a = SignalAnswer.objects.get(id=signal_id)
                        if a.answer.comment.news.journalist == j:
                            a.delete()
                            return redirect('journalist_signals')
                    else:
                        return redirect('journalist')

            # JOURNALIST SIGNALS
            comment_signals = SignalComment.objects.all().order_by('-date_send').filter(
                comment__news__journalist=j)  # .annotate(type='comment')
            answer_signals = SignalAnswer.objects.all().order_by('-date_send').filter(
                answer__comment__news__journalist=j)  # .annotate(type='answer')
            signals = sorted(
                chain(comment_signals, answer_signals),
                key=attrgetter('date_send'))

            count = comment_signals.count() + answer_signals.count()

            # PAGINATOR
            page = request.GET.get('page', 1)
            paginator = Paginator(signals, 20)
            try:
                signals = paginator.page(page)
            except PageNotAnInteger:
                signals = paginator.page(1)
            except EmptyPage:
                signals = paginator.page(paginator.num_pages)

            context = {
                'journalist': j,
                'count': count,
                'signals': signals
            }

            return render(request, 'journal/journalist/journalist_signals.html', context)

    return redirect('index')


#####################################################
#          JOURNALIST AJAX REQUEST VIEW             #
#####################################################


# ## JOURNALIST UPLOAD PRIMARY IMAGE ON CREATE FUNCTION ## #
@require_POST
def journalist_upload_primary_image(request):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY ARTICLE OR CREATE NEW ONE
    article_id = request.session.get('article', None)
    if article_id is None:
        article = News.objects.create(title='Session Article', journalist=j, active=False)
        request.session['article'] = article.id
    else:
        article = News.objects.get(id=article_id)

    # GET PRIMARY IMAGE FROM POST
    form = JournalistImagePrimaryImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.description = 'Article primary image'
        image.save()
        article.primary_image = image
        article.save()
        data = {'is_valid': True, 'name': image.image.name, 'url': image.image.url}
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


# ## JOURNALIST UPLOAD SECONDARY IMAGES ON CREATE FUNCTION ## #
@require_POST
def journalist_upload_image(request):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY ARTICLE OR CREATE NEW ONE
    article_id = request.session.get('article', None)
    if article_id is None:
        article = News.objects.create(title='Session Article', journalist=j, active=False)
        request.session['article'] = article.id
    else:
        article = News.objects.get(id=article_id)

    # GET ARTICLE IMAGES FROM POST
    form = JournalistImageImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.article = article
        image.description = 'Article image'
        image.save()
        data = {
            'is_valid': True,
            'name': image.image.name,
            'url': image.image.url,
            'id': image.id
        }
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


# ## JOURNALIST UPLOAD PRIMARY IMAGE ON UPDATE FUNCTION ## #
@require_POST
def journalist_update_primary_image(request, article_id):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY ARTICLE OR CREATE NEW ONE
    article = get_object_or_404(News, id=article_id, active=True, journalist=j)

    # GET PRIMARY IMAGE FROM POST
    form = JournalistImagePrimaryImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.description = 'Article primary image'
        image.save()
        article.primary_image = image
        article.save()
        data = {'is_valid': True, 'name': image.image.name, 'url': image.image.url}
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


# ## JOURNALIST UPLOAD SECONDARY IMAGES ON UPDATE FUNCTION ## #
@require_POST
def journalist_update_image(request, article_id):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY ARTICLE OR CREATE NEW ONE
    article = get_object_or_404(News, id=article_id, active=True, journalist=j)

    # GET ARTICLE IMAGES FROM POST
    form = JournalistImageImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.article = article
        image.description = 'Article image'
        image.save()
        data = {
            'is_valid': True,
            'name': image.image.name,
            'url': image.image.url,
            'id': image.id
        }
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


# ## JOURNALIST DELETE IMAGE ON CREATE FUNCTION ## #
def journalist_delete_image(request, image_id):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # DELETE IMAGE
    article_id = request.session.get('article', None)
    if article_id is not None:
        article = News.objects.get(id=article_id)
        if article.journalist == j:
            image = get_object_or_404(ImageNews, id=image_id)
            image.delete()
            data = {
                'message': 'success',
                'tr': '#tr' + str(image_id)
            }
            return JsonResponse(data)
        else:
            return redirect('journalist')


# ## JOURNALIST DELETE IMAGE ON UPDATE FUNCTION ## #
def journalist_delete_image_update(request, article_id, image_id):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # TEST IF IMAGE AND ARTICLE BELONG TO JOURNALIST
    get_object_or_404(News, id=article_id, active=True, journalist=j)

    # DELETE IMAGE
    image = get_object_or_404(ImageNews, id=image_id)
    image.delete()
    data = {
        'message': 'success',
        'tr': '#tr' + str(image_id)
    }
    return JsonResponse(data)


# ## JOURNALIST CREATE TAG FUNCTION ## #
def journalist_create_tag(request):
    name = request.GET.get('name', None)
    color = request.GET.get('color', None)
    description = request.GET.get('description', None)
    valid = True
    if (name is None) or (name == ''):
        valid = False
    if (color is None) or (color == ''):
        valid = False

    if valid is False:
        data = {'valid': False}
    else:
        t = Tag.objects.create(name=name, color=color, description=description)
        data = {
            'valid': True,
            'name': name,
            'id': t.id
        }
    return JsonResponse(data)


# ## JOURNALIST UPLOAD PRIMARY IMAGE ON CREATE VIDEO FUNCTION ## #
@require_POST
def journalist_upload_primary_image_video(request):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY VIDEO OR CREATE NEW ONE
    video_id = request.session.get('video', None)
    if video_id is None:
        video = Video.objects.create(title='Session Video', journalist=j, active=False)
        request.session['video'] = video.id
    else:
        video = Video.objects.get(id=video_id)

    # GET PRIMARY IMAGE FROM POST
    form = JournalistImagePrimaryImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.description = 'Video primary image'
        image.save()
        video.primary_image = image
        video.save()
        data = {'is_valid': True, 'name': image.image.name, 'url': image.image.url}
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


# ## JOURNALIST UPLOAD PRIMARY IMAGE ON UPDATE VIDEO FUNCTION ## #
@require_POST
def journalist_update_primary_image_video(request, video_id):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # GET TEMPORARY VIDEO OR CREATE NEW ONE
    video = get_object_or_404(Video, id=video_id, active=True, journalist=j)

    # GET PRIMARY IMAGE FROM POST
    form = JournalistImagePrimaryImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.description = 'Article primary image'
        image.save()
        video.primary_image = image
        video.save()
        data = {'is_valid': True, 'name': image.image.name, 'url': image.image.url}
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


# ## JOURNALIST DELETE COMMENT FUNCTION ## #
def journalist_delete_comment(request, comment_id):
    # CHECK IF JOURNALIST
    if request.user.is_authenticated:
        user = request.user
        if user.email in Journalist.email_list():
            # JOURNALIST
            j = get_object_or_404(Journalist, email=user.email)
        else:
            return redirect('journalist')
    else:
        return redirect('index')

    # DELETE COMMENT OR ANSWER
    if Comment.objects.filter(id=comment_id).exists():
        c = Comment.objects.get(id=comment_id)
        if c.news.journalist != j:
            return redirect('journalist_signals')
        c.delete()
    elif Answer.objects.filter(id=comment_id).exists():
        a = Answer.objects.get(id=comment_id)
        if a.comment.news.journalist != j:
            return redirect('journalist_signals')
        a.delete()
    else:
        return redirect('journalist')

    data = {'message': 'success'}
    return JsonResponse(data)


#####################################################
#                 SUPERVISOR PAGE                   #
#####################################################

# ## SUPERVISOR APPROVE ARTICLES PAGE ## #
def admin_approve(request):
    if is_supervisor(request):
        if request.method == 'POST':
            article_id = request.POST['article']
            article = get_object_or_404(News, id=article_id)
            article.active = False
            article.save()

        video_id = Video.objects.all().values_list('id', flat=True)
        news = News.objects.filter(active=True, approved=False).exclude(id__in=video_id).annotate(
            type=Value('news', CharField()))
        videos_ = Video.objects.filter(active=True, approved=False).annotate(type=Value('video', CharField()))
        articles = sorted(
            chain(news, videos_),
            key=attrgetter('id'))

        # PAGINATOR
        page = request.GET.get('page', 1)
        paginator = Paginator(articles, 20)
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)

        context = {
            'articles': articles,
            'count_videos': videos_.count,
            'count_articles': news.count
        }

        return render(request, 'journal/admin/admin_approve.html', context)

    return redirect('index')


#####################################################
#           SUPERVISOR AJAX REQUEST VIEW            #
#####################################################

# ## SUPERVISOR APPROVE ARTICLE FUNCTION ## #
def admin_approve_article(request):
    # CHECK IF SUPERVISOR
    if is_supervisor(request):
        article_id = request.GET.get('article', None)
        article_type = request.GET.get('type', None)
        if article_id is not None:
            article = get_object_or_404(News, id=article_id)
            article.approved = True
            article.save()
            if article_type == 'news':
                send_email(article_id)
            data = {
                'message': 'success',
                'type': article_type,
                'tr': '#tr'+str(article_id)
            }
            return JsonResponse(data)

    data = {'message': 'failed'}
    return JsonResponse(data)


#####################################################
#                    FUNCTIONS                      #
#####################################################

# ## CHECK IF USER IS A SUPERVISOR ## #
def is_supervisor(request):
    check = False
    if request.user.is_authenticated:
        user = request.user
        if user.email in Supervisor.email_list():
            check = True
    return check


# ## SEND EMAIL TO NEWSLETTER SUBSCRIBERS ## #
def send_email(id_article):
    article = News.objects.get(id=id_article)
    body = get_template('journal/email/newsletter.html')
    subject = 'BTP Newspaper'
    from_email = 'sender@example.com'
    context = {
        'article': article
    }
    html_content = body.render(context)
    msg = EmailMultiAlternatives(subject, '', from_email, [])
    for n in Newsletter.objects.filter(active=True):
        msg.to.append(n.email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
