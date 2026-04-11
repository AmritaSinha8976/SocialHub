"""
Posts app forms.
Handles post creation and comment submission.
"""

from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Form for creating and editing posts."""

    class Meta:
        model = Post
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write a caption...',
                'maxlength': 2200,
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'postImageInput',
            }),
        }

    def clean(self):
        """Require at least an image or a caption."""
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        caption = cleaned_data.get('caption', '').strip()
        if not image and not caption:
            raise forms.ValidationError('A post must have an image or a caption.')
        return cleaned_data


class CommentForm(forms.ModelForm):
    """Form for submitting comments."""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add a comment...',
                'maxlength': 1000,
                'autocomplete': 'off',
            }),
        }
        labels = {'text': ''}
