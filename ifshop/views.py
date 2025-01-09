from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Camiseta, Pedido, ImagemCamiseta
from .forms import CamisetaForm, PedidoForm, AlterarStatusPedidoForm, FiltroProdutoForm, CadastroUsuarioForm, LoginUsuarioForm, ImagemCamisetaFormSet

def index(request):
    form = FiltroProdutoForm(request.GET) 
    
    camisetas =Camiseta.objects.all()
    pedidos = Pedido.objects.all()
    
    if form.is_valid():
        turnos = form.cleaned_data.get('turnos')
        cursos = form.cleaned_data.get('cursos')

        if turnos:  
            camisetas = camisetas.filter(turnos=turnos)

        if cursos:  
            camisetas = camisetas.filter(cursos=cursos)
            
    camisetas_com_imagens = []
    for camiseta in camisetas:
        imagem_principal = camiseta.imagens.filter(principal=True).first() or camiseta.imagens.first()
        camisetas_com_imagens.append({'camiseta': camiseta, 'imagem_principal': imagem_principal})
        
    context = {
        'form': form,
        'pedidos': pedidos,
        'camisetas_com_imagens': camisetas_com_imagens,
    }
    return render(request, 'index.html', context )

####################################################################################################

def vendedor(user):
    return user.vendedor

def login_view(request):
    pedidos = Pedido.objects.all()
    
    if request.method == 'POST':
        form = LoginUsuarioForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()  
            login(request, user)
            return redirect('perfil')  
    else:
        form = LoginUsuarioForm()
    return render(request, 'login.html', {'form': form, 'pedidos': pedidos})

def logout_usuario(request):
    logout(request) 
    return redirect('login')

####################################################################################################

@login_required
def perfil(request):
    camisetas = Camiseta.objects.filter(vendedor=request.user)
    
    pedidos_relacionados = Pedido.objects.filter(camiseta__vendedor=request.user)
    
    pedidos_feitos = Pedido.objects.filter(cliente=request.user)
    
    pedidos = pedidos_relacionados | pedidos_feitos
    
    pedidos = pedidos.distinct()
    
    camisetas_com_imagens = []
    for camiseta in camisetas:
        imagem_principal = (
            camiseta.imagens.filter(principal=True).first() 
            or camiseta.imagens.first()
        )
        camisetas_com_imagens.append({'camiseta': camiseta, 'imagem_principal': imagem_principal})

    return render(request, 'perfil.html', {'pedidos': pedidos, 'camisetas_com_imagens': camisetas_com_imagens})

####################################################################################################

def cadastro_usuario(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('index') 
    else:
        form = CadastroUsuarioForm()
    return render(request, 'cadastro.html', {'form': form})

####################################################################################################

def carrinho(request):
    if request.method == "POST" and 'deletar' in request.POST:
        pedido_id = request.POST.get('pedido_id')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.delete()
        return redirect('carrinho')

    return render(request, "carrinho.html")
    


####################################################################################################

def camiseta(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta.objects.prefetch_related('imagens'), id=camiseta_id)
    tamanhos_opcoes = [t.strip() for t in camiseta.tamanhos.split(',')]
    estilos_opcoes = [e.strip() for e in camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in camiseta.forma_pag_op.split(',')]

    form = PedidoForm(
        tamanhos_opcoes=tamanhos_opcoes,
        estilos_opcoes=estilos_opcoes,
        forma_pag_opcoes=forma_pag_opcoes
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "Você precisa estar logado para fazer um pedido. Por favor, faça login ou cadastro.")
        else:
            form = PedidoForm(
                request.POST,
                tamanhos_opcoes=tamanhos_opcoes,
                estilos_opcoes=estilos_opcoes,
                forma_pag_opcoes=forma_pag_opcoes
            )
            if form.is_valid():
                pedido = form.save(commit=False)
                pedido.camiseta = camiseta
                pedido.cliente = request.user
                pedido.save()
                messages.success(request, "Pedido adicionado com sucesso!")
                return redirect('carrinho')

    return render(request, 'camiseta.html', {'camiseta': camiseta, 'form': form})

####################################################################################################

@login_required
@user_passes_test(vendedor)
def adicionar_pro(request):
    camisetas =Camiseta.objects.all()
    
    camisetas_com_imagens = []
    for camiseta in camisetas:
        imagem_principal = camiseta.imagens.filter(principal=True).first() or camiseta.imagens.first()
        camisetas_com_imagens.append({'camiseta': camiseta, 'imagem_principal': imagem_principal}) 
        
    if request.method == 'POST':
        form = CamisetaForm(request.POST, request.FILES)
        formset = ImagemCamisetaFormSet(request.POST, request.FILES, queryset=ImagemCamiseta.objects.none())

        if form.is_valid() and formset.is_valid():
            camiseta = form.save(commit=False)
            camiseta.vendedor = request.user
            camiseta.tamanhos = ', '.join(form.cleaned_data['tamanhos'])
            camiseta.estilos = ', '.join(form.cleaned_data['estilos'])
            camiseta.forma_pag_op = ', '.join(form.cleaned_data['forma_pag_op'])
            camiseta.save()
            
            for form in formset:
                if form.cleaned_data.get('imagem'):
                    imagem = form.save(commit=False)
                    imagem.camiseta = camiseta
                    imagem.save()
            
            return redirect('index')  

    else:
        form = CamisetaForm()
        formset = ImagemCamisetaFormSet(queryset=ImagemCamiseta.objects.none())
    
    return render(request, 'adicionar_pro.html', {
        'form': form,
        'formset': formset,
        'camisetas_com_imagens': camisetas_com_imagens
    })

####################################################################################################

@login_required
@user_passes_test(vendedor)
def gerenciar_pro(request):
    camisetas_com_imagens = []
    
    if request.user.is_authenticated:
        camisetas = Camiseta.objects.filter(vendedor=request.user) 
        
        if request.method == "POST" and 'deletar' in request.POST:
            camiseta_id = request.POST.get('camiseta_id')
            
            camiseta_selecionada = Camiseta.objects.get(id=camiseta_id)
            camiseta_selecionada.delete()
            return redirect('gerenciar_pro')
        
        for camiseta in camisetas:
            imagem_principal = camiseta.imagens.filter(principal=True).first() or camiseta.imagens.first()
            camisetas_com_imagens.append({'camiseta': camiseta, 'imagem_principal': imagem_principal})

    return render(request, 'gerenciar_pro.html', {'camisetas_com_imagens': camisetas_com_imagens,})
    
def edit_produto(request):
    return render(request, 'edit_produto.html')

####################################################################################################

@login_required
@user_passes_test(vendedor)
def gerenciar_pedidos(request):
    camisetas_vendedor = Camiseta.objects.filter(vendedor=request.user)
    pedidos = Pedido.objects.filter(camiseta__in=camisetas_vendedor)

    if request.method == 'POST':
        for pedido in pedidos:
            form = AlterarStatusPedidoForm(request.POST, instance=pedido)
            if form.is_valid():
                form.save()  
                messages.success(request, f"Status do pedido {pedido.id} atualizado com sucesso!")
            else:
                messages.error(request, f"Erro ao atualizar o status do pedido {pedido.id}.")
        return redirect('gerenciar_pedidos')

    pedidos_com_forms = []
    for pedido in pedidos:
        form = AlterarStatusPedidoForm(instance=pedido)
        pedidos_com_forms.append({'pedido': pedido, 'form': form})

    return render(request, 'gerenciar_pedidos.html', {'pedidos_com_forms': pedidos_com_forms})

####################################################################################################

@login_required
def edit_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    # Define opções para o formulário (baseadas no modelo relacionado à camiseta)
    tamanhos_opcoes = [t.strip() for t in pedido.camiseta.tamanhos.split(',')]
    estilos_opcoes = [e.strip() for e in pedido.camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in pedido.camiseta.forma_pag_op.split(',')]

    if request.method == 'POST':
        # Preenche o formulário com os dados enviados para edição
        form = PedidoForm(request.POST, instance=pedido, tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes,forma_pag_opcoes=forma_pag_opcoes)
        if form.is_valid():
            form.save()
            messages.success(request, "Pedido atualizado com sucesso!")
            return redirect('carrinho')  # Redireciona para o carrinho ou outra página
    else:
        # Inicializa o formulário com os dados atuais do pedido
        form = PedidoForm(instance=pedido, tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes, forma_pag_opcoes=forma_pag_opcoes)

    return render(request, 'edit_pedido.html', {'form': form, 'pedido': pedido})

@login_required
@user_passes_test(vendedor)
def edit_produto(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta, id=camiseta_id, vendedor=request.user)

    # Cria um formset para as imagens associadas à camiseta
    ImagemCamisetaFormSet = modelformset_factory(
        ImagemCamiseta,
        fields=('imagem', 'principal'),
        extra=1,
        can_delete=True
    )
    
    # Inicializa os forms
    if request.method == 'POST':
        form = CamisetaForm(request.POST, request.FILES, instance=camiseta)
        formset = ImagemCamisetaFormSet(request.POST, request.FILES, queryset=ImagemCamiseta.objects.filter(camiseta=camiseta))

        if form.is_valid() and formset.is_valid():
            # Salva a camiseta com os novos dados
            camiseta = form.save(commit=False)
            camiseta.tamanhos = ', '.join(form.cleaned_data['tamanhos'])
            camiseta.estilos = ', '.join(form.cleaned_data['estilos'])
            camiseta.forma_pag_op = ', '.join(form.cleaned_data['forma_pag_op'])
            camiseta.save()

            # Salva as imagens associadas
            for img_form in formset:
                if img_form.cleaned_data.get('imagem') or img_form.cleaned_data.get('DELETE'):
                    imagem = img_form.save(commit=False)
                    imagem.camiseta = camiseta
                    if img_form.cleaned_data.get('DELETE'):
                        imagem.delete()
                    else:
                        imagem.save()

            messages.success(request, "Camiseta atualizada com sucesso!")
            return redirect('index')
        else:
            messages.error(request, "Corrija os erros no formulário.")
    else:
        form = CamisetaForm(instance=camiseta)
        formset = ImagemCamisetaFormSet(queryset=ImagemCamiseta.objects.filter(camiseta=camiseta))

    return render(request, 'edit_produto.html', {
        'form': form,
        'formset': formset,
        'camiseta': camiseta
    })
