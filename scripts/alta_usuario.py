import os
from caja.models import Empleado, User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tesoro.settings")


def run():
    # empleado = Empleado(legajo="2537", apellido="DIAZ LEDERHOS", nombre="NAHUEL MATIAS", mail="nmdiaz@cajapopular.gov.ar", estado=True)
    # empleado.save()
    for empleado in Empleado.objects.all():
        print(empleado.apellido)
        if not User.objects.filter(mail=empleado.mail).exists():
            User.objects.create_user(empleado.mail, str(int(empleado.legajo)))
