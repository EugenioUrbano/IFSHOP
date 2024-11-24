from django.contrib.auth.models import AbstractUser
from django.db import models



class UsuarioCustom(AbstractUser):
    CURSOS_USER_OPCOES = [
        ('infoweb', 'InfoWeb'),
        ('edific', 'Edific'),
        ('mamb', 'Mamb'),
        ('outros','Outros')
    ]
    
    email = models.EmailField(unique=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=15, verbose_name="Telefone")
    matricula_cpf = models.CharField(max_length=14, unique=True, verbose_name="Matricula|CPF")
    cursos_user = models.CharField(max_length=20,verbose_name="Curso")
    
    USERNAME_FIELD = 'email'  # Define o e-mail como campo de login
    REQUIRED_FIELDS = ['nome', 'telefone', 'matricula_cpf', 'cursos']  # Campos obrigatórios além do e-mail

    def __str__(self):
        return (self.username)-(self.matricula_cpf)



####################################################################################################

class Cor(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome
    
####################################################################################################

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
