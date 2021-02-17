from django.test import TestCase
from django.urls import reverse
from .models import User, Empleado


class LoginTests(TestCase):
    test_mail = 'nmdiaz@cajapopular.gov.ar'
    test_password = 'secret'

    def setUp(self):
        test_empleado = Empleado(legajo='1234', apellido="DIAZ LEDERHOS", nombre="NAHUEL MATIAS", mail='nmdiaz@cajapopular.gov.ar', estado=True)
        test_empleado.save()
        self.credentials = {
            'mail': self.test_mail,
            'password': self.test_password}
        User.objects.create_user(**self.credentials)

    def test_login_usuario_existente(self):
        """
        Si el usuario existe, inicia sesión.
        """
        login = self.client.login(mail=self.test_mail, password=self.test_password)
        self.assertTrue(login)

    def test_login_usuario_inexistente(self):
        """
        Si el usuario no existe, no inicia sesión.
        """
        login = self.client.login(mail='prueba@cajapopular.gov.ar', password=self.test_password)
        self.assertFalse(login)

    def test_login_password_incorrecta(self):
        """
        Si la contraseña es incorrecta, no inicia sesión.
        """
        login = self.client.login(mail=self.test_mail, password='password')
        self.assertFalse(login)

    def test_login_exitoso_redireccion(self):
        """
        Si el login es exitoso, redirecciona pantalla principal.
        """
        self.client.login(mail=self.test_mail, password=self.test_password)
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'caja/index.html')
