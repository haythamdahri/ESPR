from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.index, name='index'),
    path('Accueil', views.index, name='Accueil'),
    path('login/', views.log_in, name='login'),
    path('register', views.register, name="register"),
    path('aploffre', views.aplofr, name="aploffre"),
    path('aboutus', views.aboutus, name="aboutus"),
    #path('contactus', views.contactus, name="contactus"),
    #path('authentifier', views.authentifier, name="authentifier"),
    #path('deconnexion', views.log_out, name="logout"),
    #path('sendmail', views.sendmail, name="sendmail"),
    path('inscription',views.inscriptionaa, name="inscription"),
    path('devenirPro', views.devenirPro, name="devenirPro"),

    path('NouvelleAnnonce', views.nouvelleAnnonce,name="nouvelleAnnonce" ),
    path('MesAnnonces', views.MesAnnonces, name="MesAnnonces"),
    path('NouveauProjet', views.NouveauProjet , name="NouveauProjet"),
    path('MesProjets', views.MesProjets, name="MesProjets"),
    path('MonProfile', views.MonProfile, name="MonProfile"),
    path('MESFAVORIS', views.MESFAVORIS, name="MESFAVORIS"),
    path('changePassword/<int:id>', views.changePassword, name="changePassword"),
    path('delete/<int:iduser>/<int:identreprise>', views.deleteProfile, name="deleteProfile"),
    path('updateProfile', views.updateprofile, name='updateProfile'),
    path('update', views.update, name="update"),
    path('addLot', views.addLot, name="addProjet"),
    path('detailLot/<int:idlot>',views.detailLot, name="detailLot"),
    path('deleteLot/<int:idlot>',views.deleteLot, name="deleteLot"),
    path('updateLot/<int:idlot>',views.updateLot, name="updateLot"),
    path('updateLOT/<int:idlot>',views.updateLOT, name="updateLOT"),
    path('addAnnonce', views.addAnnonce, name="addAnnonce"),
    path('detailAnnonce/<int:idannonce>',views.detailAnnonce, name="detailAnnonce"),
    path('searchMotCle', views.searchMotCle, name="searchMotCle"),
    path('categorie/<str:cat>', views.searchcategorie, name="searchcategorie"),
    path('deleteAnnonce/<int:idannonce>', views.deleteAnnonce, name="deleteAnnonce"),
    path('updateAnnonce/<int:idannonce>', views.updateAnnonce, name="updateAnnonce"),
    path('updateANNONCE/<int:idannonce>', views.updateANNONCE, name="updateANNONCE"),
    path('addfavori/<int:idannonce>', views.addfavori, name="addfavori"),
    path('deleteFavorie/<int:idFav>', views.deleteFavorie, name="deleteFavorie"),
    path('addDevis/<int:idannonce>/<int:idlot>', views.addDevis, name='addDevis'),
    path('searchDate', views.searchDate, name="searchDate"),
    path('searchDatePrecise', views.searchDatePrecise , name="searchDatePrecise"),
    path('searchDateLimite', views.searchDateLimite, name="searchDateLimite"),
    path('searchDateLimitePrecise', views.searchDateLimitePrecise , name="searchDateLimitePrecise"),
    path('EnvoieDevisFichier/<int:idannonce>/<int:idlot>', views.EnvoieDevisFichier, name="EnvoieDevisFichier"),
    path('voirReponse/<int:idannonce>', views.voirReponse, name="voirReponse"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
