from django.contrib import admin
from qa.models import *
from django_markdown.admin import MarkdownModelAdmin
from django_markdown.widgets import AdminMarkdownWidget
from django.db.models import TextField


# admin.site.register(Answer, MarkdownModelAdmin)
# class YourModelAdmin(MarkdownModelAdmin):
#     formfield_overrides = {TextField: {'widget': AdminMarkdownWidget}}
class YourModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownWidget},
    }

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_title', 'reward'] 

admin.site.register(Question , QuestionAdmin)
admin.site.register(Answer)    
admin.site.register(Comment)
admin.site.register(Tag)
# admin.site.register(Profil)
admin.site.register(Voter)
admin.site.register(Categorie)
admin.site.register(Level)
admin.site.register(Blog_qa)
admin.site.register(Answer_blog)
admin.site.register(blog_Voter)
