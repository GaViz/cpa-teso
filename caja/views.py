from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from caja.forms import LeerFactura, CrearUsuario, FinalizarPago
from django.http import JsonResponse
import datetime
from .models import Lote, Pago
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count


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


def cierre(request):
    template_name = 'caja/cierre.html'
    hoy = datetime.date.today()
    lotes = Lote.objects.filter(cajero=request.user.empleado, fecha=hoy)
    suma = 0
    count = 0
    for lote in lotes:
        pagos = Pago.objects.filter(lote=lote)
        aux = pagos.aggregate(suma_importes=Sum('importe'), count_facturas=Count('importe'))
        suma += float(aux['suma_importes'])
        count += int(aux['count_facturas'])
    context = {
        'total': suma,
        'count': count,
        'fecha': hoy,
    }
    return render(request, template_name, context)


def finalizar(request):
    from decimal import Decimal

    if request.method == 'POST' and request.is_ajax:
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
                    lote = Lote(cajero=request.user.empleado)
                    lote.save()
                    for codigo in codigos:
                        pago = Pago(codigo=codigo, lote=lote, importe=total)
                        pago.save()

                    vuelto = importe - Decimal(total)

                    # return render(request, 'caja/finalizar.html')
                    status = 200
                    data = {
                        'mensaje': 'Listo',
                        'vuelto': vuelto,
                    }

                else:
                    status = 500
                    data = {
                        'mensaje': 'Dinero insuficiente',
                    }

        else:
            status = 500
            data = {
                'mensaje': 'Sin facturas leidas',
            }

        # return render(request, 'caja/index.html', context)
        return JsonResponse(data, status=status)


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class ListadoView(View):
    template_name = 'caja/index.html'
    form_class_lectura = LeerFactura
    form_class_finalizar = FinalizarPago

    def leer_factura(request, codigo):
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
                return [{'mensaje': 'Fuera de término!'}, status]

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
                    [data, status] = self.leer_factura(codigo)
                    if status == 200:
                        facturas = request.session.get('facturas')
                        facturas['codigos'].append(codigo)
                        request.session['facturas'] = facturas

                else:
                    status = 500
                    data = {'mensaje': 'Factura ya leída'}

                return JsonResponse(data, status=status)

        context = {
            'form_lectura': form_lectura,
            'form_finalizar': form_finalizar,
        }

        return render(request, self.template_name, context)
