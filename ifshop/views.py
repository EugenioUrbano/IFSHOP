from .forms import CamisetaForm, PedidoForm, AlterarStatusPedidoForm, FiltroProdutoForm, FiltroProdutosForm, CadastroUsuarioForm, LoginUsuarioForm, ImagemCamisetaFormSet, AnexoComprovantesPedidoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Camiseta, Pedido, ImagemCamiseta, EstiloTamanho
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import openpyxl
import json, os


def index(request):
    form = FiltroProdutoForm(request.GET) 
    
    camisetas =Camiseta.objects.all()
    
    if form.is_valid():
        turnos = form.cleaned_data.get('turnos')
        cursos = form.cleaned_data.get('cursos')

        if turnos:  
            camisetas = camisetas.filter(turnos=turnos)

        if cursos:  
            camisetas = camisetas.filter(cursos=cursos)
            
    camisetas_com_imagens = []
    data_hoje = now().date()
    
    
    for camiseta in camisetas:
        imagem_principal = camiseta.imagens.filter(principal=True).first() or camiseta.imagens.first()
        data_limite = camiseta.data_limite_pedidos.date() if hasattr(camiseta.data_limite_pedidos, 'date') else camiseta.data_limite_pedidos
        disponivel = data_hoje <= data_limite
        camisetas_com_imagens.append({'camiseta': camiseta, 'imagem_principal': imagem_principal, 'disponivel': disponivel})
    
    paginator = Paginator(camisetas_com_imagens, 9)
    numero_da_pagina = request.GET.get('pagina')  
    camisetas_paginadas = paginator.get_page(numero_da_pagina)
    
    
    context = {
        'form': form,
        'camisetas_com_imagens': camisetas_paginadas,
    }
    return render(request, 'index.html', context )

####################################################################################################

def vendedor(user):
    return user.vendedor

def login_view(request):
    if request.method == 'POST':
        form = LoginUsuarioForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()  
            login(request, user)
            return redirect('perfil')  
    else:
        form = LoginUsuarioForm()
    return render(request, 'login.html', {'form': form})

def logout_usuario(request):
    logout(request) 
    return redirect('login')

####################################################################################################

@login_required
def perfil(request):
    camisetas = Camiseta.objects.filter(vendedor=request.user)
    
    if request.user.vendedor:
        camisetas_vendedor = Camiseta.objects.filter(vendedor=request.user)
        pedidos_recebidos = Pedido.objects.filter(camiseta__in=camisetas_vendedor)
    else:
        pedidos_recebidos = []
    
    camisetas_com_imagens = []
    for camiseta in camisetas:
        imagem_principal = (
            camiseta.imagens.filter(principal=True).first() 
            or camiseta.imagens.first()
        )
        camisetas_com_imagens.append({'camiseta': camiseta, 'imagem_principal': imagem_principal})

    context = {
        "pedidos_recebidos": pedidos_recebidos,
        'camisetas_com_imagens': camisetas_com_imagens
        }
    
    return render(request, 'perfil.html', context)

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
    pedido = Pedido.objects.filter(cliente=request.user) if request.user.is_authenticated else [] 
    
    if request.method == "POST" and 'deletar' in request.POST:
        pedido_id = request.POST.get('pedido_id')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.delete()
        return redirect('carrinho')

    hoje = timezone.localdate()
    return render(request, "carrinho.html", {'pedido': pedido, 'hoje': hoje})
    
def comprovantes(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    
    hoje = timezone.localdate()
    
    if request.method == 'POST':
        form = AnexoComprovantesPedidoForm(request.POST, request.FILES,instance=pedido)
        if form.is_valid():
            form.save()  
        return redirect('carrinho')
    else:
        form = AnexoComprovantesPedidoForm(instance=pedido)
        
    return render(request, 'comprovantes.html', {'form': form, 'pedido': pedido, 'hoje': hoje})

####################################################################################################

def tamanhos_por_estilojson(request):
    camiseta_id = request.GET.get('camiseta_id')
    estilo = request.GET.get('estilo')

    tamanhos = EstiloTamanho.objects.filter(camiseta_id=camiseta_id, estilo=estilo).values_list('tamanho', flat=True)
    return JsonResponse(list(tamanhos), safe=False)

def camiseta(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta.objects.prefetch_related('imagens'), id=camiseta_id)
    tamanhos_opcoes = list({t for lista in camiseta.tamanhos.values() for t in lista})
    estilos_opcoes = [e.strip() for e in camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in camiseta.forma_pag_op.split(',')]

    print("Camiseta carregada na View:", camiseta.titulo, camiseta.cores)
    
    form = PedidoForm(
        camiseta=camiseta,
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

####################################################################################################

@login_required
@user_passes_test(vendedor)
def adicionar_pro(request):
    camisetas = Camiseta.objects.all()
    
    camisetas_com_imagens = []
    for camiseta in camisetas:
        imagem_principal = camiseta.imagens.filter(principal=True).first() or camiseta.imagens.first()
        camisetas_com_imagens.append({'camiseta': camiseta, 'imagem_principal': imagem_principal}) 
        
    if request.method == 'POST':
        form = CamisetaForm(request.POST, request.FILES)
        formset = ImagemCamisetaFormSet(request.POST, request.FILES, queryset=ImagemCamiseta.objects.none())

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
            print("Form válido!")
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
                    imagem.camiseta = camiseta
                    imagem.save()
            
            return redirect('index')  

    else:
        form = CamisetaForm()
        formset = ImagemCamisetaFormSet(queryset=ImagemCamiseta.objects.none())
        print("Form errors:", form.errors)
        print("Formset errors:", formset.errors)
        
    return render(request, 'adicionar_pro.html', {
        'form': form,
        'formset': formset,
        'camisetas_com_imagens': camisetas_com_imagens
    })

####################################################################################################

@login_required
@user_passes_test(vendedor)
def gerenciar_pro(request):
    camisetas = Camiseta.objects.filter(vendedor=request.user) 

    camisetas_com_imagens = [
        {
            'camiseta': camiseta,
            'imagem_principal': camiseta.imagens.filter(principal=True).first() or camiseta.imagens.first()
        }
        for camiseta in camisetas
    ]
    
    # Paginação
    paginator = Paginator(camisetas_com_imagens, 4)
    numero_da_pagina = request.GET.get('pagina')
    camisetas_paginadas = paginator.get_page(numero_da_pagina)

    return render(request, 'gerenciar_pro.html', {'camisetas_com_imagens': camisetas_paginadas})
    
@login_required
@user_passes_test(vendedor)
def excluir_produto(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta, id=camiseta_id, vendedor=request.user)

    if request.method == "POST" and 'deletar' in request.POST:
        camiseta.delete()
        return redirect('gerenciar_pro')

    return render(request, "excluir_produto.html", {'camiseta': camiseta})

####################################################################################################

@login_required
@user_passes_test(vendedor)
def gerenciar_pedidos(request):
    form_filtro = FiltroProdutosForm(request.GET) 
    camisetas_vendedor = Camiseta.objects.filter(vendedor=request.user)
    pedidos = Pedido.objects.filter(camiseta__in=camisetas_vendedor)

    if form_filtro.is_valid():
        status = form_filtro.cleaned_data.get('status')

        if status:  
            pedidos = pedidos.filter(status=status)

    
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
        
    paginator = Paginator(pedidos_com_forms, 20)
    numero_da_pagina = request.GET.get('pagina')  
    pedidos_paginadas = paginator.get_page(numero_da_pagina)

    context = {
        'pedidos_com_forms': pedidos_paginadas,
        'form_filtro': form_filtro,
        }
    
    return render(request, 'gerenciar_pedidos.html', context)

def exportar_pedidos_excel(request):
    camisetas_vendedor = Camiseta.objects.filter(vendedor=request.user)
    pedidos = Pedido.objects.filter(camiseta__in=camisetas_vendedor, status="Pago Totalmente")

    # Criação do workbook e planilha
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pedidos Pagos"

    # Cabeçalhos da planilha
    ws.append(['Nome na Estampa', 'Número na Estampa', 'Estilo', 'Tamanho', 'Opção de Cor'])

    # Adiciona os dados dos pedidos
    for pedido in pedidos:
        ws.append([
            pedido.nome_estampa,
            pedido.numero_estampa,
            pedido.estilo,
            pedido.tamanho,
            pedido.cor_escolhida
        ])

    # Prepara a resposta para download
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=pedidos_pagos.xlsx'
    wb.save(response)
    return response

@login_required
def verificar_pedidos(request):
    pedidos_novos = Pedido.objects.filter(camiseta__vendedor=request.user, visto=False).count()
    return JsonResponse({"pedidos_novos": pedidos_novos})

@login_required
@csrf_exempt 
def marcar_pedidos_vistos(request):
    if request.method == "POST":
        Pedido.objects.filter(camiseta__vendedor=request.user, visto=False).update(visto=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Método inválido"}, status=400)

####################################################################################################

@login_required
def edit_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)

    tamanhos_opcoes = list({t for lista in pedido.camiseta.tamanhos.values() for t in lista})
    estilos_opcoes = [e.strip() for e in pedido.camiseta.estilos.split(',')]
    forma_pag_opcoes = [f.strip() for f in pedido.camiseta.forma_pag_op.split(',')]

    if request.method == 'POST':
        form = PedidoForm(request.POST, camiseta=pedido.camiseta, instance=pedido, tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes,forma_pag_opcoes=forma_pag_opcoes)
        if form.is_valid():
            form.save()
            messages.success(request, "Pedido atualizado com sucesso!")
            return redirect('carrinho') 
    else:
        form = PedidoForm(instance=pedido,camiseta=pedido.camiseta, tamanhos_opcoes=tamanhos_opcoes, estilos_opcoes=estilos_opcoes, forma_pag_opcoes=forma_pag_opcoes)
    context={
        'tamanhos_por_estilo_json': json.dumps(pedido.camiseta.tamanhos),
        'form': form, 
        'pedido': pedido
    }
    return render(request, 'edit_pedido.html', context)

@login_required
@user_passes_test(vendedor) 
def edit_produto(request, camiseta_id):
    camiseta = get_object_or_404(Camiseta, id=camiseta_id)

    if request.method == 'POST':
        form = CamisetaForm(request.POST, request.FILES, instance=camiseta)
        formset = ImagemCamisetaFormSet(request.POST, request.FILES, queryset=camiseta.imagens.all())

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
        formset = ImagemCamisetaFormSet(queryset=camiseta.imagens.all())

    return render(request, 'edit_produto.html', {'form': form, 'formset': formset})
