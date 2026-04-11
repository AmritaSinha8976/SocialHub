/**
 * SocialHub — Main JavaScript v2
 * Handles: AJAX likes, comments, follow toggle, theme (handled in base.html)
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── CSRF helper ──────────────────────────────────────────────
  function getCsrf() {
    return document.cookie.split('; ')
      .find(r => r.startsWith('csrftoken='))?.split('=')[1] || '';
  }

  // ── Like buttons (AJAX) ─────────────────────────────────────
  document.body.addEventListener('click', async e => {
    const btn = e.target.closest('.like-btn');
    if (!btn) return;
    const postId = btn.dataset.postId;
    if (!postId) return;

    const icon    = btn.querySelector('i');
    const isLiked = btn.classList.toggle('liked');
    icon.className = isLiked ? 'bi bi-heart-fill' : 'bi bi-heart';

    const countEl = document.getElementById(`likes-${postId}`);
    if (countEl) countEl.textContent = parseInt(countEl.textContent) + (isLiked ? 1 : -1);

    try {
      const fd = new FormData();
      fd.append('csrfmiddlewaretoken', getCsrf());
      const res  = await fetch(`/post/${postId}/like/`, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: fd,
      });
      const data = await res.json();
      btn.classList.toggle('liked', data.is_liked);
      icon.className = data.is_liked ? 'bi bi-heart-fill' : 'bi bi-heart';
      if (countEl) countEl.textContent = data.likes_count;
    } catch (err) {
      // Rollback
      btn.classList.toggle('liked');
      icon.className = btn.classList.contains('liked') ? 'bi bi-heart-fill' : 'bi bi-heart';
      if (countEl) countEl.textContent = parseInt(countEl.textContent) + (isLiked ? -1 : 1);
    }
  });

  // ── Inline comment forms (feed) ──────────────────────────────
  document.body.addEventListener('submit', async e => {
    const form = e.target.closest('.post-comment-form');
    if (!form) return;
    e.preventDefault();

    const input = form.querySelector('.post-comment-input');
    const text  = input.value.trim();
    if (!text) return;
    const postId = form.dataset.postId;
    input.value  = '';

    const fd = new FormData();
    fd.append('text', text);
    fd.append('csrfmiddlewaretoken', getCsrf());

    try {
      const res  = await fetch(`/post/${postId}/comment/`, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: fd,
      });
      const data = await res.json();
      if (data.success) {
        const card    = document.getElementById(`post-${postId}`);
        const preview = card?.querySelector('.post-comment-preview');
        if (preview) {
          const line = document.createElement('div');
          line.className = 'comment-preview-line';
          line.innerHTML = `<strong>${esc(data.author)}</strong> <span>${esc(text)}</span>`;
          preview.prepend(line);
        }
      }
    } catch (err) { input.value = text; }
  });

  // ── Post detail comment form ─────────────────────────────────
  const detailForm = document.querySelector('.post-detail-comment-form');
  if (detailForm) {
    detailForm.addEventListener('submit', async e => {
      e.preventDefault();
      const input  = detailForm.querySelector('.post-comment-input');
      const text   = input.value.trim();
      if (!text) return;
      const postId = detailForm.dataset.postId;
      input.value  = '';

      const fd = new FormData();
      fd.append('text', text);
      fd.append('csrfmiddlewaretoken', getCsrf());

      try {
        const res  = await fetch(`/post/${postId}/comment/`, {
          method: 'POST',
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          body: fd,
        });
        const data = await res.json();
        if (data.success) {
          const box = document.querySelector('.post-detail-comments');
          box?.querySelector('.text-muted')?.remove();
          const html = `
            <div class="post-detail-comment" id="comment-${data.comment_id}">
              <img src="${data.author_pic}" class="comment-pic" alt="">
              <div class="comment-body">
                <a href="/profile/${data.author}/" class="comment-author">${esc(data.author)}</a>
                <span class="comment-text">${esc(text)}</span>
                <div class="comment-meta"><small>Just now</small></div>
              </div>
            </div>`;
          box?.insertAdjacentHTML('beforeend', html);
          if (box) box.scrollTop = box.scrollHeight;
        }
      } catch (err) { input.value = text; }
    });
  }

  // ── Follow button (profile page AJAX) ───────────────────────
  const followForm = document.querySelector('.follow-form');
  if (followForm) {
    followForm.addEventListener('submit', async e => {
      e.preventDefault();
      const btn      = followForm.querySelector('[data-username]');
      const username = btn?.dataset.username;
      if (!username) return;

      const fd = new FormData();
      fd.append('csrfmiddlewaretoken', getCsrf());
      try {
        const res  = await fetch(`/follow/${username}/`, {
          method: 'POST',
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          body: fd,
        });
        const data = await res.json();
        if (data.error) return;

        const countEl = document.getElementById('followersCount');
        if (countEl) countEl.textContent = data.followers_count;

        // Update button state
        if (data.follow_request_status === 'pending') {
          btn.className = 'sh-btn-outline';
          btn.disabled  = true;
          btn.innerHTML = '<i class="bi bi-clock"></i> Requested';
        } else if (data.is_following) {
          btn.className = 'sh-btn-follow following';
          btn.innerHTML = '<i class="bi bi-person-check-fill"></i> Following';
        } else {
          btn.className = 'sh-btn-follow';
          btn.innerHTML = '<i class="bi bi-person-plus"></i> Follow';
        }
      } catch (err) {
        followForm.submit(); // fallback
      }
    });
  }

  // ── HTML escape utility ───────────────────────────────────────
  function esc(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }

});

// ── Save / Bookmark (AJAX) ───────────────────────────────────────
document.body.addEventListener('click', async e => {
  const btn = e.target.closest('.save-btn');
  if (!btn) return;
  const postId = btn.dataset.postId;
  if (!postId) return;

  const icon    = btn.querySelector('i');
  const isSaved = btn.classList.toggle('saved');
  icon.className = isSaved ? 'bi bi-bookmark-fill' : 'bi bi-bookmark';

  try {
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', getCsrf());
    const res  = await fetch(`/post/${postId}/save/`, {
      method: 'POST', headers: {'X-Requested-With': 'XMLHttpRequest'}, body: fd,
    });
    const data = await res.json();
    btn.classList.toggle('saved', data.is_saved);
    icon.className = data.is_saved ? 'bi bi-bookmark-fill' : 'bi bi-bookmark';
  } catch {
    btn.classList.toggle('saved');
    icon.className = btn.classList.contains('saved') ? 'bi bi-bookmark-fill' : 'bi bi-bookmark';
  }
});
