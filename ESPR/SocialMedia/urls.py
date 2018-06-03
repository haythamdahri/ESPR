from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf.urls.static import settings, static
from . import views

app_name = "SocialMedia"

urlpatterns = [
    path('profil/', views.profil, name='myprofil'),
    path('profil/activite/', views.MyProfilStatuts, name='MyProfilStatuts'),
    path('ajaxuser/', views.ajaxUser, name="AjaxUser"),
    path('profil/demandes/', views.demandesProfil, name="demandes"),
    path('changephotocouverture', views.changephotocouverture, name="changephotocouverture"),
    path('changephotoprofil', views.changephotoprofil, name="changephotoprofil"),
    path('profil/groupes', views.groupesMyProfil, name="groupes"),
    path('demandeajax', views.demandeViaAjax, name="demandeViaAjax"),


    ###Chipop###
    ##Search
    path('search_members/', views.search_members, name="search_members"),
    path('search_offers/', views.search_offres, name="search_offres"),
    path('search_groupes/', views.search_groupes, name="search_groupes"),
    path('search/', views.search, name="search"),

    ##MyProfil
    #Langue my profil
    path('test',views.test,name="test"),
    path('myprofil/ajouterLangue/', views.ajouterLangue, name="ajouterLangue"),
    path('myprofil/modifierLangue/', views.modifierLangue, name="modifierLangue"),
    path('myprofil/supprimerLangue/', views.supprimerLangue, name="supprimerLangue"),
    path('myprofil/getModifierLangue/', views.getModifierLangue, name="getModifierLangue"),

    #Langue my profil
    path('myprofil/ajouterLangue/', views.ajouterLangue, name="ajouterLangue"),
    path('myprofil/getModifierLangue/', views.getModifierLangue, name="getModifierLangue"),
    path('myprofil/modifierLangue/', views.modifierLangue, name="modifierLangue"),
    path('myprofil/supprimerLangue/', views.supprimerLangue, name="supprimerLangue"),

    #Experience myprofil
    path('myprofil/ajouterExperience/', views.ajouterExperience, name="ajouterExperience"),
    path('myprofil/supprimerExperience/', views.supprimerExperience, name="supprimerExperience"),
    path('myprofil/getModifierExperience/', views.getModifierExperience, name="getModifierExperience"),
    path('myprofil/modifierExperience/', views.modifierExperience, name="modifierExperience"),

    #Formation myprofil
    path('myprofil/ajouterFormation/', views.ajouterFormation, name="ajouterFormation"),
    path('myprofil/supprimerFormation/', views.supprimerFormation, name="supprimerFormation"),
    path('myprofil/getModifierFormation/', views.getModifierFormation, name="getModifierFormation"),
    path('myprofil/modifierFormation/', views.modifierFormation, name="modifierFormation"),

    #Benevolar myprofil
    path('myprofil/ajouterBenevolat/', views.ajouterBenevolat, name="ajouterBenevolat"),
    path('myprofil/supprimerBenevolat/', views.supprimerBenevolat, name="supprimerBenevolat"),
    path('myprofil/getModifierBenevolat/', views.getModifierBenevolat, name="getModifierBenevolat"),
    path('myprofil/modifierBenevolat/', views.modifierBenevolat, name="modifierBenevolat"),

    #Informations myprofil
    path('myprofil/getModifierInformations/', views.getModifierInformations, name="getModifierInformations"),
    path('myprofil/modifierInformations/', views.modifierInformations, name="modifierInformations"),

    #InformationsProfil myprofil
    path('myprofil/getModifierInformationsProfil/', views.getModifierInformationsProfil, name="getModifierInformationsProfil"),
    path('myprofil/modifierInformationsProfil/', views.modifierInformationsProfil, name="modifierInformationsProfil"),

    ##Page Entreprise
    path('creer_entreprise/', views.creer_entreprise, name="creer_entreprise"),
    path('entreprise/<int:id_page_entreprise>/abonnees/', views.entreprise_abonnees, name="entreprise_abonnees"),
    path('entreprise/<int:id_page_entreprise>/', views.page_entreprise, name="page_entreprise"),
    path('entreprise/desabonner/<int:id_page_entreprise>/', views.neplussuivre_entreprise,
         name="neplussuivre_entreprise"),
    path('entreprise/abonner/<int:id_page_entreprise>/', views.suivre_entreprise, name="suivre_entreprise"),
    path('entreprise/<int:id_page_entreprise>/administration', views.page_administration_entreprise,
         name="page_administration_entreprise"),
    path('entreprise/edit/admins/', views.page_administration_edit_admins, name="page_administration_edit_admins"),
    path('entreprise/add/admins/', views.page_administration_add_admins, name="page_administration_add_admins"),
    path('entreprise/<int:id_page_entreprise>/employes/', views.page_employes_entreprise,
         name="page_employes_entreprise"),
    path('entreprise/<int:id_page_entreprise>/poster_offre/', views.page_entreprise_poster_offre,
         name="page_entreprise_poster_offre"),

    #Page entreprise Offre d'emplois
    path('entreprise/<int:id_page_entreprise>/publier_offre_emploi/', views.creer_offre_emploi, name="creer_offre_emploi"),
    path('entreprise/<int:id_page_entreprise>/offres_emploi/', views.page_offres_emploi_entreprise, name="page_offres_emploi_entreprise"),
    path('entreprise/offre_emploi/<int:id_offre_emploi>/postuler/', views.page_offre_emploi_postuler, name="page_offre_emploi_postuler"),
    path('entreprise/offre_emploi/<int:id_offre_emploi>/retirer_candidature/', views.page_offre_emploi_retirer_candidature, name="page_offre_emploi_retirer_candidature"),
    path('entreprise/offre_emploi/<int:id_offre_emploi>/modifier/', views.page_offre_emploi_modifier, name="page_offre_emploi_modifier"),
    path('entreprise/offre_emploi/<int:id_offre_emploi>/', views.page_offre_emploi, name="page_offre_emploi"),

    #ajax
    path('entreprise/geteditformulaire/', views.get_modifier_entreprise, name="get_modifier_entreprise"),
    path('entreprise/<int:id_page_entreprise>/modifier_infos/', views.modifier_entreprise, name="modifier_entreprise"),
    path('entreprise/<int:id_page_entreprise>/changer_photo_profil_entreprise/', views.changer_photo_profil_entreprise, name="changer_photo_profil_entreprise"),
    path('entreprise/<int:id_page_entreprise>/changer_photo_couverture_entreprise/', views.changer_photo_couverture_entreprise, name="changer_photo_couverture_entreprise"),


    #Haytham
    #Profil/id
    path('profil/<int:pk>/', views.getProfil, name='getProfil'),
    path('profil/<int:pk>/activite', views.ProfilStatuts, name='ProfilStatuts'),
    path('profil/<int:pk>/follow', views.followProfil, name="followProfil"),
    path('profil/<int:pk>/reponse-ami', views.FriendsRequests, name="addFriend"),
    path('profil/<int:pk>/get-responses-updates', views.getRequestsUpdates, name="getUpdates"),
    path('profil/<int:pk>', views.getProfil, name='getProfil'),
    path('profil/<int:pk>/groupes', views.getProfilGroupes, name='getProfilGroupes'),
    path('groupe/<int:pk>/', views.groupe, name="groupe"),
    path('groupe/<int:pk>/demandes/', views.demandesGroupe, name="demandesGroupe"),
    path('groupe/<int:pk>/ajax-demandes-groupe/', views.demandesGroupeViaAjax, name="demandesGroupeViaAjax"),
    path('groupe/<int:pk>/membres/', views.membresGroupe, name="membresGroupe"),
    path('groupe/<int:pk>/ajax-members-groupe', views.membersGroupeViaAjax, name="membresGroupeViaAjax"),
    path('groupe/<int:pk>/joinGroupeViaAjax', views.joinGroupeViaAjax, name="joinGroupeViaAjax"),
    path('groupe/<int:pk>/more-comments', views.getMoreCommentsGroupe, name="getMoreComments"),
    path('groupe/<int:pk>/change-photo-couverture-groupe', views.changephotocouverturegroupe, name="changephotocouverturegroupe"),
    path('groupe/<int:pk>/change-photo-profil-groupe', views.changephotoprofilgroupe, name="changephotoprofilgroupe"),
    path('creer-groupe', views.creer_groupe, name="creer_groupe"),

    #Haytham 2
    #Statut
    path('more-replies', views.getMoreReplies, name="getMoreReplies"),
    path('add-reply', views.addReply, name="addReply"),
    path('like-unlike-comment', views.likeUnlikeComment, name="likeUnlikeComment"),
    path('like-unlike-reply', views.likeUnlikeReply, name="likeUnlikeReply"),
    path('edit/statut', views.editStatut, name="editStatut"),
    path('delete/statut', views.deleteStatut, name="deleteStatut"),
    path('delete/reply', views.deleteReply, name="deleteReply"),
    path('edit/comment', views.editComment, name="editComment"),
    path('delete/comment', views.deleteComment, name="deleteComment"),
    path('edit/reply', views.editReply, name="editReply"),
    path('like-unlike-statut', views.likeUnlikeStatut, name="likeUnlikeStatut"),

    #Statut groupe
    path('groupe/<int:pk>/more-comments', views.getMoreCommentsGroupe, name="getMoreComments"),
    path('groupe/add-comment', views.addComment, name="addComment"),
    path('groupe/<int:pk>/change-photo-couverture-groupe', views.changephotocouverturegroupe,
         name="changephotocouverturegroupe"),
    path('groupe/<int:pk>/add-statut', views.addStatut, name="addStatut"),
    path('groupe/<int:pk>/change-photo-profil-groupe', views.changephotoprofilgroupe,
          name="changephotoprofilgroupe"),

    #Statut Profil
    path('profil/more-comments', views.getMoreCommentsMyProfil, name="getMoreCommentsMyProfil"),
    path('profil/<int:pk>/more-comments', views.getMoreCommentsProfil, name="getMoreCommentsProfil"),
    path('profil/more-replies', views.getMoreRepliesProfil, name="getMoreRepliesProfil"),
    path('profil/add-comment', views.addCommentProfil, name="addCommentProfil"),
    path('profil/add-statut', views.addStatutMyProfil, name="addStatutMyProfil"),
    path('profil/<int:pk>/add-statut', views.addStatutProfil, name="addStatutProfil"),
    path('profil/add-reply', views.addReplyProfil, name="addReplyProfil"),
    path('profil/edit/comment', views.editCommentProfil, name="editCommentProfil"),
    path('profil/edit/reply', views.editReply, name="editReplyProfil"),

    #Statut my profil
    path('myprofil/edit/reply', views.editReply, name="editReplyMyProfil"),
    path('myprofil/add-comment', views.addCommentMyProfil, name="addCommentMyProfil"),
    path('myprofil/more-replies', views.getMoreRepliesMyProfil, name="getMoreRepliesMyProfil"),
    path('myprofil/add-reply', views.addReplyMyProfil, name="addReplyMyProfil"),
    path('myprofil/edit/comment', views.editCommentMyProfil, name="editCommentMyProfil"),
    path('statut/likers', views.getStatutLikers, name="getStatutLikers"),



    #Signales
    path('statut/signaler', views.signalerStatut, name="SignalerStatut"),
    path('commentaire/signaler', views.signalerCommentaire, name="SignalerCommentaire"),
    path('reply/signaler', views.signalerReply, name="SignalerReply"),

    #Page Statut
    path('statut/<int:pk>', views.getStatut, name="Statut"),
    path('statut/edit/reply', views.editReplyStatut, name="editReplyStatut"),
    path('statut/add-comment', views.addCommentStatut, name="addCommentStatut"),
    path('statut/more-comments', views.getMoreCommentsStatut, name="getMoreCommentsStatut"),
    path('statut/more-replies', views.getMoreRepliesStatut, name="getMoreRepliesStatut"),
    path('statut/add-reply', views.addReplyStatut, name="addReplyStatut"),
    path('statut/edit/comment', views.editCommentStatut, name="editCommentStatut"),
    path('statut/share', views.shareStatut, name="shareStatut"),

    #Notifications
    path('notifications', views.notifications, name="notifications"),
    path('notifications/delete', views.deleteNotification, name="deleteNotification"),

    #Acceuil
    path('home/add-comment', views.addCommentAcceuil, name="addCommentAcceuil"),
    path('home/more-comments', views.getMoreCommentsAcceuil, name="getMoreCommentsAcceuil"),
    path('home/more-replies', views.getMoreRepliesAcceuil, name="getMoreRepliesAcceuil"),
    path('home/add-reply', views.addReplyAcceuil, name="addReplyAcceuil"),
    path('home/edit/comment', views.editCommentAcceuil, name="editCommentAcceuil"),

    #Search For More
    path('search-members-more', views.getNextMembers, name="getNextMembers"),
    path('search-groupes-more', views.getNextGroupes, name="getNextGroupes"),
    path('search-offres-more', views.getNextOffres, name="getNextOffres"),





    path('home/', views.home, name="home"),
    path('', views.home, name="home"),



]
