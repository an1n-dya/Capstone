document.addEventListener('DOMContentLoaded', function() {
    // Initial setup
    const allEventsView = document.querySelector('#all-events-view');
    const eventView = document.querySelector('#event-view');
    const pastEventsView = document.querySelector('#past-events-view');
    const notLoggedView = document.querySelector('#notlogged');

    // Hide all views initially, then show the main one
    [eventView, pastEventsView, notLoggedView].forEach(view => view.style.display = 'none');
    allEventsView.style.display = 'block';

    // Event Listeners
    document.querySelector('#close')?.addEventListener("click", () => location.reload());
    document.getElementById('past_btn')?.addEventListener("click", showPastEvents);

    // Initial data load
    loadAndDisplayUpcomingEvents();
});

/**
 * Toggles the visibility of different views.
 * @param {string} viewToShow - The ID of the view to display ('all-events-view', 'past-events-view', 'event-view').
 */
function switchView(viewToShow) {
    document.querySelectorAll('.main-view').forEach(view => {
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
    element.className = 'event-list-item'; // Add a class for styling
    element.style.border = 'solid thin';
    element.style.borderRadius = "50px";
    element.style.marginBottom = "10px";
    element.style.marginTop = "11px";
    element.style.padding = "5px 15px";
    element.style.listStyleType = 'none';
    element.style.cursor = 'pointer';

    // Hover effect
    element.addEventListener("mouseover", () => element.style.transform = 'scale(1.02)');
    element.addEventListener("mouseout", () => element.style.transform = 'scale(1)');

    const attendees = event.attendees.join(', ');

    // Use template literals and append content safely
    element.innerHTML = `
        <h4 style='text-decoration:underline;'>Title: ${escapeHTML(event.title)}</h4>
        <ul>
            <li>Description: ${escapeHTML(event.description)}</li>
            <li>Host: ${escapeHTML(event.host)}</li>
            <li>Attendees: ${escapeHTML(attendees)}</li>
            <li>Date: ${escapeHTML(event.date)}</li>
            <li>Start: ${escapeHTML(event.start)}</li>
            <li>End: ${escapeHTML(event.end)}</li>
            <li>Category: ${escapeHTML(event.category)}</li>
            <li>Number Attending: ${event.number_attending}</li>
            <li>Location: ${escapeHTML(event.location)}</li>
        </ul>
        ${event.image ? `<img src="/media/${event.image}" width="40%" height="40%" style="margin-top: 10px; border-radius: 10px;"><br><br>` : '<br>'}
    `;
    return element;
}

/**
 * Fetches and displays past events.
 */
async function showPastEvents() {
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
            eventElement.addEventListener('click', () => showSingleEvent(event.id, 'past'));
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
async function loadAndDisplayUpcomingEvents() {
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
            eventElement.addEventListener('click', () => showSingleEvent(event.id, 'upcoming'));
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
async function showSingleEvent(id, time) {
    switchView('event-view');
    const container = document.querySelector('#list2');
    container.innerHTML = 'Loading event details...';

    try {
        const response = await fetch(`event/${id}`);
        const event = await response.json();
        container.innerHTML = '';

        const eventElement = createEventElement(event);
        container.append(eventElement);

        const username = document.getElementById('username')?.innerHTML;
        if (!username) {
            document.querySelector('#notlogged').style.display = 'block';
            return;
        }

        let buttonText = '';
        if (time === 'upcoming') {
            if (username === event.host) buttonText = 'Cancel Event';
            else if (event.attendees.includes(username)) buttonText = 'Unattend';
            else buttonText = 'Attend';
        } else if (time === 'past' && username === event.host) {
            buttonText = 'Delete Past Event';
        }

        if (buttonText) {
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
    let url, method, body;

    if (action === "Attend" || action === "Unattend") {
        url = `update/${id}`;
        method = 'PUT';
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
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: body // Will be undefined for DELETE, which is fine
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        await response.json();
        location.reload(); // Reload to reflect changes
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
    document.querySelector('#all-events-view').style.display = 'none';
    document.querySelector('#past-events-view').style.display = 'block';
    
    // Fetching past events
    fetch('past_events')
    .then(response => response.json())
    .then(data => {
        console.log("past data",data);
        const object = data;
        const contained = document.querySelector('#list3');
        object.forEach(function(element){

        let e = document.createElement('li');
        // Give div a border
        e.style.border = 'solid thin';
        e.style.borderRadius = "50px";

        // Add margin or padding to div
        e.style.marginBottom = "10px";
        e.style.marginTop = "11px";
        e.style.paddingTop = "5px";
        e.style.paddingLeft = "5px";
        e.style.paddingRight = "5px";

        // Hover
        e.addEventListener("mouseover", function(){
            e.style.transform = 'scale(1.05)';
          }),
          e.addEventListener("mouseout", function(){
            e.style.transform = 'scale(1)';  
          })
        // Create variable for attendees and comma and space
        var attendees = element.attendees;
        var spaced = attendees.join(', ');

        e.innerHTML += `<h4 list-style-type: none; style='text-decoration:underline;'>Title: ${element.title}  </h4>`;
        e.innerHTML += `<li>Description: ${element.description} </li>`; 
        e.innerHTML += `<li>Host: ${element.host} </li>`;
        e.innerHTML +=  `<li>Attendees: ${spaced} </li>`;
        e.innerHTML +=  `<li>Date: ${element.date} </li>`;
        e.innerHTML +=  `<li>Start: ${element.start} </li>`;
        e.innerHTML +=  `<li>End: ${element.end} </li>`;
        e.innerHTML +=  `<li>Category: ${element.category} </li>`;
        e.innerHTML +=  `<li>Number Attending: ${element.number_attending} </li>`;
        if (element.image){
            e.innerHTML +=  `<li>Location: ${element.location} </li><br>`;
            e.innerHTML +=  `<img src="/media/${element.image}" width="40%" height="40%"><br><br>`;
        }
        else {
            e.innerHTML +=  `<li>Location: ${element.location} </li><br><br>`;
        }
        contained.append(e);

        // Ability to click email
        e.addEventListener('click', function(){
            document.querySelector('#past-events-view').style.display = 'none';
            document.querySelector('#event-view').style.display = 'block';

            // Send id for display
            single_event(element.id, 'past');
        });
        })
    })
}

async function allevents() {
    //document.querySelector('#all-events-view').style.display = 'block';

    // Make a fetch request
    const response = await fetch('events');
    const data = await response.json();
    console.log("DATA",data)
    return data;
    }
    allevents().then(data => {
        const object = data;
        const contained = document.querySelector('#list1');
        object.forEach(function(element){
           
            
        let e = document.createElement('li');

        // Give div a border
        e.style.border = 'solid thin';
        e.style.borderRadius = "50px";

        // Add margin or padding to div
        e.style.marginBottom = "10px";
        e.style.marginTop = "11px";
        e.style.paddingTop = "5px";
        e.style.paddingLeft = "5px";
        e.style.paddingRight = "5px";
   
        

        // Hover
        e.addEventListener("mouseover", function(){
            e.style.transform = 'scale(1.05)';
          }),
          e.addEventListener("mouseout", function(){
            e.style.transform = 'scale(1)';  
          })
        // Create variable for attendees and comma and space
        var attendees = element.attendees;
        var spaced = attendees.join(', ');

        e.innerHTML += `<h4 list-style-type: none; style='text-decoration:underline;'>Title: ${element.title}  </h4>`;
        e.innerHTML += `<li>Description: ${element.description} </li>`; 
        e.innerHTML += `<li>Host: ${element.host} </li>`;
        e.innerHTML +=  `<li>Attendees: ${spaced} </li>`;
        e.innerHTML +=  `<li>Date: ${element.date} </li>`;
        e.innerHTML +=  `<li>Start: ${element.start} </li>`;
        e.innerHTML +=  `<li>End: ${element.end} </li>`;
        e.innerHTML +=  `<li>Category: ${element.category} </li>`;
        e.innerHTML +=  `<li>Number Attending: ${element.number_attending} </li>`;
        if (element.image){
            e.innerHTML +=  `<li>Location: ${element.location} </li><br>`;
            e.innerHTML +=  `<img src="/media/${element.image}" width="40%" height="40%"><br><br>`;
        }
        else {
            e.innerHTML +=  `<li>Location: ${element.location} </li><br><br>`;
        }
        contained.append(e);

        // Ability to click email
        e.addEventListener('click', function(){
            document.querySelector('#all-events-view').style.display = 'none';
            document.querySelector('#event-view').style.display = 'block';

            console.log("This ID clicked:", element.id);
            // Show event view
            // Send id for display
            single_event(element.id, 'upcoming'); 
        })
        })
    });
 
function single_event(id, time){      
    document.querySelector('#list2').innerHTML = ''; 
       
    
    console.log("Single event ran", id)
    
    // Create int variable for route
    let variable = id;
  
    // Make a get request
    fetch(`event/${variable}`)
    .then(response => response.json())
    .then(data => {
    const object = data;
    const contained2 = document.querySelector('#list2');
    
    let e = document.createElement('li');

    // Give div a border
    e.style.border = 'solid thin';
    e.style.borderRadius = "50px";

    // Add margin or padding to div
    e.style.marginBottom = "10px";
    e.style.marginTop = "11px";
    e.style.paddingTop = "5px";
    e.style.paddingLeft = "5px";
    e.style.paddingRight = "5px";

    // Create variable for attendees and comma and space
    var attendees = object.attendees;
    var spaced = attendees.join(', ');
    

    e.innerHTML += `<h4 list-style-type: none; style='text-decoration:underline;'>Title: ${object.title}  </h4>`;
    e.innerHTML += `<li>Description: ${object.description} </li>`; 
    e.innerHTML += `<li>Host: ${object.host} </li>`;
    e.innerHTML +=  `<li>Attendees: ${spaced} </li>`;
    e.innerHTML +=  `<li>Date: ${object.date} </li>`;
    e.innerHTML +=  `<li>Start: ${object.start} </li>`;
    e.innerHTML +=  `<li>End: ${object.end} </li>`;
    e.innerHTML +=  `<li>Category: ${object.category} </li>`;
    e.innerHTML +=  `<li>Number Attending: ${object.number_attending} </li>`;
    if (object.image){
        e.innerHTML +=  `<li>Location: ${object.location} </li><br>`;
        e.innerHTML +=  `<img src="/media/${object.image}" width="40%" height="40%"><br><br>`;
    }
    else {
        e.innerHTML +=  `<li>Location: ${object.location} </li><br><br>`;
    }
    
    contained2.append(e);
    
    if (time === 'upcoming'){
    try {
        var username = document.getElementById('username').innerHTML;
        let button = document.createElement('button');
        // If host, give option to cancel event
        if (username === object.host){
            button.textContent = 'Cancel Event';   
        }
        // If new condition is true and first condition false
        else if (spaced.includes(username) && !(username === object.host)) {
            button.textContent = 'Unattend';
        }
        // If both conditions are false
        else {
            button.textContent = 'Attend';
        }

        contained2.append(button);
        // Listen for button click and send access type to function 
        button.addEventListener('click', () => {
            event_access(button.textContent, object.id, username);
        }); 

    }
    catch(err) {
        console.log("Error:", err);
        contained2.append(e);
        document.querySelector('#notlogged').style.display = 'block';
    }
    }// if statement
    if (time === 'past'){
    try{
        var username = document.getElementById('username').innerHTML;
        let button = document.createElement('button');
        if (username === object.host){
            button.textContent = 'Delete Past Event'; 
            contained2.append(button); 
        }
        // Listen for button click and send access type to function 
        button.addEventListener('click', () => {
            event_access(button.textContent, object.id, username);
        });
        
    }
    catch(err){
        console.log("Error:", err);
    }
    }
    });
}



// Receives access type to do something
async function event_access(access, id, username){
    if (access === "Attend" || access === "Unattend"){
        console.log("Testing", access, id, username);
       // Make a put request
    fetch(`update/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id:id,
            attendees:username,
            number_attending:1
        })
    })
    .then(location.reload())
    //.then(response => response.json())
    .then(data => {
        console.log("From update",data);
    })
    .catch(error => {
        console.log(error);
    }); 
    }
    
    // Cancel or Delete event
    if (access === 'Cancel Event'|| access === "Delete Past Event"){
        try{
            const response = await fetch(`delete/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')}
              });
            
              if (!response.ok) {
                const message = 'Error with Status Code: ' + response.status;
                throw new Error(message);
              };
              const data = await response.json();
              console.log("data from cancel/delete:", data);
            } 
        catch (error) {
              console.log('Error:', error);
            }
            location.reload()    
    } 


}
// Use this to grab the csrf token
function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}