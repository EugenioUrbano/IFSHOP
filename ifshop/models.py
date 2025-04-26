from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.db.models import JSONField
from django.conf import settings
from django.db import models
import os


class UsuarioCustomizado(AbstractUser):
    CURSOS_OPCOES = [
        ('infoweb', 'InfoWeb'),
        ('edific', 'Edific'),
        ('mamb', 'Mamb'),
        ('outro', 'Outro'),
    ]
    email = models.EmailField(max_length=100, blank=False, null=True, unique=True)
    telefone = models.CharField(max_length=15, blank=False, null=True)
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
        ('PP', 'PP'),
        ('P', 'P'),
        ('M', 'M'),
        ('G', 'G'),
        ('GG', 'GG'),
	('XG', 'XG'),
	('XGG', 'XGG')
    ]
    
    ESTILOS_OPCOES = [
        ('Babylook', 'BabyLook'),
        ('Normal', 'Normal'),
        ('Infantil', 'Infantil')
    ]

    CURSOS_OPCOES = [
        ('infoweb', 'InfoWeb'),
        ('edific', 'Edific'),
        ('mamb', 'Mamb'),
        ('outro', 'Outro'),
    ]
    
    TURNOS_OPCOES = [
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Noturno', 'Noturno'),
    ]
    FORMA_PAG_OPCOES = [
        ('Pix', 'Pix'),
        ('Dinheiro Físico', 'Dinheiro Físico'),
        ('Parcelado 2x Pix', 'Parcelado 2x Pix'),
        ('Parcelado 2x Fisico', 'Parcelado 2x Fisica'),
        ('Negociar Pagamento', 'Negociar Pagamento'),
    ]

    titulo = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_parcela = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    forma_pag_op = models.CharField(max_length=200,null=True)
    data_limite_pedidos = models.DateField()
    data_pag1 = models.DateField(help_text="Total ou primeira parcela")
    data_pag2 = models.DateField(null=True, blank=True,help_text="Não precisa colocar")
    turnos = models.CharField(max_length=50)
    cores = models.TextField( null=True, help_text="Digite as cores separadas por vírgula. Ex: azul, vermelho, verde")
    cursos = models.CharField(max_length=50)
    imagem = models.ImageField(blank=False)
    pix_qr_code_parcela = models.ImageField(upload_to='qrcode_parcela_camisetas/', null=False, default="")
    pix_qr_code_total = models.ImageField(upload_to='qrcode_total_camisetas/', null=False, default="")
    pix_chave_parcela = models.TextField(max_length=300, null=False, default="")
    pix_chave_total = models.TextField(max_length=300, null=False, default="")
    estilos = models.CharField(max_length=50, default="" )
    tamanhos = JSONField(default=dict)
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
    
class EstiloTamanho(models.Model):
    ESTILOS_OPCOES = Camiseta.ESTILOS_OPCOES
    TAMANHOS_OPCOES = Camiseta.TAMANHOS_OPCOES

    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE, related_name='estilos_tamanhos')
    estilo = models.CharField(max_length=20, choices=ESTILOS_OPCOES)
    tamanho = models.CharField(max_length=5, choices=TAMANHOS_OPCOES)

    def __str__(self):
        return f"{self.estilo} - {self.tamanho} ({self.camiseta.titulo})"

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
	('Pendente', 'Pendente'),
        ('Pago Totalmente', 'Pago Totalmente'),
        ('Pago 1° Parcela', 'Pago 1° Parcela'),
        ('Negociando com Usuario', 'Negociando com Usuario'),        
    ]
    FORMA_PAG_OPCOES = [
        ('Pix', 'Pix'),
        ('Dinheiro Físico', 'Dinheiro Físico'),
        ('Parcelado 2x Pix', 'Parcelado 2x Pix'),
        ('Parcelado 2x Fisico', 'Parcelado 2x Fisico'),
        ('Negociar Pagamento', 'Negociar Pagamento'),
    ]
    
    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE)
    nome_estampa = models.CharField(max_length=50)
    numero_estampa = models.CharField(max_length=50)
    cor_escolhida = models.CharField(max_length=50, null=True)
    tamanho = models.CharField(max_length=10)
    estilo = models.CharField(max_length=20, default="")
    data_pedido = models.DateTimeField(auto_now_add=True)
    forma_pag = models.TextField(max_length=300,null=True)
    status = models.CharField(max_length=100, default="Pendente")
    revisado = models.BooleanField(default=True)
    visto = models.BooleanField(default=False)
    comprovante_total = models.ImageField(upload_to='qrcode_total_camisetas/', null=False, default="")
    comprovante_parcela1 = models.ImageField(upload_to='qrcode_total_camisetas/', null=False, default="")
    comprovante_parcela2 = models.ImageField(upload_to='qrcode_total_camisetas/', null=False, default="")

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="pedidos")

    def __str__(self):
        return f"Pedido para {self.camiseta.titulo} - {self.nome_estampa} ({self.numero_estampa})"

####################################################################################################
