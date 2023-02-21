from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from django.views.generic import (
    ListView, 
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Post, Category
from .forms import PostForm, EditForm

#TODO: include in the executable function in the future to remove unused categories. 
def clear_category_list():
    cat_posts = Post.objects.all()
    cat_menu = Category.objects.all()

    post_categories_list = []

    for posts_item in cat_posts:
        post_categories_list.append(posts_item.category) 
    
    for menu_item in cat_menu:
        if str(menu_item) not in post_categories_list:
            q = Category.objects.get(name=menu_item)
            q.delete()

def get_category_menu_context(self, view, *args, **kwargs):
        category_menu = Category.objects.all()

        context = super(view, self).get_context_data(*args, **kwargs)
        context['category_menu']= category_menu
        return context

def LikeView(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('article_detail', args=[str(pk)]))

def CategoryView(request, category):
    category_menu  = Category.objects.all()
    category_posts = Post.objects.filter(category=category.replace('-', ' '))
    return render(request, 'categories.html', {'category_menu': category_menu, 'category':category.title().replace('-', ' '), 'category_posts': category_posts})

class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    ordering = ['-post_date']

    def get_context_data(self, *args, **kwargs):
        return get_category_menu_context(self, HomeView, *args, **kwargs)
        
class ArticleDetailView(DetailView):
    model = Post
    template_name = 'article_details.html'

    def get_context_data(self, *args, **kwargs):
        category_menu = Category.objects.all()

        post_obj = get_object_or_404(Post, id=self.kwargs['pk'])
        total_likes = post_obj.total_likes()

        liked = False
        if post_obj.likes.filter(id=self.request.user.id).exists():
            liked = True

        context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)
        context['category_menu'] = category_menu
        context['total_likes'] = total_likes
        context['liked'] = liked

        return context

class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'add_post.html'

    def get_context_data(self, *args, **kwargs):
        return get_category_menu_context(self, AddPostView, *args, **kwargs)

class AddCategoryView(CreateView):
    model = Category
    template_name = 'add_category.html'
    fields = '__all__'

    def get_context_data(self, *args, **kwargs):
        return get_category_menu_context(self, AddCategoryView, *args, **kwargs)

class UpdatePostView(UpdateView):
    model = Post
    form_class = EditForm
    template_name = 'update_post.html'

    def get_context_data(self, *args, **kwargs):
        return get_category_menu_context(self, UpdatePostView, *args, **kwargs)

class DeletePostView(DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *args, **kwargs):
        return get_category_menu_context(self, DeletePostView, *args, **kwargs)