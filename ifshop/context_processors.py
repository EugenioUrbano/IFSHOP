from .models import Pedido

def pedidos_usuario(request):
    pedidos_feitos = []
    pedidos = []
    
    if request.user.is_authenticated:
        pedidos = Pedido.objects.filter(cliente=request.user)
    
    for pedido in pedidos:
            imagem_principal = (
                pedido.camiseta.imagens.filter(principal=True).first()
                or pedido.camiseta.imagens.first()
            )
            pedidos_feitos.append({
                'pedido': pedido,
                'imagem_principal': imagem_principal
            })


    return {"pedidos_feitos": pedidos_feitos}