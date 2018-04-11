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
