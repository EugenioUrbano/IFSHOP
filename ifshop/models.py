from django.contrib.auth.models import User
from django.db import models



class Camiseta(models.Model):
    TAMANHOS_OPCOES = [
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
        ('GG', 'Extra Grande')
    ]
    
    ESTILOS_OPCOES = [
        ('babylook', 'BabyLook'),
        ('normal', 'Normal'),
        ('infantil', 'Infantil')
    ]

    CURSOS_OPCOES = [
        ('infoweb', 'InfoWeb'),
        ('edific', 'Edific'),
        ('mamb', 'Mamb')
    ]
    
    TURNOS_OPCOES = [
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino')
    ]

    titulo = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data_limite_pedidos = models.DateField()
    data_para_entrega = models.DateField()
    cores = models.CharField(max_length=200) 
    tamanhos = models.CharField(max_length=50) 
    turnos = models.CharField(max_length=50)
    cursos = models.CharField(max_length=50)
    estilos = models.CharField(max_length=50, default="" )  
    imagens = models.ImageField(upload_to="imagens_camisetas/", blank=True, null=True)

    def __str__(self):
        return self.titulo

####################################################################################################

class Pedido(models.Model):
    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE)
    nome_estampa = models.CharField(max_length=50)
    numero_estampa = models.IntegerField()
    cor = models.CharField(max_length=20)
    tamanho = models.CharField(max_length=10)
    estilo = models.CharField(max_length=20, default="")
    data_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido para {self.camiseta.titulo} - {self.nome_estampa} ({self.numero_estampa})"
