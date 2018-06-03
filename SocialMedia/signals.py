from django.db.models import Q
from django.db.models.signals import pre_save, post_save, m2m_changed, post_init
from django.dispatch import receiver
from SocialMedia.models import *
from main_app.models import *


def get_full_name(profil):
    return profil.user.first_name + " " + profil.user.last_name


# Likes [STATUT-COMMENTAIRE-REPLY]

@receiver(m2m_changed, sender=Statut.likes.through)
def get_likes_statut(sender, instance, action, reverse, model, pk_set, **kwargs):
    global st
    if action == "pre_add":
        st = tuple(instance.likes.all())
    if action == "post_add":
        for like in instance.likes.all():
            if like not in st and instance.publisher != like:
                msg = "{0} <b>aime votre statut</b>".format(get_full_name(like))
                Notification.objects.create(profil_to_notify=instance.publisher, statut=instance, profil=like,
                                            message=msg, type=0)


@receiver(m2m_changed, sender=Reply.likes.through)
def get_likes_reply(sender, instance, action, reverse, model, pk_set, **kwargs):
    global st
    if action == "pre_add":
        st = tuple(instance.likes.all())
    if action == "post_add":
        for like in instance.likes.all():
            if like not in st and instance.user != like:
                msg = "{0} <b>aime votre reponse</b>".format(get_full_name(like))
                Notification.objects.create(profil_to_notify=instance.user, statut=instance.commentaire.statut,
                                            profil=like, message=msg, type=0)


@receiver(m2m_changed, sender=Commentaire.likes.through)
def get_likes_commentaire(sender, instance, action, reverse, model, pk_set, **kwargs):
    global st
    if action == "pre_add":
        st = tuple(instance.likes.all())
    if action == "post_add":
        for like in instance.likes.all():
            if like not in st and instance.user != like:
                msg = "{0} <b>aime votre commentaire</b>".format(get_full_name(like))
                Notification.objects.create(profil_to_notify=instance.user, statut=instance.statut, profil=like,
                                            message=msg, type=0)


@receiver(m2m_changed, sender=Groupe.admins.through)
def inform_admins_adminsChanges(sender, instance, action, reverse, model, pk_set, **kwargs):
    global oldadmins
    admins = dict()
    if action == "pre_add":
        oldadmins = tuple(instance.admins.all())
    if action == "post_add":
        for admin in instance.admins.all():
            if admin not in oldadmins:
                admins[admin] = admin
        for admin in instance.admins.all():
            for ad in admins:
                if ad != admin:
                    msg = "{0} <b>à été designé autant qu'administrateur du groupe {1}</b>".format(get_full_name(ad),
                                                                                            instance.nom)
                    Notification.objects.create(type=1, profil=ad, message=msg, profil_to_notify=admin, groupe=instance)


@receiver(m2m_changed, sender=Groupe.moderators.through)
def inform_admins_moderatorsChanges(sender, instance, action, reverse, model, pk_set, **kwargs):
    global oldmoderators
    moderators = dict()
    if action == "pre_add":
        oldmoderators = tuple(instance.moderators.all())
    if action == "post_add":
        for moderator in instance.moderators.all():
            if moderator not in oldmoderators:
                moderators[moderator] = moderator
        for admin in instance.admins.all():
            for mod in moderators:
                msg = "{0} <b>à été designé autant que moderateur du groupe {1}</b>".format(get_full_name(mod), instance.nom)
                Notification.objects.create(type=1, profil=mod, message=msg, profil_to_notify=admin, groupe=instance)


@receiver(m2m_changed, sender=Groupe.adherents.through)
def inform_admins_adherentsChanges(sender, instance, action, reverse, model, pk_set, **kwargs):
    global oldadherents
    adherents = dict()
    if action == "pre_add":
        oldadherents = tuple(instance.adherents.all())
    if action == "post_add":
        for adherent in instance.adherents.all():
            if adherent not in oldadherents:
                adherents[adherent] = adherent
        for admin in instance.admins.all():
            for adh in adherents:
                msg = "{0} <b>à été designé autant qu'adherent du groupe {1}</b>".format(get_full_name(adh), instance.nom)
                Notification.objects.create(type=1, message=msg, profil_to_notify=admin, groupe=instance, profil=adh)


@receiver(m2m_changed, sender=PageEntreprise.abonnees.through)
def abonner_entreprise(sender, instance, action, reverse, model, pk_set, **kwargs):
    global oldabonnees
    abonnees = dict()
    if action == "pre_add":
        oldabonnees = tuple(instance.abonnees.all())
    if action == "post_add":
        for abonnee in instance.abonnees.all():
            if abonnee not in oldabonnees:
                abonnees[abonnee] = abonnee
        for admin in instance.administrateurs.all():
            for ab in abonnees:
                msg = "{0} <b>est abonné avec votre entreprise: {1}</b>".format(get_full_name(ab), instance.entreprise.nom)
                Notification.objects.create(type=4, message=msg, profil=ab, profil_to_notify=admin, entreprise=instance)


@receiver(m2m_changed, sender=PageEntreprise.moderateurs.through)
def moderateur_entreprise(sender, instance, action, reverse, model, pk_set, **kwargs):
    global oldmoderateurs
    moderateurs = dict()
    if action == "pre_add":
        oldmoderateurs = tuple(instance.moderateurs.all())
    if action == "post_add":
        for moderateur in instance.moderateurs.all():
            if moderateur not in oldmoderateurs:
                moderateurs[moderateur] = moderateur
        for admin in instance.administrateurs.all():
            for mod in moderateurs:
                msg = "{0} <b>à été designé autant que moderateur pour votre entreprise: {1}</b>".format(get_full_name(mod),
                                                                                                  instance.entreprise.nom)
                Notification.objects.create(type=4, message=msg, profil_to_notify=admin, profil=mod,
                                            entreprise=instance)


@receiver(m2m_changed, sender=PageEntreprise.administrateurs.through)
def admins_entreprise(sender, instance, action, reverse, model, pk_set, **kwargs):
    global oldadminstrateurs
    administrateurs = dict()
    if action == "pre_add":
        oldadminstrateurs = tuple(instance.administrateurs.all())
    if action == "post_add":
        for administrateur in instance.administrateurs.all():
            if administrateur not in oldadminstrateurs:
                administrateurs[administrateur] = administrateur
        for admin in instance.administrateurs.all():
            for ad in administrateurs:
                if admin != ad:
                    msg = "{0} <b>à été designé autant qu'administrateur pour votre entreprise: {1}</b>".format(
                        get_full_name(ad), instance.entreprise.nom)
                    Notification.objects.create(type=4, message=msg, profil_to_notify=admin, entreprise=instance,
                                                profil=ad)


@receiver(m2m_changed, sender=OffreEmploi.profil_postulants.through)
def offre_emploi_profil_postul(sender, instance, action, reverse, model, pk_set, **kwargs):
    global old_postulants
    postulants = dict()
    if action == "pre_add":
        old_postulants = tuple(instance.profil_postulants.all())
    if action == "post_add":
        if instance.poste != None:
            poste = instance.poste.nom_poste
        else:
            poste = instance.nom_poste
        for p in instance.profil_postulants.all():
            if p not in old_postulants:
                postulants[p] = p
        for admin in instance.page_entreprise.administrateurs.all():
            for p in postulants:
                msg = "{0} <b>à postulé(e) à votre offre d'emploi pour le poste {0}</b>".format(get_full_name(p), poste)
                Notification.objects.create(profil_to_notify=admin, profil=p, message=msg, type=3, offreEmploi=instance)


# Statut Notifications
def notify_members_statut(instance, created):
    if created:
        for admin in instance.mur_groupe.admins.all():
            if admin != instance.publisher:
                Notification.objects.create(message="{0} <b>à ajouter un nouveau statut sur le mur du groupe {1}</b>".format(
                    get_full_name(instance.publisher), instance.mur_groupe.nom), type=0, profil_to_notify=admin,
                    groupe=instance.mur_groupe, statut=instance, profil=instance.publisher)
        for moderator in instance.mur_groupe.moderators.all():
            if moderator != instance.publisher:
                Notification.objects.create(message="{0} <b>à ajouter un nouveau statut sur le mur du groupe {1}</b>".format(
                    get_full_name(instance.publisher), instance.mur_groupe.nom), type=0, profil_to_notify=moderator,
                    groupe=instance.mur_groupe, statut=instance, profil=instance.publisher)
        for adherent in instance.mur_groupe.adherents.all():
            if adherent != instance.publisher:
                Notification.objects.create(message="{0} <b>à ajouter un nouveau statut sur le mur du groupe {1}</b>".format(
                    get_full_name(instance.publisher), instance.mur_groupe.nom), type=0, profil_to_notify=adherent,
                    groupe=instance.mur_groupe, statut=instance, profil=instance.publisher)
    else:
        for admin in instance.mur_groupe.admins.all():
            if admin != instance.publisher:
                Notification.objects.create(message="{0} <b>à modifier son statut sur le mur du groupe {1}</b>".format(
                    get_full_name(instance.publisher), instance.mur_groupe.nom), type=0, profil_to_notify=admin,
                    groupe=instance.mur_groupe, statut=instance, profil=instance.publisher)
        for moderator in instance.mur_groupe.moderators.all():
            if moderator != instance.publisher:
                Notification.objects.create(message="{0} <b>à modifier son statut sur le mur du groupe {1}</b>".format(
                    get_full_name(instance.publisher), instance.mur_groupe.nom), type=0, profil_to_notify=moderator,
                    groupe=instance.mur_groupe, statut=instance, profil=instance.publisher)
        for adherent in instance.mur_groupe.adherents.all():
            if adherent != instance.publisher:
                Notification.objects.create(message="{0} <b>à modifier son statut sur le mur du groupe {1}</b>".format(
                    get_full_name(instance.publisher), instance.mur_groupe.nom), type=0, profil_to_notify=adherent,
                    groupe=instance.mur_groupe, statut=instance, profil=instance.publisher)


def notify_friends_statut(instance, created):
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.publisher, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.publisher, statut=1).values()
    if created:
        for friend in receivedRequest.values('emetteur_id'):
            p = Profil.objects.get(id=friend['emetteur_id'])
            Notification.objects.create(profil_to_notify=p, statut=instance, profil=instance.publisher,
                                        message="{0} <b>à ajouter un nouveau statut</b>".format(
                                            get_full_name(instance.publisher)), type=0)
        for friend in sentRequests.values('recepteur_id'):
            p = Profil.objects.get(id=friend['recepteur_id'])
            Notification.objects.create(profil_to_notify=p, statut=instance, profil=instance.publisher,
                                        message="{0} <b>à ajouter un nouveau statut</b>".format(
                                            get_full_name(instance.publisher)), type=0)
    else:
        for friend in receivedRequest.values('emetteur_id'):
            p = Profil.objects.get(id=friend['emetteur_id'])
            Notification.objects.create(profil_to_notify=p, statut=instance, profil=instance.publisher,
                                        message="{0} <b>à modifier son statut</b>".format(get_full_name(instance.publisher)),
                                        type=0)
        for friend in sentRequests.values('recepteur_id'):
            p = Profil.objects.get(id=friend['recepteur_id'])
            Notification.objects.create(profil_to_notify=p, statut=instance, profil=instance.publisher,
                                        message="{0} <b>à modifier son statut</b>".format(get_full_name(instance.publisher)),
                                        type=0)


def notify_suiveurs_statut(instance, created):
    suiveurs = Suivie.objects.filter(followed_profil=instance.publisher).values()
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.publisher, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.publisher, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    if created:
        for s in suiveurs:
            if s['follower_id'] not in emetteurs and s['follower_id'] not in recepteurs:
                p = Profil.objects.get(id=s['follower_id'])
                Notification.objects.create(profil_to_notify=p, statut=instance, profil=instance.publisher,
                                            message="{0} <b>à ajouter un nouveau statut</b>".format(
                                                get_full_name(instance.publisher)), type=0)
    else:
        for s in suiveurs:
            if s['follower_id'] not in emetteurs and s['follower_id'] not in recepteurs:
                p = Profil.objects.get(id=s['follower_id'])
                Notification.objects.create(profil_to_notify=p, statut=instance, profil=instance.publisher,
                                            message="{0} <b>à modifier son statut</b>".format(
                                                get_full_name(instance.publisher)), type=0)


def notify_mur_owner_statut(instance, created):
    if created:
        Notification.objects.create(profil_to_notify=instance.mur_profil, statut=instance, profil=instance.publisher,
                                    message="{0} <b>à ajouter un nouveau statut sur votre mur</b>".format(
                                        get_full_name(instance.publisher)), type=0)
    else:
        Notification.objects.create(profil_to_notify=instance.mur_profil, statut=instance, profil=instance.publisher,
                                    message="{0} <b>à modifier son statut sur votre mur</b>".format(
                                        get_full_name(instance.publisher)), type=0)


@receiver(post_save, sender=Statut)
def send_statut_notifications(sender, instance, created, **kwargs):
    if instance.is_group_statut:
        notify_members_statut(instance, created)
    else:
        if instance.mur_profil == instance.publisher:
            notify_friends_statut(instance, created)
            notify_suiveurs_statut(instance, created)
        else:
            notify_mur_owner_statut(instance, created)


# Commentaires Statut
def notify_members_commentaire(instance, created):
    if created:
        for admin in instance.statut.mur_groupe.admins.all():
            if instance.user != admin:
                if instance.statut.publisher == admin:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur votre statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                elif instance.user != instance.statut.publisher:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur le statut de {1} dans le mur du groupe {2}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.statut.publisher),
                        instance.statut.mur_groupe.nom)
                else:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur son statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                Notification.objects.create(message=msg, type=0, profil_to_notify=admin,
                                            groupe=instance.statut.mur_groupe, statut=instance.statut,
                                            profil=instance.user)
        for moderator in instance.statut.mur_groupe.moderators.all():
            if instance.user != moderator:
                if moderator == instance.statut.publisher:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur votre statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                elif instance.user != instance.statut.publisher:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur le statut de {1} dans le mur du groupe {2}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.statut.publisher),
                        instance.statut.mur_groupe.nom)
                else:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur son statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                Notification.objects.create(message=msg, type=0, profil_to_notify=moderator,
                                            groupe=instance.statut.mur_groupe, statut=instance.statut,
                                            profil=instance.user)
        for adherent in instance.statut.mur_groupe.adherents.all():
            if instance.user != adherent:
                if instance.statut.publisher == adherent:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur votre statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                elif instance.user != instance.statut.publisher:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur le statut de {1} dans le mur du groupe {2}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.statut.publisher),
                        instance.statut.mur_groupe.nom)
                else:
                    msg = "{0} <b>à ajouter un nouveau commentaire sur son statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                Notification.objects.create(message=msg, type=0, profil_to_notify=adherent,
                                            groupe=instance.statut.mur_groupe, statut=instance.statut,
                                            profil=instance.user)
    else:
        for admin in instance.statut.mur_groupe.admins.all():
            if instance.user != admin:
                if admin == instance.statut.publisher:
                    msg = "{0} <b>à modifier son commentaire sur votre statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                if instance.user != instance.statut.publisher:
                    msg = "{0} <b>à modifier son commentaire sur le statut de {1} dans le mur du groupe {2}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.statut.publisher),
                        instance.statut.mur_groupe.nom)
                else:
                    msg = "{0} <b>à modifier son commentaire sur son statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                Notification.objects.create(message=msg, type=0, profil_to_notify=admin,
                                            groupe=instance.statut.mur_groupe, statut=instance.statut,
                                            profil=instance.user)
        for moderator in instance.statut.mur_groupe.moderators.all():
            if instance.user != moderator:
                if instance.statut.publisher == moderator:
                    msg = "{0} <b>à modifier son commentaire sur votre statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                elif instance.user != instance.statut.publisher:
                    msg = "{0} <b>à modifier son commentaire sur le statut de {1} dans le mur du groupe {2}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.statut.publisher),
                        instance.statut.mur_groupe.nom)
                else:
                    msg = "{0} <b>à modifier son commentaire sur son statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                Notification.objects.create(message=msg, type=0, profil_to_notify=moderator,
                                            groupe=instance.statut.mur_groupe, statut=instance.statut,
                                            profil=instance.user)
        for adherent in instance.statut.mur_groupe.adherents.all():
            if instance.user != adherent:
                if instance.statut.publisher == adherent:
                    msg = "{0} <b>à modifier son commentaire sur votre statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                if instance.user != instance.statut.publisher:
                    msg = "{0} <b>à modifier son commentaire sur le statut de {1} dans le mur du groupe {2}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.statut.publisher),
                        instance.statut.mur_groupe.nom)
                else:
                    msg = "{0} <b>à modifier son commentaire sur son statut dans le mur du groupe {1}</b>".format(
                        get_full_name(instance.user), instance.statut.mur_groupe.nom)
                Notification.objects.create(message=msg, type=0, profil_to_notify=adherent,
                                            groupe=instance.statut.mur_groupe, statut=instance.statut,
                                            profil=instance.user)


def notify_users_commentators(instance, created):
    suivs = Suivie.objects.filter(followed_profil=instance.user).values()
    st = instance.statut.commentaire_set.all().exclude(user=instance.user).values('user').distinct()
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.user, statut=1).distinct().values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.user, statut=1).distinct().values()
    s = [entry for entry in suivs.values('follower_id')]
    suiveurs = [entry['follower_id'] for entry in s]
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    for user in st:
        p = Profil.objects.get(id=user['user'])
        if p.id not in suiveurs and p.id not in recepteurs and p.id not in emetteurs:
            if created:
                msg = "{0} <b>à ajouter un nouveau commentaire sur le statut de {1}</b>".format(get_full_name(instance.user),
                                                                                         get_full_name(
                                                                                             instance.statut.publisher))
            else:
                msg = "{0} <b>à modifier son commentaire sur le statut de {1}</b>".format(get_full_name(instance.user),
                                                                                   get_full_name(
                                                                                       instance.statut.publisher))
            Notification.objects.create(profil=instance.statut.publisher, statut=instance.statut, profil_to_notify=p,
                                        message=msg, type=0)


def notify_friends_commentaire(instance, created):
    u = [entry for entry in instance.statut.commentaire_set.all().values('user')]
    users = [entry['user'] for entry in u]
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.user, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.user, statut=1).values()
    if created:
        for friend in receivedRequest.values('emetteur_id'):
            p = Profil.objects.get(id=friend['emetteur_id'])
            if p != instance.statut.publisher and p != instance.statut.mur_profil:
                if instance.user != p:
                    if instance.statut.publisher == p:
                        msg = "{0} <b>à ajouter un nouveau commentaire sur votre statut</b>".format(
                            get_full_name(instance.user))
                    elif instance.statut.publisher == instance.user:
                        msg = "{0} <b>à ajouter un nouveau commentaire sur son statut</b>".format(get_full_name(instance.user))
                    else:
                        msg = "{0} <b>à ajouter un nouveau commentaire sur le statut de {1}</b>".format(
                            get_full_name(instance.user), get_full_name(instance.statut.publisher))
                    Notification.objects.create(profil=instance.user, statut=instance.statut, profil_to_notify=p,
                                                message=msg, type=0)

        for friend in sentRequests.values('recepteur_id'):
            p = Profil.objects.get(id=friend['recepteur_id'])
            if p != instance.statut.publisher and p != instance.statut.mur_profil:
                if instance.user != p:
                    if instance.statut.publisher == p:
                        msg = "{0} <b>à ajouter un nouveau commentaire sur votre statut</b>".format(
                            get_full_name(instance.user))
                    elif instance.statut.publisher == instance.user:
                        msg = "{0} <b>à ajouter un nouveau commentaire sur son statut</b>".format(get_full_name(instance.user))
                    else:
                        msg = "{0} <b>à ajouter un nouveau commentaire sur le statut de {1}</b>".format(
                            get_full_name(instance.user), get_full_name(instance.statut.publisher))
                    Notification.objects.create(profil=instance.user, statut=instance.statut, profil_to_notify=p,
                                                message=msg, type=0)

    else:
        for friend in receivedRequest.values('emetteur_id'):
            p = Profil.objects.get(id=friend['emetteur_id'])
            if p != instance.statut.publisher and p != instance.statut.mur_profil:
                if instance.user != p:
                    if instance.statut.publisher == p:
                        msg = "{0} <b>à modifier son commentaire sur votre statut</b>".format(get_full_name(instance.user))
                    elif instance.statut.publisher == instance.user:
                        msg = "{0} <b>à modifier son commentaire sur son statut</b>".format(get_full_name(instance.user))
                    else:
                        msg = "{0} <b>à modifier son commentaire sur le statut de {1}</b>".format(get_full_name(instance.user),
                                                                                           get_full_name(
                                                                                               instance.statut.publisher))
                    Notification.objects.create(profil=instance.user, statut=instance.statut, profil_to_notify=p,
                                                message=msg, type=0)

        for friend in sentRequests.values('recepteur_id'):
            p = Profil.objects.get(id=friend['recepteur_id'])
            if p != instance.statut.publisher and p != instance.statut.mur_profil:
                if instance.user != p:
                    if instance.statut.publisher == p:
                        msg = "{0} <b>à modifier son commentaire sur votre statut</b>".format(get_full_name(instance.user))
                    elif instance.statut.publisher == instance.user:
                        msg = "{0} <b>à modifier son commentaire sur son statut</b>".format(get_full_name(instance.user))
                    else:
                        msg = "{0} <b>à modifier son commentaire sur le statut de {1}</b>".format(get_full_name(instance.user),
                                                                                           get_full_name(
                                                                                               instance.statut.publisher))
                    Notification.objects.create(profil=instance.user, statut=instance.statut, profil_to_notify=p,
                                                message=msg, type=0)


def notify_suiveurs_commentaire(instance, created):
    suiveurs = Suivie.objects.filter(followed_profil=instance.statut.publisher).values()
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.statut.publisher, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.statut.publisher, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    if created:
        for s in suiveurs:
            if s['follower_id'] not in emetteurs and s['follower_id'] not in recepteurs:
                p = Profil.objects.get(id=s['follower_id'])
                if p != instance.statut.publisher and p != instance.statut.mur_profil:
                    if instance.user != p:
                        if instance.user == instance.statut.publisher:
                            msg = "{0} <b>à ajouter un nouveau commentaire sur son statut</b>".format(
                                get_full_name(instance.user))
                        else:
                            msg = "{0} <b>à ajouter un nouveau commentaire sur le statut de {1} publié sur son mur</b>".format(
                                get_full_name(instance.user), get_full_name(instance.statut.publisher))
                        Notification.objects.create(profil=instance.user, statut=instance.statut, profil_to_notify=p,
                                                    message=msg, type=0)

    else:
        for s in suiveurs:
            if s['follower_id'] not in emetteurs and s['follower_id'] not in recepteurs:
                p = Profil.objects.get(id=s['follower_id'])
                if p != instance.statut.publisher and p != instance.statut.mur_profil:
                    if instance.user != p:
                        if instance.user == instance.statut.publisher:
                            msg = "{0} <b>à modifier son commentaire sur son statut</b>".format(get_full_name(instance.user))
                        else:
                            msg = "{0} <b>à modifier son commentaire sur le statut de {1} publié sur son mur</b>".format(
                                get_full_name(instance.user), get_full_name(instance.statut.publisher))
                        Notification.objects.create(profil=instance.user, statut=instance.statut, profil_to_notify=p,
                                                    message=msg, type=0)


def notify_mur_owner_commentaire(instance, created):
    if created:
        msg = "{0} <b>à ajouter un nouveau commentaire sur votre statut</b>".format(get_full_name(instance.user))
        Notification.objects.create(profil_to_notify=instance.statut.mur_profil, statut=instance.statut,
                                    profil=instance.user, message=msg, type=0)
    else:
        msg = "{0} <b>à modifier son commentaire sur votre statut</b>".format(get_full_name(instance.user))
        Notification.objects.create(profil_to_notify=instance.statut.mur_profil, statut=instance.statut,
                                    profil=instance.user, message=msg, type=0)


def notify_statut_owner_commentaire(instance, created):
    if created:
        if instance.user == instance.statut.mur_profil:
            msg = "{0} <b>à ajouter un nouveau commentaire sur votre statut publié dans son mur</b>".format(
                get_full_name(instance.user))
        else:
            msg = "{0} <b>à ajouter un nouveau commentaire sur votre statut publié dans le mur de {1}</b>".format(
                get_full_name(instance.user), get_full_name(instance.statut.mur_profil))
        Notification.objects.create(profil_to_notify=instance.statut.publisher, statut=instance.statut,
                                    profil=instance.user, message=msg, type=0)
    else:
        if instance.user == instance.statut.mur_profil:
            msg = "{0} <b>à modifier son commentaire sur votre statut publié dans son mur</b>".format(
                get_full_name(instance.user))
        else:
            msg = "{0} <b>à modifier son commentaire sur votre statut publié dans le mur de {1}</b>".format(
                get_full_name(instance.user), get_full_name(instance.statut.mur_profil))
        Notification.objects.create(profil_to_notify=instance.statut.publisher, statut=instance.statut,
                                    profil=instance.user, message=msg, type=0)


@receiver(post_save, sender=Commentaire)
def send_commentaire_notifications(sender, instance, created, **kwargs):
    if instance.statut.is_group_statut:
        notify_members_commentaire(instance, created)
    else:
        notify_friends_commentaire(instance, created)
        notify_suiveurs_commentaire(instance, created)
        notify_users_commentators(instance, created)
        if instance.user != instance.statut.mur_profil and instance.user != instance.statut.mur_profil:
            notify_mur_owner_commentaire(instance, created)
        if instance.user != instance.statut.publisher and instance.statut.publisher != instance.statut.mur_profil:
            notify_statut_owner_commentaire(instance, created)


# Commentaires Statut
def notify_members_reply(instance, created):
    if created:
        for admin in instance.commentaire.statut.mur_groupe.admins.all():
            if instance.user != admin:
                if instance.commentaire.user == admin:
                    msg = "{0} <b>à ajouter une nouvelle reponse a votre commentaire</b>".format(get_full_name(instance.user))
                elif instance.user != instance.commentaire.user:
                    msg = "{0} <b>à ajouter une nouvelle reponse au commentaire de {1}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.commentaire.user))
                else:
                    msg = "{0} <b>à ajouter une nouvelle reponse a son commentaire</b>".format(get_full_name(instance.user))
                Notification.objects.create(message=msg, type=0, profil_to_notify=admin,
                                            groupe=instance.commentaire.statut.mur_groupe,
                                            statut=instance.commentaire.statut, profil=instance.user)
        for moderator in instance.commentaire.statut.mur_groupe.moderators.all():
            if instance.user != moderator:
                if moderator == instance.commentaire.user:
                    msg = "{0} <b>à ajouter une nouvelle reponse a votre commentaire</b>".format(get_full_name(instance.user))
                elif instance.user != instance.commentaire.user:
                    msg = "{0} <b>à ajouter une nouvelle reponse au commentaire de {1}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.commentaire.user))
                else:
                    msg = "{0} <b>à ajouter une nouvelle reponse a son commentaire</b>".format(get_full_name(instance.user))
                Notification.objects.create(message=msg, type=0, profil_to_notify=moderator,
                                            groupe=instance.commentaire.statut.mur_groupe,
                                            statut=instance.commentaire.statut, profil=instance.user)
        for adherent in instance.commentaire.statut.mur_groupe.adherents.all():
            if instance.user != adherent:
                if instance.commentaire.user == adherent:
                    msg = "{0} <b>à ajouter une nouvelle reponse a votre commentaire</b>".format(get_full_name(instance.user))
                elif instance.user != instance.commentaire.user:
                    msg = "{0} <b>à ajouter une nouvelle reponse au commentaire de {1}</b>".format(
                        get_full_name(instance.user), get_full_name(instance.commentaire.user))
                else:
                    msg = "{0} <b>à ajouter une nouvelle reponse a son commentaire</b>".format(get_full_name(instance.user))
                Notification.objects.create(message=msg, type=0, profil_to_notify=adherent,
                                            groupe=instance.commentaire.statut.mur_groupe,
                                            statut=instance.commentaire.statut, profil=instance.user)
    else:
        for admin in instance.commentaire.statut.mur_groupe.admins.all():
            if instance.user != admin:
                if admin == instance.commentaire.user:
                    msg = "{0} <b>à modifier son reponse de votre commentaire</b>".format(get_full_name(instance.user))
                if instance.user != instance.commentaire.user:
                    msg = "{0} <b>à modifier sa reponse du commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                                   get_full_name(
                                                                                       instance.commentaire.user))
                else:
                    msg = "{0} <b>à modifier sa reponse de son commentaire</b>".format(get_full_name(instance.user))
                Notification.objects.create(message=msg, type=0, profil_to_notify=admin,
                                            groupe=instance.commentaire.statut.mur_groupe,
                                            statut=instance.commentaire.statut, profil=instance.user)
        for moderator in instance.commentaire.statut.mur_groupe.moderators.all():
            if instance.user != moderator:
                if instance.commentaire.user == moderator:
                    msg = "{0} <b>à modifier son reponse de votre commentaire</b>".format(get_full_name(instance.user))
                elif instance.user != instance.statut.publisher:
                    msg = "{0} <b>à modifier sa reponse du commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                                   get_full_name(
                                                                                       instance.commentaire.user))
                else:
                    msg = "{0} <b>à modifier sa reponse de son commentaire</b>".format(get_full_name(instance.user))
                Notification.objects.create(message=msg, type=0, profil_to_notify=moderator,
                                            groupe=instance.commentaire.statut.mur_groupe,
                                            statut=instance.commentaire.statut, profil=instance.user)
        for adherent in instance.commentaire.statut.mur_groupe.adherents.all():
            if instance.user != adherent:
                if instance.commentaire.user == adherent:
                    msg = "{0} <b>à modifier son reponse de votre commentaire</b>".format(get_full_name(instance.user))
                if instance.user != instance.commentaire.user:
                    msg = "{0} <b>à modifier sa reponse du commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                                   get_full_name(
                                                                                       instance.commentaire.user))
                else:
                    msg = "{0} <b>à modifier sa reponse de son commentaire</b>".format(get_full_name(instance.user))
                Notification.objects.create(message=msg, type=0, profil_to_notify=adherent,
                                            groupe=instance.commentaire.statut.mur_groupe,
                                            statut=instance.commentaire.statut, profil=instance.user)


def notify_users_who_replyed(instance, created):
    suivs = Suivie.objects.filter(followed_profil=instance.user).values()
    st = instance.commentaire.reply_set.all().exclude(user=instance.user).values('user').distinct()
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.user, statut=1).distinct().values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.user, statut=1).distinct().values()
    s = [entry for entry in suivs.values('follower_id')]
    suiveurs = [entry['follower_id'] for entry in s]
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    for user in st:
        p = Profil.objects.get(id=user['user'])
        if p.id not in suiveurs and p.id not in recepteurs and p.id not in emetteurs:
            if created:
                msg = "{0} <b>à ajouter une nouvelle reponse au commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                                        get_full_name(
                                                                                            instance.commentaire.user))
            else:
                msg = "{0} <b>à modifier son commentaire sur le statut de {1}</b>".format(get_full_name(instance.user),
                                                                                   get_full_name(
                                                                                       instance.commentaire.user))
            Notification.objects.create(profil=instance.user, statut=instance.commentaire.statut, profil_to_notify=p,
                                        message=msg, type=0)


def notify_friends_reply(instance, created):
    u = [entry for entry in instance.commentaire.reply_set.all().values('user')]
    users = [entry['user'] for entry in u]
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.user, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.user, statut=1).values()
    if created:
        for friend in receivedRequest.values('emetteur_id'):
            p = Profil.objects.get(id=friend['emetteur_id'])
            if instance.user != p:
                if instance.commentaire.user == p:
                    msg = "{0} <b>à ajouter une nouvelle reponse a votre commentaire</b>".format(get_full_name(instance.user))
                elif instance.commentaire.user == instance.user:
                    msg = "{0} <b>à ajouter un nouvelle reponse a son commentaire</b>".format(get_full_name(instance.user))
                else:
                    msg = "{0} <b>à ajouter un nouvelle reponse au commentaire {1}</b>".format(get_full_name(instance.user),
                                                                                        get_full_name(
                                                                                            instance.commentaire.user))
                Notification.objects.create(profil=instance.user, statut=instance.commentaire.statut,
                                            profil_to_notify=p, message=msg, type=0)

        for friend in sentRequests.values('recepteur_id'):
            p = Profil.objects.get(id=friend['recepteur_id'])
            if instance.user != p:
                if instance.commentaire.user == p:
                    msg = "{0} <b>à ajouter une nouvelle reponse a votre commentaire</b>".format(get_full_name(instance.user))
                elif instance.commentaire.user == instance.user:
                    msg = "{0} <b>à ajouter un nouvelle reponse a son commentaire</b>".format(get_full_name(instance.user))
                else:
                    msg = "{0} <b>à ajouter un nouvelle reponse au commentaire {1}</b>".format(get_full_name(instance.user),
                                                                                        get_full_name(
                                                                                            instance.commentaire.user))
                Notification.objects.create(profil=instance.user, statut=instance.commentaire.statut,
                                            profil_to_notify=p, message=msg, type=0)

    else:
        for friend in receivedRequest.values('emetteur_id'):
            p = Profil.objects.get(id=friend['emetteur_id'])
            if instance.commentaire.user == p:
                if instance.statut.publisher == p:
                    msg = "{0} <b>à modifier sa reponse de votre commentaire</b>".format(get_full_name(instance.user))
                elif instance.commentaire.user == instance.user:
                    msg = "{0} <b>à modifier sa reponse de son commentaire</b>".format(get_full_name(instance.user))
                else:
                    msg = "{0} <b>à modifier sa reponse du commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                                   get_full_name(
                                                                                       instance.commentaire.user))
                Notification.objects.create(profil=instance.user, statut=instance.commentaire.statut,
                                            profil_to_notify=p, message=msg, type=0)

        for friend in sentRequests.values('recepteur_id'):
            p = Profil.objects.get(id=friend['recepteur_id'])
            if instance.user != p:
                if instance.commentaire.user == p:
                    msg = "{0} <b>à modifier sa reponse de votre commentaire</b>".format(get_full_name(instance.user))
                elif instance.statut.publisher == instance.user:
                    msg = "{0} <b>à modifier sa reponse de son commentaire</b>".format(get_full_name(instance.user))
                else:
                    msg = "{0} <b>à modifier sa reponse du commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                                   get_full_name(
                                                                                       instance.commentaire.user))
                Notification.objects.create(profil=instance.user, statut=instance.commentaire.statut,
                                            profil_to_notify=p, message=msg, type=0)


def notify_suiveurs_reply(instance, created):
    suiveurs = Suivie.objects.filter(followed_profil=instance.commentaire.user).values()
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.commentaire.user, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.commentaire.user, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    if created:
        for s in suiveurs:
            if s['follower_id'] not in emetteurs and s['follower_id'] not in recepteurs:
                p = Profil.objects.get(id=s['follower_id'])
                if instance.user != p:
                    if instance.user == instance.commentaire.user:
                        msg = "{0} <b>à ajouter une nouvelle reponse sur son commentaire</b>".format(
                            get_full_name(instance.user))
                    else:
                        msg = "{0} <b>à ajouter une nouvelle reponse au commentaire de {1}</b>".format(
                            get_full_name(instance.user), get_full_name(instance.commentaire.user))
                    Notification.objects.create(profil=instance.user, statut=instance.commentaire.statut,
                                                profil_to_notify=p, message=msg, type=0)

    else:
        for s in suiveurs:
            if s['follower_id'] not in emetteurs and s['follower_id'] not in recepteurs:
                p = Profil.objects.get(id=s['follower_id'])
                if instance.user != p:
                    if instance.user == instance.commentaire.user:
                        msg = "{0} <b>à modifier sa reponse sur son commentaire</b>".format(get_full_name(instance.user))
                    else:
                        msg = "{0} <b>à modifier sa reponse au commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                                       get_full_name(
                                                                                           instance.statut.publisher))
                    Notification.objects.create(profil=instance.user, statut=instance.commentaire.statut,
                                                profil_to_notify=p, message=msg, type=0)


def notify_mur_owner_reply(instance, created):
    if created:
        if instance.commentaire.statut.publisher != instance.commentaire.user and instance.commentaire.statut.publisher == instance.commentaire.statut.mur_profil:
            msg = "{0} <b>à ajouter une nouvelle reponse a votre commentaire sur le statut publié dans votre mur</b>".format(
                get_full_name(instance.user))
        else:
            msg = "{0} <b>à ajouter une nouvelle reponse au commentaire de {1} sur le statut publié dans votre mur</b>".format(
                get_full_name(instance.user), get_full_name(instance.commentaire.user))
        Notification.objects.create(profil_to_notify=instance.commentaire.statut.mur_profil,
                                    statut=instance.commentaire.statut, profil=instance.user, message=msg, type=0)
    else:
        if instance.commentaire.statut.publisher == instance.commentaire.user:
            msg = "{0} <b>à modifier sa reponse de votre commentaire sur le statut publié dans votre mur</b>".format(
                get_full_name(instance.user))
        else:
            msg = "{0} <b>à modifier sa reponse au commentaire de {1} sur le statut publié dans votre mur</b>".format(
                get_full_name(instance.user), get_full_name(instance.commentaire.user))
        Notification.objects.create(profil_to_notify=instance.commentaire.statut.mur_profil,
                                    statut=instance.commentaire.statut, profil=instance.user, message=msg, type=0)


def notify_statut_owner_reply(instance, created):
    if instance.user != instance.commentaire.statut.publisher:
        if created:
            if instance.user != instance.commentaire.user:
                msg = "{0} <b>à ajouter une nouvelle reponse au commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                                        get_full_name(
                                                                                            instance.commentaire.user))
                Notification.objects.create(profil_to_notify=instance.statut.mur_profil, statut=instance.statut,
                                            profil=instance.user, message=msg, type=0)
        else:
            if instance.user != instance.commentaire.user:
                msg = "{0} <b>à modifier sa reponse au commentaire de {1}</b>".format(get_full_name(instance.user),
                                                                               get_full_name(instance.commentaire.user))
                Notification.objects.create(profil_to_notify=instance.statut.mur_profil, statut=instance.statut,
                                            profil=instance.user, message=msg, type=0)


def notify_commentaire_owner_reply(instance, created):
    if instance.user == instance.commentaire.user:
        if created:
            msg = "{0} <b>à ajouter une nouvelle reponse sur votre commentaire</b>".format(get_full_name(instance.user))
            Notification.objects.create(profil_to_notify=instance.commentaire.user, statut=instance.commentaire.statut,
                                        profil=instance.user, message=msg, type=0)
        else:
            msg = "{0} <b>à modifier sa reponse sur votre commentaire</b>".format(get_full_name(instance.user))
            Notification.objects.create(profil_to_notify=instance.commentaire.user, statut=instance.commentaire.statut,
                                        profil=instance.user, message=msg, type=0)


@receiver(post_save, sender=Reply)
def send_reply_notifications(sender, instance, created, **kwargs):
    if instance.commentaire.statut.is_group_statut:
        notify_members_reply(instance, created)
    else:
        notify_friends_reply(instance, created)
        notify_suiveurs_reply(instance, created)
        notify_users_who_replyed(instance, created)
        if instance.user != instance.commentaire.user:
            notify_commentaire_owner_reply(instance, created)
        if instance.user != instance.commentaire.user and instance.user != instance.commentaire.statut.mur_profil:
            notify_mur_owner_reply(instance, created)


@receiver(post_save, sender=DemandeAmi)
def demandes_amis(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        if instance.statut == 1:
            msg = "{0} <b>à accepter votre demande, vous pouvez partager tes moments avec lui</b>".format(
                get_full_name(instance.recepteur))
            Notification.objects.create(type=2, profil_to_notify=instance.emetteur, profil=instance.recepteur,
                                        message=msg)


@receiver(post_save, sender=DemandeGroupe)
def demandes_groupes(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        if instance.reponse:
            msg = "Votre de demande de rejoindre le groupe {0} <b>à été approuvée.</b>".format(instance.groupe_recepteur.nom)
            Notification.objects.create(type=1, profil_to_notify=instance.emetteur, groupe=instance.groupe_recepteur,
                                        message=msg)


@receiver(post_save, sender=Suivie)
def suivie_amis(sender, instance, created, **kwargs):
    if created:
        msg = "{0} <b>vous suivre</b>".format(get_full_name(instance.follower))
        Notification.objects.create(type=2, message=msg,profil=instance.follower, profil_to_notify=instance.followed_profil)


@receiver(post_save, sender=OffreEmploi)
def offreEmploi_signal(sender, instance, created, **kwargs):
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.profil_publicateur, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.profil_publicateur, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    if created:
        for demande in DemandeAmi.objects.filter(
                Q(emetteur=instance.profil_publicateur) | Q(recepteur=instance.profil_publicateur)):
            if demande.emetteur == instance.profil_publicateur:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            if instance.poste != None:
                poste = instance.poste.nom_poste
            else:
                poste = instance.nom_poste
            msg = "{0} <b>à postuler un offre d'emploi pour le poste: {1}</b>".format(
                get_full_name(instance.profil_publicateur), poste)
            Notification.objects.create(type=3, profil_to_notify=friend, profil=instance.profil_publicateur,
                                        message=msg, offreEmploi=instance)
        for follower in Suivie.objects.filter(followed_profil=instance.profil_publicateur).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à postuler un offre d'emploi pour le poste: {1}</b>".format(
                    get_full_name(instance.profil_publicateur), poste)
                Notification.objects.create(type=3, profil_to_notify=p, profil=instance.profil_publicateur, message=msg,
                                            offreEmploi=instance)
    else:
        for demande in DemandeAmi.objects.filter(
                Q(emetteur=instance.profil_publicateur) | Q(recepteur=instance.profil_publicateur)):
            if demande.emetteur == instance.profil_publicateur:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            if instance.poste != None:
                poste = instance.poste.nom_poste
            else:
                poste = instance.nom_poste
            msg = "{0} <b>à modifier son offre d'emploi pour le poste: {1}</b>".format(
                get_full_name(instance.profil_publicateur), poste)
            Notification.objects.create(type=3, profil_to_notify=friend, profil=instance.profil_publicateur,
                                        message=msg, offreEmploi=instance)
        for follower in Suivie.objects.filter(followed_profil=instance.profil_publicateur).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à postuler un offre d'emploi pour le poste: {1}</b>".format(
                    get_full_name(instance.profil_publicateur), poste)
                Notification.objects.create(type=3, profil_to_notify=p, profil=instance.profil_publicateur, message=msg,
                                            offreEmploi=instance)


@receiver(post_save, sender=Experience)
def experience_signal(sender, instance, created, **kwargs):
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.profil, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.profil, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    if instance.entreprise != None:
        entreprise = instance.entreprise.nom
    else:
        entreprise = instance.nom_entreprise
    if instance.poste != None:
        poste = instance.poste.nom_poste
    else:
        poste = instance.nom_poste
    if created:
        for demande in DemandeAmi.objects.filter(Q(emetteur=instance.profil) | Q(recepteur=instance.profil)):
            if demande.emetteur == instance.profil:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            msg = "{0} <b>à ajouter une experience au sein de {1} pour le poste {2} entre: {3} et {4}</b>".format(
                get_full_name(instance.profil), entreprise, poste, instance.date_debut, instance.date_fin)
            Notification.objects.create(type=2, profil_to_notify=friend, profil=instance.profil, message=msg)
        for follower in Suivie.objects.filter(followed_profil=instance.profil).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à ajouter une experience au sein de {1} pour le poste {2} entre: {3} et {4}</b>".format(
                    get_full_name(instance.profil), entreprise, poste, instance.date_debut, instance.date_fin)
                Notification.objects.create(type=2, profil_to_notify=p, profil=instance.profil, message=msg)
    else:
        for demande in DemandeAmi.objects.filter(Q(emetteur=instance.profil) | Q(recepteur=instance.profil)):
            if demande.emetteur == instance.profil:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            msg = "{0} <b>à modifier son experience au sein de {1} pour le poste {2} entre: {3} et {4}</b>".format(
                get_full_name(instance.profil), entreprise, poste, instance.date_debut, instance.date_fin)
            Notification.objects.create(type=2, profil_to_notify=friend, profil=instance.profil, message=msg)
        for follower in Suivie.objects.filter(followed_profil=instance.profil).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à modifier son experience au sein de {1} pour le poste {2} entre: {3} et {4}</b>".format(
                    get_full_name(instance.profil), entreprise, poste, instance.date_debut, instance.date_fin)
                Notification.objects.create(type=2, profil_to_notify=p, profil=instance.profil, message=msg)


@receiver(post_save, sender=Formation)
def formation_signal(sender, instance, created, **kwargs):
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.profil, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.profil, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    if instance.ecole != None:
        ecole = instance.ecole.nom
    else:
        ecole = instance.nom_ecole
    if created:
        for demande in DemandeAmi.objects.filter(Q(emetteur=instance.profil) | Q(recepteur=instance.profil)):
            if demande.emetteur == instance.profil:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            msg = "{0} <b>à ajouter une formation au sein de {1} entre: {2} et {3} sous le titre: {4}</b>".format(
                get_full_name(instance.profil), ecole, instance.annee_debut, instance.annee_fin,
                instance.titre_formation)
            Notification.objects.create(type=2, profil_to_notify=friend, profil=instance.profil, message=msg)
        for follower in Suivie.objects.filter(followed_profil=instance.profil).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à ajouter une formation au sein de {1} entre: {2} et {3} sous le titre: {4}</b>".format(
                    get_full_name(instance.profil), ecole, instance.annee_debut, instance.annee_fin,
                    instance.titre_formation)
                Notification.objects.create(type=2, profil_to_notify=p, profil=instance.profil, message=msg)
    else:
        for demande in DemandeAmi.objects.filter(Q(emetteur=instance.profil) | Q(recepteur=instance.profil)):
            if demande.emetteur == instance.profil:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            msg = "{0} <b>à modifier sa formation au sein de {1} entre: {2} et {3} sous le titre: {4}</b>".format(
                get_full_name(instance.profil), ecole, instance.annee_debut, instance.annee_fin,
                instance.titre_formation)
            Notification.objects.create(type=2, profil_to_notify=friend, profil=instance.profil, message=msg)
        for follower in Suivie.objects.filter(followed_profil=instance.profil).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à modifier sa formation au sein de {1} entre: {2} et {3} sous le titre: {4}</b>".format(
                    get_full_name(instance.profil), ecole, instance.annee_debut, instance.annee_fin,
                    instance.titre_formation)
                Notification.objects.create(type=2, profil_to_notify=p, profil=instance.profil, message=msg)


@receiver(post_save, sender=ActionBenevole)
def actionBenevole_signal(sender, instance, created, **kwargs):
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.profil, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.profil, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]
    if instance.poste != None:
        poste = instance.poste.nom_poste
    else:
        poste = instance.nom_poste
    if instance.organisme != None:
        organisme = instance.organisme.nom
    else:
        organisme = instance.nom_organisme
    if created:
        for demande in DemandeAmi.objects.filter(Q(emetteur=instance.profil) | Q(recepteur=instance.profil)):
            if demande.emetteur == instance.profil:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            msg = "{0} <b>à ajouter une action benevole au sein de {1} pour le poste {2} entre: {3} et {4}</b>".format(
                get_full_name(instance.profil), organisme, poste, instance.date_debut, instance.date_fin)
            Notification.objects.create(type=2, profil_to_notify=friend, profil=instance.profil, message=msg)
        for follower in Suivie.objects.filter(followed_profil=instance.profil).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à ajouter une action benevole au sein de {1} pour le poste {2} entre: {3} et {4}</b>".format(
                    get_full_name(instance.profil), organisme, poste, instance.date_debut, instance.date_fin)
                Notification.objects.create(type=2, profil_to_notify=p, profil=instance.profil, message=msg)
    else:
        for demande in DemandeAmi.objects.filter(Q(emetteur=instance.profil) | Q(recepteur=instance.profil)):
            if demande.emetteur == instance.profil:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            msg = "{0} <b>à modifier son action benevole au sein de {1} pour le poste {2} entre: {3} et {4}</b>".format(
                get_full_name(instance.profil), organisme, poste, instance.date_debut, instance.date_fin)
            Notification.objects.create(type=2, profil_to_notify=friend, profil=instance.profil, message=msg)
        for follower in Suivie.objects.filter(followed_profil=instance.profil).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à modifier son action benevole au sein de {1} pour le poste {2} entre: {3} et {4}</b>".format(
                    get_full_name(instance.profil), organisme, poste, instance.date_debut, instance.date_fin)
                Notification.objects.create(type=2, profil_to_notify=p, profil=instance.profil, message=msg)


@receiver(post_save, sender=LangueProfil)
def langueProfil_signal(sender, instance, created, **kwargs):
    receivedRequest = DemandeAmi.objects.filter(recepteur=instance.profil, statut=1).values()
    sentRequests = DemandeAmi.objects.filter(emetteur=instance.profil, statut=1).values()
    e = [entry for entry in receivedRequest.values('emetteur_id')]
    emetteurs = [entry['emetteur_id'] for entry in e]
    r = [entry for entry in sentRequests.values('recepteur_id')]
    recepteurs = [entry['recepteur_id'] for entry in r]

    if created:
        for demande in DemandeAmi.objects.filter(Q(emetteur=instance.profil) | Q(recepteur=instance.profil)):
            if demande.emetteur == instance.profil:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            msg = "{0} <b>à ajouter la langue: {1} pour le niveau: {2}</b>".format(get_full_name(instance.profil),
                                                                            instance.langue.nom, instance.niveau.niveau)
            Notification.objects.create(type=2, profil_to_notify=friend, profil=instance.profil, message=msg)
        for follower in Suivie.objects.filter(followed_profil=instance.profil).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à ajouter la langue: {1} pour le niveau: {2}</b>".format(get_full_name(instance.profil),
                                                                                instance.langue.nom,
                                                                                instance.niveau.niveau)
                Notification.objects.create(type=2, profil_to_notify=p, profil=instance.profil, message=msg)
    else:
        for demande in DemandeAmi.objects.filter(Q(emetteur=instance.profil) | Q(recepteur=instance.profil)):
            if demande.emetteur == instance.profil:
                friend = demande.recepteur
            else:
                friend = demande.emetteur
            msg = "{0} <b>à modifier la langue: {1} pour le niveau: {2}</b>".format(get_full_name(instance.profil),
                                                                             instance.langue.nom,
                                                                             instance.niveau.niveau)
            Notification.objects.create(type=2, profil_to_notify=friend, profil=instance.profil, message=msg)
        for follower in Suivie.objects.filter(followed_profil=instance.profil).values('follower'):
            p = Profil.objects.get(id=follower['follower'])
            if p.id not in emetteurs and p.id not in recepteurs:
                msg = "{0} <b>à modifier la langue: {1} pour le niveau: {2}</b>".format(get_full_name(instance.profil),
                                                                                 instance.langue.nom,
                                                                                 instance.niveau.niveau)
                Notification.objects.create(type=2, profil_to_notify=p, profil=instance.profil, message=msg)
