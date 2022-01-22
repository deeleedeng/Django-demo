# Create your views here.

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import Question, Choice


# django 通用视图
class IndexView(generic.ListView):
    """
    IndexViwe：需要提供一个问题列表，也就是 lastest_question_list
    template_name: 指定 ListView 使用的模版，否则 django 将寻找默认模版 <app name>/<model name>_list.html
    context_object_name：指定模版中使用的 context 变量，否则 django 将使用默认变量 question_list
    """
    template_name = 'polls/index.html'
    context_object_name = 'lastest_question_list'

    def get_queryset(self):
        # 返回最新的 5 条问题，通过 django 提供的数据库 API 操作数据
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """
    DetailView：需要提供一个 question 对象以及模版
    model：model 变量可以提供一个模型对象，也就是 question
    """
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    """
    ResulstView：需要提供一个 question 对象以及模版
    model：model 变量可以提供一个模型对象，也就是 question
    """
    model = Question
    template_name = 'polls/results.html'


# 以下为普通视图
def index(request):
    # 战士最新发布的 5 条问题
    lastet_question_list = Question.objects.order_by('-pub_date')[:5]

    # output = ', '.join([q.question_text for q in lastet_question_list])
    # return HttpResponse(output)

    # template = loader.get_template('polls/index.html')
    # context = {
    #     "lastest_question_list": lastet_question_list
    # }
    # return HttpResponse(template.render(context, request))

    context = {"lastest_question_list": lastet_question_list}
    return render(request, 'polls/index.html', context)


def detail(reqeust, question_id):
    # 问题详情页面

    # try:
    #     question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #     raise Http404('Question is not exist')
    # return render(reqeust, 'polls/detail.html', {"question": question})

    question = get_object_or_404(Question, pk=question_id)
    return render(reqeust, 'polls/detail.html', {"question": question})


def results(request, question_id):
    # 问题投票结果页面

    # return HttpResponse(f"You're looking at the results of question {question_id}")

    questtion = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {"question": questtion})


def vote(request, question_id):
    # 投票页面

    # return HttpResponse(f"You'er voting on question {queston_id}")

    question = get_object_or_404(Question, pk=question_id)
    try:
        select_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            "question": question,
            "error_message": "You didn't select a choice."
        })
    else:
        select_choice.votes += 1
        select_choice.save()

        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
