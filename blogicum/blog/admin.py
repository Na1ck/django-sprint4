from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Category, Location, Post, Comment

User = get_user_model()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
        'get_comment_count',
    )
    list_editable = ('is_published',)
    list_filter = (
        'is_published',
        'category',
        'location',
        'pub_date',
        'created_at',
    )
    search_fields = ('title', 'text')
    filter_horizontal = ()
    date_hierarchy = 'pub_date'
    raw_id_fields = ('author',)
    readonly_fields = ('created_at', 'get_comment_count')
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'image', 'author')
        }),
        ('Дополнительные опции', {
            'fields': (
                'pub_date',
                'location',
                'category',
                'is_published',
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def get_comment_count(self, obj):
        return obj.comment.count()
    get_comment_count.short_description = 'Количество комментариев'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'author',
        'created_at',
    )
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'post__title', 'author__username')
    readonly_fields = ('created_at',)
