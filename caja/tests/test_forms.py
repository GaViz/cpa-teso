from django.test import TestCase
from caja.forms import LeerFactura

class FormLeerFacturaTest(TestCase):

    def test_lectura_solo_numeros(self):
        test_codigo = '0125653'
        form_data = {
            'codigo': test_codigo
        }
        form = LeerFactura(data=form_data)
        self.assertTrue(form.is_valid())

    def test_lectura_letras(self):
        test_codigo = 'a123456'
        form_data = {
            'codigo': test_codigo
        }
        form = LeerFactura(data=form_data)
        self.assertFalse(form.is_valid())
