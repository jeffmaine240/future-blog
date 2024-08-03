from django.contrib import admin
from .models import Post, Comment

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = [ 'status', 'created', 'publish']
    search_fields = [ 'status', 'created', 'publish', 'title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    search_fields = ['name', 'email', 'body']
    list_filter = ['active', 'created', 'updated']


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)