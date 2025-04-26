from django.contrib import admin
from .models import BlogPost, BlogComment, SavedPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'views', 'createdAt']
    list_filter = ['status']
    search_fields = ['title', 'content']
    readonly_fields = ['views', 'slug', 'readTime']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'content', 'createdAt']
    list_filter = ['post']
    search_fields = ['content']
    readonly_fields = ['user', 'createdAt']

@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'savedAt']
    list_filter = ['user']
    search_fields = ['post__title']
    readonly_fields = ['user', 'savedAt'] 