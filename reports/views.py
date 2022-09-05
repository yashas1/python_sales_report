from django.shortcuts import render,get_object_or_404
from profiles.models import Profile
from django.http import JsonResponse
from .utils import get_report_image
from .models import Report 
from django.shortcuts import HttpResponse
from django.views.generic import TemplateView

from django.views.generic import ListView, DetailView
from sales.models import Sale,Position,CSV
from produtcs.models import Product
from customers.models import Customer
import csv
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from django.utils.dateparse import parse_date
from datetime import datetime

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class ReportListView(LoginRequiredMixin,ListView):
    model=Report
    template_name= 'reports/main.html'

class ReportDetailView(LoginRequiredMixin,DetailView):
    model = Report
    template_name= 'reports/detail.html'

class UploadTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/form_file.html'
    




def csv_upload_view(request):
    print('file is being')

    if request.method == 'POST':
        csv_file_name = request.FILES.get('file').name
        csv_file = request.FILES.get('file')
        obj, created = CSV.objects.get_or_create(file_name=csv_file_name)

        if created:
            obj.csv_file = csv_file
            obj.save()
            with open(obj.csv_file.path, 'r') as f:
                reader = csv.reader(f)
                reader.__next__()    
                for row in reader:
                   
                    data = ";".join(row)
                    
                    data = data.split(';')

                    transaction_id = data[1]
                    product = data[2]
                    quantity = int(data[3])
                    customer = data[4]
                    date = datetime.strptime(data[5], "%d-%m-%Y").date()

                    print(date)

                    try:
                        product_obj = Product.objects.get(name__iexact=product)
                        
                    except Product.DoesNotExist:
                        product_obj = None
                    
                   
                    if product_obj is not None:
                       
                        customer_obj, _ = Customer.objects.get_or_create(name=customer) 
                      
                        salesman_obj = Profile.objects.get(user=request.user)

                        position_obj = Position.objects.create(product=product_obj, quantity=quantity, created=date)

                        sale_obj, _ = Sale.objects.get_or_create(transaction_id=transaction_id, customer=customer_obj, salesman=salesman_obj, created=date)
                        sale_obj.positions.add(position_obj)
                        sale_obj.save()
                return JsonResponse({'ex': False})
        else:
            return JsonResponse({'ex': True})

    return HttpResponse()

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def create_report_view(request):
    if is_ajax(request=request):  
        name= request.POST.get('name')
        remarks= request.POST.get('remarks')
        image= request.POST.get('image')
        img=get_report_image(image)
        
        author=Profile.objects.get(user=request.user)
        Report.objects.create(name=name,remarks=remarks,image=img,author=author)

        return JsonResponse({'msg':'send'})
    return JsonResponse({})
    
@login_required
def render_pdf_view(request, pk):
    template_path = 'reports/pdf.html'
    obj = get_object_or_404(Report, pk=pk)
    context = {'obj': obj}

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'filename="report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
       html, dest=response)

    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
    