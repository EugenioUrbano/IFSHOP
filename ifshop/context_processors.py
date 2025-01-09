from .models import Pedido

def pedidos_com_imagens(request):
    if not request.user.is_authenticated:
        return {'pedidos_com_imagem': []}

    pedidos = Pedido.objects.filter(cliente=request.user)
    
    pedidos_com_imagem = []
    for pedido in pedidos:
        imagem_principal = (
            pedido.camiseta.imagens.filter(principal=True).first()
            or pedido.camiseta.imagens.first()
        )
        pedidos_com_imagem.append({
            'pedido': pedido,
            'imagem_principal': imagem_principal
        })
    
    return {'pedidos_com_imagem': pedidos_com_imagem}