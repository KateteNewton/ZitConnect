// static/js/student_common.js

document.addEventListener('DOMContentLoaded', function() {

    // ---- Hamburger Toggle ----
    const hamburger = document.getElementById('hamburgerBtn');
    const sidebar = document.querySelector('.sidebar');

    // Create overlay if it doesn't exist
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
    }

    function toggleSidebar() {
        if (!sidebar) return;
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
    }

    if (hamburger) {
        hamburger.addEventListener('click', toggleSidebar);
    } else {
        console.warn('Hamburger button not found!');
    }

    // Click overlay to close
    overlay.addEventListener('click', function() {
        if (sidebar) sidebar.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    });

    // Press Escape to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // ---- Notification Badge ----
    function updateStudentNotifCount() {
        fetch('/api/unread-count')
            .then(response => response.json())
            .then(data => {
                const badge = document.getElementById('student-notif-badge');
                if (badge) {
                    if (data.count > 0) {
                        badge.textContent = data.count;
                        badge.style.display = 'inline';
                    } else {
                        badge.style.display = 'none';
                    }
                }
            })
            .catch(err => console.log('Notification fetch error:', err));
    }

    updateStudentNotifCount();
    setInterval(updateStudentNotifCount, 10000);

});