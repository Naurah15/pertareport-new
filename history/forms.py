# forum/forms.py
from django import forms
from .models import ForumEntry, Comment

class ForumEntryForm(forms.ModelForm):
    class Meta:
        model = ForumEntry
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'text-center'}),
            'description': forms.Textarea(attrs={'class': 'text-center'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']