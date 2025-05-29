from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from .models import Comment

# Количество постов на странице
POST_ON_PAGE = 10


class PaginatorMixin:
    paginate_by = POST_ON_PAGE


class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class CommentMixin(LoginRequiredMixin, AuthorRequiredMixin):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
    raise_exception = True

    def test_func(self):
        """Строгая проверка - только автор может удалить"""
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )


class AuthRedirectToPostMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        post_id = self.kwargs.get('post_id')
        return redirect('blog:post_detail', post_id=post_id)
