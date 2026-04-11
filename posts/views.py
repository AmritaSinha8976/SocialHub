"""
Posts app views — feed includes story bundles for the stories rail.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Post, Like, Comment
from .forms import PostForm, CommentForm
from users.models import Follow
from notifications.models import Notification


def _build_story_bundles(user):
    """
    Return a list of story bundles for the stories rail.
    Includes own stories + stories from followed users.
    Own story bundle always appears first.
    """
    from stories.models import Story, StoryView

    following_ids = list(Follow.objects.filter(
        follower=user
    ).values_list('following_id', flat=True))

    # Include own stories
    all_author_ids = following_ids + [user.id]

    now = timezone.now()
    active_stories = (
        Story.objects
        .filter(author_id__in=all_author_ids, expires_at__gt=now)
        .select_related('author', 'author__profile')
        .order_by('author_id', '-created_at')
    )

    seen_story_ids = set(
        StoryView.objects.filter(viewer=user).values_list('story_id', flat=True)
    )

    bundles = {}
    for story in active_stories:
        uid = story.author_id
        if uid not in bundles:
            bundles[uid] = {
                'user': story.author,
                'first_story_id': story.pk,
                'all_seen': True,
            }
        if story.pk not in seen_story_ids:
            bundles[uid]['all_seen'] = False

    result = []
    # Own story first
    if user.id in bundles:
        result.append(bundles.pop(user.id))
    # Others unseen first
    result.extend(sorted(bundles.values(), key=lambda b: b['all_seen']))
    return result


@login_required
def feed_view(request):
    following_ids = list(
        Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    )
    feed_user_ids = following_ids + [request.user.id]

    posts = Post.objects.filter(
        author_id__in=feed_user_ids
    ).select_related('author', 'author__profile').prefetch_related('likes', 'comments')

    paginator = Paginator(posts, 10)
    page_obj  = paginator.get_page(request.GET.get('page'))

    suggested_users = User.objects.exclude(
        id__in=feed_user_ids
    ).select_related('profile')[:5]

    stories = _build_story_bundles(request.user)

    return render(request, 'posts/feed.html', {
        'page_obj': page_obj,
        'suggested_users': suggested_users,
        'comment_form': CommentForm(),
        'stories': stories,
    })


@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post shared successfully! ✨')
            return redirect('posts:feed')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_detail_view(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile')
                    .prefetch_related('likes', 'comments__author__profile'),
        pk=pk
    )

    # Access control for private profiles
    if post.author.profile.is_private:
        if not request.user.is_authenticated:
            return redirect('users:login')
        if request.user != post.author:
            if not Follow.objects.filter(follower=request.user, following=post.author).exists():
                messages.error(request, 'This account is private.')
                return redirect('users:profile', username=post.author.username)

    comments     = post.comments.filter(parent=None).order_by('created_at')
    comment_form = CommentForm()

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': post.is_liked_by(request.user),
    })


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('posts:feed')
    return render(request, 'posts/confirm_delete.html', {'post': post})


@login_required
def toggle_like_view(request, pk):
    if request.method != 'POST':
        return redirect('posts:post_detail', pk=pk)
    post     = get_object_or_404(Post, pk=pk)
    like_obj = Like.objects.filter(user=request.user, post=post)
    if like_obj.exists():
        like_obj.delete()
        is_liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        is_liked = True
        if post.author != request.user:
            Notification.objects.get_or_create(
                recipient=post.author,
                actor=request.user,
                notif_type='post_like',
                defaults={'message': f'{request.user.username} liked your post.', 'url': f'/post/{post.pk}/'},
            )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_liked': is_liked, 'likes_count': post.likes_count})
    return redirect(request.META.get('HTTP_REFERER', 'posts:feed'))


@login_required
def add_comment_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post   = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    comment.parent = Comment.objects.get(pk=parent_id, post=post)
                except Comment.DoesNotExist:
                    pass
            comment.save()
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    notif_type='comment',
                    message=f'{request.user.username} commented on your post.',
                    url=f'/post/{post.pk}/',
                )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment_id': comment.pk,
                    'author': comment.author.username,
                    'author_pic': comment.author.profile.profile_picture.url,
                    'text': comment.text,
                    'created_at': comment.created_at.strftime('%b %d, %Y'),
                    'comments_count': post.comments_count,
                })
            messages.success(request, 'Comment added!')
    return redirect(request.META.get('HTTP_REFERER', 'posts:post_detail'), pk=pk)


@login_required
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user not in (comment.author, comment.post.author):
        messages.error(request, 'Not allowed.')
        return redirect('posts:post_detail', pk=comment.post.pk)
    if request.method == 'POST':
        post_pk = comment.post.pk
        comment.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, 'Comment deleted.')
        return redirect('posts:post_detail', pk=post_pk)
    return redirect('posts:post_detail', pk=comment.post.pk)


def explore_view(request):
    posts = Post.objects.select_related(
        'author', 'author__profile'
    ).prefetch_related('likes', 'comments').order_by('-created_at')

    # Hide posts from private profiles for non-followers
    if request.user.is_authenticated:
        following_ids = set(
            Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        )
        following_ids.add(request.user.id)
        posts = [
            p for p in posts
            if not p.author.profile.is_private or p.author_id in following_ids
        ]
    else:
        posts = [p for p in posts if not p.author.profile.is_private]

    paginator = Paginator(posts, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'posts/explore.html', {'page_obj': page_obj})


@login_required
def toggle_save_view(request, pk):
    """Bookmark / unbookmark a post."""
    if request.method != 'POST':
        return redirect('posts:post_detail', pk=pk)
    from .models import SavedPost
    post   = get_object_or_404(Post, pk=pk)
    saved  = SavedPost.objects.filter(user=request.user, post=post)
    if saved.exists():
        saved.delete()
        is_saved = False
    else:
        SavedPost.objects.create(user=request.user, post=post)
        is_saved = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_saved': is_saved})
    return redirect(request.META.get('HTTP_REFERER', 'posts:feed'))


@login_required
def saved_posts_view(request):
    """Show all posts saved by the current user."""
    from .models import SavedPost
    saved = SavedPost.objects.filter(user=request.user).select_related(
        'post','post__author','post__author__profile'
    ).prefetch_related('post__likes')
    return render(request, 'posts/saved_posts.html', {'saved': saved})