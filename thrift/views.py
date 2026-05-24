from django.shortcuts import render, HttpResponse

# Create your views here.
def home(request):
    return render(request, 'thrift/base.html')

def contact(request):
    return HttpResponse("This is contact")

def about(request): 
    return HttpResponse('This is about')
