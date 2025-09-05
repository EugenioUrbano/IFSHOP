from .models import PedidoBase, PedidoCamiseta

def pedidos_usuario(request):
    pedidos_feitos = []
    
    if request.user.is_authenticated:
        pedidos = PedidoBase.objects.filter(cliente=request.user).select_related("produto")
        
        for pedido in pedidos:
            imagem_principal = (
                pedido.produto.imagens.filter(principal=True).first()
                or pedido.produto.imagens.first()
            )
            
            camisetas = PedidoCamiseta.objects.filter(pedido=pedido).select_related("camiseta")
            
            pedidos_feitos.append({
                "pedido": pedido,              
                "imagem_principal": imagem_principal,
                "camisetas": camisetas,        
            })
    
    return {"pedidos_feitos": pedidos_feitos}