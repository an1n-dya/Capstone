/**
 * This script handles dynamic, AJAX-powered interactions for the Playfield app.
 * It is designed for a server-side rendered application with progressive enhancement.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners for any dynamic buttons on the page.
    // This uses event delegation to handle elements that might be added to the DOM later.
    document.body.addEventListener('click', (event) => {
        const toggleBtn = event.target.closest('#toggle-attendance-btn');
        const cancelBtn = event.target.closest('#cancel-event-btn');
        const cancelBtnConfirm = event.target.closest('.cancel-event-btn-confirm');

        // Toggle Attendance Button
        if (toggleBtn) {
            handleToggleAttendance(toggleBtn);
        }

        // Cancel Event Button
        if (cancelBtn) {
            if (confirm('Are you sure you want to cancel this event? This action cannot be undone.')) {
                handleCancelEvent(cancelBtn);
            }
        }

        // Generic confirmation for cancel buttons on list pages
        if (cancelBtnConfirm) {
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

        const data = await response.json();

        if (!response.ok) {
            // Handle error response
            alert(data.message || 'An unexpected error occurred.');
            button.disabled = false;
            return;
        }

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
            alert(data.message || 'An error occurred.');
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

        const data = await response.json();

        if (!response.ok) {
            alert(data.message || 'An unexpected error occurred.');
            return;
        }

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

        const data = await response.json();

        if (!response.ok) {
            alert(data.message || 'Failed to post comment.');
            return;
        }

        if (data.success) {
            // Create new comment element and add it to the list
            const commentsList = document.getElementById('comments-list');
            const noCommentsEl = document.getElementById('no-comments');
            if (noCommentsEl) noCommentsEl.remove();

            const newComment = document.createElement('div');
            newComment.className = 'd-flex mb-3 pb-3 border-bottom';

            // Create the structure safely to prevent XSS
            const authorPicDiv = document.createElement('div');
            authorPicDiv.className = 'flex-shrink-0';
            
            const authorLink = document.createElement('a');
            authorLink.href = data.comment.author_profile_url;
            
            const authorImg = document.createElement('img');
            authorImg.src = data.comment.author_pic_url;
            authorImg.className = 'rounded-circle';
            authorImg.width = 40;
            authorImg.height = 40;
            authorImg.alt = data.comment.author;
            
            authorLink.appendChild(authorImg);
            authorPicDiv.appendChild(authorLink);

            const commentBodyDiv = document.createElement('div');
            commentBodyDiv.className = 'ms-3 flex-grow-1';

            const commentHeaderDiv = document.createElement('div');
            commentHeaderDiv.className = 'd-flex justify-content-between';
            
            const authorNameLink = document.createElement('a');
            authorNameLink.href = data.comment.author_profile_url;
            authorNameLink.className = 'text-decoration-none text-dark';
            
            const authorStrong = document.createElement('strong');
            authorStrong.textContent = data.comment.author;
            authorNameLink.appendChild(authorStrong);
            
            const timeSmall = document.createElement('small');
            timeSmall.className = 'text-muted';
            timeSmall.textContent = data.comment.naturaltime;
            
            commentHeaderDiv.appendChild(authorNameLink);
            commentHeaderDiv.appendChild(timeSmall);

            const commentContentP = document.createElement('p');
            commentContentP.className = 'mb-0 mt-1';
            commentContentP.textContent = data.comment.content;

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
            span.textContent = attendee.username;

            containerDiv.appendChild(img);
            containerDiv.appendChild(span);
            
            if (attendee.is_host) {
                const hostBadge = document.createElement('span');
                hostBadge.className = 'badge bg-warning ms-2';
                hostBadge.textContent = 'Host';
                containerDiv.appendChild(hostBadge);
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
        const noAttendeesEl = document.createElement('p');
        noAttendeesEl.className = 'text-muted';
        noAttendeesEl.textContent = 'No attendees yet.';
        attendeesListEl.appendChild(noAttendeesEl);
    }
}
