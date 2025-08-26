from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import cadastro_usuario, logout_usuario, verificar_pedidos, marcar_pedidos_vistos, gerenciar_vendedores

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.login_view, name='login'),
    path('cadastro/',cadastro_usuario, name='cadastro'),
    ##########################################################################
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    ##########################################################################
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', logout_usuario, name='logout'),
    path('gerenciar_pro/', views.gerenciar_pro, name='gerenciar_pro'),
    path('excluir_produto/<int:camiseta_id>/', views.excluir_produto, name='excluir_produto'),
    path('edit_produto/<int:camiseta_id>/', views.edit_produto, name='edit_produto'),
    path('gerenciar_pedidos/', views.gerenciar_pedidos, name="gerenciar_pedidos"),
    path('exportar-pedidos/', views.exportar_pedidos_excel, name='exportar_pedidos'),
    path('adicionar_pro/', views.adicionar_pro, name='adicionar_pro'),
    ##########################################################################
    path('carrinho/', views.carrinho, name='carrinho'),
    path('comprovantes/<int:pedido_id>/', views.comprovantes, name='comprovantes'),
    path('edit_pedido/<int:pedido_id>/',views.edit_pedido, name='edit_pedido'),
    path('excluir_pedido/<int:pedido_id>/', views.excluir_pedido, name='excluir_pedido'),
    path("verificar-pedidos/", verificar_pedidos, name="verificar_pedidos"),
    path("marcar-pedidos-vistos/", marcar_pedidos_vistos, name="marcar_pedidos_vistos"),
    path('camiseta/<int:camiseta_id>/', views.camiseta, name='camiseta'),
    path('gerenciar_vendedores/', views.gerenciar_vendedores, name='gerenciar_vendedores'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
