from django.urls import path
from . import views


app_name = 'polls'

# 视同普通视图
# urlpatterns = [
#     # ex: /polls/
#     path('', views.index, name='index'),
#     # ex: /polls/1/
#     path('<int:question_id>/', views.detail, name='detail'),
#     # ex: /polls/1/results/
#     path('<int:question_id>/results/', views.results, name='results'),
#     # ex: /polls/1/vote/
#     path('<int:question_id>/vote/', views.vote, name='vote'),
# ]

# 使用通用视图
urlpatterns = [
    # ex: /polls/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /polls/1/
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex: /polls/1/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /polls/1/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]