from django.contrib.auth import get_user_model
from django import forms
from .models import Post

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Поле должно быть заполнено')
        return data
