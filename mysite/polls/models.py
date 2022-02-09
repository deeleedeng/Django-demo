# Create your models here.

"""
继承 django Model 类，定义模型的字段名，django 会默认给表定义 ID 字段，并设置为主键
__str__：默认返回内容，如果没有这个方法，当实例化类时展示的是 Object 对象，不会展示 Object 的内容

django ORM 常用方法：
新增：

查询：
Question.objects.all 查询所有，相当于 sql - select * from Question
Question.objects.get(id=1) 查询 id=1 的数据，相当于 sql - select * from Question where id=1，如果没有查到则报错
Question.objects.filter(id=1) 和 get 类似，不一样的地方是，如果没有查到则返回空列表，不会报错

更新：

删除：

"""

import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    # admin.display 装饰器，用来根据某个对象值，设置是否展示对应的项
    # 比如下面是根据 was_published_recently 方法返回的布尔值来确定在页面上是否展示该项
    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    # 关联外键，Question 表的主键，on_delete 参数：关联模式（假如 Question 不存在了，关联的 Choice 是否删除？）
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
