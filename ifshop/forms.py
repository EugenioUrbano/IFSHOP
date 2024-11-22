from django import forms
from .models import Camiseta, Pedido

class CamisetaForm(forms.ModelForm):
    tamanhos = forms.MultipleChoiceField(
        choices=Camiseta.TAMANHOS_OPCOES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'd-inline-block form-check-inline'
        }),
        required=True
    )
    estilos = forms.MultipleChoiceField(
        choices=Camiseta.ESTILOS_OPCOES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'd-inline-block form-check-inline'
        }),
        required=True
    )
    data_limite_pedidos = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',  # Usa o calendário do navegador
            'class': 'form-control',
        }),
        required=True
    )
    data_para_entrega = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',  # Usa o calendário do navegador
            'class': 'form-control',
        }),
        required=True
    )
    titulo = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o titulo da camisa',
        })
    )
    imagens = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
        })
    )
    cores = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Digite as cores. Ex.: Azul, Roxo, Vermelho',
        })
    )
    preco = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o preço da camiseta',
        })
    )
    cursos = forms.ChoiceField(
        choices=Camiseta.CURSOS_OPCOES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    turnos = forms.ChoiceField(
        choices=Camiseta.TURNOS_OPCOES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    class Meta:
        model = Camiseta
        fields = ['titulo', 'preco', 'data_limite_pedidos', 'data_para_entrega' ,'cores', 'tamanhos', 'estilos', 'imagens', 'turnos', 'cursos']
        
        


class PedidoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        tamanhos_opcoes = kwargs.pop('tamanhos_opcoes', [])
        estilos_opcoes = kwargs.pop('estilos_opcoes', [])
        super().__init__(*args, **kwargs)

        self.fields['tamanho'].choices = [(op, op) for op in tamanhos_opcoes]
        self.fields['estilo'].choices = [(op, op) for op in estilos_opcoes]

    nome_estampa = forms.CharField(max_length=50)
    numero_estampa = forms.IntegerField()
    tamanho = forms.ChoiceField()
    estilo = forms.ChoiceField()

    class Meta:
        model = Pedido
        fields = ['nome_estampa', 'numero_estampa', 'tamanho', 'estilo']