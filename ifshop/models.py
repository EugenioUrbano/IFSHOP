from django.db import models
from django.contrib.auth.models import AbstractUser


####################################################################################################

class Cor(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome
    

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
        ('mamb', 'Mamb'),
        ('outro', 'Outro'),
    ]
    
    TURNOS_OPCOES = [
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
        ('noturno', 'Noturno'),
    ]

    titulo = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data_limite_pedidos = models.DateField()
    data_para_entrega = models.DateField()
    cores = models.ManyToManyField(Cor, blank=True) 
    tamanhos = models.CharField(max_length=50) 
    turnos = models.CharField(max_length=50)
    cursos = models.CharField(max_length=50)
    imagem = models.ImageField(blank=True)
    estilos = models.CharField(max_length=50, default="" )  

    def __str__(self):
        return self.titulo

####################################################################################################

class Pedido(models.Model):
    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE)
    nome_estampa = models.CharField(max_length=50)
    numero_estampa = models.CharField(max_length=50)
    cor = models.CharField(max_length=20)
    tamanho = models.CharField(max_length=10)
    estilo = models.CharField(max_length=20, default="")
    data_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido para {self.camiseta.titulo} - {self.nome_estampa} ({self.numero_estampa})"

####################################################################################################


