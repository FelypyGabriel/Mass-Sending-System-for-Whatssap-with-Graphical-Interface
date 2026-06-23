from django import forms
from .models import Contato

class MensagemForm(forms.Form):
    contatos = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="números de telefone (um por linha)"
    )
    mensagem = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        label="mensagem"
    )

class ContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'nome completo'}),
            'telefone': forms.TextInput(attrs={'placeholder': '+55 ...'}),
        }