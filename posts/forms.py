from django.db.models import fields
from django.forms import ModelForm, Textarea, widgets

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите сюда что-нибудь...'
            })
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Расскажите, что думаете по этому поводу?',
            })
        }
