from .forms import CamisetaForm, PedidoBaseForm, PedidoCamisetaForm, AlterarStatusPedidoForm, FiltroProdutoForm, FiltroPedidosForm, CadastroUsuarioForm, LoginUsuarioForm, ImagemProdutoBaseFormSet, AnexoComprovantesPedidoForm
from .models import Camiseta, ProdutoBase, PedidoBase, ImagemProdutoBase, EstiloTamanho, PedidoCamiseta, UsuarioCustomizado
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.db.models import Prefetch
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import openpyxl, json, os


# ---- index ----- #

def index(request):
    form = FiltroProdutoForm(request.GET or None)
    
    camisetas = Camiseta.objects.all()
    produtos_base = ProdutoBase.objects.filter(camiseta__isnull=True)

    if form.is_valid():
        turnos = form.cleaned_data.get('turnos')
        cursos = form.cleaned_data.get('cursos')

        if turnos:
            camisetas = camisetas.filter(produto__turnos=turnos)
            produtos_base = produtos_base.filter(turnos=turnos)

        if cursos:
            camisetas = camisetas.filter(produto__cursos__id=cursos.id)
            produtos_base = produtos_base.filter(cursos__id=cursos.id)

    produtos = list(camisetas) + list(produtos_base)
    
    produtos_com_imagens = []
    data_hoje = now().date()
    
    for produto in produtos:
        base = produto.produto if hasattr(produto, 'produto') else produto
        imagem_principal = base.imagens.filter(principal=True).first() or base.imagens.first()
        disponivel = data_hoje <= base.data_limite_pedidos if base.data_limite_pedidos else True

        produtos_com_imagens.append({
            'produto': produto,
            'imagem_principal': imagem_principal,
            'disponivel': disponivel,
            'tipo': 'camiseta' if isinstance(produto, Camiseta) else 'produto'
        })

    paginator = Paginator(produtos_com_imagens, 9)
    page_number = request.GET.get('pagina')
    produtos_paginados = paginator.get_page(page_number)

    return render(request, 'index.html', {'form': form, 'produtos_com_imagens': produtos_paginados})

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
    camisetas = Camiseta.objects.filter(vendedor=request.user)

    pedidos_recebidos = PedidoBase.objects.filter(produto__vendedor=request.user) if request.user.vendedor else []

    produtos_com_imagens = [
        {
            'produto': p,
            'imagem_principal': p.imagens.filter(principal=True).first() or p.imagens.first()
        } for p in produtos
    ]
    camisetas_com_imagens = [
        {
            'camiseta': c,
            'imagem_principal': c.imagens.filter(principal=True).first() or c.imagens.first()
        } for c in camisetas
    ]

    return render(request, 'perfil.html', {
        'produtos_com_imagens': produtos_com_imagens,
        'camisetas_com_imagens': camisetas_com_imagens,
        'pedidos_recebidos': pedidos_recebidos
    })

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

def exportar_pedidos_camisetas_excel(request):
    camisetas_vendedor = Camiseta.objects.filter(produto__vendedor=request.user)
    pedidos = PedidoCamiseta.objects.filter(
        camiseta__in=camisetas_vendedor,
        pedido__status__in=["Pago Totalmente", "Pago 1° Parcela"]
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

# ---- pedidos ----- #

@login_required
def carrinho(request):
    pedidos_qs = (
        PedidoBase.objects
        .filter(cliente=request.user)
        .select_related('produto')
        .prefetch_related(
            Prefetch('camisetas', queryset=PedidoCamiseta.objects.select_related('camiseta')),
            'produto__imagens',
            'camisetas__camiseta__imagens'
        )
    )

    pedidos_feitos = []
    hoje = timezone.localdate()

    for pedido in pedidos_qs:
        imagem_principal = None
        produto = pedido.produto

        if produto is not None:
            imagem_principal = produto.imagens.filter(principal=True).first() or produto.imagens.first()

        if not imagem_principal:
            primeira_pc = pedido.camisetas.all().first()
            if primeira_pc:
                cam = primeira_pc.camiseta
                imagem_principal = cam.imagens.filter(principal=True).first() or cam.imagens.first()

        camisetas_rel = pedido.camisetas.all()

        pedidos_feitos.append({
            'pedido': pedido,
            'imagem_principal': imagem_principal,
            'camisetas': camisetas_rel,
        })

    return render(request, "carrinho.html", {
        'pedidos_feitos': pedidos_feitos,
        'hoje': hoje,
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
    pedidos_all = PedidoCamiseta.objects.filter(camiseta__vendedor=request.user).select_related('pedido', 'camiseta').order_by('-pedido__data_pedido')

    form_filtro = FiltroPedidosForm(request.GET or None)
    if form_filtro.is_valid():
        status = form_filtro.cleaned_data.get('status')
        if status:
            pedidos_all = pedidos_all.filter(pedido__status=status)

    pedidos_com_forms = [{'pedido': p, 'form': AlterarStatusPedidoForm(instance=p.pedido)} for p in pedidos_all]

    paginator = Paginator(pedidos_com_forms, 10)
    page = request.GET.get("pagina")
    pedidos_paginados = paginator.get_page(page)

    return render(request, 'gerenciar_pedidos.html', {
        'pedidos_com_forms': pedidos_paginados,
        'form_filtro': form_filtro,
        'total_pedidos': pedidos_all.count(),
        'total_pagos': pedidos_all.filter(pedido__status='Pago Totalmente').count(),
        'total_pago_primeira': pedidos_all.filter(pedido__status='Pago 1° Parcela').count(),
        'arrecadado': sum(
            p.camiseta.produto.preco if p.pedido.status == "Pago Totalmente" else
            p.camiseta.produto.preco_parcela if p.pedido.status == "Pago 1° Parcela" else 0
            for p in pedidos_all
        )
    })

@login_required
def edit_pedido_camiseta(request, pedido_id):
    pedido_camiseta = get_object_or_404(PedidoCamiseta, id=pedido_id, pedido__cliente=request.user)
    pedido_base = pedido_camiseta.pedido
    produto = pedido_camiseta.camiseta.produto

    tamanhos_opcoes = list({t for lista in pedido_camiseta.camiseta.tamanhos.values() for t in lista})
    estilos_opcoes = [e.strip() for e in pedido_camiseta.camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in produto.forma_pag_op.split(',')]

    if request.method == 'POST':
        form_base = PedidoBaseForm(request.POST, request.FILES, instance=pedido_base, produto=produto, forma_pag_opcoes=forma_pag_opcoes)
        form_camiseta = PedidoCamisetaForm(request.POST, instance=pedido_camiseta, tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes)

        if form_base.is_valid() and form_camiseta.is_valid():
            form_base.save()
            form_camiseta.save()
            messages.success(request, "Pedido de camiseta atualizado com sucesso!")
            return redirect('carrinho')
    else:
        form_base = PedidoBaseForm(instance=pedido_base, produto=produto, forma_pag_opcoes=forma_pag_opcoes)
        form_camiseta = PedidoCamisetaForm(instance=pedido_camiseta, tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes)

    return render(request, 'edit_pedido_camiseta.html', {
        'form_base': form_base,
        'form_camiseta': form_camiseta,
        'pedido_camiseta': pedido_camiseta,
        'pedido_base': pedido_base,
        'tamanhos_por_estilo_json': json.dumps(pedido_camiseta.camiseta.tamanhos)
    })


# ---- camiseta ----- #

def camiseta(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta.objects.prefetch_related('imagens'), id=camiseta_id)
    tamanhos_opcoes = list({t for lista in camiseta.tamanhos.values() for t in lista})
    estilos_opcoes = [e.strip() for e in camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in camiseta.forma_pag_op.split(',')]

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "Você precisa estar logado para fazer um pedido.")
            return redirect('login')

        form_base = PedidoBaseForm(
            request.POST,
            request.FILES,
            produto=camiseta,
            forma_pag_opcoes=forma_pag_opcoes
        )
        form_camiseta = PedidoCamisetaForm(
            request.POST,
            tamanhos_opcoes=tamanhos_opcoes,
            estilos_opcoes=estilos_opcoes
        )

        if form_base.is_valid() and form_camiseta.is_valid():
            pedido_base = form_base.save(commit=False)
            pedido_base.produto = camiseta
            pedido_base.cliente = request.user
            pedido_base.save()

            pedido_camiseta = form_camiseta.save(commit=False)
            pedido_camiseta.camiseta = camiseta
            pedido_camiseta.pedido = pedido_base
            pedido_camiseta.save()

            messages.success(request, "Pedido de camiseta realizado com sucesso!")
            return redirect('carrinho')

    else:
        form_base = PedidoBaseForm(
            produto=camiseta,
            forma_pag_opcoes=forma_pag_opcoes
        )
        form_camiseta = PedidoCamisetaForm(
            tamanhos_opcoes=tamanhos_opcoes,
            estilos_opcoes=estilos_opcoes
        )

    return render(request, 'camiseta.html', {
        'form_base': form_base,
        'form_camiseta': form_camiseta,
        'camiseta': camiseta,
        'tamanhos_por_estilo_json': json.dumps(camiseta.tamanhos)
    })


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
            camiseta.estilos = ", ".join(form.cleaned_data['estilos'])
            camiseta.tamanhos = tamanhos_por_estilo
            camiseta.save()
            form.save_m2m()

            # limpa os tamanhos antigos e salva novos
            EstiloTamanho.objects.filter(camiseta=camiseta).delete()
            for estilo, tamanhos in tamanhos_por_estilo.items():
                for tamanho in tamanhos:
                    EstiloTamanho.objects.create(
                        camiseta=camiseta,
                        estilo=estilo,
                        tamanho=tamanho
                    )

            # salva imagens
            for f in formset:
                if f.cleaned_data.get('imagem'):
                    imagem = f.save(commit=False)
                    imagem.produto = camiseta  # ✅ agora aponta direto para a Camiseta (ProdutoBase)
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
                # remover imagens antigas
                for imagem in camiseta.imagens.all():
                    if imagem.imagem and os.path.isfile(imagem.imagem.path):
                        os.remove(imagem.imagem.path)
                camiseta.imagens.all().delete()

                # atualizar campos extras
                camiseta.tamanhos = form.cleaned_data['tamanhos']
                camiseta.estilos = ", ".join(form.cleaned_data['estilos'])
                camiseta.forma_pag_op = ", ".join(form.cleaned_data.get('forma_pag_op', []))

                form.save()

                # salvar novas imagens
                for imagem in formset.save(commit=False):
                    imagem.produto = camiseta  # ✅ corrigido
                    imagem.save()
                formset.save_m2m()

            messages.success(request, 'Camiseta atualizada com sucesso!')
            return redirect('gerenciar_produtos')
        else:
            messages.error(request, 'Erro ao atualizar a camiseta. Verifique os campos.')
    else:
        form = CamisetaForm(instance=camiseta)
        formset = ImagemProdutoBaseFormSet(queryset=camiseta.imagens.all())

    return render(request, 'edit_camiseta.html', {'form': form, 'formset': formset})

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
    produtos_base = ProdutoBase.objects.filter(vendedor=request.user, camiseta__isnull=True)
    camisetas = Camiseta.objects.filter(vendedor=request.user)

    itens = [
        {'tipo': 'produto', 'produto': p, 'imagem_principal': p.imagens.filter(principal=True).first() or p.imagens.first()}
        for p in produtos_base
    ] + [
        {'tipo': 'camiseta', 'camiseta': c, 'produto': c, 'imagem_principal': c.imagens.filter(principal=True).first() or c.imagens.first()}
        for c in camisetas
    ]

    paginator = Paginator(itens, 6)
    page_number = request.GET.get('pagina')
    itens_paginados = paginator.get_page(page_number)

    return render(request, 'gerenciar_produtos.html', {'itens': itens_paginados})

    
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

def edit_pedido_produto(request):
    return render(request, 'edit_pedido_produto.html')

def criar_produto(request):
    return render(request, 'criar_produto.html')

def pedidos_produtos(request):
    return render(request, 'pedidos_produtos.html')

def produto(request):
    return render(request, 'produto.html')