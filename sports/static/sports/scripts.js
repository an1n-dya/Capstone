document.addEventListener('DOMContentLoaded', function() {
    // Initial setup
    const allEventsView = document.getElementById('all-events-view');
    const eventView = document.getElementById('event-view');
    const pastEventsView = document.getElementById('past-events-view');
    const notLoggedView = document.getElementById('notlogged');

    // Hide all views initially, then show the main one
    [eventView, pastEventsView, notLoggedView].forEach(view => view.style.display = 'none');
    allEventsView.style.display = 'block';

    // Event Listeners
    document.getElementById('close')?.addEventListener("click", () => location.reload());
    document.getElementById('past_btn')?.addEventListener("click", () => showPastEvents());

    // Initial data load
    loadAndDisplayUpcomingEvents(); // This will load the initial view
});

/**
 * Toggles the visibility of different views.
 * @param {string} viewToShow - The ID of the view to display ('all-events-view', 'past-events-view', 'event-view').
 */
function switchView(viewToShow) {
    document.querySelectorAll('.main-view').forEach(view => { // Assuming .main-view class is on all main view containers
        view.style.display = view.id === viewToShow ? 'block' : 'none';
    });
}

/**
 * Creates a DOM element for an event.
 * @param {object} event - The event data object.
 * @returns {HTMLElement} - The created list item element for the event.
 */
function createEventElement(event) {
    const element = document.createElement('li');
    element.className = 'event-list-item'; // Add a class for styling and easier targeting
    element.style.border = 'solid thin'; // Example styling
    element.style.borderRadius = '50px';
    element.style.marginBottom = '10px';
    element.style.marginTop = '11px';
    element.style.padding = '5px 15px';
    element.style.listStyleType = 'none'; // Remove bullet points
    element.style.cursor = 'pointer'; // Indicate clickable

    // Hover effect
    element.addEventListener("mouseover", () => element.style.transform = 'scale(1.02)');
    element.addEventListener("mouseout", () => element.style.transform = 'scale(1)');

    const attendees = event.attendees.join(', ');

    // Use template literals and append content safely
    element.innerHTML = `
        <h4 style='text-decoration:underline;'>Title: ${escapeHTML(event.title)}</h4> <!-- Use escapeHTML for all user-generated content -->
        <ul>
            <li>Description: ${escapeHTML(event.description)}</li>
            <li>Host: ${escapeHTML(event.host)}</li>
            <li>Attendees: ${escapeHTML(attendees)}</li>
            <li>Date: ${escapeHTML(event.date)}</li>
            <li>Start: ${escapeHTML(event.start)}</li>
            <li>End: ${escapeHTML(event.end)}</li> <!-- Ensure all dynamic content is escaped -->
            <li>Category: ${escapeHTML(event.category_display || event.category)}</li> <!-- Use display name if available -->
            <li>Number Attending: ${event.number_attending} / ${event.max_attendees}</li>
            <li>Location: ${escapeHTML(event.location)}</li>
        </ul>
        ${event.image ? `<img src="/media/${event.image}" width="40%" height="40%" style="margin-top: 10px; border-radius: 10px;"><br><br>` : '<br>'}
    `;
    return element;
}

/**
 * Fetches and displays past events.
 */
async function showPastEvents() { // Renamed from showPastEvents to be consistent with other functions
    switchView('past-events-view');
    const container = document.querySelector('#list3');
    container.innerHTML = 'Loading past events...'; // Provide feedback

    try {
        const response = await fetch('past_events');
        const events = await response.json();
        container.innerHTML = ''; // Clear loading message

        if (events.length === 0) {
            container.innerHTML = '<p>No past events found.</p>';
            return;
        }

        events.forEach(event => {
            const eventElement = createEventElement(event);
            eventElement.addEventListener('click', () => showSingleEvent(event.id, 'past')); // Pass 'past' to indicate context
            container.append(eventElement);
        });
    } catch (error) {
        console.error("Error fetching past events:", error);
        container.innerHTML = '<p>Could not load past events. Please try again later.</p>';
    }
}

/**
 * Fetches and displays upcoming events.
 */
async function loadAndDisplayUpcomingEvents() { // Renamed from allevents for clarity
    const container = document.querySelector('#list1');
    container.innerHTML = 'Loading events...';

    try {
        const response = await fetch('events');
        const events = await response.json();
        container.innerHTML = '';

        if (events.length === 0) {
            container.innerHTML = '<p>No upcoming events. Why not create one?</p>';
            return;
        }

        events.forEach(event => {
            const eventElement = createEventElement(event);
            eventElement.addEventListener('click', () => showSingleEvent(event.id, 'upcoming')); // Pass 'upcoming' to indicate context
            container.append(eventElement);
        });
    } catch (error) {
        console.error("Error fetching upcoming events:", error);
        container.innerHTML = '<p>Could not load events. Please try again later.</p>';
    }
}

/**
 * Fetches and displays a single event's details.
 * @param {number} id - The ID of the event.
 * @param {string} time - 'upcoming' or 'past'.
 */
async function showSingleEvent(id, time) { // Renamed from single_event for clarity
    switchView('event-view');
    const container = document.querySelector('#list2');
    container.innerHTML = 'Loading event details...';

    try {
        const response = await fetch(`event/${id}`);
        const event = await response.json();
        container.innerHTML = '';

        // Append the event details using the reusable function
        const eventElement = createEventElement(event);
        container.append(eventElement);

        // Check if user is logged in to show action buttons
        const username = document.getElementById('username')?.innerHTML;
        if (!username) {
            // If not logged in, just display the event, no action buttons
            // The #notlogged view should be handled by Django template logic if needed
            return;
        }

        let buttonText = '';
        if (time === 'upcoming') {
            if (username === event.host) {
                buttonText = 'Cancel Event';
            } else if (event.attendees.includes(username)) {
                buttonText = 'Unattend';
            } else if (!event.is_full) { // Only allow attending if not full
                buttonText = 'Attend';
            }
        } else if (time === 'past' && username === event.host) {
            buttonText = 'Delete Past Event';
        }

        if (buttonText) { // Only create button if an action is possible
            const button = document.createElement('button');
            button.textContent = buttonText;
            button.className = 'btn btn-primary mt-2';
            button.addEventListener('click', () => handleEventAction(buttonText, event.id, username));
            container.append(button);
        }
    } catch (error) {
        console.error(`Error fetching event ${id}:`, error);
        container.innerHTML = '<p>Could not load event details.</p>';
    }
}

/**
 * Handles user actions on an event (attend, unattend, cancel, delete).
 * @param {string} action - The action to perform.
 * @param {number} id - The event ID.
 * @param {string} username - The current user's username.
 */
async function handleEventAction(action, id, username) {
    let url, method, body = {};

    if (action === "Attend" || action === "Unattend") {
        url = `update/${id}`;
        method = 'PUT'; // Use PUT for updating event attendees
        body = JSON.stringify({ id, attendees: username, number_attending: 1 });
    } else if (action === 'Cancel Event' || action === "Delete Past Event") {
        url = `delete/${id}`;
        method = 'DELETE';
    } else {
        return;
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Always send CSRF token for state-changing requests
            },
            body: body // Will be undefined for DELETE, which is fine
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        await response.json();
        location.reload(); // Reload the page to reflect the change in event status/attendance
    } catch (error) {
        console.error(`Error performing action '${action}':`, error);
        alert(`An error occurred. Could not ${action.toLowerCase()}.`);
    }
}

/**
 * Gets a cookie value by name.
 * @param {string} name - The name of the cookie.
 * @returns {string|null}
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
 * Escapes HTML to prevent XSS attacks when using innerHTML.
 * @param {string} str - The string to escape.
 * @returns {string}
 */
function escapeHTML(str) {
    const p = document.createElement("p");
    p.appendChild(document.createTextNode(str));
    return p.innerHTML;
}