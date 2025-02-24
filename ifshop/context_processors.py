from .models import Pedido

def pedidos_usuario(request):
    if request.user.is_authenticated:
        pedidos_feitos = Pedido.objects.filter(cliente=request.user)
    
    else:
        pedidos_feitos = []
        for pedido in pedidos_feitos:
            imagem_principal = (
                pedido.camiseta.imagens.filter(principal=True).first()
                or pedido.camiseta.imagens.first()
            )
        pedidos_feitos.append({
            'pedido': pedido,
            'imagem_principal': imagem_principal
        })

    return {"pedidos_feitos": pedidos_feitos}