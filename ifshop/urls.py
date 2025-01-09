from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import cadastro_usuario, logout_usuario

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.login_view, name='login'),
    path('cadastro/',cadastro_usuario, name='cadastro'),
    ##########################################################################
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', logout_usuario, name='logout'),
    path('gerenciar_pro/', views.gerenciar_pro, name='gerenciar_pro'),
    path('edit_produto/', views.edit_produto, name='edit_produto'),
    path('gerenciar_pedidos/', views.gerenciar_pedidos, name="gerenciar_pedidos"),
    path('adicionar_pro/', views.adicionar_pro, name='adicionar_pro'),
    ##########################################################################
    path('carrinho/', views.carrinho, name='carrinho'),
    path('edit_pedido/<int:pedido_id>/',views.edit_pedido, name='edit_pedido'),
    path('camiseta/<int:camiseta_id>', views.camiseta, name='camiseta'),
    
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)