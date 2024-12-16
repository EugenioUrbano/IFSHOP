from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import cadastro_usuario, LoginUsuarioView

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', LoginUsuarioView.as_view(), name='login'),
    path('cadastro/', cadastro_usuario, name='cadastro'),
    path('perfil/', views.perfil, name='perfil'),
    path('gerenciar_pro/', views.gerenciar_pro, name='gerenciar_pro'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('camiseta/<int:camiseta_id>', views.camiseta, name='camiseta'),
    path('adicionar_pro/', views.adicionar_pro, name='adicionar_pro'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)