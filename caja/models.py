from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid


class Empleado(models.Model):
    legajo = models.CharField(max_length=4, unique=True)
    apellido = models.CharField(max_length=25)
    nombre = models.CharField(max_length=25)
    mail = models.EmailField()

    estado = models.BooleanField()

    class Meta:
        db_table = 'empleados'


class Empresa(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'empresas'


class Sucursal(models.Model):
    nombre = models.CharField(max_length=20)

    class Meta:
        db_table = 'sucursales'


class Lote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    cajero = models.ForeignKey('Empleado', models.PROTECT)
    sucursal = models.ForeignKey('Sucursal', models.PROTECT, null=True)
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'lotes'


class Pago(models.Model):
    codigo = models.CharField(max_length=50)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    numero_factura = models.CharField(max_length=10)
    importe = models.DecimalField(max_digits=8, decimal_places=2)

    empresa = models.ForeignKey('Empresa', models.PROTECT, null=True)
    lote = models.ForeignKey('Lote', models.PROTECT)

    class Meta:
        db_table = 'pagos'


class UserManager(BaseUserManager):
    def create_user(self, mail, password=None):
        if not mail:
            raise ValueError('Debe ingresar un mail')

        if not Empleado.objects.filter(mail=mail).exists():
            raise ValueError('No existe empleado')

        user = self.model(mail=self.normalize_email(mail))
        user.set_password(password)
        user.empleado = Empleado.objects.get(mail=mail)
        user.save(using=self._db)
        return user

    def create_superuser(self, mail, password=None):
        user = self.create_user(mail=mail, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    mail = models.EmailField(verbose_name='mail', max_length=255, unique=True)
    empleado = models.OneToOneField(Empleado, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'mail'
    EMAIL_FIELD = 'mail'

    objects = UserManager()

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def natural_key(self):
        return self.mail

    def __str__(self):
        return self.mail

    class Meta:
        db_table = 'usuarios'
