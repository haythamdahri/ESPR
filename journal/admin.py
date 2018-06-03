from django.contrib import admin

from .models import Journalist, Category, News, Image, Tag, Newsletter, Video, Comment, Answer, \
    SignalComment, SignalAnswer, CommentFilter, ImageNews, Supervisor, ContactMessage, JoinMessage

admin.site.site_header = "BTP Administration"
admin.site.site_title = "BTP Administration"


@admin.register(Journalist)
class JournalistAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'date_creation', 'active']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ('first_name', 'last_name')
    list_filter = ('active',)
    date_hierarchy = 'date_creation'
    actions = ['active_journalist', 'deactivate_journalist']

    def active_journalist(self, request, queryset):
        for journalist in queryset:
            journalist.active = True
            journalist.save()
    active_journalist.short_description = 'Activer les Journalistes sélectionnés'

    def deactivate_journalist(self, request, queryset):
        for journalist in queryset:
            journalist.active = False
            journalist.save()
    deactivate_journalist.short_description = 'Désactiver les Journalistes sélectionnés'


@admin.register(Category)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'displayed_text', 'color', 'icon', 'tab_home']
    search_fields = ['name', 'displayed_text']
    ordering = ('name',)


@admin.register(Tag)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color']
    ordering = ('name',)
    search_fields = ['name']


@admin.register(News)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date_publication', 'view_number', 'comment_enable', 'share_enable', 'journalist',
                    'category', 'active', 'approved']
    search_fields = ['title']
    ordering = ('-date_publication',)
    list_filter = ['category', 'journalist', 'approved', 'active', 'share_enable', 'comment_enable', 'tag']
    date_hierarchy = 'date_publication'
    actions = ['active_articles', 'active_comment', 'active_share', 'deactivate_articles', 'deactivate_comment',
               'deactivate_share']

    def active_articles(self, request, queryset):
        for article in queryset:
            article.active = True
            article.save()
    active_articles.short_description = 'Activer les Articles sélectionnés'

    def deactivate_articles(self, request, queryset):
        for article in queryset:
            article.active = False
            article.save()
    deactivate_articles.short_description = 'Désactiver les Articles sélectionnés'

    def active_comment(self, request, queryset):
        for article in queryset:
            article.comment_enable = True
            article.save()
    active_comment.short_description = 'Activer les commentaires pour les Articles sélectionnés'

    def deactivate_comment(self, request, queryset):
        for article in queryset:
            article.comment_enable = False
            article.save()
    deactivate_comment.short_description = 'Désactiver les commentaires pour les Articles sélectionnés'

    def active_share(self, request, queryset):
        for article in queryset:
            article.share_enable = True
            article.save()
    active_share.short_description = 'Activer le partage pour les Articles sélectionnés'

    def deactivate_share(self, request, queryset):
        for article in queryset:
            article.share_enable = False
            article.save()
    deactivate_share.short_description = 'Désactiver le partage pour les Articles sélectionnés'


@admin.register(Video)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date_publication', 'video_url', 'view_number', 'journalist',
                    'active', 'approved']
    search_fields = ['title']
    ordering = ('-date_publication',)
    list_filter = ['category', 'journalist', 'data_merge', 'approved', 'active', 'share_enable', 'comment_enable', 'tag']
    date_hierarchy = 'date_publication'
    actions = ['active_videos', 'active_comment', 'active_share', 'deactivate_videos', 'deactivate_comment',
               'deactivate_share']

    def active_videos(self, request, queryset):
        for article in queryset:
            article.active = True
            article.save()
    active_videos.short_description = 'Activer les Videos sélectionnés'

    def deactivate_videos(self, request, queryset):
        for article in queryset:
            article.active = False
            article.save()
    deactivate_videos.short_description = 'Désactiver les Videos sélectionnés'

    def active_comment(self, request, queryset):
        for article in queryset:
            article.comment_enable = True
            article.save()
    active_comment.short_description = 'Activer les commentaires pour les Videos sélectionnés'

    def deactivate_comment(self, request, queryset):
        for article in queryset:
            article.comment_enable = False
            article.save()
    deactivate_comment.short_description = 'Désactiver les commentaires pour les Videos sélectionnés'

    def active_share(self, request, queryset):
        for article in queryset:
            article.share_enable = True
            article.save()
    active_share.short_description = 'Activer le partage pour les Videos sélectionnés'

    def deactivate_share(self, request, queryset):
        for article in queryset:
            article.share_enable = False
            article.save()
    deactivate_share.short_description = 'Désactiver le partage pour les Videos sélectionnés'


@admin.register(Image)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'date_publication']
    date_hierarchy = 'date_publication'
    ordering = ('-date_publication',)


@admin.register(ImageNews)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'date_publication', 'article']
    date_hierarchy = 'date_publication'
    ordering = ('-date_publication',)


@admin.register(Comment)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'full_name', 'news', 'date_publication', 'number_like']
    date_hierarchy = 'date_publication'
    search_fields = ['email', 'full_name']
    ordering = ('-date_publication',)


@admin.register(Answer)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'full_name', 'comment', 'date_publication', 'number_like']
    date_hierarchy = 'date_publication'
    search_fields = ['email', 'full_name']
    ordering = ('-date_publication',)


@admin.register(SignalComment)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'comment', 'cause', 'date_send']
    date_hierarchy = 'date_send'
    search_fields = ['email']
    ordering = ('-date_send',)
    actions = ['delete_comment']

    def delete_comment(self, request, queryset):
        for signal in queryset:
            signal.comment.delete()
            signal.delete()
    delete_comment.short_description = 'Supprimer les commentaires correspondants aux Signals sélectionnés'


@admin.register(SignalAnswer)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'answer', 'cause', 'date_send']
    date_hierarchy = 'date_send'
    search_fields = ['email']
    ordering = ('-date_send',)
    actions = ['delete_comment']

    def delete_comment(self, request, queryset):
        for signal in queryset:
            signal.answer.delete()
            signal.delete()
    delete_comment.short_description = 'Supprimer les réponses correspondants aux Signals sélectionnés'


@admin.register(Newsletter)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['email', 'register_date', 'active']
    date_hierarchy = 'register_date'
    search_fields = ['email']
    ordering = ('-register_date',)
    actions = ['deactivate', 'activate']
    list_filter = ['active']

    def deactivate(self, request, queryset):
        for n in queryset:
            n.active = False
            n.save()
    deactivate.short_description = 'Désactiver les Newsletter selectionnés'

    def activate(self, request, queryset):
        for n in queryset:
            n.active = True
            n.save()
    activate.short_description = 'Activer les Newsletter selectionnés'


@admin.register(CommentFilter)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'word']


@admin.register(ContactMessage)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'name', 'date_send', 'website', 'open']
    date_hierarchy = 'date_send'
    search_fields = ['email', 'name']
    ordering = ('-date_send',)
    actions = ['open', 'n_open']
    list_filter = ['open']

    def open(self, request, queryset):
        for message in queryset:
            message.open = True
            message.save()
    open.short_description = 'Marquer les Messages sélectionnés comme lu'

    def n_open(self, request, queryset):
        for message in queryset:
            message.open = False
            message.save()
    n_open.short_description = 'Marquer les Messages sélectionnés comme non lu'


@admin.register(Supervisor)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'active', 'date_creation']
    date_hierarchy = 'date_creation'
    search_fields = ['email']
    ordering = ('-date_creation',)
    actions = ['activate', 'deactivate']
    list_filter = ['active']

    def activate(self, request, queryset):
        for s in queryset:
            s.active = True
            s.save()
    activate.short_description = 'Activer les Superviseurs sélectionnés'

    def deactivate(self, request, queryset):
        for s in queryset:
            s.active = False
            s.save()
    deactivate.short_description = 'Désactiver les Superviseurs sélectionnés'


@admin.register(JoinMessage)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'date_send', 'website', 'read']
    date_hierarchy = 'date_send'
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ('-date_send',)
    actions = ['open', 'n_open']
    list_filter = ['read']

    def open(self, request, queryset):
        for message in queryset:
            message.read = True
            message.save()
    open.short_description = 'Marquer les Messages sélectionnés comme lu'

    def n_open(self, request, queryset):
        for message in queryset:
            message.read = False
            message.save()
    n_open.short_description = 'Marquer les Messages sélectionnés comme non lu'
