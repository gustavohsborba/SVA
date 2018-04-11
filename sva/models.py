from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User
from django.core.validators import *
from django.db import models

# Create your models here.
from .validators import validate_sigla


class Campus(models.Model):
    class Meta:
        verbose_name_plural = _('campi')

    CIDADE_CHOICES = {
         ('BELO HORIZONTE', 'Belo Horizonte'),
         ('LEOPOLDINA', 'Leopoldina'),
         ('ARAXA', 'Araxá'),
         ('DIVINOPOLIS', 'Divinópolis'),
         ('VARGINHA', 'Varginha'),
         ('TIMOTEO', 'Timóteo'),
         ('NEPOMUCENO', 'Nepomuceno'),
         ('CURVELO', 'Curvelo'),
         ('CONTAGEM', 'Contagem')
    }

    nome = models.CharField(max_length=45, null=False)
    cidade = models.CharField(max_length=45, null=False, choices=CIDADE_CHOICES)
    sigla = models.CharField(max_length=5, null=False, unique=True, validators=[validate_sigla])


class Curso(models.Model):
    NIVEL_ENSINO_CHOICES = {
        (1, 'TECNICO'),
        (2, 'GRADUACAO'),
        (3, 'MESTRADO'),
        (4, 'DOUTORADO'),
        (5, 'ESPECIALIZACAO')
    }
    nome = models.CharField(max_length=45, null=False)
    sigla = models.CharField(max_length=5, null=False, unique=True, validators=[validate_sigla])
    nivel_ensino = models.IntegerField(null=False, choices=NIVEL_ENSINO_CHOICES)


class Perfil(User):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, null=True, validators=[validate_integer])
    curso = models.ForeignKey(to=Curso, null=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Perfil.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.perfil.save()
