from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from caja.forms import LeerFactura, CrearUsuario, FinalizarPago
from django.http import JsonResponse
import datetime
from .models import Lote, Pago
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = CrearUsuario(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('login'))

    else:
        form = CrearUsuario()

    template_name = 'registration/register.html'
    context = {
        'form': form,
    }

    return render(request, template_name, context)


def finalizar(request):
    if request.method == 'POST':
        form_finalizar = FinalizarPago(request.POST)
        codigos = request.session.get('facturas')['codigos']
        if codigos:
            total = 0
            if form_finalizar.is_valid():
                importe = form_finalizar.cleaned_data['importe']
                for codigo in codigos:
                    tot = int(codigo[12:20]) / 100
                    total += tot

                if importe >= total:
                    lote = Lote()
                    lote.save()
                    for codigo in codigos:
                        pago = Pago(codigo=codigo, lote=lote, importe=total)
                        pago.save()

                    return render(request, 'caja/finalizar.html')

                else:
                    context = {
                        'form_lectura': LeerFactura(),
                        'form_finalizar': form_finalizar,
                        'mensaje': 'Dinero insuficiente,'
                    }

        else:
            context = {
                'form_lectura': LeerFactura(),
                'form_finalizar': form_finalizar,
                'mensaje': 'Sin facturas leidas',
            }

        return render(request, 'caja/index.html', context)


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class ListadoView(View):
    template_name = 'caja/index.html'
    form_class_lectura = LeerFactura
    form_class_finalizar = FinalizarPago

    def validar_factura(request, codigo):
        if codigo[:2] == '01':
            numero_factura = codigo[4:12]
            importe = int(codigo[12:20]) / 100
            fecha = datetime.datetime.strptime(codigo[20:25], "%y%j").date()

            if(datetime.date.today() <= fecha):
                data = {
                    'codigo': codigo,
                    'empresa': 'EDET',
                    'numero_factura': numero_factura,
                    'importe': importe,
                    'fecha': fecha
                }
                status = 200

                return [data, status]
            else:
                status = 500
                return [{'message': 'Fuera de término!'}, status]

    def get(self, request):
        form_lectura = self.form_class_lectura()
        form_finalizar = self.form_class_finalizar()
        context = {
            'form_lectura': form_lectura,
            'form_finalizar': form_finalizar,
        }

        request.session['facturas'] = {'codigos': []}

        return render(request, self.template_name, context)

    def post(self, request):
        if request.is_ajax:
            form_lectura = self.form_class_lectura(request.POST)
            form_finalizar = self.form_class_finalizar()

            if form_lectura.is_valid():
                codigo = form_lectura.cleaned_data['codigo']

                if codigo not in request.session.get('facturas')['codigos']:
                    [data, status] = self.validar_factura(codigo)
                    if status == 200:
                        facturas = request.session.get('facturas')
                        facturas['codigos'].append(codigo)
                        request.session['facturas'] = facturas

                else:
                    status = 500
                    data = {'message': 'Factura ya leída'}

                return JsonResponse(data, status=status)

        context = {
            'form_lectura': form_lectura,
            'form_finalizar': form_finalizar,
        }

        return render(request, self.template_name, context)
