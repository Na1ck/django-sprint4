from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from .mixins import (
    AuthRedirectToPostMixin, AuthorRequiredMixin, CommentMixin, PaginatorMixin
)


class ProfileView(PaginatorMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._profile_user = None

    @property
    def profile_user(self):
        if self._profile_user is None:
            username = self.kwargs.get('username')
            self._profile_user = get_object_or_404(User, username=username)
        return self._profile_user

    def get_queryset(self):
        queryset = Post.objects.filter(author=self.profile_user)
        if not self.request.user == self.profile_user:
            queryset = Post.objects.published()

        return queryset.select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile_user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostListView(PaginatorMixin, ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self
        return context


class CategoryListView(PaginatorMixin, LoginRequiredMixin, ListView):
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    slug_url_kwarg = 'category_slug'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._category = None

    @property
    def category(self):
        if self._category is None:
            slug = self.kwargs['category_slug']
            self._category = get_object_or_404(
                Category.objects.filter(is_published=True),
                slug=slug
            )
        return self._category

    def get_queryset(self):
        return Post.objects.by_category(
            category=self.category
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        if post.author != self.request.user:
            queryset = Post.objects.published()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related(
            'author'
        ).order_by('created_at')

        return context


class PostEditView(AuthorRequiredMixin, AuthRedirectToPostMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(CommentMixin, UpdateView):
    fields = ['text']


class CommentDeleteView(CommentMixin, DeleteView):
    pass
