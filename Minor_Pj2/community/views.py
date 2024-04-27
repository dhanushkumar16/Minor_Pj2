from django.shortcuts import render,redirect
from django.views.generic import ListView, DetailView, CreateView
from .models import Post
from .forms import PostForm

# def home(request):
#     return render(request,'community/home.html',{})

class HomeView(ListView):
    model = Post
    template_name='home.html'
    
class ArticleDetailView(DetailView):
    model = Post
    template_name= 'article_details.html'
    
# class AddPostView(CreateView):
#     model=Post
#     form_class=PostForm
#     template_name='add_post.html'
#     # fields='__all__'
#     # fields=('title','body')


def create_blog_post(request):
    if request.method=='POST':
        form=PostForm(request.POST)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user  # Set the author to the logged-in user
            blog_post.save()
            return redirect('blog-home')
    else:
        form = PostForm()
    return render(request, 'add_post.html', {'form': form})