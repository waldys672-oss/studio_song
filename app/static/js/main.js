

/* ═══════════════════════════════════════
   سمو — Main JavaScript
   Interactions, Animations, Form Logic
   ═══════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initMobileMenu();
    initScrollAnimations();
    initFlashMessages();
    initSmoothScroll();
    initShareButtons();
    initSmoPlayers();
});

/* ═══════════════════════════════
   NAVBAR SCROLL EFFECT
   ═══════════════════════════════ */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    }, { passive: true });
}

/* ═══════════════════════════════
   MOBILE MENU
   ═══════════════════════════════ */
function initMobileMenu() {
    const toggle = document.getElementById('menuToggle');
    const navLinks = document.getElementById('navLinks');
    const overlay = document.getElementById('navOverlay');

    if (!toggle || !navLinks) return;

    toggle.addEventListener('click', () => {
        toggle.classList.toggle('active');
        navLinks.classList.toggle('open');
        if (overlay) overlay.classList.toggle('active');
        document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
    });

    // Close on overlay click
    if (overlay) {
        overlay.addEventListener('click', () => {
            toggle.classList.remove('active');
            navLinks.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    // Close on link click
    navLinks.querySelectorAll('a:not(.btn)').forEach(link => {
        link.addEventListener('click', () => {
            toggle.classList.remove('active');
            navLinks.classList.remove('open');
            if (overlay) overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
}

/* ═══════════════════════════════
   SCROLL REVEAL ANIMATIONS
   ═══════════════════════════════ */
function initScrollAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    if (elements.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Stagger animation by index
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 80);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    elements.forEach(el => observer.observe(el));
}

/* ═══════════════════════════════
   FLASH MESSAGES AUTO-DISMISS
   ═══════════════════════════════ */
function initFlashMessages() {
    const container = document.getElementById('flashMessages');
    if (!container) return;

    const alerts = container.querySelectorAll('.alert');
    alerts.forEach((alert, i) => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
        }, 4000 + (i * 500));
    });
}

/* ═══════════════════════════════
   SMOOTH SCROLL FOR ANCHORS
   ═══════════════════════════════ */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                const navHeight = document.getElementById('navbar')?.offsetHeight || 0;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

function initShareButtons() {
    const buttons = document.querySelectorAll('.js-share-sample');
    if (buttons.length === 0) return;

    buttons.forEach((btn) => {
        btn.addEventListener('click', async () => {
            const sharePath = btn.getAttribute('data-share-path') || '';
            const shareTitle = btn.getAttribute('data-share-title') || '';
            if (!sharePath) return;

            const shareUrl = new URL(sharePath, window.location.origin).toString();

            try {
                if (navigator.share) {
                    await navigator.share({ title: shareTitle, text: shareTitle, url: shareUrl });
                    return;
                }
                await copyToClipboard(shareUrl);
                showClientToast('تم نسخ رابط المشاركة', 'success');
            } catch (err) {
                try {
                    await copyToClipboard(shareUrl);
                    showClientToast('تم نسخ رابط المشاركة', 'success');
                } catch (copyErr) {
                    showClientToast('تعذر نسخ الرابط، انسخه يدوياً من شريط العنوان', 'error');
                }
            }
        });
    });
}

async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
    }

    const input = document.createElement('input');
    input.value = text;
    input.setAttribute('readonly', '');
    input.style.position = 'fixed';
    input.style.top = '-1000px';
    input.style.left = '-1000px';
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    input.remove();
}

function showClientToast(message, type) {
    const toastType = type || 'info';
    let container = document.getElementById('clientFlashMessages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        container.id = 'clientFlashMessages';
        document.body.appendChild(container);
    }

    const icon = toastType === 'success'
        ? 'fa-check-circle'
        : toastType === 'error'
            ? 'fa-exclamation-circle'
            : toastType === 'warning'
                ? 'fa-exclamation-triangle'
                : 'fa-info-circle';

    const alert = document.createElement('div');
    alert.className = `alert alert-${toastType}`;
    alert.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
        <button class="alert-close" type="button" aria-label="إغلاق">×</button>
    `.trim();

    const closeBtn = alert.querySelector('.alert-close');
    closeBtn.addEventListener('click', () => alert.remove());

    container.appendChild(alert);

    setTimeout(() => {
        if (!alert.isConnected) return;
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        setTimeout(() => alert.remove(), 300);
    }, 3500);
}

/* ═══════════════════════════════
   SMO AUDIO PLAYER
   ═══════════════════════════════ */
function initSmoPlayers() {
    const players = document.querySelectorAll('.smo-player');
    if (players.length === 0) return;

    players.forEach(player => {
        const audio     = player.querySelector('.smo-player__audio');
        const playBtn   = player.querySelector('.smo-player__play');
        const scrubber  = player.querySelector('.smo-player__scrubber');
        const fill      = player.querySelector('.smo-player__progress-fill');
        const curTime   = player.querySelector('.smo-player__current');
        const durTime   = player.querySelector('.smo-player__duration');
        const volBtn    = player.querySelector('.smo-player__vol-btn');
        const volSlider = player.querySelector('.smo-player__vol-slider');

        if (!audio || !playBtn) return;

        // ── Format seconds to m:ss ──
        function fmtTime(s) {
            if (!isFinite(s) || s < 0) return '0:00';
            const m = Math.floor(s / 60);
            const sec = Math.floor(s % 60);
            return m + ':' + (sec < 10 ? '0' : '') + sec;
        }

        // ── Stop all other players ──
        function pauseOthers() {
            document.querySelectorAll('.smo-player').forEach(p => {
                if (p === player) return;
                const otherAudio = p.querySelector('.smo-player__audio');
                if (otherAudio && !otherAudio.paused) {
                    otherAudio.pause();
                    p.classList.remove('is-playing');
                    const otherBtn = p.querySelector('.smo-player__play i');
                    if (otherBtn) otherBtn.className = 'fas fa-play';
                }
            });
        }

        // ── Play / Pause ──
        playBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (audio.paused) {
                pauseOthers();
                audio.play().catch(() => {});
            } else {
                audio.pause();
            }
        });

        audio.addEventListener('play', () => {
            player.classList.add('is-playing');
            playBtn.querySelector('i').className = 'fas fa-pause';
        });

        audio.addEventListener('pause', () => {
            player.classList.remove('is-playing');
            playBtn.querySelector('i').className = 'fas fa-play';
        });

        audio.addEventListener('ended', () => {
            player.classList.remove('is-playing');
            playBtn.querySelector('i').className = 'fas fa-play';
            if (fill) fill.style.width = '0%';
            if (scrubber) scrubber.value = 0;
        });

        // ── Duration loaded ──
        audio.addEventListener('loadedmetadata', () => {
            if (durTime) durTime.textContent = fmtTime(audio.duration);
            if (scrubber) scrubber.max = 100;
        });

        // Also try on durationchange for some browsers
        audio.addEventListener('durationchange', () => {
            if (durTime && isFinite(audio.duration)) {
                durTime.textContent = fmtTime(audio.duration);
            }
        });

        // Force duration check on init if metadata already loaded
        if (audio.readyState >= 1) {
            if (durTime && isFinite(audio.duration)) durTime.textContent = fmtTime(audio.duration);
            if (scrubber) scrubber.max = 100;
        }

        // ── Time update — progress bar & current time ──
        audio.addEventListener('timeupdate', () => {
            if (!audio.duration) return;
            const pct = (audio.currentTime / audio.duration) * 100;
            if (fill) fill.style.width = pct + '%';
            if (scrubber && !scrubber._dragging) scrubber.value = pct;
            if (curTime) curTime.textContent = fmtTime(audio.currentTime);
        });

        // ── Scrubber interaction ──
        if (scrubber) {
            scrubber._dragging = false;

            scrubber.addEventListener('mousedown', () => { scrubber._dragging = true; });
            scrubber.addEventListener('touchstart', () => { scrubber._dragging = true; }, { passive: true });

            scrubber.addEventListener('input', () => {
                if (!audio.duration) return;
                const seekTo = (scrubber.value / 100) * audio.duration;
                if (fill) fill.style.width = scrubber.value + '%';
                if (curTime) curTime.textContent = fmtTime(seekTo);
            });

            scrubber.addEventListener('change', () => {
                scrubber._dragging = false;
                if (!audio.duration) return;
                audio.currentTime = (scrubber.value / 100) * audio.duration;
            });

            scrubber.addEventListener('mouseup', () => { scrubber._dragging = false; });
            scrubber.addEventListener('touchend', () => { scrubber._dragging = false; });
        }

        // ── Volume slider ──
        if (volSlider) {
            volSlider.addEventListener('input', () => {
                audio.volume = parseFloat(volSlider.value);
                audio.muted = false;
                updateVolIcon();
            });
        }

        // ── Volume mute toggle ──
        if (volBtn) {
            volBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                audio.muted = !audio.muted;
                updateVolIcon();
            });
        }

        function updateVolIcon() {
            if (!volBtn) return;
            const icon = volBtn.querySelector('i');
            if (!icon) return;
            if (audio.muted || audio.volume === 0) {
                icon.className = 'fas fa-volume-xmark';
            } else if (audio.volume < 0.5) {
                icon.className = 'fas fa-volume-low';
            } else {
                icon.className = 'fas fa-volume-high';
            }
        }
    });
}

/* ═══════════════════════════════
   CATEGORY FILTER
   ═══════════════════════════════ */
document.addEventListener('DOMContentLoaded', function() {
    const mainBtns = document.querySelectorAll('.main-cat-btn');
    const subBtns = document.querySelectorAll('.sub-filter-btn');
    const allBtn = document.querySelector('[data-filter="all"]');
    const subRows = document.querySelectorAll('.sub-filter-row');
    const sampleItems = document.querySelectorAll('.sample-item');

    // If the page doesn't have any filter UI, skip all of this.
    if (sampleItems.length === 0 || (mainBtns.length === 0 && subBtns.length === 0 && !allBtn)) {
        return;
    }

    function updateActiveStyles(activeBtn, group) {
        if (!activeBtn) return;
        group.forEach(btn => {
            if (!btn) return;
            btn.classList.remove('btn-primary', 'btn-outline', 'active');
            btn.classList.add('btn-ghost');
        });
        activeBtn.classList.remove('btn-ghost');
        if (activeBtn.classList.contains('sub-filter-btn')) {
            activeBtn.classList.add('btn-outline', 'active');
        } else {
            activeBtn.classList.add('btn-primary', 'active');
        }
    }

    function filterItems(filterValue, isSubLevel = false) {
        sampleItems.forEach(item => {
            const itemCat = item.getAttribute('data-category');
            const itemParent = item.getAttribute('data-parent');

            if (filterValue === 'all') {
                item.style.display = '';
            } else if (isSubLevel) {
                item.style.display = (itemCat === filterValue) ? '' : 'none';
            } else {
                item.style.display = (itemParent === filterValue) ? '' : 'none';
            }
        });
    }

    mainBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const mainGroup = [...mainBtns];
            if (allBtn) mainGroup.push(allBtn);
            updateActiveStyles(this, mainGroup);

            const targetId = this.getAttribute('data-target-sub');
            subRows.forEach(row => row.style.display = 'none');

            const targetRow = document.getElementById(targetId);
            if (targetRow) {
                targetRow.style.display = 'flex';
                const defaultSub = targetRow.querySelector('.sub-filter-btn');
                updateActiveStyles(defaultSub, targetRow.querySelectorAll('.sub-filter-btn'));
            }
            filterItems(this.getAttribute('data-filter'), false);
        });
    });

    subBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const currentSubGroup = this.closest('.sub-filter-row').querySelectorAll('.sub-filter-btn');
            updateActiveStyles(this, currentSubGroup);
            filterItems(this.getAttribute('data-filter'), true);
        });
    });

    if (allBtn) {
        allBtn.addEventListener('click', function() {
            updateActiveStyles(this, [...mainBtns, allBtn]);
            subRows.forEach(row => row.style.display = 'none');
            filterItems('all');
        });
    }
});
