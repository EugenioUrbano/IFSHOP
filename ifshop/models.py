import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

     
class UsuarioCustomizado(AbstractUser):
    CURSOS_OPCOES = [
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
    FORMA_PAG_OPCOES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
        ('cartão', 'Cartão'),
        ('em duas vezes', 'Em duas Vezes')
    ]

    titulo = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pag_op = models.CharField(max_length=100,null=True)
    data_limite_pedidos = models.DateField()
    data_para_entrega = models.DateField()
    tamanhos = models.CharField(max_length=50) 
    turnos = models.CharField(max_length=50)
    cores = models.TextField( null=True, help_text="Digite as cores separadas por vírgula. Ex: azul, vermelho, verde")
    cursos = models.CharField(max_length=50)
    imagem = models.ImageField(blank=False)
    estilos = models.CharField(max_length=50, default="" )
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="camisetas")

    def lista_cores(self):
        return [cor.strip() for cor in self.cores.split(",") if cor.strip()]
    
    def save(self, *args, **kwargs):
        if self.pk: 
            pedidos = Pedido.objects.filter(camiseta=self)
            pedidos.update(revisado=False) 
            
        self.cores = ", ".join(self.lista_cores())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
    


class ImagemCamiseta(models.Model):
    camiseta = models.ForeignKey(Camiseta, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='imagens_camisetas/', null=True)
    principal = models.BooleanField(default=False) 

    def delete(self, *args, **kwargs):
        if self.imagem and os.path.isfile(self.imagem.path):
            os.remove(self.imagem.path)  
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        if self.principal:
            ImagemCamiseta.objects.filter(camiseta=self.camiseta, principal=True).update(principal=False)
        super().save(*args, **kwargs)
        
####################################################################################################

class Pedido(models.Model):
    STATUS_OPCOES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('negociando', 'Negociando'),
    ]
    FORMA_PAG_OPCOES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
        ('cartão', 'Cartão'),
        ('em duas vezes', 'Em duas Vezes')
    ]
    
    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE)
    nome_estampa = models.CharField(max_length=50)
    numero_estampa = models.CharField(max_length=50)
    cor_escolhida = models.CharField(max_length=50, null=True)
    tamanho = models.CharField(max_length=10)
    estilo = models.CharField(max_length=20, default="")
    data_pedido = models.DateTimeField(auto_now_add=True)
    forma_pag = models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=100, default="Pendente")
    revisado = models.BooleanField(default=True)
    visto = models.BooleanField(default=False)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="pedidos")

    def __str__(self):
        return f"Pedido para {self.camiseta.titulo} - {self.nome_estampa} ({self.numero_estampa})"

####################################################################################################