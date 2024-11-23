from django import forms
from .models import Camiseta, Pedido, Cor



class CamisetaForm(forms.ModelForm):
    tamanhos = forms.MultipleChoiceField(
        choices=Camiseta.TAMANHOS_OPCOES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'd-inline-block form-check-input'
        }),
        required=True
    )
    estilos = forms.MultipleChoiceField(
        choices=Camiseta.ESTILOS_OPCOES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'd-inline-block form-check-input '
        }),
        required=True
    )
    data_limite_pedidos = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',  # Usa o calendário do navegador
            'class': 'form-control rounded-3',
        }),
        required=True
    )
    data_para_entrega = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',  # Usa o calendário do navegador
            'class': 'form-control rounded-3',
        }),
        required=True
    )
    titulo = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-3',
        })
    )
    cores_input = forms.CharField(
        max_length=400,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-3',
        })
    )
    preco = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control rounded-3',
        })
    )
    cursos = forms.ChoiceField(
        choices=Camiseta.CURSOS_OPCOES,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-3',
        })
    )
    turnos = forms.ChoiceField(
        choices=Camiseta.TURNOS_OPCOES,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-3',
        })
    )
    imagem = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control rounded-3',
        })
    )
    class Meta:
        model = Camiseta
        fields = ['titulo', 'preco', 'data_limite_pedidos', 'data_para_entrega', 'tamanhos', 'estilos', 'imagem', 'turnos', 'cursos']

    def save(self, commit=True):
        camiseta = super().save(commit=False)
        cores_texto = self.cleaned_data.get('cores_input', '')
        cores_nomes = [nome.strip().lower() for nome in cores_texto.split(',') if nome.strip()]
        cores_objetos = []

        for nome in cores_nomes:
            cor, created = Cor.objects.get_or_create(nome=nome)
            cores_objetos.append(cor)

        if commit:
            camiseta.save()
            camiseta.cores.set(cores_objetos)
            camiseta.save()

        return camiseta

        

class PedidoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        tamanhos_opcoes = kwargs.pop('tamanhos_opcoes', [])
        estilos_opcoes = kwargs.pop('estilos_opcoes', [])
        super().__init__(*args, **kwargs)

        self.fields['tamanho'].choices = [(op, op) for op in tamanhos_opcoes]
        self.fields['estilo'].choices = [(op, op) for op in estilos_opcoes]

    nome_estampa = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }))
    numero_estampa = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }))
    tamanho = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    estilo = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    cor = forms.ModelChoiceField(
        queryset=Cor.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    class Meta:
        model = Pedido
        fields = ['nome_estampa', 'numero_estampa', 'tamanho', 'estilo', "cor"]