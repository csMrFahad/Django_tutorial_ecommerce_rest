from django.shortcuts import render
from django.http import HttpResponse

def say_hello(request):
    # return HttpResponse('Hello world')
    return render(request, 'hello.html', {'name': 'test'})