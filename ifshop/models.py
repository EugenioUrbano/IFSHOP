from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField
from django.utils.timezone import now
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.db import models
import random
import os

class Curso(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class UsuarioCustomizado(AbstractUser):
    email = models.EmailField(max_length=100, blank=False, null=True, unique=True)
    telefone = models.CharField(max_length=15, blank=False, null=True)
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, blank=True)
    vendedor = models.BooleanField(default=False)
    nome = models.CharField(max_length=150)
    
    def save(self, *args, **kwargs):
        if not self.username: 
            primeiro_nome = self.nome.split()[0]  
            contador = 1
            username_base = primeiro_nome.lower()
            username_gerado = username_base

            while UsuarioCustomizado.objects.filter(username=username_gerado).exists():
                contador += 1
                username_gerado = f"{username_base}_{contador}"

            self.username = username_gerado

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email
    
####################################################################################################

class ProdutoBase(models.Model):
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
    preco_parcela = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    forma_pag_op = models.CharField(max_length=200,null=True, blank=True)
    
    data_limite_pedidos = models.DateField()
    data_pag1 = models.DateField(help_text="Total ou primeira parcela")
    data_pag2 = models.DateField(null=True, blank=True,help_text="Não precisa colocar")
    
    turma = models.CharField(max_length=50)
    
    turnos = models.CharField(max_length=50)
    curso = models.ManyToManyField('Curso')
    
    imagem = models.ImageField(blank=True, null=True)
    pix_qr_code_parcela = models.ImageField(upload_to='qrcode_parcela_produtos/', null=False, default="")
    pix_qr_code_total = models.ImageField(upload_to='qrcode_total_produtos/', null=False, default="")
    pix_chave_parcela = models.TextField(max_length=300, null=False, default="")
    pix_chave_total = models.TextField(max_length=300, null=False, default="")
    
    opcoes = models.TextField( null=True, help_text="Digite as opções separadas por vírgula. Ex: azul, vermelho, verde")
    
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="produtos")
    
    def lista_opcoes(self):
        return [opcao.strip() for opcao in self.opcoes.split(",") if opcao.strip()]
        
    def __str__(self):
        return self.titulo
    
    @property
    def media_avaliacoes(self):
        """Calcula a média das avaliações"""
        avaliacoes = self.avaliacoes.all()
        if avaliacoes:
            return sum(av.estrelas for av in avaliacoes) / len(avaliacoes)
        return 0
    
    @property
    def total_avaliacoes(self):
        """Retorna o total de avaliações"""
        return self.avaliacoes.count()
    
    def get_avaliacoes_por_estrela(self, estrelas):
        """Retorna avaliações por quantidade de estrelas"""
        return self.avaliacoes.filter(estrelas=estrelas).count()
    
    def get_distribuicao_estrelas(self):
        """Retorna a distribuição percentual das estrelas"""
        total = self.total_avaliacoes
        if total == 0:
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        return {
            estrelas: (self.get_avaliacoes_por_estrela(estrelas) / total) * 100
            for estrelas in range(1, 6)
        }

class ImagemProdutoBase(models.Model):
    produto = models.ForeignKey(ProdutoBase, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='imagens_produtos/', null=True)
    principal = models.BooleanField(default=False) 

    def delete(self, *args, **kwargs):
        if self.imagem and os.path.isfile(self.imagem.path):
            os.remove(self.imagem.path)  
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        if self.principal:
            ImagemProdutoBase.objects.filter(produto=self.produto, principal=True).update(principal=False)
        super().save(*args, **kwargs)


class Camiseta(ProdutoBase):
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

    estilos = models.CharField(max_length=50, default="")
    tamanhos = JSONField(default=dict)

    def __str__(self):
        return f"Camiseta: {self.titulo}"


class EstiloTamanho(models.Model):
    ESTILOS_OPCOES = Camiseta.ESTILOS_OPCOES
    TAMANHOS_OPCOES = Camiseta.TAMANHOS_OPCOES

    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE, related_name='estilos_tamanhos')
    estilo = models.CharField(max_length=20, choices=ESTILOS_OPCOES)
    tamanho = models.CharField(max_length=5, choices=TAMANHOS_OPCOES)

    def __str__(self):
        return f"{self.estilo} - {self.tamanho} ({self.camiseta.titulo})"
        
####################################################################################################

class PedidoBase(models.Model):
    STATUS_OPCOES = [
	    ('Pendente', 'Pendente'),
        ('Pago Totalmente', 'Pago Totalmente'),
        ('Pago 1° Parcela', 'Pago 1° Parcela'),
        ('Negociando com Usuario', 'Negociando com Usuario'), 
        ('Entregue','Entregue')       
    ]
    FORMA_PAG_OPCOES = [
        ('Pix', 'Pix'),
        ('Dinheiro Físico', 'Dinheiro Físico'),
        ('Parcelado 2x Pix', 'Parcelado 2x Pix'),
        ('Parcelado 2x Fisico', 'Parcelado 2x Fisico'),
        ('Negociar Pagamento', 'Negociar Pagamento'),
    ]
    
    produto = models.ForeignKey(ProdutoBase, null=True, on_delete=models.CASCADE, related_name="pedidos_base")
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="pedidos")
    
    opcao_escolhida = models.CharField(max_length=50, null=True)
    
    data_pedido = models.DateTimeField(auto_now_add=True)
    
    forma_pag = models.TextField(max_length=300,null=True)
    status = models.CharField(max_length=100, default="Pendente")
    revisado = models.BooleanField(default=True)
    visto = models.BooleanField(default=False)
    
    comprovante_total = models.ImageField(upload_to='comprovante_total_produto/', null=True, blank=True, default="")
    comprovante_parcela1 = models.ImageField(upload_to='comprovante_parcela1_produto/', null=True, blank=True, default="")
    comprovante_parcela2 = models.ImageField(upload_to='comprovante_parcela2_produto/', null=True, blank=True, default="")
    
    
class PedidoCamiseta(models.Model):
    pedido = models.ForeignKey(PedidoBase, on_delete=models.CASCADE, related_name="camisetas")
    camiseta = models.ForeignKey(Camiseta, on_delete=models.CASCADE)
    
    nome_estampa = models.CharField(max_length=50)
    numero_estampa = models.CharField(max_length=50)
    
    tamanho = models.CharField(max_length=10)
    estilo = models.CharField(max_length=20, default="")
    
    def __str__(self):
        return f"Pedido de camiseta para {self.camiseta.titulo} - {self.nome_estampa} ({self.numero_estampa})"
    
    @property
    def pode_ser_avaliado(self):
        """Verifica se o pedido pode ser avaliado"""
        return self.status == 'Entregue'
    
    def get_avaliacao_cliente(self):
        """Retorna a avaliação do cliente para este pedido"""
        return self.avaliacoes.filter(cliente=self.cliente).first()


####################################################################################################

class Avaliacao(models.Model):
    ESTRELAS_OPCOES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    produto = models.ForeignKey(
        'ProdutoBase', 
        on_delete=models.CASCADE, 
        related_name='avaliacoes'
    )
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='avaliacoes'
    )
    pedido = models.ForeignKey(
        'PedidoBase', 
        on_delete=models.CASCADE, 
        related_name='avaliacoes'
    )
    estrelas = models.IntegerField(
        choices=ESTRELAS_OPCOES,
        verbose_name='Avaliação'
    )
    comentario = models.TextField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name='Comentário'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['produto', 'cliente', 'pedido']  # Uma avaliação por pedido
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Avaliação de {self.cliente.nome} para {self.produto.titulo} - {self.estrelas} estrelas"
    
    def get_estrelas_display(self):
        """Retorna as estrelas em formato de texto"""
        return '⭐' * self.estrelas
    
    
class Codigo2FA(models.Model):
    usuario = models.ForeignKey(UsuarioCustomizado, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)
    utilizado = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.usuario.email} - {self.codigo}"
    
    def esta_valido(self):
        """Verifica se o código ainda é válido (10 minutos)"""
        return (timezone.now() - self.criado_em) < timedelta(minutes=10) and not self.utilizado
    
    @classmethod
    def gerar_codigo(cls, usuario):
        """Gera um novo código 2FA"""
        # Remove códigos antigos
        cls.objects.filter(usuario=usuario).delete()
        
        # Gera código de 6 dígitos
        codigo = str(random.randint(100000, 999999))
        
        return cls.objects.create(usuario=usuario, codigo=codigo)