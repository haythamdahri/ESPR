from django.contrib import admin
from .models import Courses,Formation,Theme,Lessons,Exam,Question


# Register your models here.



class PageAdmin_1(admin.ModelAdmin):
    list_display=('libelle', 'date_creation')
    ordering=('libelle',)
    search_fields=('libelle',)
admin.site.register(Formation,PageAdmin_1)

class PageAdmin_2(admin.ModelAdmin):
    list_display=('id', 'libelle')
    ordering=('libelle',)
    search_fields=('libelle',)
admin.site.register(Theme,PageAdmin_2)

class PageAdmin(admin.ModelAdmin):
    list_display=('course_title', 'course_price')
    ordering=('course_title',)
    search_fields=('course_title',)

admin.site.register(Courses,PageAdmin)

class PageAdmin_3(admin.ModelAdmin):
    list_display=('lesson_title', 'lesson_duration')
    ordering=('lesson_title',)
    search_fields=('lesson_title',)
admin.site.register(Lessons,PageAdmin_3)

class PageAdmin_4(admin.ModelAdmin):
    list_display=('id', 'name')
    ordering=('id',)
    search_fields=('id',)
admin.site.register(Exam,PageAdmin_4)
admin.site.register(Question)



