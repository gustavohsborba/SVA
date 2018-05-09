# -*- coding: utf-8 -*- 
import re

from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import _lazy_re_compile, RegexValidator



reg = _lazy_re_compile(r'^[a-zA-Z0-9]')
validate_sigla = RegexValidator(
    reg,
    _("Valor inválido para sigla. Use apenas letras e números!"),
    'invalid'
)

def validate_email(value):
    if '@' not in value:
        raise ValidationError(
            _('%Insira um (value) válido!'),
            params={'value': value},
        )

def isGerenteVaga(user):
    return user.groups.filter(name='Gerente Vagas').exists()


""" CPF/CNPJ
__author__ = "Théo Carranza theocarranza@gmail.com"
__copyright__ = "Copyright (C) 2017 Théo Carranza"
__license__ = "Public Domain"
__version__ = "1.0"

 This is a slight modification from the class created by author dudus
 (https://djangosnippets.org/users/dudus/) for use on the model layer.
 It is optimized for Python 3.5  and PEP8 compliant. """

error_messages = {
    'invalid': _("CPF inválido."),
    'invalidCNPJ': _("CNPJ inválido."),
    'digits_only': _("Este campo requer apenas números."),
    'max_digits': _("Este campo permite apenas 11 digitos."),
}


def DV_maker(v):
    if v >= 2:
        return 11 - v
    return 0


def validate_CPF(value):
    """
    Value can be either a string in the format XXX.XXX.XXX-XX or an
    11-digit number.
    """

    if value in EMPTY_VALUES:
        return u''
    if not value.isdigit():
        value = re.sub("[-\.]", "", value)
    orig_value = value[:]
    try:
        int(value)
    except ValueError:
        raise ValidationError(error_messages['digits_only'])
    if len(value) != 11:
        raise ValidationError(error_messages['max_digits'])
    orig_dv = value[-2:]

    new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(10, 1, -1))])
    new_1dv = DV_maker(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(11, 1, -1))])
    new_2dv = DV_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise ValidationError(error_messages['invalid'])

    return orig_value


def validate_CNPJ(value):
    """
    Value can be either a string in the format XX.XXX.XXX/XXXX-XX or a
    group of 14 characters.
    :type value: object
    """
    value = str(value)
    if value in EMPTY_VALUES:
        return u''
    if not value.isdigit():
        value = re.sub("[-/\.]", "", value)
    orig_value = value[:]
    try:
        int(value)
    except ValueError:
        raise ValidationError(error_messages['digits_only'])
    if len(value) > 14:
        raise ValidationError(error_messages['max_digits'])
    orig_dv = value[-2:]

    new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(list(range(5, 1, -1)) + list(range(9, 1, -1)))])
    new_1dv = DV_maker(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(list(range(6, 1, -1)) + list(range(9, 1, -1)))])
    new_2dv = DV_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise ValidationError(error_messages['invalidCNPJ'])

    return orig_value


def validate_cpf_or_cnpj(value):
    valido = False
    try:
        validate_CPF(value)
        valido = True
    except ValidationError:
        pass
    try:
        validate_CNPJ(value)
        valido = True
    except ValidationError:
        pass
    if valido:
        return value
    else:
        raise ValidationError('Entre com um CPF ou CNPJ')
