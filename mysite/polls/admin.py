from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Question, Choice


# 通过 admin.ModelAdmin 在后台新增功能以及展示内容，通过 register 到 amdin 后台

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'pub_date', 'was_published_recently']
    search_fields = ['question_text']
    list_filter = ['pub_date']

    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ('Date information', {"fields": ["pub_date"], "classes": ["collape"]})
    ]
    inlines = [ChoiceInline]


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'votes', 'question']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
