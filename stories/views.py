from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from .models import Story, StoryView, StoryLike, StoryPollVote
from .forms import StoryForm
from users.models import Follow
from notifications.models import Notification


@login_required
def create_story_view(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            return redirect('posts:feed')
    else:
        form = StoryForm()
    return render(request, 'stories/create_story.html', {'form': form})


@login_required
def view_story_view(request, pk):
    story = get_object_or_404(Story, pk=pk)
    if not story.is_active:
        return redirect('posts:feed')

    if story.author.profile.is_private:
        if not Follow.objects.filter(follower=request.user, following=story.author).exists() \
                and request.user != story.author:
            return redirect('posts:feed')

    if request.user != story.author:
        StoryView.objects.get_or_create(story=story, viewer=request.user)

    # Next / prev stories by same author
    author_stories = list(Story.objects.filter(
        author=story.author, expires_at__gt=timezone.now()
    ).order_by('created_at').values_list('pk', flat=True))
    idx     = author_stories.index(pk) if pk in author_stories else 0
    prev_id = author_stories[idx-1] if idx > 0 else None
    next_id = author_stories[idx+1] if idx < len(author_stories)-1 else None

    # Poll state
    user_poll_vote = None
    poll_a_count = poll_b_count = 0
    if story.poll_question:
        poll_a_count = story.poll_votes.filter(choice='a').count()
        poll_b_count = story.poll_votes.filter(choice='b').count()
        vote = story.poll_votes.filter(user=request.user).first()
        if vote:
            user_poll_vote = vote.choice

    import json
    stickers = []
    try:
        stickers = json.loads(story.stickers_json or '[]')
    except Exception:
        pass

    return render(request, 'stories/view_story.html', {
        'story': story,
        'viewers': story.views.select_related('viewer').order_by('-viewed_at'),
        'is_liked': story.is_liked_by(request.user),
        'prev_id': prev_id, 'next_id': next_id,
        'poll_a_count': poll_a_count, 'poll_b_count': poll_b_count,
        'user_poll_vote': user_poll_vote,
        'stickers': stickers,
    })


@login_required
def delete_story_view(request, pk):
    story = get_object_or_404(Story, pk=pk, author=request.user)
    if request.method == 'POST':
        story.delete()
    return redirect('posts:feed')


@login_required
def toggle_story_like_view(request, pk):
    if request.method != 'POST':
        return redirect('stories:view', pk=pk)
    story = get_object_or_404(Story, pk=pk)
    like  = StoryLike.objects.filter(user=request.user, story=story)
    if like.exists():
        like.delete(); is_liked = False
    else:
        StoryLike.objects.create(user=request.user, story=story)
        is_liked = True
        if story.author != request.user:
            Notification.objects.create(
                recipient=story.author, actor=request.user, notif_type='story_like',
                message=f'{request.user.username} liked your story.',
                url=f'/stories/{story.pk}/',
            )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_liked': is_liked, 'likes_count': story.story_likes.count()})
    return redirect('stories:view', pk=pk)


@login_required
def vote_poll_view(request, pk):
    """Submit a vote on a story poll."""
    if request.method != 'POST':
        return redirect('stories:view', pk=pk)
    story  = get_object_or_404(Story, pk=pk)
    choice = request.POST.get('choice')
    if choice not in ('a','b'):
        return redirect('stories:view', pk=pk)

    StoryPollVote.objects.update_or_create(
        story=story, user=request.user,
        defaults={'choice': choice}
    )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'a': story.poll_votes.filter(choice='a').count(),
            'b': story.poll_votes.filter(choice='b').count(),
            'voted': choice,
        })
    return redirect('stories:view', pk=pk)
