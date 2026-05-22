from django.shortcuts import render
from .models import Sport, News

# Create your views here.
def index(request):
    sports = Sport.objects.all()
    news   = News.objects.all()
    return render(request, 'index.html', {
        'sports': sports,
        'news':   news,
    })