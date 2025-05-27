from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Post, Category


def posts():
    now_date = timezone.now()
    post = Post.objects.select_related(
        'author',
        'location',
        'category'
    ).filter(
        is_published=True,
        pub_date__lte=now_date,
        category__is_published=True,
    )
    return post


def index(request):
    post = posts().order_by('-pub_date')[:5]

    context = {'post_list': post}

    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = get_object_or_404(
        posts(),
        id=id,
    )

    context = {'post': post}

    return render(request, 'blog/detail.html', context)


def category_posts(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug,
        is_published=True,
    )

    post = posts().filter(
        category=category,
    ).order_by('-pub_date')

    context = {
        'category': category,
        'post_list': post
    }

    return render(request, 'blog/category.html', context)
