from django.test import TestCase

# Create your tests here.

import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        超过一天的未来的时间，was_published_recently() 应返回 False
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        一天之前的时间，was_published_recently() 应返回 False
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        一天之内的时间，was_published_recently() 应返回 False
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    根据 question_text days 参数创建一个 question，日期可以是过去也可以是未来
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTest(TestCase):

    def test_no_question(self):
        """
        如果没有问题，页面应返回 No polls are available
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['lastest_question_list'], [])

    def test_past_question(self):
        """
        创建一个过去日期的 question
        """
        question = create_question(question_text='Past question', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['lastest_question_list'], [question])

    def test_future_question(self):
        """
        创建一个未来日期的 question
        """
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['lastest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        同时存在一天之前的日期 question 和一天之后的日期 question，只展示一天之前的 question
        """
        queston = create_question(question_text='Past question', days=-30)
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['lastest_question_list'], [queston])

    def test_two_past_question(self):
        """
        如果有多条一天之内或之前的 question，应展示多条
        """
        question1 = create_question(question_text='Past question1', days=-30)
        question2 = create_question(question_text='Past question2', days=-5)
        response = self.client.get((reverse('polls:index')))
        self.assertQuerysetEqual(response.context['lastest_question_list'], [question2, question1])


class QuestionDetailViewTest(TestCase):

    def test_future_question(self):
        """
        查询未来日期的 question 的详情会报 404
        """
        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        查询当天内或之前的 question 详情正确展示
        """
        past_question = create_question(question_text='Past question', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class TemplateTest(TestCase):

    @classmethod
    def setUpClass(cls):
        time = timezone.now()
        Question.object.create(id=1, question_text="Which you will choice?", pub_date=time)
        Question.object.create(id=2, question_text="Which you will choice?")
        Choice.object.create(question=1, choice_text="choice one", votes=5)
        Choice.object.create(question=1, choice_text="choice two", votes=10)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_indextemplate(self):
        response = self.client.get('/polls/')
        self.assertTemplateUsed(response, 'polls/index.html')
