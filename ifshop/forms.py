import re
from django import forms
from django.forms import modelformset_factory
from .models import Camiseta, ProdutoBase, PedidoBase, PedidoCamiseta, UsuarioCustomizado, ImagemProdutoBase, EstiloTamanho, Curso, Avaliacao, VendeCrud
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm



######################## login e cadastro de usuario  #############################       
        
class CadastroUsuarioForm(UserCreationForm):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}),
        empty_label="Selecione um curso"
    )
    
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
    
    telefone = forms.CharField(
        min_length=10,
        max_length=100,
        widget=forms.TextInput(attrs={'type': 'number', 'class': 'form-control rounded-3 ', 'placeholder': 'Ex.: 8499999999'}))
    
    foto = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = UsuarioCustomizado
        fields = ['nome', 'email', 'telefone', 'curso', 'password1', 'password2', 'foto' ]
        

class UsuarioEditarForm(UserChangeForm):
    # Remova os campos de senha do formulário de edição
    password = None
    
    class Meta:
        model = UsuarioCustomizado
        fields = ['nome', 'telefone', 'curso', 'foto']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'curso': forms.Select(attrs={'type': 'number', 'class': 'form-control rounded-3 ', 'placeholder': 'Ex.: 8499999999'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remova o campo password completamente
        self.fields.pop('password', None) 
        
class LoginUsuarioForm(AuthenticationForm):
    username = forms.EmailField(label="Email",widget=forms.EmailInput(attrs={'class': 'form-control rounded-3 '}))
    password = forms.CharField(label="Senha",widget=forms.PasswordInput(attrs={'class': 'form-control rounded-3 '}))
    
### Filtro ###
class FiltroAvaliacoesForm(forms.Form):
    ORDENACAO_OPCOES = [
        ('-data_criacao', 'Mais Recentes'),
        ('data_criacao', 'Mais Antigas'),
        ('-estrelas', 'Melhores Avaliações'),
        ('estrelas', 'Piores Avaliações'),
    ]
    
    ESTRELAS_OPCOES = [
        ('', 'Todas as Estrelas'),
        (5, '⭐️⭐️⭐️⭐️⭐️ (5 estrelas)'),
        (4, '⭐️⭐️⭐️⭐️ (4 estrelas)'),
        (3, '⭐️⭐️⭐️ (3 estrelas)'),
        (2, '⭐️⭐️ (2 estrelas)'),
        (1, '⭐️ (1 estrela)'),
    ]
    
    ordenacao = forms.ChoiceField(
        choices=ORDENACAO_OPCOES,
        required=False,
        initial='-data_criacao',
        label='Ordenar por',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estrelas = forms.ChoiceField(
        choices=ESTRELAS_OPCOES,
        required=False,
        label='Filtrar por estrelas',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    apenas_com_comentarios = forms.BooleanField(
        required=False,
        initial=False,
        label='Apenas avaliações com comentários',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class FiltroProdutoForm(forms.Form):
    turnos = forms.ChoiceField(
        choices=[
            ('', 'Todos os Turnos'),  
            ('Matutino', 'Matutino'),
            ('Vespertino', 'Vespertino'),
            ('Noturno', 'Noturno')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm d-inline p-2'})
    )
    cursos = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        required=False,
        empty_label="Todos os Cursos",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm d-inline p-2'})
    )

class FiltroPedidosForm(forms.Form):
    status = forms.ChoiceField(
        choices=[
            ('', 'Todos os Pedidos'),  
            ('Pendente', 'Pendente'),
            ('Pago Totalmente', 'Pago Totalmente'),
            ('Pago 1° Parcela', 'Pago 1° Parcela'),
            ('Negociando com Usuario', 'Negociando com Usuario'),
            ('Entregue', 'Entregue')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm d-inline p-2'})
    )
    
### Filtro ###

class ProdutoBaseForm(forms.ModelForm):
    data_limite_pedidos = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-3'}), 
        required=True
    )
    
    data_pag1 = forms.DateField(
        label="Data para pagamento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-3'}), 
        required=True
    )
    
    data_pag2 = forms.DateField(
        label="Data para pagamento da segunda parcela",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control rounded-3'}), 
        required=False
    )
    
    titulo = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control rounded-3','placeholder': 'Ex.: Camisa De InfoWeb4M...'}), 
        required=True
    )
    
    preco = forms.DecimalField(
        label="Preço Total",
        widget=forms.NumberInput(attrs={'class': 'form-control rounded-3','placeholder': 'Ex.: 00,00'}), 
        required=True
    )
    
    preco_parcela = forms.DecimalField(
        label="Preço Parcelas",
        widget=forms.NumberInput(attrs={'class': 'form-control rounded-3','placeholder': 'Ex.: 00,00'}), 
        required=False
    )
    
    forma_pag_op = forms.MultipleChoiceField(
        choices=ProdutoBase.FORMA_PAG_OPCOES,
        label='Formas de Pagamento Disponíveis',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'd-inline-block form-check-input'}), 
        required=True
    )
    
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}),
        required=True,
        label="Cursos deste produto"
    )
    
    turma = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control rounded-3','placeholder': 'Ex.: InfoWeb4M'}), 
        required=True
    )
    
    turnos = forms.ChoiceField(
        choices=ProdutoBase.TURNOS_OPCOES,
        widget=forms.Select(attrs={'class': 'form-select rounded-3'}), 
        required=True
    )
    
    pix_qr_code_total = forms.ImageField(
        label="Imagem Do QrCode Total",
        widget=forms.FileInput(attrs={'class': 'form-control'}), 
        required=False
    )
    
    pix_qr_code_parcela = forms.ImageField(
        label="Imagem Do QrCode Parcela",
        widget=forms.FileInput(attrs={'class': 'form-control'}), 
        required=False
    )
    
    pix_chave_total = forms.CharField(
        label="Coloque a chave pix para o pagamento",
        widget=forms.TextInput(attrs={'class': 'form-control'}), 
        required=False
    )
    
    pix_chave_parcela = forms.CharField(
        label="Coloque a chave pix para o pagamento",
        widget=forms.TextInput(attrs={'class': 'form-control'}), 
        required=False
    )
    class Meta:
        model = ProdutoBase
        fields = ['titulo', 'preco', 'preco_parcela', 'forma_pag_op', 'opcoes', 'data_limite_pedidos', 'curso', 
                  'turnos', "pix_qr_code_parcela", "pix_qr_code_total", "pix_chave_parcela", "pix_chave_total",
                  "turma", "data_pag1", "data_pag2"]
        widgets = {
            'opcoes': forms.TextInput(attrs={'placeholder': 'Ex: azul, vermelho, verde'})
        }

    def save(self, commit=True):
        produto = super().save(commit=False)
        if 'forma_pag_op' in self.cleaned_data:
            formas_pagamento = self.cleaned_data['forma_pag_op']
            produto.forma_pag_op = ", ".join(formas_pagamento)
        
        if 'opcoes' in self.cleaned_data and self.cleaned_data['opcoes']:
            opcoes_texto = self.cleaned_data['opcoes']
            if isinstance(opcoes_texto, str):
                opcoes_lista = [opcao.strip() for opcao in opcoes_texto.split(",") if opcao.strip()]
                produto.opcoes = ", ".join(opcoes_lista)
        
        if commit:
            produto.save()
            self.save_m2m()
        
        return produto

    
ImagemProdutoBaseFormSet = modelformset_factory(
    ImagemProdutoBase,
    fields=('imagem', 'principal'),
    extra=4,
    can_delete=True,
    widgets={
        'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)

class CamisetaForm(ProdutoBaseForm):
    tamanhos = forms.MultipleChoiceField(
        choices=Camiseta.TAMANHOS_OPCOES,
        label='Tamanhos',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    estilos = forms.MultipleChoiceField(
        choices=Camiseta.ESTILOS_OPCOES,
        label='Estilos',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )

    class Meta(ProdutoBaseForm.Meta):
        model = Camiseta
        fields = ProdutoBaseForm.Meta.fields + ['tamanhos', 'estilos']

    def clean(self):
        cleaned_data = super().clean()
        estilos = cleaned_data.get("estilos", [])
        tamanhos_por_estilo = {}

        for estilo in estilos:
            tamanhos = self.data.getlist(f"tamanhos_{estilo}")
            if tamanhos:
                tamanhos_por_estilo[estilo] = tamanhos

        cleaned_data['tamanhos'] = tamanhos_por_estilo
        return cleaned_data   

    def save(self, commit=True):
        camiseta = super().save(commit=False)
        camiseta.tamanhos = self.cleaned_data['tamanhos']
        camiseta.estilos = ", ".join(self.cleaned_data['estilos'])

        if commit:
            camiseta.save()
            EstiloTamanho.objects.filter(camiseta=camiseta).delete()
            for estilo, tamanhos in self.cleaned_data['tamanhos'].items():
                for tamanho in tamanhos:
                    EstiloTamanho.objects.create(
                        camiseta=camiseta,
                        estilo=estilo,
                        tamanho=tamanho
                    )
        return camiseta

####################################################################################################      

class PedidoBaseForm(forms.ModelForm):
    opcao_escolhida = forms.ChoiceField(label="Escolha uma opção", choices=[], required=True)
    
    comprovante_total = forms.ImageField(
        label="Anexe o Comprovante",
        widget=forms.FileInput(attrs={'class': 'form-control'}), required=False
    )
    
    comprovante_parcela1 = forms.ImageField(
        label="Anexe o Comprovante da Primeira Parcela",
        widget=forms.FileInput(attrs={'class': 'form-control'}), required=False
    )
    
    comprovante_parcela2 = forms.ImageField(
        label="Anexe o Comprovante da Segunda Parcela",
        widget=forms.FileInput(attrs={'class': 'form-control'}), required=False
    )
    
    forma_pag = forms.ChoiceField(
        label="Forma de Pagamento",
        widget=forms.Select(attrs={'class': 'card-text mb-auto form-select'})
    )

    class Meta:
        model = PedidoBase
        fields = ['opcao_escolhida', "forma_pag", "comprovante_total", "comprovante_parcela1", "comprovante_parcela2"]
        
    def __init__(self, *args, **kwargs):
        produto = kwargs.pop('produto', None)  
        forma_pag_opcoes = kwargs.pop('forma_pag_opcoes', [])
        
        super().__init__(*args, **kwargs)

        self.fields['forma_pag'].choices = [(op, op) for op in forma_pag_opcoes]
        
        if produto:
            opcoes_disponiveis = produto.lista_opcoes()
            if opcoes_disponiveis:
                self.fields['opcao_escolhida'].choices = [(opcao, opcao) for opcao in opcoes_disponiveis]
            else:
                self.fields['opcao_escolhida'].choices = [("", "Nenhuma opção disponível")]
                self.fields['opcao_escolhida'].widget.attrs['disabled'] = True


class PedidoCamisetaForm(forms.ModelForm):
    nome_estampa = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'card-text mb-auto form-control'})
    )
    
    numero_estampa = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'card-text mb-auto form-control'})
    )
    
    tamanho = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'card-text mb-auto form-select', 'id': 'id_tamanho'})
    )
    
    estilo = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'card-text mb-auto form-select', 'id': 'id_estilo'})
    )

    class Meta:
        model = PedidoCamiseta
        fields = ['nome_estampa', 'numero_estampa', 'tamanho', 'estilo']
        
    def __init__(self, *args, **kwargs):
        tamanhos_opcoes = kwargs.pop('tamanhos_opcoes', [])
        estilos_opcoes = kwargs.pop('estilos_opcoes', [])
        super().__init__(*args, **kwargs)

        self.fields['tamanho'].choices = [(op, op) for op in tamanhos_opcoes]
        self.fields['estilo'].choices = [(op, op) for op in estilos_opcoes]


class AlterarStatusPedidoForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=PedidoBase.STATUS_OPCOES, 
        widget=forms.Select(attrs={'class': 'card-text mb-auto form-select'})
    )
    
    class Meta:
        model = PedidoBase
        fields = ['status']


class AnexoComprovantesPedidoForm(forms.ModelForm):
    comprovante_total = forms.ImageField(
        label="Anexe o Comprovante",
        widget=forms.FileInput(attrs={'class': 'form-control'}), required=False
    )
    
    comprovante_parcela1 = forms.ImageField(
        label="Anexe o Comprovante da Primeira Parcela",
        widget=forms.FileInput(attrs={'class': 'form-control'}), required=False
    )
    
    comprovante_parcela2 = forms.ImageField(
        label="Anexe o Comprovante da Segunda Parcela",
        widget=forms.FileInput(attrs={'class': 'form-control'}), required=False
    )
    
    class Meta:
        model = PedidoBase
        fields = ['comprovante_total', 'comprovante_parcela1', 'comprovante_parcela2']

        
class AvaliacaoForm(forms.ModelForm):
    estrelas = forms.ChoiceField(
        choices=Avaliacao.ESTRELAS_OPCOES,
        widget=forms.RadioSelect(attrs={
            'class': 'estrelas-radio',
            'style': 'display: none;'  # Esconde os radios padrão
        }),
        label='',
        required=True
    )
    
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Compartilhe sua experiência com este produto... (opcional)',
            'maxlength': '500'
        }),
        required=False,
        label='Comentário'
    )
    
    class Meta:
        model = Avaliacao
        fields = ['estrelas', 'comentario']
        labels = {
            'estrelas': 'Sua Avaliação',
            'comentario': 'Comentário (opcional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar labels das estrelas
        self.fields['estrelas'].choices = [
            (1, '1 Estrela - Péssimo'),
            (2, '2 Estrelas - Ruim'),
            (3, '3 Estrelas - Regular'),
            (4, '4 Estrelas - Bom'),
            (5, '5 Estrelas - Excelente'),
        ]
    
    def clean_estrelas(self):
        estrelas = self.cleaned_data.get('estrelas')
        if estrelas:
            return int(estrelas)
        return estrelas
    
    def clean_comentario(self):
        comentario = self.cleaned_data.get('comentario')
        if comentario and len(comentario.strip()) < 10:
            raise forms.ValidationError(
                "O comentário deve ter pelo menos 10 caracteres."
            )
        return comentario
    
class VendForm(forms.ModelForm):
    texto = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control rounded-3', 'placeholder': 'Informe seu nome, turma, matricula e motivo para querer vender...'}), 
        required=True
    )
    class Meta:
        model = VendeCrud
        fields = ['texto']