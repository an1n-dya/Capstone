/**
 * This script handles dynamic, AJAX-powered interactions for the Playfield app.
 * It is designed for a server-side rendered application with progressive enhancement.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners for any dynamic buttons on the page.
    // This uses event delegation to handle elements that might be added to the DOM later.
    document.body.addEventListener('click', (event) => {
        // Toggle Attendance Button
        if (event.target.matches('#toggle-attendance-btn')) {
            handleToggleAttendance(event.target);
        }

        // Cancel Event Button
        if (event.target.matches('#cancel-event-btn')) {
            if (confirm('Are you sure you want to cancel this event? This action cannot be undone.')) {
                handleCancelEvent(event.target);
            }
        }

        // Generic confirmation for cancel buttons on list pages
        if (event.target.matches('.cancel-event-btn-confirm')) {
            if (!confirm('Are you sure you want to cancel this event? This action cannot be undone.')) {
                event.preventDefault();
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

    // Disable the button to prevent multiple clicks
    button.disabled = true;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            let errorMessage = 'An unexpected error occurred.';
            try {
                // Try to parse a JSON error message from the server
                const errorData = await response.json();
                if (errorData && errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (e) {
                // The response was not JSON, use the generic error.
                throw new Error('An unexpected error occurred.');
            }
            alert(errorMessage);
        } else {
            const data = await response.json();
            if (data.success) {
            // Update button text and style
            button.textContent = data.button_text;
            button.classList.toggle('btn-danger', data.attending);
            button.classList.toggle('btn-success', !data.attending);

            // Update attendee count and spots available on the page
            const attendeesCountEl = document.getElementById('attendees-count');
            if (attendeesCountEl) attendeesCountEl.textContent = data.attendees_count;

            const spotsAvailableEl = document.getElementById('spots-available');
            if (spotsAvailableEl) {
                const isFull = data.spots_available <= 0;
                spotsAvailableEl.textContent = isFull ? 'Full' : `${data.spots_available} spots available`;
                spotsAvailableEl.classList.toggle('bg-success', !isFull);
                spotsAvailableEl.classList.toggle('bg-warning', isFull);
            }

            // Update progress bar
            updateProgressBar(data.attendees_count, data.max_attendees);

            // Update the visual list of attendees
            updateAttendeesList(data.attendees_list, data.attendees_count);
            } else {
                alert(data.message); // Or display the error more gracefully
            }
        }
    } catch (error) {
        console.error('Error toggling attendance:', error);
        alert('An error occurred. Please try again.');
    } finally {
        // Re-enable the button once the request is complete
        button.disabled = false;
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

/**
 * Handles the AJAX request for submitting a new comment.
 * @param {Event} event The form submission event.
 */
async function handleCommentSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const url = form.action;
    const formData = new FormData(form);
    const csrfToken = getCookie('csrftoken');

    // Disable the submit button to prevent multiple submissions
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = true;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });

        if (!response.ok) throw new Error('Network response was not ok.');

        const data = await response.json();

        if (data.success) {
            // Create new comment element and add it to the list
            const commentsList = document.getElementById('comments-list');
            const noCommentsEl = document.getElementById('no-comments');
            if (noCommentsEl) noCommentsEl.remove();

            const newComment = document.createElement('div');
            newComment.className = 'd-flex mb-3 pb-3 border-bottom'; // This will be the main container

            // Create the structure safely to prevent XSS
            const authorPicDiv = document.createElement('div');
            authorPicDiv.className = 'flex-shrink-0';
            authorPicDiv.innerHTML = `<img src="${data.comment.author_pic_url}" class="rounded-circle" width="40" height="40" alt="${data.comment.author}">`;

            const commentBodyDiv = document.createElement('div');
            commentBodyDiv.className = 'ms-3 flex-grow-1';

            const commentHeaderDiv = document.createElement('div');
            commentHeaderDiv.className = 'd-flex justify-content-between';
            commentHeaderDiv.innerHTML = `
                <strong><a href="${data.comment.author_profile_url}" class="text-decoration-none text-dark">${data.comment.author}</a></strong>
                <small class="text-muted">${data.comment.naturaltime}</small>
            `;

            const commentContentP = document.createElement('p');
            commentContentP.className = 'mb-0 mt-1';
            commentContentP.textContent = data.comment.content; // Use textContent to safely insert user content

            // Assemble the element
            commentBodyDiv.appendChild(commentHeaderDiv);
            commentBodyDiv.appendChild(commentContentP);

            newComment.appendChild(authorPicDiv);
            newComment.appendChild(commentBodyDiv);

            commentsList.prepend(newComment);

            // Update comment count badge
            const commentsCountEl = document.getElementById('comments-count');
            if (commentsCountEl) {
                commentsCountEl.textContent = parseInt(commentsCountEl.textContent) + 1;
            }

            // Clear the form
            form.reset();
        } else {
            alert(data.message || 'Failed to post comment.');
        }
    } catch (error) {
        console.error('Error submitting comment:', error);
        alert('An error occurred. Please try again.');
    } finally {
        // Re-enable the submit button
        if (submitButton) submitButton.disabled = false;
    }
}

/**
 * Utility function to get a cookie by name.
 * This is essential for Django's CSRF protection with AJAX.
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

/**
 * Updates the attendance progress bar on the event detail page.
 * @param {number} current The current number of attendees.
 * @param {number} max The maximum number of attendees.
 */
function updateProgressBar(current, max) {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const percentage = max > 0 ? (current / max) * 100 : 0;
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = `${current}/${max}`;
        progressBar.setAttribute('aria-valuenow', current);
    }
}

/**
 * Updates the visual list of attendees on the event detail page.
 * @param {Array} attendees An array of attendee objects.
 * @param {number} totalAttendees The total number of attendees.
 */
function updateAttendeesList(attendees, totalAttendees) {
    const attendeesListEl = document.getElementById('attendees-list');
    if (!attendeesListEl) return;

    // Clear the current list
    attendeesListEl.innerHTML = '';

    if (attendees.length > 0) {
        attendees.forEach(attendee => {
            const attendeeEl = document.createElement('a');
            attendeeEl.href = attendee.profile_url;
            attendeeEl.className = 'text-decoration-none text-dark';

            const containerDiv = document.createElement('div');
            containerDiv.className = 'd-flex align-items-center mb-2';

            const img = document.createElement('img');
            img.src = attendee.profile_picture_url;
            img.className = 'rounded-circle me-2';
            img.width = 30;
            img.height = 30;
            img.alt = attendee.username;

            const span = document.createElement('span');
            span.textContent = attendee.username; // Use textContent for security

            containerDiv.appendChild(img);
            containerDiv.appendChild(span);
            if (attendee.is_host) {
                containerDiv.innerHTML += ' <span class="badge bg-warning ms-2">Host</span>';
            }

            attendeeEl.appendChild(containerDiv);
            attendeesListEl.appendChild(attendeeEl);
        });

        // Add the "and X more..." text if needed
        if (totalAttendees > 10) {
            const moreEl = document.createElement('p');
            moreEl.className = 'text-muted mt-3 mb-0';
            moreEl.textContent = `And ${totalAttendees - 10} more...`;
            attendeesListEl.appendChild(moreEl);
        }
    } else {
        attendeesListEl.innerHTML = '<p class="text-muted">No attendees yet.</p>';
    }
}
