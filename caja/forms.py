from django import forms
from django.core.validators import RegexValidator
from .models import User, Empleado
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class LeerFactura(forms.Form):
    solo_numeros = RegexValidator(r'^[0-9]*$')

    codigo = forms.CharField(label='', validators=[solo_numeros], required=True, widget=forms.NumberInput(attrs={'placeholder': 'código de barras', 'class': 'form-control'}))


class FinalizarPago(forms.Form):
    importe = forms.DecimalField(max_digits=10, decimal_places=2, label='', required=True, widget=forms.NumberInput(attrs={'placeholder': 'importe recibido', 'class': 'form-control'}))


class CrearUsuario(forms.Form):
    mail = forms.EmailField(label='', widget=forms.EmailInput(attrs={'placeholder': 'email institucional', 'class': 'form-control', 'size': 30}))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'contraseña', 'class': 'form-control'}), validators=[validate_password])
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'contraseña (confirmación', 'class': 'form-control'}),
                                help_text=_("Para verificar, introduzca la misma contraseña anterior."))

    def clean_mail(self):
        mail = self.cleaned_data['mail'].lower()
        if not mail.endswith('@cajapopular.gov.ar'):
            raise ValidationError(_('El mail ingresado no corresponde al de la Institución.'))
        if User.objects.filter(mail=mail).exists():
            raise ValidationError(_('El mail ya se encuentra registrado'))
        if not Empleado.objects.filter(mail=mail).exists():
            raise ValidationError(_('Empleado no encontrado'))

        return mail

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Las contraseñas no coinciden'))

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(self.cleaned_data['mail'], self.cleaned_data['password1'])
        return user
