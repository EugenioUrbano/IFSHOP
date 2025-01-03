from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Camiseta, Pedido, ImagemCamiseta
from .forms import CamisetaForm, PedidoForm, FiltroProdutoForm, CadastroUsuarioForm, LoginUsuarioForm, ImagemCamisetaFormSet

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
        'camisetas': camisetas,
        'pedidos': pedidos,
        'camisetas_com_imagens': camisetas_com_imagens
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
    pedidos = Pedido.objects.all()
    if request.user.is_authenticated:
        camisetas = Camiseta.objects.filter(vendedor=request.user)  
    else:
        camisetas = [] 

    return render(request, 'perfil.html', {'camisetas': camisetas, 'pedidos': pedidos})

####################################################################################################

def cadastro_usuario(request):
    pedidos = Pedido.objects.all()
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('index') 
    else:
        form = CadastroUsuarioForm()
    return render(request, 'cadastro.html', {'form': form, 'pedidos': pedidos})

####################################################################################################

def carrinho(request):
    pedidos = Pedido.objects.all()

    if request.method == "POST" and 'deletar' in request.POST:
        pedido_id = request.POST.get('pedido_id')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.delete()
        return redirect('carrinho')
    return render(request, "carrinho.html", {'pedidos': pedidos})

####################################################################################################

def camiseta(request, camiseta_id):
    camiseta = Camiseta.objects.get(id=camiseta_id)
    pedidos = Pedido.objects.all()
    
    tamanhos_opcoes = [t.strip() for t in camiseta.tamanhos.split(',')]
    estilos_opcoes = [e.strip() for e in camiseta.estilos.split(',')]

    if request.method == 'POST':
        form = PedidoForm(request.POST, tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.camiseta = camiseta
            pedido.usuario = request.user
            pedido.save()
            return redirect('carrinho')
    else:
        form = PedidoForm(tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes)

    return render(request, 'camiseta.html', {'camiseta': camiseta, 'form': form, 'pedidos': pedidos})

####################################################################################################

@login_required
@user_passes_test(vendedor)
def adicionar_pro(request):
    pedidos = Pedido.objects.all()
    if request.method == 'POST':
        form = CamisetaForm(request.POST, request.FILES)
        formset = ImagemCamisetaFormSet(request.POST, request.FILES, queryset=ImagemCamiseta.objects.none())

        if form.is_valid() and formset.is_valid():
            camiseta = form.save(commit=False)
            camiseta.vendedor = request.user
            camiseta.tamanhos = ', '.join(form.cleaned_data['tamanhos'])
            camiseta.estilos = ', '.join(form.cleaned_data['estilos'])
            camiseta.save()
            
            for form in formset:
                if form.cleaned_data.get('imagem'):
                    imagem = form.save(commit=False)
                    imagem.camiseta = camiseta
                    imagem.save()
            
            return redirect('index')  # Redirecionar para uma página de sucesso

    else:
        form = CamisetaForm()
        formset = ImagemCamisetaFormSet(queryset=ImagemCamiseta.objects.none())
    
    return render(request, 'adicionar_pro.html', {
        'form': form,
        'pedidos': pedidos,
        'formset': formset,
    })

####################################################################################################

@login_required
@user_passes_test(vendedor)
def gerenciar_pro(request):
    pedidos = Pedido.objects.all()
    if request.user.is_authenticated:
        camisetas = Camiseta.objects.filter(vendedor=request.user) 
        if request.method == "POST" and 'deletar' in request.POST:
            camiseta_id = request.POST.get('camiseta_id')
            camiseta = camiseta.objects.get(id=camiseta_id)
            camiseta.delete()
            return redirect('gerenciar_pro')
    else:
        camisetas = []
    return render(request, 'gerenciar_pro.html', {'camisetas': camisetas, 'pedidos': pedidos})

####################################################################################################

@login_required
@user_passes_test(vendedor)
def gerenciar_pedidos(request):
    if request.user.is_authenticated:
        pedidos = Pedido.objects.filter(vendedor=request.user)  
    else:
        pedidos = [] 
    return render(request, 'gerenciar_pro.html', {'pedidos': pedidos})