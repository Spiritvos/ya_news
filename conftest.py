import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Алеша')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news

@pytest.fixture
def id_news_for_args(news):
    return (news.id,)

@pytest.fixture
def id_comment_for_args(comment):
    return (comment.id,)

@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст коментария',
    )
    return comment