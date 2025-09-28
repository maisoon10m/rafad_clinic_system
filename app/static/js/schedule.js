/**
 * Schedule management JavaScript for Rafad Clinic System
 * Provides real-time updates for appointment schedules
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize schedule calendar if available
    initializeScheduleCalendar();
    
    // Initialize real-time slot updates
    initializeSlotUpdates();
    
    // Initialize schedule conflict checking
    initializeConflictChecker();
});

/**
 * Initialize the schedule calendar view
 */
function initializeScheduleCalendar() {
    const weeklyViewElement = document.getElementById('weekly-schedule');
    if (!weeklyViewElement) return;

    // Get doctor ID from data attribute
    const doctorId = weeklyViewElement.dataset.doctorId;
    if (!doctorId) return;

    // Fetch and display schedule
    fetchDoctorSchedule(doctorId);
}

/**
 * Fetch doctor schedule data
 * @param {number} doctorId - The doctor ID
 */
function fetchDoctorSchedule(doctorId) {
    fetch(`/api/doctor-schedule/${doctorId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch doctor schedule');
            }
            return response.json();
        })
        .then(data => {
            renderWeeklySchedule(data.schedules);
        })
        .catch(error => {
            console.error('Error fetching schedule:', error);
            showAlert('error', 'Failed to load doctor schedule. Please try again.');
        });
}

/**
 * Render weekly schedule in the calendar
 * @param {Array} schedules - Array of schedule objects
 */
function renderWeeklySchedule(schedules) {
    const weeklyViewElement = document.getElementById('weekly-schedule');
    if (!weeklyViewElement) return;
    
    // Clear previous content
    weeklyViewElement.innerHTML = '';
    
    // Create schedule table
    const table = document.createElement('table');
    table.className = 'table table-bordered schedule-table';
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    // Add time column header
    const timeHeader = document.createElement('th');
    timeHeader.textContent = 'Time';
    headerRow.appendChild(timeHeader);
    
    // Add day columns
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    days.forEach(day => {
        const dayHeader = document.createElement('th');
        dayHeader.textContent = day;
        headerRow.appendChild(dayHeader);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    // Create hour slots from 8:00 to 20:00
    for (let hour = 8; hour < 20; hour++) {
        const timeSlot = document.createElement('tr');
        
        // Time column
        const timeCol = document.createElement('td');
        timeCol.className = 'time-label';
        timeCol.textContent = `${hour.toString().padStart(2, '0')}:00`;
        timeSlot.appendChild(timeCol);
        
        // Day columns
        for (let day = 0; day < 7; day++) {
            const dayCol = document.createElement('td');
            dayCol.className = 'schedule-slot';
            dayCol.dataset.day = day;
            dayCol.dataset.hour = hour;
            
            // Find if there's a schedule for this time slot
            const schedule = schedules.find(s => 
                s.day_of_week === day && 
                parseInt(s.start_time.split(':')[0]) <= hour && 
                parseInt(s.end_time.split(':')[0]) > hour
            );
            
            if (schedule) {
                dayCol.classList.add('scheduled');
                dayCol.dataset.scheduleId = schedule.id;
                
                // Only add details in the first hour of the schedule
                if (parseInt(schedule.start_time.split(':')[0]) === hour) {
                    const scheduleInfo = document.createElement('div');
                    scheduleInfo.className = 'schedule-info';
                    scheduleInfo.textContent = `${schedule.start_time} - ${schedule.end_time}`;
                    
                    const appointmentDuration = document.createElement('div');
                    appointmentDuration.className = 'appointment-duration small';
                    appointmentDuration.textContent = `${schedule.appointment_duration} min/appointment`;
                    
                    dayCol.appendChild(scheduleInfo);
                    dayCol.appendChild(appointmentDuration);
                }
            }
            
            timeSlot.appendChild(dayCol);
        }
        
        tbody.appendChild(timeSlot);
    }
    
    table.appendChild(tbody);
    weeklyViewElement.appendChild(table);
}

/**
 * Initialize real-time slot updates for appointment creation
 */
function initializeSlotUpdates() {
    // Elements for appointment slot selection
    const doctorSelect = document.getElementById('doctor-select') || document.getElementById('doctor_id');
    const dateInput = document.getElementById('appointment_date') || document.getElementById('date');
    const timeSelect = document.getElementById('appointment_time');
    
    if (!doctorSelect || !dateInput) return;
    
    // Add event listeners for doctor and date changes
    doctorSelect.addEventListener('change', updateAvailableSlots);
    dateInput.addEventListener('change', updateAvailableSlots);
    
    // Initial update if values are already set
    if (doctorSelect.value && dateInput.value) {
        updateAvailableSlots();
    }
}

/**
 * Update available appointment slots based on doctor and date selection
 */
function updateAvailableSlots() {
    const doctorSelect = document.getElementById('doctor-select') || document.getElementById('doctor_id');
    const dateInput = document.getElementById('appointment_date') || document.getElementById('date');
    const timeSelect = document.getElementById('appointment_time');
    
    if (!doctorSelect || !dateInput || !timeSelect) return;
    
    const doctorId = doctorSelect.value;
    const date = dateInput.value;
    
    if (!doctorId || !date) {
        clearTimeOptions(timeSelect);
        return;
    }
    
    // Show loading indicator
    timeSelect.disabled = true;
    if (timeSelect.parentNode.querySelector('.spinner-border')) {
        timeSelect.parentNode.querySelector('.spinner-border').remove();
    }
    
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border spinner-border-sm text-primary ml-2';
    spinner.setAttribute('role', 'status');
    timeSelect.insertAdjacentElement('afterend', spinner);
    
    // Get appointment ID if we're editing
    const appointmentId = document.getElementById('appointment_id') ? 
        document.getElementById('appointment_id').value : null;
    
    // Fetch available slots
    fetch(`/api/available-slots?doctor_id=${doctorId}&date=${date}${appointmentId ? '&exclude_appointment_id='+appointmentId : ''}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch available slots');
            }
            return response.json();
        })
        .then(data => {
            // Remove spinner
            if (timeSelect.parentNode.querySelector('.spinner-border')) {
                timeSelect.parentNode.querySelector('.spinner-border').remove();
            }
            timeSelect.disabled = false;
            
            // Update time options
            updateTimeOptions(timeSelect, data.slots);
            
            // Show availability message
            showAvailabilityMessage(data.slots);
        })
        .catch(error => {
            console.error('Error fetching slots:', error);
            
            // Remove spinner
            if (timeSelect.parentNode.querySelector('.spinner-border')) {
                timeSelect.parentNode.querySelector('.spinner-border').remove();
            }
            timeSelect.disabled = false;
            
            // Clear time options
            clearTimeOptions(timeSelect);
            
            // Show error message
            showAlert('error', 'Failed to load available slots. Please try again.');
        });
}

/**
 * Update time select options with available slots
 * @param {HTMLElement} timeSelect - The time select element
 * @param {Array} slots - Array of available time slots
 */
function updateTimeOptions(timeSelect, slots) {
    // Save the currently selected value
    const currentValue = timeSelect.value;
    
    // Clear existing options
    clearTimeOptions(timeSelect);
    
    if (!slots || slots.length === 0) {
        const noOption = document.createElement('option');
        noOption.value = '';
        noOption.textContent = 'No available slots';
        timeSelect.appendChild(noOption);
        timeSelect.disabled = true;
        return;
    }
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- Select Time --';
    timeSelect.appendChild(defaultOption);
    
    // Add slot options
    slots.forEach(slot => {
        const option = document.createElement('option');
        option.value = slot;
        option.textContent = slot;
        timeSelect.appendChild(option);
    });
    
    // Restore previously selected value if it exists in new options
    if (currentValue) {
        const exists = Array.from(timeSelect.options).some(option => option.value === currentValue);
        if (exists) {
            timeSelect.value = currentValue;
        }
    }
    
    timeSelect.disabled = false;
}

/**
 * Clear all options from time select
 * @param {HTMLElement} timeSelect - The time select element
 */
function clearTimeOptions(timeSelect) {
    while (timeSelect.options.length > 0) {
        timeSelect.remove(0);
    }
}

/**
 * Show availability message near time select
 * @param {Array} slots - Array of available time slots
 */
function showAvailabilityMessage(slots) {
    const timeSelect = document.getElementById('appointment_time');
    if (!timeSelect) return;
    
    // Remove existing message if any
    const existingMsg = document.getElementById('availability-message');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.id = 'availability-message';
    messageDiv.className = slots && slots.length > 0 ? 'text-success mt-1 small' : 'text-danger mt-1 small';
    
    if (slots && slots.length > 0) {
        messageDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${slots.length} time slot${slots.length > 1 ? 's' : ''} available`;
    } else {
        messageDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> No available slots for this date`;
    }
    
    // Insert after time select
    timeSelect.parentNode.appendChild(messageDiv);
}

/**
 * Initialize appointment conflict checker
 */
function initializeConflictChecker() {
    const appointmentForm = document.querySelector('form[action*="appointment"]');
    if (!appointmentForm) return;
    
    appointmentForm.addEventListener('submit', function(e) {
        const doctorId = document.getElementById('doctor-select')?.value || document.getElementById('doctor_id')?.value;
        const dateInput = document.getElementById('appointment_date')?.value || document.getElementById('date')?.value;
        const timeInput = document.getElementById('appointment_time')?.value;
        
        if (!doctorId || !dateInput || !timeInput) return;
        
        // Get appointment ID if we're editing
        const appointmentId = document.getElementById('appointment_id') ? 
            document.getElementById('appointment_id').value : null;
        
        e.preventDefault();
        
        // Check for conflicts before submitting
        checkConflicts(doctorId, dateInput, timeInput, appointmentId)
            .then(result => {
                if (result.valid) {
                    appointmentForm.submit();
                } else {
                    showAlert('error', result.message || 'This appointment conflicts with an existing booking.');
                }
            })
            .catch(error => {
                console.error('Error checking conflicts:', error);
                // Show error but allow submission in case of API failure
                if (confirm('Could not validate appointment for conflicts. Do you want to proceed anyway?')) {
                    appointmentForm.submit();
                }
            });
    });
}

/**
 * Check for appointment conflicts
 * @param {string} doctorId - Doctor ID
 * @param {string} date - Appointment date
 * @param {string} time - Appointment time
 * @param {string} appointmentId - Optional current appointment ID (for edits)
 * @returns {Promise} - Promise resolving to validation result
 */
function checkConflicts(doctorId, date, time, appointmentId = null) {
    const url = '/api/validate-appointment';
    const params = new URLSearchParams({
        doctor_id: doctorId,
        date: date,
        time: time
    });
    
    if (appointmentId) {
        params.append('appointment_id', appointmentId);
    }
    
    return fetch(`${url}?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to validate appointment');
            }
            return response.json();
        });
}

/**
 * Show alert message
 * @param {string} type - Alert type ('success', 'error', 'warning', 'info')
 * @param {string} message - Alert message
 */
function showAlert(type, message) {
    // Remove existing alert if any
    const existingAlert = document.querySelector('.alert-floating');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Map type to Bootstrap class
    const typeClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert ${typeClass} alert-dismissible alert-floating fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    // Add to document
    document.body.appendChild(alert);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 150);
        }
    }, 5000);
}