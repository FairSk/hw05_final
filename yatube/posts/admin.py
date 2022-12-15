from django.contrib import admin

from .models import Group, Post, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class CommentwAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'text'
    )
    search_fields = ('post', 'author')
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment, CommentwAdmin)
