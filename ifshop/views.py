from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Camiseta, Pedido
from .forms import CamisetaForm, PedidoForm

def index(request):
    camisetas = Camiseta.objects.all()
    return render(request, 'index.html', {'camisetas': camisetas})

####################################################################################################

def login(request):
    return render(request, "login.html")

####################################################################################################

def perfil(request):
    return render(request, "perfil.html")

####################################################################################################

def cadastro(request):
    
    return render(request, 'cadastro.html')

####################################################################################################

def carrinho(request):
    pedidos = Pedido.objects.all()
    if request.method == "POST" and 'deletar' in request.POST:
        pedido_id = request.POST.get('pedido_id')
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.delete()
        return redirect('carrinho')
    
    return render(request, "carrinho.html", {'pedidos': pedidos})

####################################################################################################

def camiseta(request, camiseta_id):
    camiseta = Camiseta.objects.get(id=camiseta_id)
    
    tamanhos_opcoes = [t.strip() for t in camiseta.tamanhos.split(',')]
    estilos_opcoes = [e.strip() for e in camiseta.estilos.split(',')]

    if request.method == 'POST':
        form = PedidoForm(request.POST, tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.camiseta = camiseta
            pedido.save()
            return redirect('carrinho')
    else:
        form = PedidoForm(tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes)

    return render(request, 'camiseta.html', {'camiseta': camiseta, 'form': form})

####################################################################################################

def adicionar_pro(request):
    if request.method == 'POST':
        camiseta_form = CamisetaForm(request.POST, request.FILES)

        if camiseta_form.is_valid():
            camiseta = camiseta_form.save(commit=False)
            camiseta.tamanhos = ', '.join(camiseta_form.cleaned_data['tamanhos'])
            camiseta.estilos = ', '.join(camiseta_form.cleaned_data['estilos'])
            camiseta.save()
            return redirect('index')
          
    
    else:
        camiseta_form = CamisetaForm()
    return render(request, 'adicionar_pro.html', {'camiseta_form': camiseta_form})

####################################################################################################