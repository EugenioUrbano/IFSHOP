from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('camiseta/<int:camiseta_id>', views.camiseta, name='camiseta'),
    path('adicionar_pro/', views.adicionar_pro, name='adicionar_pro')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)