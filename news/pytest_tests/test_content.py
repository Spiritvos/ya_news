from datetime import timedelta

import pytest
from django.shortcuts import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


TIME_NOW = timezone.now()
HOME_URL = reverse('news:home')

# Количество новостей на главной странице — не более 10.
# Новости отсортированы от самой свежей к самой старой. 
# Свежие новости в начале списка.
@pytest.mark.django_db
def test_news_sort_count(client):
    News.objects.bulk_create(
        News(
            title=f'Новость № {index}',
            text='Набор буковок',
            date=TIME_NOW - timedelta(weeks=index)
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert len(object_list) == NEWS_COUNT_ON_HOME_PAGE
    assert all_dates == sorted(all_dates, reverse=True)


# Комментарии на странице отдельной новости отсортированы в хронологическом 
# порядке: старые в начале списка, новые — в конце.
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_news_for_args')),
    )
)
def test_commemt_sort(client, author, news, name, args):
    for index in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Флуд № {index}'
        )
        comment.created = TIME_NOW - timedelta(hours=index)
        comment.save()
    url = reverse(name, args=args)
    response = client.get(url)
    object_list = response.context['news'].comment_set.all()
    all_comments = [comment.created for comment in object_list]
    assert all_comments == sorted(all_comments)


# Анонимному пользователю недоступна форма для отправки комментария на 
# странице отдельной новости, а авторизованному доступна.
@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_news',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_news_for_args')),
    )
)
def test_pages_contains_form(parametrized_client, form_in_news, name, args):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_news 