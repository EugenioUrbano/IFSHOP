from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_usuario, name='cadastro'),
    
    # Autenticação
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # Usuário
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', views.logout_usuario, name='logout'),
    
    # Gestão de Produtos
    path('gerenciar_produtos/', views.gerenciar_produtos, name='gerenciar_produtos'),
    path('excluir_produto/<int:produto_id>/', views.excluir_produto, name='excluir_produto'),
    
<<<<<<< HEAD
    ##########################################################################
    
    path('edit_camiseta/<int:camiseta_id>/', views.edit_camiseta, name='edit_camiseta'),
    path('pedidos_camisetas/', views.pedidos_camisetas, name="pedidos_camisetas"),
    path('exportar_pedidos_excel/', views.exportar_pedidos_excel, name='exportar_pedidos_excel'),
=======
    # Camisetas
>>>>>>> 8b06a518006c3f36b671532231db8c76d37a97bf
    path('criar_camiseta/', views.criar_camiseta, name='criar_camiseta'),
    path('camiseta/<int:camiseta_id>/', views.camiseta, name='camiseta'),
    path('edit_camiseta/<int:camiseta_id>/', views.edit_camiseta, name='edit_camiseta'),
    
    # Produtos Base
    path('criar_produto/', views.criar_produto, name='criar_produto'),
    path('produto/<int:produto_id>/', views.produto, name='produto'),
    path('edit_produto/<int:produto_id>/', views.edit_produto, name='edit_produto'),
    
    # Pedidos
    path('pedidos_camisetas/', views.pedidos_camisetas, name="pedidos_camisetas"),
    path('pedidos_produtos/', views.pedidos_produtos, name="pedidos_produtos"),
    path('edit_pedido_camiseta/<int:pedido_id>/', views.edit_pedido_camiseta, name='edit_pedido_camiseta'),
    path('edit_pedido_produto/<int:pedido_id>/', views.edit_pedido_produto, name='edit_pedido_produto'),
    path('exportar_pedidos_camisetas_excel/', views.exportar_pedidos_camisetas_excel, name='exportar_pedidos_camisetas_excel'),
    
    # Carrinho e Comprovantes
    path('carrinho/', views.carrinho, name='carrinho'),
    path('comprovantes/<int:pedido_id>/', views.comprovantes, name='comprovantes'),
    path('excluir_pedido/<int:pedido_id>/', views.excluir_pedido, name='excluir_pedido'),
    
    # Utilidades
    path("verificar-pedidos/", views.verificar_pedidos, name="verificar_pedidos"),
    path("marcar-pedidos-vistos/", views.marcar_pedidos_vistos, name="marcar_pedidos_vistos"),
    
    # Admin
    path('gerenciar_vendedores/', views.gerenciar_vendedores, name='gerenciar_vendedores'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
