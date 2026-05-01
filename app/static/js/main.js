// /* ═══════════════════════════════════════
//    سمو — Main JavaScript
//    Interactions, Animations, Form Logic
//    ═══════════════════════════════════════ */

// document.addEventListener('DOMContentLoaded', () => {
//     initNavbar();
//     initMobileMenu();
//     initScrollAnimations();
//     initFlashMessages();
//     initSmoothScroll();
// });

// /* ═══════════════════════════════
//    NAVBAR SCROLL EFFECT
//    ═══════════════════════════════ */
// function initNavbar() {
//     const navbar = document.getElementById('navbar');
//     if (!navbar) return;

//     let lastScroll = 0;

//     window.addEventListener('scroll', () => {
//         const currentScroll = window.pageYOffset;

//         if (currentScroll > 50) {
//             navbar.classList.add('scrolled');
//         } else {
//             navbar.classList.remove('scrolled');
//         }

//         lastScroll = currentScroll;
//     }, { passive: true });
// }

// /* ═══════════════════════════════
//    MOBILE MENU
//    ═══════════════════════════════ */
// function initMobileMenu() {
//     const toggle = document.getElementById('menuToggle');
//     const navLinks = document.getElementById('navLinks');
//     const overlay = document.getElementById('navOverlay');

//     if (!toggle || !navLinks) return;

//     toggle.addEventListener('click', () => {
//         toggle.classList.toggle('active');
//         navLinks.classList.toggle('open');
//         if (overlay) overlay.classList.toggle('active');
//         document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
//     });

//     // Close on overlay click
//     if (overlay) {
//         overlay.addEventListener('click', () => {
//             toggle.classList.remove('active');
//             navLinks.classList.remove('open');
//             overlay.classList.remove('active');
//             document.body.style.overflow = '';
//         });
//     }

//     // Close on link click
//     navLinks.querySelectorAll('a:not(.btn)').forEach(link => {
//         link.addEventListener('click', () => {
//             toggle.classList.remove('active');
//             navLinks.classList.remove('open');
//             if (overlay) overlay.classList.remove('active');
//             document.body.style.overflow = '';
//         });
//     });
// }

// /* ═══════════════════════════════
//    SCROLL REVEAL ANIMATIONS
//    ═══════════════════════════════ */
// function initScrollAnimations() {
//     const elements = document.querySelectorAll('.animate-on-scroll');
//     if (elements.length === 0) return;

//     const observer = new IntersectionObserver((entries) => {
//         entries.forEach((entry, index) => {
//             if (entry.isIntersecting) {
//                 // Stagger animation by index
//                 setTimeout(() => {
//                     entry.target.classList.add('visible');
//                 }, index * 80);
//                 observer.unobserve(entry.target);
//             }
//         });
//     }, {
//         threshold: 0.1,
//         rootMargin: '0px 0px -50px 0px'
//     });

//     elements.forEach(el => observer.observe(el));
// }

// /* ═══════════════════════════════
//    FLASH MESSAGES AUTO-DISMISS
//    ═══════════════════════════════ */
// function initFlashMessages() {
//     const container = document.getElementById('flashMessages');
//     if (!container) return;

//     const alerts = container.querySelectorAll('.alert');
//     alerts.forEach((alert, i) => {
//         setTimeout(() => {
//             alert.style.opacity = '0';
//             alert.style.transform = 'translateY(-20px)';
//             setTimeout(() => alert.remove(), 300);
//         }, 4000 + (i * 500));
//     });
// }

// /* ═══════════════════════════════
//    SMOOTH SCROLL FOR ANCHORS
//    ═══════════════════════════════ */
// function initSmoothScroll() {
//     document.querySelectorAll('a[href^="#"]').forEach(anchor => {
//         anchor.addEventListener('click', function (e) {
//             const targetId = this.getAttribute('href');
//             if (targetId === '#') return;

//             const target = document.querySelector(targetId);
//             if (target) {
//                 e.preventDefault();
//                 const navHeight = document.getElementById('navbar')?.offsetHeight || 0;
//                 const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 20;

//                 window.scrollTo({
//                     top: targetPosition,
//                     behavior: 'smooth'
//                 });
//             }
//         });
//     });
// }

// function togglePlay(wrapper) {
//     const audio = wrapper.querySelector('.audio-element');
    
//     // إيقاف أي مقطع آخر يعمل حالياً (اختياري)
//     document.querySelectorAll('.audio-element').forEach(el => {
//         if (el !== audio) {
//             el.pause();
//             el.parentElement.classList.remove('is-playing');
//         }
//     });

//     if (audio.paused) {
//         audio.play();
//         wrapper.classList.add('is-playing');
//     } else {
//         audio.pause();
//         wrapper.classList.remove('is-playing');
//     }
    
//     // إعادة إظهار الزر عند انتهاء المقطع
//     audio.onended = function() {
//         wrapper.classList.remove('is-playing');
//     };
// }
// /****** ******************************************************/























// document.addEventListener('DOMContentLoaded', function() {
//     const mainBtns = document.querySelectorAll('.main-cat-btn');
//     const subBtns = document.querySelectorAll('.sub-filter-btn');
//     const allBtn = document.querySelector('[data-filter="all"]');
//     const subRows = document.querySelectorAll('.sub-filter-row');
//     const sampleItems = document.querySelectorAll('.sample-item');

//     // دالة التحكم في تنسيق الأزرار النشطة
//     function updateActiveStyles(activeBtn, group) {
//         group.forEach(btn => {
//             btn.classList.remove('btn-primary', 'btn-outline', 'active');
//             btn.classList.add('btn-ghost');
//         });
//         activeBtn.classList.remove('btn-ghost');
//         if (activeBtn.classList.contains('sub-filter-btn')) {
//             activeBtn.classList.add('btn-outline', 'active');
//         } else {
//             activeBtn.classList.add('btn-primary', 'active');
//         }
//     }

//     // دالة الفلترة الأساسية
//     function filterItems(filterValue, isSubLevel = false) {
//         sampleItems.forEach(item => {
//             const itemCat = item.getAttribute('data-category');
//             const itemParent = item.getAttribute('data-parent');
            
//             if (filterValue === 'all') {
//                 item.style.display = '';
//             } else if (isSubLevel) {
//                 item.style.display = (itemCat === filterValue) ? '' : 'none';
//             } else {
//                 item.style.display = (itemParent === filterValue) ? '' : 'none';
//             }
//         });
//     }

//     // حدث الضغط على الأقسام الرئيسية
//     mainBtns.forEach(btn => {
//         btn.addEventListener('click', function() {
//             updateActiveStyles(this, [...mainBtns, allBtn]);
            
//             const targetId = this.getAttribute('data-target-sub');
//             subRows.forEach(row => row.style.display = 'none');
            
//             const targetRow = document.getElementById(targetId);
//             if (targetRow) {
//                 targetRow.style.display = 'flex';
//                 const defaultSub = targetRow.querySelector('.sub-filter-btn');
//                 updateActiveStyles(defaultSub, targetRow.querySelectorAll('.sub-filter-btn'));
//             }
//             filterItems(this.getAttribute('data-filter'), false);
//         });
//     });

//     // حدث الضغط على الأقسام الفرعية
//     subBtns.forEach(btn => {
//         btn.addEventListener('click', function() {
//             const currentSubGroup = this.closest('.sub-filter-row').querySelectorAll('.sub-filter-btn');
//             updateActiveStyles(this, currentSubGroup);
//             filterItems(this.getAttribute('data-filter'), true);
//         });
//     });

//     // زر "الكل" الرئيسي
//     allBtn.addEventListener('click', function() {
//         updateActiveStyles(this, [...mainBtns, allBtn]);
//         subRows.forEach(row => row.style.display = 'none');
//         filterItems('all');
//     });
// });

// // دالة تشغيل الصوت للملفات المرفوعة
// function togglePlay(wrapper) {
//     const audio = wrapper.querySelector('.audio-element');
//     const isPlaying = wrapper.classList.contains('is-playing');
    
//     document.querySelectorAll('.custom-player-wrapper').forEach(p => {
//         p.querySelector('.audio-element').pause();
//         p.classList.remove('is-playing');
//     });

//     if (!isPlaying) {
//         audio.play();
//         wrapper.classList.add('is-playing');
//     }
// }








// document.querySelectorAll('.main-filter-btn').forEach(btn => {
//     btn.addEventListener('click', function() {
//         // 1. Update active button style
//         document.querySelectorAll('.main-filter-btn').forEach(b => {
//             b.classList.replace('btn-primary', 'btn-ghost');
//             b.classList.remove('active');
//         });
//         this.classList.replace('btn-ghost', 'btn-primary');
//         this.classList.add('active');

//         // 2. Filter Samples by 'data-parent' (Main Category)
//         const mainSlug = this.getAttribute('data-main-filter');
//         const items = document.querySelectorAll('.sample-item');

//         items.forEach(item => {
//             item.style.display = (item.getAttribute('data-parent') === mainSlug) ? 'block' : 'none';
//         });
//         // 3. Update URL without refreshing (SEO friendly)
//         window.history.pushState({}, '', `/category/${mainSlug}`);
        
//         // 4. Update the Title text
//         document.getElementById('category-title').innerText = this.innerText.trim();
//     });
// });



// document.querySelectorAll('.main-filter-btn').forEach(btn => {
//     btn.addEventListener('click', function() {
//         // 1. Update active button style
//         document.querySelectorAll('.main-filter-btn').forEach(b => {
//             b.classList.replace('btn-primary', 'btn-ghost');
//             b.classList.remove('active');
//         });
//         this.classList.replace('btn-ghost', 'btn-primary');
//         this.classList.add('active');

//         // 2. Filter Samples by 'data-parent' (Main Category)
//         const mainSlug = this.getAttribute('data-main-filter');
//         const items = document.querySelectorAll('.sample-item');

//         items.forEach(item => {
//             item.style.display = (item.getAttribute('data-parent') === mainSlug) ? 'block' : 'none';
//         });

//         // 3. Update URL without refreshing (SEO friendly)
//         window.history.pushState({}, '', `/category/${mainSlug}`);
        
//         // 4. Update the Title text
//         document.getElementById('category-title').innerText = this.innerText.trim();
//     });
// });


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

function togglePlay(wrapper) {
    const audio = wrapper.querySelector('.audio-element');
    
    // إيقاف أي مقطع آخر يعمل حالياً (اختياري)
    document.querySelectorAll('.audio-element').forEach(el => {
        if (el !== audio) {
            el.pause();
            el.parentElement.classList.remove('is-playing');
        }
    });

    if (audio.paused) {
        audio.play();
        wrapper.classList.add('is-playing');
    } else {
        audio.pause();
        wrapper.classList.remove('is-playing');
    }
    
    // إعادة إظهار الزر عند انتهاء المقطع
    audio.onended = function() {
        wrapper.classList.remove('is-playing');
    };
}
/****** ******************************************************/























document.addEventListener('DOMContentLoaded', function() {
    const mainBtns = document.querySelectorAll('.main-cat-btn');
    const subBtns = document.querySelectorAll('.sub-filter-btn');
    const allBtn = document.querySelector('[data-filter="all"]');
    const subRows = document.querySelectorAll('.sub-filter-row');
    const sampleItems = document.querySelectorAll('.sample-item');

    // دالة التحكم في تنسيق الأزرار النشطة
    function updateActiveStyles(activeBtn, group) {
        group.forEach(btn => {
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

    // دالة الفلترة الأساسية
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

    // حدث الضغط على الأقسام الرئيسية
    mainBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            updateActiveStyles(this, [...mainBtns, allBtn]);
            
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

    // حدث الضغط على الأقسام الفرعية
    subBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const currentSubGroup = this.closest('.sub-filter-row').querySelectorAll('.sub-filter-btn');
            updateActiveStyles(this, currentSubGroup);
            filterItems(this.getAttribute('data-filter'), true);
        });
    });

    // زر "الكل" الرئيسي
    allBtn.addEventListener('click', function() {
        updateActiveStyles(this, [...mainBtns, allBtn]);
        subRows.forEach(row => row.style.display = 'none');
        filterItems('all');
    });
});

// دالة تشغيل الصوت للملفات المرفوعة
function togglePlay(wrapper) {
    const audio = wrapper.querySelector('.audio-element');
    const isPlaying = wrapper.classList.contains('is-playing');
    
    document.querySelectorAll('.custom-player-wrapper').forEach(p => {
        p.querySelector('.audio-element').pause();
        p.classList.remove('is-playing');
    });

    if (!isPlaying) {
        audio.play();
        wrapper.classList.add('is-playing');
    }
}








document.querySelectorAll('.main-filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // 1. Update active button style
        document.querySelectorAll('.main-filter-btn').forEach(b => {
            b.classList.replace('btn-primary', 'btn-ghost');
            b.classList.remove('active');
        });
        this.classList.replace('btn-ghost', 'btn-primary');
        this.classList.add('active');

        // 2. Filter Samples by 'data-parent' (Main Category)
        const mainSlug = this.getAttribute('data-main-filter');
        const items = document.querySelectorAll('.sample-item');

        items.forEach(item => {
            item.style.display = (item.getAttribute('data-parent') === mainSlug) ? 'block' : 'none';
        });
        // 3. Update URL without refreshing (SEO friendly)
        window.history.pushState({}, '', `/category/${mainSlug}`);
        
        // 4. Update the Title text
        document.getElementById('category-title').innerText = this.innerText.trim();
    });
});



document.querySelectorAll('.main-filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // 1. Update active button style
        document.querySelectorAll('.main-filter-btn').forEach(b => {
            b.classList.replace('btn-primary', 'btn-ghost');
            b.classList.remove('active');
        });
        this.classList.replace('btn-ghost', 'btn-primary');
        this.classList.add('active');

        // 2. Filter Samples by 'data-parent' (Main Category)
        const mainSlug = this.getAttribute('data-main-filter');
        const items = document.querySelectorAll('.sample-item');

        items.forEach(item => {
            item.style.display = (item.getAttribute('data-parent') === mainSlug) ? 'block' : 'none';
        });

        // 3. Update URL without refreshing (SEO friendly)
        window.history.pushState({}, '', `/category/${mainSlug}`);
        
        // 4. Update the Title text
        document.getElementById('category-title').innerText = this.innerText.trim();
    });
});


