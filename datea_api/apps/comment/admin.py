from django.contrib import admin
from comment.models import Comment

class CommentAdmin(admin.ModelAdmin):
    model = Comment

admin.site.register(Comment, CommentAdmin)
