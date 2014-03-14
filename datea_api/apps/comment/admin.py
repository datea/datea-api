from django.contrib import admin
from .models import Comment

class CommentAdmin(admin.ModelAdmin):
    model = Comment

admin.site.register(Comment, CommentAdmin)
