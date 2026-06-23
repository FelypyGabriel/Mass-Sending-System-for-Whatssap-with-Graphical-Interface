from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxLengthValidator


class AntiBanConfig(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    intervalo_min = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)]
    )

    intervalo_max = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1)]
    )

    limite_diario = models.IntegerField(
        default=200,
        validators=[MinValueValidator(1)]
    )

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nome = self.usuario.username if self.usuario else "user_desconhecido"
        return f"AntiBan - {nome}"

    def clean(self):
        if self.intervalo_min > self.intervalo_max:
            raise ValueError("intervalo minimo maior que o max... nao faz sentido né")


class Grupo(models.Model):
    nome = models.CharField(
        max_length=50,
        validators=[MaxLengthValidator(50)]
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grupos"
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['nome', 'usuario'],
                name='unique_grupo_por_usuario'
            )
        ]
        indexes = [
            models.Index(fields=['usuario'])
        ]

    def __str__(self):
        return self.nome.strip() if self.nome else "grupo_sem_nome"


class Contato(models.Model):
    nome = models.CharField(
        max_length=100
    )

    telefone = models.CharField(
        max_length=20
    )

    grupo = models.ForeignKey(
        Grupo,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contatos"
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    ativo = models.BooleanField(default=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['telefone'])
        ]

    def __str__(self):
        nome = self.nome.strip() if self.nome else "sem_nome"
        tel = self.telefone.strip() if self.telefone else "sem_num"
        return f"{nome} - {tel}"


class Mensagem(models.Model):
    texto = models.TextField(
        validators=[MaxLengthValidator(5000)]
    )

    intervalo_base = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['usuario'])
        ]

    def __str__(self):
        return f"Msg {self.id}"


class LogEnvio(models.Model):
    STATUS_CHOICES = (
        ('ENVIADO', 'Enviado'),
        ('ERRO', 'Erro'),
        ('BLOQUEADO', 'Bloqueado'),
        ('IGNORADO', 'Ignorado'),
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    contato = models.ForeignKey(
        Contato,
        on_delete=models.CASCADE
    )

    mensagem = models.ForeignKey(
        Mensagem,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        db_index=True
    )

    erro = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(1000)]
    )

    enviado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['enviado_em'])
        ]

    def __str__(self):
        return f"{self.status} - {self.enviado_em}"