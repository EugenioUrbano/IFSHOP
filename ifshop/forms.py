from django import forms
from .models import Camiseta, Pedido, Cor, UsuarioCustomizado
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field


######################## login e cadastro de usuario  #############################       
        
class CadastroUsuarioForm(UserCreationForm):
    curso = forms.ChoiceField(
        choices=Camiseta.CURSOS_OPCOES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3 '}))
    
    nome = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control rounded-3 '}))
    
    email = forms.EmailField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control rounded-3 '}))
    
    password1 = forms.CharField(
        label="Digite uma senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control rounded-3 '}))
    
    password2 = forms.CharField(
        label="Confirme a senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control rounded-3 '}))
    
    matricula_cpf = forms.CharField(
        label="Matricula ou CPF",
        widget=forms.TextInput(attrs={'class': 'form-control rounded-3', 'placeholder': 'Somente numeros sem espaço', 'type': 'number'}))
    
    telefone = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'type': 'number', 'class': 'form-control rounded-3 ', 'placeholder': 'Somente numeros sem espaço'}))
    
    class Meta:
        model = UsuarioCustomizado
        fields = ['nome', 'email', 'telefone', 'matricula_cpf', 'curso', 'password1', 'password2' ]
        
    
    
        
class LoginUsuarioForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(),)
    password = forms.CharField(label="Senha", widget=forms.PasswordInput())
    
### Filtro ###
class FiltroProdutoForm(forms.Form):
    turnos = forms.ChoiceField(
        choices=[
            ('', 'Todos os Turnos'),  
            ('matutino', 'Matutino'),
            ('vespertino', 'Vespertino'),
            ('noturno', 'Noturno')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm d-inline p-2'})
    )
    cursos = forms.ChoiceField(
        choices=[
            ('', 'Todos os Cursos'),  
            ('infoweb', 'InfoWeb'),
            ('edific', 'Edific'),
            ('mamb', 'Mamb'),
            ('outro', 'Outro'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm d-inline p-2'})
    )
### Filtro ###

class CamisetaForm(forms.ModelForm):
    tamanhos = forms.MultipleChoiceField(
        choices=Camiseta.TAMANHOS_OPCOES,
        label= 'Tamanhos',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'd-inline-block form-check-input' }), required=True)
    
    estilos = forms.MultipleChoiceField(
        choices=Camiseta.ESTILOS_OPCOES,
        label= 'Estilos' ,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'd-inline-block form-check-input '}), required=True)
    
    data_limite_pedidos = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-3 ',}), required=True)
    
    data_para_entrega = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-3',}), required=True)
    
    titulo = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control rounded-3','placeholder': 'Ex.: Camisa De InfoWeb4M...'}))
    
    cores_input = forms.CharField(
        max_length=400,
        label="Cores",
        widget=forms.TextInput(attrs={'class': 'form-control rounded-3','placeholder': 'Ex.: Vermelho, Azul, Roxo...'}))
    
    preco = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control rounded-3','placeholder': 'Ex.: 00,00'}))
    
    cursos = forms.ChoiceField(
        choices=Camiseta.CURSOS_OPCOES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3',}))
    
    turnos = forms.ChoiceField(
        choices=Camiseta.TURNOS_OPCOES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3',}))
    
    imagem = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control rounded-3',}))
    
    class Meta:
        model = Camiseta
        fields = ['titulo', 'preco', 'cores_input', 'imagem', 'data_limite_pedidos', 'data_para_entrega', 'cursos', 'turnos', 'tamanhos', 'estilos']

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

####################################################################################################      

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
            'class': 'card-text mb-auto form-control',}))
    
    numero_estampa = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'card-text mb-auto form-control',}))
    
    tamanho = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'card-text mb-auto form-select',}))
    
    estilo = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'card-text mb-auto form-select',}))
    
    cor = forms.ModelChoiceField(
        queryset=Cor.objects.all(),
        widget=forms.Select(attrs={'class': 'card-text mb-auto form-select',}))

    class Meta:
        model = Pedido
        fields = ['nome_estampa', 'numero_estampa', 'tamanho', 'estilo', "cor"]