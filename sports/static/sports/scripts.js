/**
 * This script handles dynamic, AJAX-powered interactions for the Playfield app.
 * It is designed for a server-side rendered application with progressive enhancement.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners for any dynamic buttons on the page.
    // This uses event delegation to handle elements that might be added to the DOM later.
    document.body.addEventListener('click', (event) => {
        // Toggle Attendance Button
        if (event.target && event.target.id === 'toggle-attendance-btn') {
            handleToggleAttendance(event.target);
        }

        // Cancel Event Button
        if (event.target && event.target.id === 'cancel-event-btn') {
            if (confirm('Are you sure you want to cancel this event? This action cannot be undone.')) {
                handleCancelEvent(event.target);
            }
        }
    });

    // Handle Comment Form Submission
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', handleCommentSubmit);
    }
});

/**
 * Handles the AJAX request for joining or leaving an event.
 * @param {HTMLButtonElement} button The button that was clicked.
 */
async function handleToggleAttendance(button) {
    const url = button.dataset.url;
    const csrfToken = getCookie('csrftoken');

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) throw new Error('Network response was not ok.');

        const data = await response.json();

        if (data.success) {
            // Update button text and style
            button.textContent = data.attending ? 'Leave Event' : 'Join Event';
            button.classList.toggle('btn-danger', data.attending);
            button.classList.toggle('btn-success', !data.attending);

            // Update attendee count and spots available on the page
            document.getElementById('attendees-count').textContent = data.attendees_count;
            document.getElementById('spots-available').textContent = `${data.spots_available} spots left`;
            
            // Optionally, show a success message (e.g., using a toast notification library)
            console.log(data.message);
        } else {
            alert(data.message); // Or display the error more gracefully
        }
    } catch (error) {
        console.error('Error toggling attendance:', error);
        alert('An error occurred. Please try again.');
    }
}

/**
 * Handles the AJAX request for cancelling an event.
 * @param {HTMLButtonElement} button The button that was clicked.
 */
async function handleCancelEvent(button) {
    const url = button.dataset.url;
    const csrfToken = getCookie('csrftoken');

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) throw new Error('Network response was not ok.');

        const data = await response.json();

        if (data.success) {
            // Reload the page to show the "Cancelled" state
            window.location.reload();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error cancelling event:', error);
        alert('An error occurred. Please try again.');
    }
}

// The rest of your functions (handleCommentSubmit, getCookie) would go here.
// getCookie function remains the same.

/**
 * Utility function to get a cookie by name.
 * @param {string} name The name of the cookie.
 * @returns {string|null} The cookie value or null if not found.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
