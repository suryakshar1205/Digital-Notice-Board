document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Update time remaining bars
    function updateTimeRemainingBars() {
        document.querySelectorAll('.time-remaining-bar').forEach(function(bar) {
            var timeRemaining = parseInt(bar.getAttribute('aria-valuenow'));
            var totalDuration = parseInt(bar.getAttribute('aria-valuemax'));
            
            if (timeRemaining > 0) {
                // Update time remaining
                timeRemaining--;
                bar.setAttribute('aria-valuenow', timeRemaining);
                
                // Calculate and update width
                var percentage = (timeRemaining / totalDuration) * 100;
                bar.style.width = percentage + '%';
                
                // Update text
                var minutes = Math.floor(timeRemaining / 60);
                if (minutes < 60) {
                    bar.textContent = minutes + ' minutes remaining';
                } else {
                    var hours = (minutes / 60).toFixed(1);
                    bar.textContent = hours + ' hours remaining';
                }
                
                // Update color based on time remaining
                if (percentage < 25) {
                    bar.classList.add('danger');
                    bar.classList.remove('warning');
                } else if (percentage < 50) {
                    bar.classList.add('warning');
                    bar.classList.remove('danger');
                }
            }
        });
    }

    // Update time remaining bars every second
    setInterval(updateTimeRemainingBars, 1000);

    // Auto-refresh the page every 5 minutes to get updated class information
    setTimeout(function() {
        window.location.reload();
    }, 5 * 60 * 1000);

    // Initialize progress bars
    function updateProgressBars() {
        document.querySelectorAll('.progress-bar[data-time-remaining]').forEach(bar => {
            const remaining = parseFloat(bar.dataset.timeRemaining);
            const total = parseFloat(bar.dataset.totalDuration);
            if (!isNaN(remaining) && !isNaN(total)) {
                const progress = ((total - remaining) / total * 100);
                bar.style.width = progress + '%';
                bar.setAttribute('aria-valuenow', progress);
            }
        });
    }

    // Update time remaining displays
    function updateTimeDisplays() {
        document.querySelectorAll('.time-remaining[data-remaining]').forEach(elem => {
            let remaining = parseFloat(elem.dataset.remaining);
            if (!isNaN(remaining) && remaining > 0) {
                remaining--;
                elem.dataset.remaining = remaining;
                const minutes = Math.max(0, Math.round(remaining / 60));
                elem.textContent = minutes + ' minutes remaining';
            }
        });
    }

    // Initialize and update progress
    updateProgressBars();
    setInterval(() => {
        updateProgressBars();
        updateTimeDisplays();
    }, 1000);

    // Flash messages functionality
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });

    // Add animation classes
    const animateElements = document.querySelectorAll('.card, .navbar');
    animateElements.forEach((el, index) => {
        el.classList.add('animate', `delay-${index}`);
    });

    // Handle offline/online status
    function updateOnlineStatus() {
        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'connection-status';
        
        if (!navigator.onLine) {
            statusIndicator.classList.add('offline');
            statusIndicator.innerHTML = '<i class="fas fa-wifi-slash"></i> You are offline';
            document.body.appendChild(statusIndicator);
        } else {
            const existingIndicator = document.querySelector('.connection-status');
            if (existingIndicator) {
                existingIndicator.remove();
            }
        }
    }

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();

    // Refresh page periodically to keep content updated
    let refreshTimeout;
    function scheduleRefresh() {
        if (refreshTimeout) clearTimeout(refreshTimeout);
        refreshTimeout = setTimeout(() => {
            if (navigator.onLine) {
                window.location.reload();
            } else {
                scheduleRefresh(); // Try again in 30 seconds if offline
            }
        }, 300000); // 5 minutes
    }

    scheduleRefresh();

    // Clear refresh timeout when page is hidden
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            clearTimeout(refreshTimeout);
        } else {
            scheduleRefresh();
        }
    });

    // Handle progress bars
    const progressBars = document.querySelectorAll('.progress-bar[data-progress]');
    progressBars.forEach(bar => {
        const progress = bar.getAttribute('data-progress');
        bar.style.width = `${progress}%`;
    });
});
