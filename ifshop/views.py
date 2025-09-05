from .forms import CamisetaForm, PedidoBaseForm, PedidoCamisetaForm, AlterarStatusPedidoForm, FiltroProdutoForm, FiltroPedidosForm, CadastroUsuarioForm, LoginUsuarioForm, ImagemProdutoBaseFormSet, AnexoComprovantesPedidoForm
from .models import Camiseta, ProdutoBase, PedidoBase, ImagemProdutoBase, EstiloTamanho, PedidoCamiseta, UsuarioCustomizado
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import openpyxl, json, os


# ---- index ----- #

def index(request):
    form = FiltroProdutoForm(request.GET) 
    
    camisetas = Camiseta.objects.all()
    produto = ProdutoBase.objects.all()
    
    if form.is_valid():
        turnos = form.cleaned_data.get('turnos')
        cursos = form.cleaned_data.get('cursos')

        if turnos:  
            camisetas = camisetas.filter(produto__turnos=turnos)
            produto = produto.filter(produto__turnos=turnos)


        if cursos:
            camisetas = camisetas.filter(produto__cursos__id=cursos.id)
            produto = produto.filter(produto__cursos__id=cursos.id)

    
    produtos = list(camisetas) + list(produto)

    produtos_com_imagens = []
    data_hoje = now().date()
    
    for produto in produtos:
        base = produto.produto if hasattr(produto, "produto") else produto
        imagem_principal = base.imagens.filter(principal=True).first() or base.imagens.first()
        
        data_limite = base.data_limite_pedidos
        disponivel = data_hoje <= data_limite if data_limite else True
        
        produtos_com_imagens.append({
            'produto': produto, 
            'imagem_principal': imagem_principal, 
            'disponivel': disponivel
        })
    
    paginator = Paginator(produtos_com_imagens, 9)
    numero_da_pagina = request.GET.get('pagina')  
    produtos_paginadas = paginator.get_page(numero_da_pagina)
    
    context = {'form': form, 'produtos_com_imagens': produtos_paginadas,}
    
    return render(request, 'index.html', context)

# ---- usuario ----- #

def vendedor(user):
    return user.vendedor

def login_view(request):
    if request.method == 'POST':
        form = LoginUsuarioForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()  
            login(request, user)
            return redirect('index')  
    else:
        form = LoginUsuarioForm()
    return render(request, 'login.html', {'form': form})

def logout_usuario(request):
    logout(request) 
    return redirect('login')

@login_required
def perfil(request):
    produtos = ProdutoBase.objects.filter(vendedor=request.user)

    if request.user.vendedor:
        pedidos_recebidos = PedidoBase.objects.filter(produto__in=produtos)
    else:
        pedidos_recebidos = []

    produtos_com_imagens = []
    for produto in produtos:
        imagem_principal = (
            produto.imagens.filter(principal=True).first()
            or produto.imagens.first()
        )
        produtos_com_imagens.append({
            'produto': produto,
            'imagem_principal': imagem_principal
        })

    context = {
        "pedidos_recebidos": pedidos_recebidos,
        "produtos_com_imagens": produtos_com_imagens,
    }
    return render(request, "perfil.html", context)

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


# ---- utilidades do site ----- #

def tamanhos_por_estilojson(request):
    camiseta_id = request.GET.get('camiseta_id')
    estilo = request.GET.get('estilo')

    tamanhos = EstiloTamanho.objects.filter(camiseta_id=camiseta_id, estilo=estilo).values_list('tamanho', flat=True)
    return JsonResponse(list(tamanhos), safe=False)

def exportar_pedidos_camisetas_excel(request):
    camisetas_vendedor = Camiseta.objects.filter(vendedor=request.user)
    
    pedidos = PedidoCamiseta.objects.filter(
        camiseta__in=camisetas_vendedor,
        status__in=["Pago Totalmente", "Pago 1° Parcela"]
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pedidos Pagos"

    ws.append(['Nome na Estampa', 'Número na Estampa', 'Estilo', 'Tamanho', 'Opção de Cor'])

    for pedido in pedidos:
        ws.append([
            pedido.nome_estampa,
            pedido.numero_estampa,
            pedido.estilo,
            pedido.tamanho,
            pedido.pedido.opcao_escolhida
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=pedidos_pagos.xlsx'
    wb.save(response)
    return response

@login_required
def verificar_pedidos(request):
    pedidos_novos = PedidoBase.objects.filter(camiseta__vendedor=request.user, visto=False).count()
    return JsonResponse({"pedidos_novos": pedidos_novos})

@login_required
@csrf_exempt 
def marcar_pedidos_vistos(request):
    if request.method == "POST":
        PedidoBase.objects.filter(camiseta__vendedor=request.user, visto=False).update(visto=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Método inválido"}, status=400)

# ---- pedidos ----- #

@login_required
def carrinho(request):
    pedidos_feitos = PedidoBase.objects.filter(cliente=request.user).select_related('produto')

    if request.method == "POST" and 'deletar' in request.POST:
        pedido_id = request.POST.get('pedido_id')
        pedido = get_object_or_404(PedidoBase, id=pedido_id, cliente=request.user)
        pedido.delete()
        return redirect('carrinho')

    hoje = timezone.localdate()
    return render(request, "carrinho.html", {
        'pedidos_feitos': pedidos_feitos,
        'hoje': hoje
    })

def excluir_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoBase, id=pedido_id, cliente=request.user)

    if request.method == "POST" and 'deletar' in request.POST:
        pedido.delete()
        return redirect('carrinho')

    return render(request, "excluir_pedido.html", {'pedido': pedido})
    
def comprovantes(request, pedido_id):
    pedido = get_object_or_404(PedidoBase, id=pedido_id, cliente=request.user)
    hoje = timezone.localdate()

    if request.method == 'POST':
        form = AnexoComprovantesPedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, "Comprovante enviado com sucesso!")
        else:
            messages.error(request, "Erro ao enviar o comprovante. Verifique os campos.")
        return redirect('comprovantes', pedido_id=pedido.id)
    else:
        form = AnexoComprovantesPedidoForm(instance=pedido)
    return render(request, 'comprovantes.html', {'form': form,'pedido': pedido,'hoje': hoje})
    
@login_required
@user_passes_test(vendedor)
def pedidos_camisetas(request):
    pedidos_all = PedidoCamiseta.objects.filter(camiseta__vendedor=request.user).order_by('-data_pedido')

    total_pedidos = pedidos_all.count()
    total_pagos = pedidos_all.filter(status='Pago Totalmente').count()
    total_pago_primeira = pedidos_all.filter(status='Pago 1° Parcela').count()

    arrecadado = sum(
        pedido.camiseta.produto.preco if pedido.pedido.status == "Pago Totalmente"
        else pedido.camiseta.produto.preco_parcela if pedido.pedido.status == "Pago 1° Parcela"
        else 0
        for pedido in pedidos_all
    )
    
    pedidos = pedidos_all

    form_filtro = FiltroPedidosForm(request.GET or None)
    if form_filtro.is_valid():
        status = form_filtro.cleaned_data.get('status')
        if status:
            pedidos = pedidos.filter(status=status)
    
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        if pedido_id:
            try:
                pedido = PedidoCamiseta.objects.get(id=pedido_id, camiseta__vendedor=request.user)
                form = AlterarStatusPedidoForm(request.POST, instance=pedido)
                if form.is_valid():
                    form.save()
                    messages.success(request, f"Status do pedido {pedido_id} atualizado com sucesso!")
                    return redirect('pedidos_camisetas') 
                else:
                    messages.error(request, f"Erro ao atualizar o pedido {pedido_id}.")
            except PedidoCamiseta.DoesNotExist:
                messages.error(request, f"Pedido {pedido_id} não encontrado.")

    pedidos_com_forms = []
    for pedido in pedidos:
        form = AlterarStatusPedidoForm(instance=pedido)
        pedidos_com_forms.append({'pedido': pedido, 'form': form})

    paginator = Paginator(pedidos_com_forms, 10) 
    page = request.GET.get("pagina")
    pedidos_paginados = paginator.get_page(page)

    return render(request, 'gerenciar_pedidos.html', {'pedidos_com_forms': pedidos_paginados,'form_filtro': form_filtro, 'total_pedidos': total_pedidos, 'total_pagos': total_pagos, 'total_pago_primeira': total_pago_primeira, 'arrecadado': arrecadado})
    
@login_required
def edit_pedido_camiseta(request, pedido_id):
    pedido_camiseta = get_object_or_404(
        PedidoCamiseta,
        id=pedido_id,
        pedido__cliente=request.user
    )

    pedido_base = pedido_camiseta.pedido
    produto = pedido_camiseta.camiseta.produto  

    # Opções do produto/camiseta
    tamanhos_opcoes = list({t for lista in pedido_camiseta.camiseta.tamanhos.values() for t in lista})
    estilos_opcoes = [e.strip() for e in pedido_camiseta.camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in produto.forma_pag_op.split(',')]

    if request.method == 'POST':
        form_base = PedidoBaseForm(
            request.POST,
            request.FILES,
            instance=pedido_base,
            produto=produto,
            forma_pag_opcoes=forma_pag_opcoes
        )
        form_camiseta = PedidoCamisetaForm(
            request.POST,
            instance=pedido_camiseta,
            tamanhos_opcoes=tamanhos_opcoes,
            estilos_opcoes=estilos_opcoes
        )

        if form_base.is_valid() and form_camiseta.is_valid():
            form_base.save()
            form_camiseta.save()
            messages.success(request, "Pedido de camiseta atualizado com sucesso!")
            return redirect('carrinho')

    else:
        form_base = PedidoBaseForm(
            instance=pedido_base,
            produto=produto,
            forma_pag_opcoes=forma_pag_opcoes
        )
        form_camiseta = PedidoCamisetaForm(
            instance=pedido_camiseta,
            tamanhos_opcoes=tamanhos_opcoes,
            estilos_opcoes=estilos_opcoes
        )

    context = {
        'tamanhos_por_estilo_json': json.dumps(pedido_camiseta.camiseta.tamanhos),
        'form_base': form_base,
        'form_camiseta': form_camiseta,
        'pedido_camiseta': pedido_camiseta,
        'pedido_base': pedido_base
    }
    return render(request, 'edit_pedido_camiseta.html', context)


# ---- camiseta ----- #

def camiseta(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta.objects.prefetch_related('imagens'), id=camiseta_id)
    tamanhos_opcoes = list({t for lista in camiseta.tamanhos.values() for t in lista})
    estilos_opcoes = [e.strip() for e in camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in camiseta.produto.forma_pag_op.split(',')]

    print("Camiseta carregada na View:", camiseta.produto.titulo, camiseta.produto.opcoes)
    
    form = PedidoCamisetaForm(
        camiseta=camiseta,
        tamanhos_opcoes=tamanhos_opcoes,
        estilos_opcoes=estilos_opcoes,
        forma_pag_opcoes=forma_pag_opcoes
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "Você precisa estar logado para fazer um pedido. Por favor, faça login ou cadastro.")
        else:
            form = PedidoCamisetaForm(
                request.POST,
                camiseta=camiseta,
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
    
    context = {
    'form': form,
    'camiseta': camiseta,
    'tamanhos_por_estilo_json': json.dumps(camiseta.tamanhos)
}
    
    return render(request, 'camiseta.html', context)

@login_required
@user_passes_test(vendedor)
def criar_camiseta(request):
    camisetas = Camiseta.objects.filter(vendedor=request.user)
    
    camisetas_com_imagens = []
    for camiseta in camisetas:
        imagem_principal = camiseta.imagens.filter(principal=True).first() or camiseta.imagens.first()
        camisetas_com_imagens.append({'camiseta': camiseta, 'imagem_principal': imagem_principal}) 
        
    if request.method == 'POST':
        form = CamisetaForm(request.POST, request.FILES)
        formset = ImagemProdutoBaseFormSet(request.POST, request.FILES, queryset=ImagemProdutoBase.objects.none())

        tamanhos_por_estilo = {}
            
        for estilo, _ in Camiseta.ESTILOS_OPCOES:
            tamanhos_marcados = request.POST.getlist(f'tamanhos_{estilo}')
            if tamanhos_marcados:
                tamanhos_por_estilo[estilo] = tamanhos_marcados

        if not request.POST.getlist('estilos'):
            form.add_error('estilos', 'Você deve selecionar pelo menos um estilo.')
        
        if not tamanhos_por_estilo:
            form.add_error('tamanhos', 'Você deve selecionar pelo menos um tamanho para algum estilo.')

        if form.is_valid() and formset.is_valid():
            camiseta = form.save(commit=False)
            camiseta.vendedor = request.user
            
            form.cleaned_data['tamanhos'] = tamanhos_por_estilo
            camiseta.estilos = ', '.join(form.cleaned_data['estilos'])
            camiseta.forma_pag_op = ', '.join(form.cleaned_data['forma_pag_op'])
            camiseta.save()
            
            EstiloTamanho.objects.filter(camiseta=camiseta).delete()
            for estilo, tamanhos in tamanhos_por_estilo.items():
                for tamanho in tamanhos:
                    EstiloTamanho.objects.create(
                        camiseta=camiseta,
                        estilo=estilo,
                        tamanho=tamanho
                    )
            
            for form in formset:
                if form.cleaned_data.get('imagem'):
                    imagem = form.save(commit=False)
                    imagem.produto = camiseta 
                    imagem.save()
            
            return redirect('index')  

    else:
        form = CamisetaForm()
        formset = ImagemProdutoBaseFormSet(queryset=ImagemProdutoBase.objects.none())
        
    return render(request, 'criar_camiseta.html', {
        'form': form,
        'formset': formset,
        'camisetas_com_imagens': camisetas_com_imagens
    })


    
@login_required
@user_passes_test(vendedor) 
def edit_camiseta(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta, id=camiseta_id)

    if request.method == 'POST':
        form = CamisetaForm(request.POST, request.FILES, instance=camiseta)
        formset = ImagemProdutoBaseFormSet(request.POST, request.FILES, queryset=camiseta.imagens.all())

        if form.is_valid() and formset.is_valid():
            
            with transaction.atomic():
                for imagem in camiseta.imagens.all():
                    if imagem.imagem and os.path.isfile(imagem.imagem.path):
                        os.remove(imagem.imagem.path)

                camiseta.imagens.all().delete()
                camiseta.tamanhos = ', '.join(form.cleaned_data['tamanhos'])
                camiseta.estilos = ', '.join(form.cleaned_data['estilos'])
                camiseta.forma_pag_op = ', '.join(form.cleaned_data['forma_pag_op'])
                
                form.save()

                imagens = formset.save(commit=False)  
                for imagem in imagens:
                    imagem.camiseta = camiseta  
                    imagem.save()

                formset.save_m2m() 

            messages.success(request, 'Camiseta atualizada com sucesso!')
            return redirect('gerenciar_pro')
        else:
            messages.error(request, 'Erro ao atualizar a camiseta. Verifique os campos.')
    else:
        form = CamisetaForm(instance=camiseta)
        formset = ImagemProdutoBaseFormSet(queryset=camiseta.imagens.all())

    return render(request, 'edit_produto.html', {'form': form, 'formset': formset})


# ---- admin-----#


def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def gerenciar_vendedores(request):
    usuarios = UsuarioCustomizado.objects.all().order_by('nome')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        acao = request.POST.get('acao')
        
        if user_id and acao:
            usuario = get_object_or_404(UsuarioCustomizado, id=user_id)
            
            if acao == 'tornar_vendedor':
                usuario.vendedor = True
                usuario.save()
            elif acao == 'remover_vendedor':
                usuario.vendedor = False
                usuario.save()
                
        return redirect('gerenciar_vendedores')
    
    return render(request, 'gerenciar_vendedores.html', {
        'usuarios': usuarios
    })

# ---- produto ----- #

@login_required
@user_passes_test(vendedor)
def gerenciar_produtos(request):
    produtos = ProdutoBase.objects.filter(vendedor=request.user)

    produtos_com_imagens = [
        {
            'tipo': 'produto',
            'produto': produto,
            'imagem_principal': produto.imagens.filter(principal=True).first() or produto.imagens.first()
        }
        for produto in produtos
    ]

    camisetas = Camiseta.objects.filter(produto__vendedor=request.user)

    camisetas_com_imagens = [
        {
            'tipo': 'camiseta',
            'camiseta': camiseta,
            'produto': camiseta.produto,
            'imagem_principal': camiseta.produto.imagens.filter(principal=True).first() or camiseta.produto.imagens.first()
        }
        for camiseta in camisetas
    ]

    itens = produtos_com_imagens + camisetas_com_imagens

    paginator = Paginator(itens, 6)  
    numero_da_pagina = request.GET.get('pagina')
    itens_paginados = paginator.get_page(numero_da_pagina)

    return render(
        request,
        'gerenciar_produtos.html',
        {'itens': itens_paginados}
    )
    
@login_required
@user_passes_test(vendedor)
def excluir_produto(request, produto_id):
    produto = get_object_or_404(ProdutoBase, id=produto_id, vendedor=request.user)

    if request.method == "POST" and 'deletar' in request.POST:
        produto.delete()
        return redirect('gerenciar_produtos')

    return render(request, "excluir_produto.html", {'produto': produto})

def edit_produto(request):
    return render(request, 'edit_produto.html')

def criar_produto(request):
    return render(request, 'criar_produto.html')

def pedidos_produtos(request):
    return render(request, 'pedidos_produtos.html')

def produto(request):
    return render(request, 'produto.html')