from django.shortcuts import render,redirect


def photogallery(request):
    return render(request, 'pages/photo_gallery.html')