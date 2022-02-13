# Register your models here.

from django.contrib import admin
from .models import Question, Choice


# 通过 admin.ModelAdmin 在后台新增功能以及展示内容，通过 register 到 amdin 后台

# 新增 Question 页面，同时展示所需要的 Choice，个数由 extra 决定，需要在 QuestionAdmin 中声明 inlines
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


# Question 展示页面，新增展示的字段 list_display，以及搜索功能 search_fields，过滤功能 list_filter
# Question 新增页面，通过 fieldssets 字段来定义展示的项和内容
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'pub_date', 'was_published_recently']
    search_fields = ['question_text']
    list_filter = ['pub_date']

    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ('Date information', {"fields": ["pub_date"], "classes": ["collape"]})
    ]
    inlines = [ChoiceInline]


# Choice 展示页面，新增展示的字段 list_display
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'votes', 'question']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
