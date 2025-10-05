// Dynamic search/filter (AJAX optional; GET form works for now)
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            // Could fetch('/search/?q=' + this.value) for live updates
            console.log('Searching: ' + this.value);  // Placeholder for real-time
        });
    }
});

function requestJoin(groupId) {
    fetch(`/group/${groupId}/request_join/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
    }).then(() => location.reload());
}

// Smooth scroll to forms on load
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('form')) {
        document.querySelector('form').scrollIntoView({ behavior: 'smooth' });
    }
    
    // Confetti on successful register (fun bonus—needs confetti.js library, or skip)
    // If you add <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script> to base.html head
    // Then: if (window.location.pathname === '/dashboard/') { confetti(); }
});