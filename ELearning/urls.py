from django.conf.urls import url,include
from . import views


urlpatterns = [

    url(r'^index$', views.lister_cours, name='index'),
    url(r'^index1$',views.lister_cours_1,name='index_1'),
    url(r'^index2$', views.lister_cours_2, name='index_2'),
    url(r'^about$', views.about, name='about'),
    url(r'^prof$', views.prof, name='prof'),
    url(r'^dashboard$', views.dash, name='dash'),
    url(r'^formation/(?P<formateur_id>[0-9]+)/$', views.formation_add, name='formation'),
    url(r'^listeFormation/(?P<formateur_id>[0-9]+)/$', views.lister_formation, name='aff_1'),
    url(r'^formation_mod/(?P<id>[0-9]+)/(?P<formateur_id>[0-9]+)/$',views.formation,name='avant_mod'),
    url(r'^modifier_form/(?P<id>[0-9]+)/(?P<formateur_id>[0-9]+)$', views.modifier_form, name='modifier'),
    url(r'^listeFormation/(?P<formateur_id>[0-9]+)/supprimer_form/(?P<id>[0-9]+)/$', views.supprimer_form,name='supprimer'),
    url(r'^theme/(?P<formation_id>[0-9]+)/(?P<formateur_id>[0-9]+)$', views.theme_add, name='theme'),
    url(r'^listeTheme/(?P<formateur_id>[0-9]+)/$', views.lister_theme, name='aff_2'),
    url(r'^theme_mod/(?P<id>[0-9]+)/(?P<formateur_id>[0-9]+)/$', views.theme, name='avant_mod_1'),
    url(r'^modifier_theme/(?P<id>[0-9]+)/(?P<formateur_id>[0-9]+)$', views.modifier_theme, name='modifier_1'),
    url(r'^listeTheme/(?P<formateur_id>[0-9]+)/supprimer_theme/(?P<id>[0-9]+)/$', views.supprimer_theme,name='supprimer_1'),
    url(r'^listeCours/(?P<formateur_id>[0-9]+)/$', views.lister_cours_prof, name='aff_3'),
    url(r'^course/(?P<theme_id>[0-9]+)/(?P<formateur_id>[0-9]+)/$',views.cours_add,name='cours'),
    url(r'^cours_mod/(?P<id>[0-9]+)/(?P<formateur_id>[0-9]+)/$', views.cours, name='avant_mod_2'),
    url(r'^modifier_cours/(?P<id>[0-9]+)/(?P<formateur_id>[0-9]+)$', views.modifier_cours, name='modifier_2'),
    url(r'^listeCours/(?P<formateur_id>[0-9]+)/supprimer_cours/(?P<id>[0-9]+)/$', views.supprimer_cours,name='supprimer_2'),
    url(r'^leçon/(?P<course_id>[0-9]+)/(?P<formateur_id>[0-9]+)/$',views.leçon_add,name='leçon'),
    url(r'^lesson_mod/(?P<id>[0-9]+)/(?P<formateur_id>[0-9]+)/$', views.leçons, name='avant_mod_3'),
    url(r'^modifier_leçon/(?P<id>[0-9]+)/(?P<formateur_id>[0-9]+)$', views.modifier_leçon, name='modifier_3'),
    url(r'^listeLeçon/(?P<formateur_id>[0-9]+)/$', views.lister_leçons, name='aff_4'),
    url(r'^listeLeçon/(?P<formateur_id>[0-9]+)/supprimer_leçon/(?P<id>[0-9]+)/$', views.supprimer_leçon,name='supprimer_3'),
    url(r'^cours-list/(?P<theme_id>[0-9]+)$',views.lister_cours_3,name='liste'),
    url(r'^course-detail/(?P<id>[0-9]+)/$', views.detail_cours, name='detail'),
    url(r'^cours-list/$', views.lister_cours_4, name='liste2'),

]