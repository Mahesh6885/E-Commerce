from django.http import HttpResponse

def home(request):
    return HttpResponse("Working Normally")


def category(request):
    return HttpResponse("Working Normally")