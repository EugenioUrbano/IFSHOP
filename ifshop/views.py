from datetime import timedelta
from .forms import CamisetaForm, PedidoBaseForm, ProdutoBaseForm, PedidoCamisetaForm
from.forms import AlterarStatusPedidoForm, FiltroProdutoForm, FiltroPedidosForm, CadastroUsuarioForm
from .forms import LoginUsuarioForm, ImagemProdutoBaseFormSet, AnexoComprovantesPedidoForm, AvaliacaoForm
from .models import Camiseta, ProdutoBase, PedidoBase, ImagemProdutoBase, EstiloTamanho, PedidoCamiseta, UsuarioCustomizado, Avaliacao
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from .views_2fa import enviar_codigo_2fa
from django.utils.timezone import now
from django.db.models import Prefetch, Sum, Count
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import openpyxl, json, os
from datetime import timedelta


def index(request):
    form = FiltroProdutoForm(request.GET)
    
    produtos_base = ProdutoBase.objects.all().prefetch_related('imagens', 'curso') 
    camisetas_ids = Camiseta.objects.values_list('produtobase_ptr_id', flat=True)
    
    if form.is_valid():
        turnos = form.cleaned_data.get('turnos')
        
        if turnos:  
            produtos_base = produtos_base.filter(turnos__iexact=turnos)
            print(f"Filtro turnos aplicado: {turnos}")
        
        print(f"Produtos após filtro: {produtos_base.count()}")
    else:
        print("Form inválido")
        print("Errors:", form.errors)

    produtos_com_imagens = [] 
    data_hoje = now().date()
    
    for produto in produtos_base:  
        tipo = 'camiseta' if produto.id in camisetas_ids else 'produto'
        imagem_principal = produto.imagens.filter(principal=True).first() or produto.imagens.first()
        disponivel = data_hoje <= produto.data_limite_pedidos if produto.data_limite_pedidos else True

        produtos_com_imagens.append({  
            'produto': produto,
            'imagem_principal': imagem_principal,
            'disponivel': disponivel,
            'tipo': tipo
        })

    print(f"Total produtos para exibir: {len(produtos_com_imagens)}")

    paginator = Paginator(produtos_com_imagens, 9)  
    page_number = request.GET.get('pagina')
    produtos_paginados = paginator.get_page(page_number)

    return render(request, 'core/index.html', {
        'form': form, 
        'produtos_com_imagens': produtos_paginados  
    })

# ---- usuario ----- #

def vendedor(user):
    return user.vendedor

def login_view(request):
    if request.method == 'POST':
        form = LoginUsuarioForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # ⬇️ VERIFICAÇÃO 2FA - Redireciona para verificação ⬇️
            if hasattr(user, 'email'):  # Garante que é seu UsuarioCustomizado
                # Envia código 2FA por email
                enviar_codigo_2fa(request, user)
                
                # Salva ID do usuário na sessão para verificação posterior
                request.session['usuario_2fa_id'] = user.id
                request.session['usuario_autenticado'] = True
                
                # Redireciona para página de verificação 2FA
                return redirect('verificar_2fa')
            
            # ⬇️ FALLBACK - Se algo der errado, faz login normal ⬇️
            login(request, user)
            return redirect('index')
            
    else:
        form = LoginUsuarioForm()
    
    return render(request, 'registration/login.html', {'form': form})

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

    # Adicionar dados do dashboard apenas para vendedores
    dashboard_data = {}
    if request.user.vendedor:
        try:
            # Data atual e do mês anterior
            hoje = timezone.now()
            mes_atual = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Métricas do mês atual
            vendas_camisetas_mes = PedidoCamiseta.objects.filter(
                camiseta__vendedor=request.user,
                pedido__data_pedido__gte=mes_atual,
                pedido__status__in=['Pago Totalmente', 'Pago 1° Parcela']
            ).aggregate(total=Sum('camiseta__preco'))['total'] or 0
            
            vendas_produtos_mes = PedidoBase.objects.filter(
                produto__vendedor=request.user,
                produto__camiseta__isnull=True,
                data_pedido__gte=mes_atual,
                status__in=['Pago Totalmente', 'Pago 1° Parcela']
            ).aggregate(total=Sum('produto__preco'))['total'] or 0
            
            vendas_mes = float(vendas_camisetas_mes) + float(vendas_produtos_mes)
            
            # Produtos vendidos
            produtos_vendidos = (
                PedidoCamiseta.objects.filter(
                    camiseta__vendedor=request.user,
                    pedido__data_pedido__gte=mes_atual,
                    pedido__status__in=['Pago Totalmente', 'Pago 1° Parcela']
                ).count() +
                PedidoBase.objects.filter(
                    produto__vendedor=request.user,
                    produto__camiseta__isnull=True,
                    data_pedido__gte=mes_atual,
                    status__in=['Pago Totalmente', 'Pago 1° Parcela']
                ).count()
            )
            
            # Novos clientes
            novos_clientes = UsuarioCustomizado.objects.filter(
                pedidos__produto__vendedor=request.user,
                pedidos__data_pedido__gte=mes_atual
            ).distinct().count()
            
            # Estatísticas gerais
            total_camisetas = Camiseta.objects.filter(vendedor=request.user).count()
            total_produtos = ProdutoBase.objects.filter(vendedor=request.user, camiseta__isnull=True).count()
            pedidos_pendentes = PedidoBase.objects.filter(
                produto__vendedor=request.user,
                status='Pendente'
            ).count()
            
            # Pedidos recentes (limitado para o perfil)
            pedidos_recentes_dashboard = PedidoBase.objects.filter(
                produto__vendedor=request.user
            ).select_related('cliente').order_by('-data_pedido')[:3]
            
            # Produtos em destaque (limitado para o perfil)
            produtos_destaque = []
            
            # Camisetas
            camisetas_destaque = Camiseta.objects.filter(
                vendedor=request.user
            ).annotate(
                total_vendido=Count('pedidos_base')
            ).order_by('-total_vendido')[:2]
            
            for camiseta in camisetas_destaque:
                produtos_destaque.append({
                    'nome': camiseta.titulo,
                    'total_vendido': camiseta.total_vendido,
                    'estoque': 50,
                    'imagem': camiseta.imagens.first()
                })
            
            # Produtos base
            produtos_base_destaque = ProdutoBase.objects.filter(
                vendedor=request.user,
                camiseta__isnull=True
            ).annotate(
                total_vendido=Count('pedidos_base')
            ).order_by('-total_vendido')[:2]
            
            for produto in produtos_base_destaque:
                produtos_destaque.append({
                    'nome': produto.titulo,
                    'total_vendido': produto.total_vendido,
                    'estoque': 30,
                    'imagem': produto.imagens.first()
                })
            
            dashboard_data = {
                'vendas_mes': vendas_mes,
                'produtos_vendidos': produtos_vendidos,
                'novos_clientes': novos_clientes,
                'total_camisetas': total_camisetas,
                'total_produtos': total_produtos,
                'pedidos_pendentes': pedidos_pendentes,
                'pedidos_recentes_dashboard': pedidos_recentes_dashboard,
                'produtos_destaque_dashboard': produtos_destaque,
                'is_vendedor': True
            }
            
        except Exception as e:
            print(f"Erro ao carregar dados do dashboard no perfil: {e}")
            dashboard_data = {
                'vendas_mes': 0,
                'produtos_vendidos': 0,
                'novos_clientes': 0,
                'total_camisetas': 0,
                'total_produtos': 0,
                'pedidos_pendentes': 0,
                'pedidos_recentes_dashboard': [],
                'produtos_destaque_dashboard': [],
                'is_vendedor': True,
                'erro_dashboard': str(e)
            }
    else:
        dashboard_data = {'is_vendedor': False}

    return render(request, 'usuarios/perfil.html', {
        'produtos_com_imagens': produtos_com_imagens,
        'camisetas_com_imagens': camisetas_com_imagens,
        'pedidos_recebidos': pedidos_recebidos,
        **dashboard_data  # Desempacota os dados do dashboard
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
    return render(request, 'registration/cadastro.html', {'form': form})


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

def exportar_pedidos_camisetas(request):
    camisetas_vendedor = Camiseta.objects.filter(vendedor=request.user)

    pedidos = PedidoCamiseta.objects.filter(
        camiseta__in=camisetas_vendedor,
        pedido__status__in=["Pago Totalmente", "Pago 1° Parcela"]
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pedidos Pagos"
    ws.append(['Nome na Estampa', 'Numero na Estampa', 'Estilo', 'Tamanho', 'Opção escolhida', "Status"])

    for pedido in pedidos:
        ws.append([
            pedido.nome_estampa,
            pedido.numero_estampa,
            pedido.estilo,
            pedido.tamanho,
            pedido.pedido.opcao_escolhida,
            pedido.pedido.status
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

    return render(request, "usuarios/carrinho.html", {
        'pedidos_feitos': pedidos_feitos,
        'hoje': hoje,
    })

def excluir_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoBase, id=pedido_id, cliente=request.user)

    if request.method == "POST" and 'deletar' in request.POST:
        pedido.delete()
        return redirect('carrinho')

    return render(request, "pedidos/excluir_pedido.html", {'pedido': pedido})
    
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
    return render(request, 'pedidos/comprovantes.html', {'form': form,'pedido': pedido,'hoje': hoje})
    
@login_required
@user_passes_test(vendedor)
def pedidos_camisetas(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        novo_status = request.POST.get('status')
        
        if pedido_id and novo_status:
            try:
                pedido = PedidoBase.objects.get(
                    id=pedido_id, 
                    produto__vendedor=request.user 
                )
                pedido.status = novo_status
                pedido.save()
                messages.success(request, f'Status do pedido #{pedido_id} atualizado para {novo_status}!')
            except PedidoBase.DoesNotExist:
                messages.error(request, 'Pedido não encontrado ou você não tem permissão para editá-lo.')
        
        return redirect('pedidos_camisetas')  
    
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

    return render(request, 'pedidos/pedidos_camisetas.html', {
        'pedidos_com_forms': pedidos_paginados,
        'form_filtro': form_filtro,
        'total_pedidos': pedidos_all.count(),
        'total_pagos': pedidos_all.filter(pedido__status='Pago Totalmente').count(),
        'total_pago_primeira': pedidos_all.filter(pedido__status='Pago 1° Parcela').count(),
        'arrecadado': sum(
            p.camiseta.preco if p.pedido.status == "Pago Totalmente" else
            p.camiseta.preco_parcela if p.pedido.status == "Pago 1° Parcela" else 0
            for p in pedidos_all
        )
    })
   
@login_required
@user_passes_test(vendedor)
def pedidos_produtos(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        novo_status = request.POST.get('status')
        
        if pedido_id and novo_status:
            try:
                pedido = PedidoBase.objects.get(
                    id=pedido_id, 
                    produto__vendedor=request.user 
                )
                pedido.status = novo_status
                pedido.save()
                messages.success(request, f'Status do pedido #{pedido_id} atualizado para {novo_status}!')
            except PedidoBase.DoesNotExist:
                messages.error(request, 'Pedido não encontrado ou você não tem permissão para editá-lo.')
        
        return redirect('pedidos_produtos')
    
    pedidos_all = PedidoBase.objects.filter(
        produto__vendedor=request.user,  
        produto__camiseta__isnull=True   
    ).select_related('produto', 'cliente').prefetch_related('produto__imagens').order_by('-data_pedido')

    form_filtro = FiltroPedidosForm(request.GET or None)
    if form_filtro.is_valid():
        status = form_filtro.cleaned_data.get('status')
        if status:
            pedidos_all = pedidos_all.filter(status=status)

    pedidos_com_forms = [{'pedido': p, 'form': AlterarStatusPedidoForm(instance=p)} for p in pedidos_all]

    paginator = Paginator(pedidos_com_forms, 10)
    page = request.GET.get("pagina")
    pedidos_paginados = paginator.get_page(page)

    return render(request, 'pedidos/pedidos_produtos.html', {
        'pedidos_com_forms': pedidos_paginados,
        'form_filtro': form_filtro,
        'total_pedidos': pedidos_all.count(),
        'total_pagos': pedidos_all.filter(status='Pago Totalmente').count(),
        'total_pago_primeira': pedidos_all.filter(status='Pago 1° Parcela').count(),
        'arrecadado': sum(
            p.produto.preco if p.status == "Pago Totalmente" else
            p.produto.preco_parcela if p.status == "Pago 1° Parcela" else 0
            for p in pedidos_all
        )
    })

@login_required
def edit_pedido_camiseta(request, pedido_id):
    pedido_camiseta = get_object_or_404(PedidoCamiseta, id=pedido_id, pedido__cliente=request.user)
    pedido_base = pedido_camiseta.pedido
    produto = pedido_camiseta.camiseta

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

    return render(request, 'pedidos/edit_pedido_camiseta.html', {
        'form_base': form_base,
        'form_camiseta': form_camiseta,
        'pedido_camiseta': pedido_camiseta,
        'pedido_base': pedido_base,
        'tamanhos_por_estilo_json': json.dumps(pedido_camiseta.camiseta.tamanhos)
    })

def edit_pedido_produto(request, pedido_id):
    pedido = get_object_or_404(PedidoBase, id=pedido_id, pedido__cliente=request.user)
    
    forma_pag_opcoes = [f.strip() for f in produto.forma_pag_op.split(',')]

    if request.method == 'POST':
        form_base = PedidoBaseForm(request.POST, request.FILES, instance=pedido, produto=produto, forma_pag_opcoes=forma_pag_opcoes)
        

        if form_base.is_valid():
            form_base.save()
            messages.success(request, "Pedido do seu produto atualizado com sucesso!")
            return redirect('carrinho')
    else:
        form_base = PedidoBaseForm(instance=pedido, produto=produto, forma_pag_opcoes=forma_pag_opcoes)

    return render(request, 'pedidos/edit_pedido_produto.html', {
        'form_base': form_base,
        'pedido': pedido,
    })

# ---- avaliações ----- #

@login_required
def criar_avaliacao(request, pedido_id):
    pedido = get_object_or_404(PedidoBase, id=pedido_id, cliente=request.user)
    
    if pedido.status != 'Entregue':
        messages.error(request, 'Você só pode avaliar produtos após a entrega.')
        return redirect('carrinho')
    
    avaliacao_existente = Avaliacao.objects.filter(pedido=pedido, cliente=request.user).first()
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=avaliacao_existente)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.produto = pedido.produto
            avaliacao.cliente = request.user
            avaliacao.pedido = pedido
            avaliacao.save()
            
            messages.success(request, 'Avaliação enviada com sucesso!')
            return redirect('carrinho')
    else:
        form = AvaliacaoForm(instance=avaliacao_existente)
    
    return render(request, 'avaliacoes/criar_avaliacao.html', {
        'form': form,
        'pedido': pedido,
        'avaliacao_existente': avaliacao_existente
    })
# ---- camiseta ----- #

def camiseta(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta.objects.prefetch_related('imagens', 'avaliacoes__cliente'), id=camiseta_id)
    tamanhos_opcoes = list({t for lista in camiseta.tamanhos.values() for t in lista})
    estilos_opcoes = [e.strip() for e in camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in camiseta.forma_pag_op.split(',')]

    avaliacoes = camiseta.avaliacoes.all().select_related('cliente')
    pagina_avaliacoes_num = request.GET.get('pagina_avaliacoes', 1)
    paginator_avaliacoes = Paginator(avaliacoes, 5)  # 5 avaliações por página
    pagina_avaliacoes = paginator_avaliacoes.get_page(pagina_avaliacoes_num)

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

    return render(request, 'camisetas/camiseta.html', {
        'form_base': form_base,
        'form_camiseta': form_camiseta,
        'camiseta': camiseta,
        'avaliacoes_paginadas': pagina_avaliacoes,
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
            form.save()

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

    return render(request, 'camisetas/criar_camiseta.html', {
        'form': form,
        'formset': formset,
        'camisetas_com_imagens': camisetas_com_imagens
    })

    
@login_required
@user_passes_test(vendedor)
def edit_camiseta(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta, id=camiseta_id)
    
    # Debug inicial
    print("=== EDIT CAMISETA ===")
    print("Método:", request.method)
    if request.method == 'POST':
        print("POST data:", dict(request.POST))
        print("FILES:", dict(request.FILES))

    if request.method == 'POST':
        form = CamisetaForm(request.POST, request.FILES, instance=camiseta)
        formset = ImagemProdutoBaseFormSet(request.POST, request.FILES, queryset=camiseta.imagens.all(), prefix='imagens')

        print("Form is_valid:", form.is_valid())
        print("Formset is_valid:", formset.is_valid())
        
        if form.is_valid():
            print("Form válido - Campos cleaned_data:")
            for field, value in form.cleaned_data.items():
                print(f"  {field}: {value}")
        else:
            print("Form errors:", form.errors)
            
        if not formset.is_valid():
            print("Formset errors:", formset.errors)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Salvar a camiseta
                    camiseta = form.save()
                    print("Camiseta salva com sucesso")

                    # Salvar o formset de imagens
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.produto = camiseta
                        instance.save()
                        print(f"Imagem {instance.id} salva")

                    # Deletar imagens marcadas para exclusão
                    for imagem_form in formset.deleted_forms:
                        if imagem_form.instance.pk:
                            imagem_instance = imagem_form.instance
                            if imagem_instance.imagem and os.path.isfile(imagem_instance.imagem.path):
                                os.remove(imagem_instance.imagem.path)
                            imagem_instance.delete()
                            print(f"Imagem {imagem_instance.id} deletada")

                messages.success(request, 'Camiseta atualizada com sucesso!')
                print("Redirecionando para gerenciar_produtos")
                return redirect('gerenciar_produtos')
                
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {str(e)}')
                print(f"Erro: {e}")
        else:
            messages.error(request, 'Erro no formulário. Verifique os campos.')
            print("Formulário inválido")
    else:
        # GET request - inicializar forms com dados atuais
        form = CamisetaForm(instance=camiseta)
        formset = ImagemProdutoBaseFormSet(queryset=camiseta.imagens.all(), prefix='imagens')
        
        # CORREÇÃO: Remover o .all() dos campos que são strings
        print("Valores iniciais da camiseta:")
        print(f"Turnos: {camiseta.turnos}")
        print(f"Estilos: {camiseta.estilos}")  # Removido .all()
        print(f"Tamanhos: {camiseta.tamanhos}")  # Removido .all()
        print(f"Forma pag op: {camiseta.forma_pag_op}")  # Removido .all()

    return render(request, 'camisetas/edit_camiseta.html', {
        'form': form, 
        'formset': formset,
        'camiseta': camiseta
    })

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
    
    return render(request, 'gestao/gerenciar_vendedores.html', {
        'usuarios': usuarios
    })

@login_required
def vendedor_crud(request):
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
    
    return render(request, 'usuarios/vendedor_crud.html', {
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

    return render(request, 'produtos/gerenciar_produtos.html', {'itens': itens_paginados})

@login_required
@user_passes_test(vendedor)
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoBaseForm(request.POST, request.FILES)
        formset = ImagemProdutoBaseFormSet(request.POST, request.FILES, queryset=ImagemProdutoBase.objects.none())
        
        if form.is_valid() and formset.is_valid():
            try:
                produto = form.save(commit=False)
                produto.vendedor = request.user
                produto.save()
                
                for form_img in formset:
                    if form_img.cleaned_data.get('imagem'):
                        imagem = form_img.save(commit=False)
                        imagem.produto = produto
                        imagem.save()
                
                messages.success(request, 'Produto criado com sucesso!')
                
                if 'adicionar_outro' in request.POST:
                    return redirect('criar_produto')
                else:
                    return redirect('gerenciar_produtos')
                    
            except Exception as e:
                messages.error(request, f'Erro ao salvar produto: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = ProdutoBaseForm()
        formset = ImagemProdutoBaseFormSet(queryset=ImagemProdutoBase.objects.none())
    
    return render(request, 'produtos/criar_produto.html', {
        'form': form,
        'formset': formset
    })
@login_required
@user_passes_test(vendedor)
def excluir_produto(request, produto_id):
    produto = get_object_or_404(ProdutoBase, id=produto_id, vendedor=request.user)

    if request.method == "POST" and 'deletar' in request.POST:
        produto.delete()
        return redirect('gerenciar_produtos')

    return render(request, "produtos/excluir_produto.html", {'produto': produto})

@login_required
@user_passes_test(vendedor)
def edit_produto(request, produto_id):
    produto = get_object_or_404(ProdutoBase, id=produto_id, vendedor=request.user)
    
    print("=== DEBUG EDIT PRODUTO ===")
    print("Produto:", produto.titulo)
    print("Cursos do produto:", list(produto.curso.values_list('nome', flat=True)))
    
    if request.method == 'POST':
        form = ProdutoBaseForm(request.POST, request.FILES, instance=produto)
        print("POST data - curso:", request.POST.getlist('curso'))
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    produto = form.save(commit=False)
                    produto.save()
                    
                    form.save_m2m()  
                    
                    messages.success(request, 'Produto atualizado com sucesso!')
                    return redirect('gerenciar_produtos')
                    
            except Exception as e:
                messages.error(request, f'Erro ao salvar produto: {str(e)}')
                print(f"Erro: {e}")
        else:
            messages.error(request, 'Erro no formulário. Verifique os campos.')
            print("Form errors:", form.errors)
    else:
        form = ProdutoBaseForm(instance=produto)
        print("Form initial - curso:", form['curso'].value())
    
    return render(request, 'produtos/edit_produto.html', {
        'form': form,
        'produto': produto
    })

def produto(request, produto_id):
    produto = get_object_or_404(ProdutoBase.objects.prefetch_related('imagens', 'avaliacoes__cliente'), id=produto_id)
    forma_pag_opcoes = [f.strip() for f in produto.forma_pag_op.split(',')]

    avaliacoes = produto.avaliacoes.all().select_related('cliente')
    pagina_avaliacoes_num = request.GET.get('pagina_avaliacoes', 1)
    paginator_avaliacoes = Paginator(avaliacoes, 5)  # 5 avaliações por página
    pagina_avaliacoes = paginator_avaliacoes.get_page(pagina_avaliacoes_num)


    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "Você precisa estar logado para fazer um pedido.")
            return redirect('login')

        form_base = PedidoBaseForm(
            request.POST,
            request.FILES,
            produto=produto,  
            forma_pag_opcoes=forma_pag_opcoes
        )

        if form_base.is_valid():
            pedido_base = form_base.save(commit=False)
            pedido_base.produto = produto  
            pedido_base.cliente = request.user
            pedido_base.save()

            messages.success(request, "Pedido realizado com sucesso!")
            return redirect('carrinho')

    else:
        form_base = PedidoBaseForm(
            produto=produto,  
            forma_pag_opcoes=forma_pag_opcoes
        )

    return render(request, 'produtos/produto.html', {
        'produto': produto,
        'form_base': form_base,
        'avaliacoes_paginadas': pagina_avaliacoes,
    })
