from django.test import TestCase
from django.urls import reverse
from caja.models import User, Empleado


class LoginTests(TestCase):
    test_mail = 'nmdiaz@cajapopular.gov.ar'
    test_password = 'secret'

    def setUp(self):
        Empleado.objects.create(legajo='1234', apellido="DIAZ LEDERHOS", nombre="NAHUEL MATIAS", mail='nmdiaz@cajapopular.gov.ar', estado=True)
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

    def test_login_exitoso_index(self):
        """
        Si está logueado, puede ver pantalla principal.
        """
        self.client.login(mail=self.test_mail, password=self.test_password)
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'caja/index.html')

    def test_redireccion_sin_login(self):
        """
        Si no se está logueado, se redirecciona a la página de login.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))


class ListadoViewTest(TestCase):
    test_mail = 'nmdiaz@cajapopular.gov.ar'
    test_password = 'secret'

    def setUp(self):
        test_empleado = Empleado(legajo='1234', apellido="DIAZ LEDERHOS", nombre="NAHUEL MATIAS", mail='nmdiaz@cajapopular.gov.ar', estado=True)
        test_empleado.save()
        self.credentials = {
            'mail': self.test_mail,
            'password': self.test_password}
        User.objects.create_user(**self.credentials)
        self.client.login(mail=self.test_mail, password=self.test_password)

        session = self.client.session
        session['facturas'] = {'codigos': []}
        session.save()

    def test_primera_vista_sin_facturas(self):
        """
        Primer acceso sin facturas leídas.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['facturas'], {'codigos': []})

    def test_finalizar_sin_facturas(self):
        """
        Sin facturas no se puede finalizar el cobro.
        """
        response = self.client.post(reverse('finalizar'))
        self.assertEqual(response.status_code, 500)

    def test_codigo_ya_leido(self):
        """
        Si la factura ya se leyó, mostrar error.
        """
        session = self.client.session
        session['facturas']['codigos'].append('01005237707000815000210624')
        session.save()
        response = self.client.post(reverse('index'), {'codigo': '01005237707000815000210624'})
        self.assertJSONEqual(response.content, {'mensaje': 'Factura ya leída'})
        self.assertEqual(response.status_code, 500)

    def test_lectura_codigo_edet(self):
        """
        Lectura correcto factura EDET.
        """
        response = self.client.post(reverse('index'), {'codigo': '01005237707000815000210624'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'codigo': '01005237707000815000210624',
            'empresa': 'EDET',
            'fecha': '2021-03-03',
            'importe': 8150.0,
            'numero_factura': '52377070'
        })

    def test_codigo_edet_vencido(self):
        """
        Si la factura de EDET está vencida, mostrar error.
        """
        session = self.client.session
        session['facturas']['codigos'].append('01005237707000815000210304')
        session.save()
        response = self.client.post(reverse('index'), {'codigo': '01005237707000815000210104'})
        self.assertJSONEqual(response.content, {'mensaje': 'Fuera de término!'})
        self.assertEqual(response.status_code, 500)
