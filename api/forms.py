from django import forms
from django.contrib.auth import authenticate, login, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from .models import Post, UserProfile


# La seguente classe permette la gestione del form per la scrittura dei posts
class PostForm(forms.ModelForm):
    title = forms.CharField(label=_('Titolo'), max_length=200, required=True, widget=forms.TextInput(attrs={
                            'class': 'form-control', 'placeholder': 'Scrivi qui il titolo che vuoi dare al tuo post.'}))
    content = forms.CharField(label=_('Contenuto'), required=True, widget=forms.TextInput(attrs={
                            'class': 'form-control', 'placeholder': 'Scrivi qui il contenuto del tuo post.'}))

    class Meta:
        model = Post
        fields = ['title', 'content']

    # Le seguenti funzioni introducono un sistema di controllo che proibisca l'inserimento della parola "hack" sia
    # nei titoli che nei contenuti di ciascun post
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if 'hack' in title.lower():
            return None
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if 'hack' in content.lower():
            return None
        return content


username_validator = UnicodeUsernameValidator()


# La seguente classe permette la gestione del form per la registrazione
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label=_('Nome'), max_length=20, min_length=3, required=True,
                                 help_text='Obbligatorio: inserisci il tuo nome.',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mario'}))
    last_name = forms.CharField(label=_('Cognome'), max_length=20, min_length=3, required=True,
                                help_text='Obbligatorio: inserisci il tuo cognome.',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rossi'}))
    password1 = forms.CharField(label=_('Password'), help_text='La tua password non può essere troppo simile alle altre'
                                ' tue informazioni, nè essere una password comunemente usata. Deve contenere almeno 8'
                                ' caratteri che non possono essere tutti numeri.',
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(label=_('Conferma password'),
                                help_text=_('Inserisci la stessa password, come conferma.'),
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    username = forms.CharField(label=_('Nome utente'), max_length=150,
                               help_text=_('Obbligatorio. 150 caratteri o meno. Solo lettere, cifre e @/./+/-/_'),
                               validators=[username_validator],
                               error_messages={'unique': _("Ci dispiace! Esiste già un utente con questo username :(")},
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MarioRossi10'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('ipAddress',)
        widgets = {'ipAddress': forms.HiddenInput()}
