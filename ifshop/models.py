from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField
from django.utils.timezone import now
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from cloudinary.models import CloudinaryField
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
    foto = CloudinaryField(
        'foto_perfil',
        default=None,  # Cloudinary usa None em vez de string vazia
        null=True,
        blank=True,
        folder='ifshop/usuarios',
        transformation={'quality': 'auto:good', 'width': 300, 'height': 300, 'crop': 'fill'},
        help_text='Foto de perfil do usuário'
    )
    
    def save(self, *args, **kwargs):
        if not self.username: 
            primeiro_nome = self.nome.split()[0] if self.nome else 'user'
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
    
    tem_estoque = models.BooleanField(default=False)
    estoque = models.IntegerField(default=0, null=True, blank=True, verbose_name="Quantidade em estoque")
    
    data_limite_pedidos = models.DateField()
    data_pag1 = models.DateField(help_text="Total ou primeira parcela")
    data_pag2 = models.DateField(null=True, blank=True,help_text="Não precisa colocar")
    
    turma = models.CharField(max_length=50)
    
    turnos = models.CharField(max_length=50)
    curso = models.ManyToManyField('Curso')
    
    imagem = CloudinaryField(
        'imagem_principal',
        default=None,
        null=True,
        blank=True,
        folder='ifshop/produtos',
        transformation={'quality': 'auto:good', 'width': 800, 'height': 600, 'crop': 'fill'},
        help_text='Imagem principal do produto'
    )
    pix_qr_code_parcela = CloudinaryField(
        'qr_code_parcela',
        default=None,
        null=True,
        blank=True,
        folder='ifshop/produtos/qr_codes',
        help_text='QR Code Pix para pagamento parcelado'
    )
    pix_qr_code_total = CloudinaryField(
        'qr_code_total',
        default=None,
        null=True,
        blank=True,
        folder='ifshop/produtos/qr_codes',
        help_text='QR Code Pix para pagamento total'
    )
    pix_chave_parcela = models.TextField(max_length=300, null=True, blank=True, default="")
    pix_chave_total = models.TextField(max_length=300, null=True, blank=True, default="")
    
    opcoes = models.TextField(null=True, help_text="Digite as opções separadas por vírgula. Ex: azul, vermelho, verde")
    
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="produtos")
    
    def lista_opcoes(self):
        if self.opcoes:
            return [opcao.strip() for opcao in self.opcoes.split(",") if opcao.strip()]
        return []
        
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
    imagem = CloudinaryField(
        'imagem_produto',
        default=None,
        null=True,
        blank=True,
        folder='ifshop/produtos/galeria',
        transformation={'quality': 'auto:good', 'width': 800, 'height': 600, 'crop': 'fill'},
        help_text='Imagem adicional do produto'
    )
    principal = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.principal:
            # Desmarca outras imagens como principais para este produto
            ImagemProdutoBase.objects.filter(produto=self.produto, principal=True).update(principal=False)
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        # Cloudinary gerencia automaticamente a exclusão de arquivos
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"Imagem de {self.produto.titulo}"


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
    
    opcao_escolhida = models.CharField(max_length=50, null=True, blank=True)
    
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_entrega = models.DateTimeField(null=True, blank=True)
    
    forma_pag = models.TextField(max_length=300, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_OPCOES, default="Pendente")
    revisado = models.BooleanField(default=True)
    visto = models.BooleanField(default=False)
    
    comprovante_total = CloudinaryField(
        'comprovante_total',
        default=None,
        null=True,
        blank=True,
        folder='ifshop/comprovantes/total',
        resource_type='auto',
        help_text='Comprovante de pagamento total'
    )
    comprovante_parcela1 = CloudinaryField(
        'comprovante_parcela1',
        default=None,
        null=True,
        blank=True,
        folder='ifshop/comprovantes/parcela1',
        resource_type='auto',
        help_text='Comprovante da primeira parcela'
    )
    comprovante_parcela2 = CloudinaryField(
        'comprovante_parcela2',
        default=None,
        null=True,
        blank=True,
        folder='ifshop/comprovantes/parcela2',
        resource_type='auto',
        help_text='Comprovante da segunda parcela'
    )
    
    def save(self, *args, **kwargs):
        """Sobrescreve o save para atualizar estoque quando status muda para Entregue"""
        # Verifica se é uma atualização (tem ID) e não uma criação
        if self.pk:
            try:
                # Obtém o pedido antigo do banco
                pedido_antigo = PedidoBase.objects.get(pk=self.pk)
                status_antigo = pedido_antigo.status
                
                # Se o status mudou de qualquer coisa para "Entregue"
                if status_antigo != 'Entregue' and self.status == 'Entregue':
                    # Atualiza o estoque do produto
                    produto = self.produto
                    
                    if produto.tem_estoque and produto.estoque is not None:
                        if produto.estoque > 0:
                            produto.estoque -= 1
                            produto.save()
                            print(f"Estoque atualizado para {produto.titulo}: {produto.estoque}")
                        else:
                            raise ValueError(f"Produto '{produto.titulo}' esgotado! Não é possível marcar como entregue.")
                    
                    # Atualiza a data de entrega
                    self.data_entrega = timezone.now()
                    
            except PedidoBase.DoesNotExist:
                pass  # É uma criação, não precisa fazer nada
        
        # Salva o pedido
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.produto.titulo if self.produto else 'Sem produto'}"


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
        return self.pedido.status == 'Entregue'
    
    def get_avaliacao_cliente(self):
        """Retorna a avaliação do cliente para este pedido"""
        from .models import Avaliacao
        return Avaliacao.objects.filter(pedido=self.pedido, cliente=self.pedido.cliente).first()


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
    
    @classmethod
    def gerar_codigo(cls, usuario):
        # Gera código de 6 dígitos
        import random
        codigo = str(random.randint(100000, 999999))
        
        # Invalida códigos anteriores
        cls.objects.filter(usuario=usuario, utilizado=False).update(utilizado=True)
        
        return cls.objects.create(usuario=usuario, codigo=codigo)
    
    def esta_valido(self):
        from django.utils import timezone
        from datetime import timedelta
        
        # Código válido por 10 minutos
        tempo_expiracao = timedelta(minutes=10)
        return (not self.utilizado and 
                timezone.now() <= self.criado_em + tempo_expiracao)
    
    def __str__(self):
        return f"Código 2FA para {self.usuario.email} - {self.codigo}"


class VendeCrud(models.Model):
    usuario = models.ForeignKey(UsuarioCustomizado, on_delete=models.CASCADE)
    texto = models.CharField(max_length=500)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.texto} (por {self.usuario.nome})"