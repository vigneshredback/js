from django.shortcuts import render 
from app.models import Blog


# Create your views here.



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from app.models import Blog
from app.forms import BlogForm


def blog_detail(request,pk):
    blog = Blog.objects.get(id=pk)
    return render(request,'pages/blog_detail.html',{'blog':blog})

# List view
def blog_list(request):
    blogs = Blog.objects.all()[:10]
    return render(request, 'adminpages/adminbloglist.html', {'blogs': blogs})

#Create view
def blog_create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogForm()
    return render(request, 'adminpages/adminblogform.html', {'form': form})


# Update view
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'adminpages/adminblogform.html', {'form': form})

# Delete view
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog.delete()
        return redirect('blog_list')
    return render(request, 'adminpages/confirmblogdelete.html', {'blog': blog})
