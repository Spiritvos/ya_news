from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError


from news.forms import WARNING, BAD_WORDS
from news.models import Comment


UNIVERSAL_PK = (1,)

NEWS_URL = reverse('news:detail', args=UNIVERSAL_PK)
COMMENT_EDIT = reverse('news:edit', args=UNIVERSAL_PK)
COMMENT_DELETE = reverse('news:delete', args=UNIVERSAL_PK)


# Авторизованный пользователь может редактировать свои комментарии.
def test_author_can_edit_comment(
    author_client, author, form_data, news, comment
):
    response = author_client.post(COMMENT_EDIT, form_data)
    assertRedirects(response, NEWS_URL + '#comments')
    comment.refresh_from_db()
    update_comment = Comment.objects.get()
    assert update_comment.news == news
    assert update_comment.text == form_data['text']
    assert update_comment.author == author


# Авторизованный пользователь не может редактировать чужие комментарии.
def test_other_user_cant_edit_comment(admin_client, form_data, news, comment):
    start_comment = Comment.objects.get()
    response = admin_client.post(COMMENT_EDIT, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    end_comment = Comment.objects.get()
    assert start_comment == end_comment


# Анонимный пользователь не может отправить комментарий.
def test_user_can_create_comment(author_client, author, form_data, news):
    assert Comment.objects.count() == 0
    author_client.post(NEWS_URL, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


# Авторизованный пользователь может отправить комментарий.
@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data):
    assert Comment.objects.count() == 0
    client.post(NEWS_URL, data=form_data)
    assert Comment.objects.count() == 0


# Вызываем фикстуру отдельной заметки, чтобы в базе появилась запись.
def test_warning_word(admin_client, news, form_data):
    assert Comment.objects.count() == 0
    form_data['text'] = f'Бранное слово {BAD_WORDS[0]}...'
    response = admin_client.post(NEWS_URL, data=form_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


# Авторизованный пользователь может удалять свои комментарии.
def test_author_can_delete_note(author_client, comment):
    assert Comment.objects.count() == 1
    response = author_client.post(COMMENT_DELETE)
    assertRedirects(response, NEWS_URL + '#comments')
    assert Comment.objects.count() == 0


# Авторизованный пользователь не может удалять чужие комментарии.
def test_other_user_cant_delete_note(admin_client, comment):
    assert Comment.objects.count() == 1
    response = admin_client.post(COMMENT_DELETE)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
