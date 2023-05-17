from django import forms
from .models import User, Profile, Upload, Voto
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    aceito = forms.BooleanField(widget=forms.CheckboxInput(),
                           label=mark_safe('Aceito a <a class="x" href="https://www.vorwerk.com/pt/pt/c/home/geral/politica-de-privacidade" target="_blank">Política de Privacidade</a>'))

    class Meta:
        model = User
        fields = ['email', 'username', 'last_name', 'aceito', 'role']
        help_texts = {
            'password1': '',
            'password2': ''
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['hidden'] = True
        self.fields['password2'].widget.attrs['hidden'] = True
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['email'].label = 'E-mail'
        self.fields['aceito'].required = True


class ProfileRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].required = False


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)
        self.initial['user'] = User.objects.get(id=user_id)


class VotoForm(forms.ModelForm):
    class Meta:
        model = Voto
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)
        self.initial['upload'] = Upload.objects.get(user=user_id)