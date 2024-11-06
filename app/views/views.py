from django.http import JsonResponse
from django.db.models import Q
from app.models import User
from django.shortcuts import render

def search_users(request):
    query = request.GET.get('query', '')
    if query:
        users = User.objects.filter(id=query )[:10]  # Limit to 10 results
        results = [{'name': user.name, 'city': user.biodata.city.name, 'id': user.id} for user in users]
    else:
        results = []

    return JsonResponse(results, safe=False)

def search_page(request):
    return render(request, 'pages/usersearch.html')
