from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, Like, Comment, Follow
from .forms import PostForm, CommentForm

def home(request):
    # Для отладки выведем информацию о пользователе и постах
    print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        # Получаем ID пользователей, на которых подписан текущий пользователь
        following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        # Добавляем ID текущего пользователя, чтобы видеть свои посты
        following_ids = list(following_ids) + [request.user.id]
        posts = Post.objects.filter(author_id__in=following_ids).select_related('author').prefetch_related('likes', 'comments')
        print(f"Following IDs: {following_ids}")
        print(f"Posts count (authenticated): {posts.count()}")
    else:
        # Для неавторизованных пользователей показываем все посты
        posts = Post.objects.all().select_related('author').prefetch_related('likes', 'comments')
        print(f"Posts count (anonymous): {posts.count()}")
    
    # Сортируем по дате создания (новые сверху)
    posts = posts.order_by('-created_at')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    if request.user.is_authenticated:
        context['form'] = PostForm()
    
    return render(request, 'social/home.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост успешно создан!')
            return redirect('home')
    return redirect('home')

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    
    return render(request, 'social/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user != user_to_follow:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        if not created:
            follow.delete()
    
    return redirect('profile', username=username)

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    is_following = False
    
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()
    
    followers_count = user.followers.count()
    following_count = user.following.count()
    
    return render(request, 'social/profile.html', {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count
    })

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'social/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удален!')
        return redirect('home')
    
    return render(request, 'social/delete_post.html', {'post': post})
