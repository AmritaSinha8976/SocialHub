from django import forms
from .models import Story

class StoryForm(forms.ModelForm):
    class Meta:
        model  = Story
        fields = ['image','caption','text_color','text_size','text_align','text_style',
                  'bg_color','bg_gradient','filter_name','stickers_json',
                  'music_title','music_artist','poll_question','poll_option_a','poll_option_b']
        widgets = {
            'image':          forms.FileInput(attrs={'accept':'image/*','id':'storyImageFile'}),
            'caption':        forms.TextInput(attrs={'placeholder':'Type something...','maxlength':300}),
            'text_color':     forms.TextInput(attrs={'type':'color'}),
            'text_size':      forms.NumberInput(attrs={'min':12,'max':80,'step':2}),
            'text_align':     forms.Select(),
            'text_style':     forms.Select(),
            'bg_color':       forms.TextInput(attrs={'type':'color'}),
            'bg_gradient':    forms.HiddenInput(),
            'filter_name':    forms.HiddenInput(),
            'stickers_json':  forms.HiddenInput(),
            'music_title':    forms.TextInput(attrs={'placeholder':'Song title','maxlength':100}),
            'music_artist':   forms.TextInput(attrs={'placeholder':'Artist','maxlength':100}),
            'poll_question':  forms.TextInput(attrs={'placeholder':'Ask a question...','maxlength':120}),
            'poll_option_a':  forms.TextInput(attrs={'placeholder':'Option A','maxlength':60}),
            'poll_option_b':  forms.TextInput(attrs={'placeholder':'Option B','maxlength':60}),
        }

    def clean(self):
        cd = super().clean()
        if not cd.get('image') and not cd.get('caption','').strip():
            raise forms.ValidationError('Add an image or some text.')
        return cd
