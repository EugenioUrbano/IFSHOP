from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

     
class UsuarioCustomizado(AbstractUser):
    CURSOs_OPCOES = [
        ('infoweb', 'InfoWeb'),
        ('edific', 'Edific'),
        ('mamb', 'Mamb'),
        ('outro', 'Outro'),
    ]
    email = models.EmailField(max_length=100, blank=False, null=True, unique=True)
    telefone = models.CharField(max_length=15, blank=False, null=True)
    matricula_cpf = models.CharField(max_length=15, blank=False, null=True, unique=True)
    curso = models.CharField(max_length=50, blank=False, null=True)
    vendedor = models.BooleanField(default=False)
    nome = models.CharField(max_length=150)
    
    def save(self, *args, **kwargs):
        if not self.username:  # Apenas gera username se estiver vazio
            primeiro_nome = self.nome.split()[0]  # Captura o primeiro nome
            contador = 1
            username_base = primeiro_nome.lower()
            username_gerado = username_base

            # Garante que o username seja único
            while UsuarioCustomizado.objects.filter(username=username_gerado).exists():
                contador += 1
                username_gerado = f"{username_base}_{contador}"

            self.username = username_gerado

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email
    
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
    cores = models.ManyToManyField(Cor, blank=False) 
    tamanhos = models.CharField(max_length=50) 
    turnos = models.CharField(max_length=50)
    cursos = models.CharField(max_length=50)
    imagem = models.ImageField(blank=False)
    estilos = models.CharField(max_length=50, default="" )
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="camisetas")

    def __str__(self):
        return self.titulo
    
    
class ImagemCamiseta(models.Model):
    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='imagens_camisetas/')
    principal = models.BooleanField(default=False)  # Indica se é a imagem principal

    def save(self, *args, **kwargs):
        # Garante que só uma imagem seja marcada como principal
        if self.principal:
            ImagemCamiseta.objects.filter(camiseta=self.camiseta, principal=True).update(principal=False)
        super().save(*args, **kwargs)
####################################################################################################

class Pedido(models.Model):
    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE)
    nome_estampa = models.CharField(max_length=50)
    numero_estampa = models.CharField(max_length=50)
    cor = models.CharField(max_length=20)
    tamanho = models.CharField(max_length=10)
    estilo = models.CharField(max_length=20, default="")
    data_pedido = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="pedidos")

    def __str__(self):
        return f"Pedido para {self.camiseta.titulo} - {self.nome_estampa} ({self.numero_estampa})"

####################################################################################################