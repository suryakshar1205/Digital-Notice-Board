function initializeSectionSwitcher() {
    const sectionsData = document.getElementById('sections-data');
    if (!sectionsData) return;
    
    const sections = JSON.parse(sectionsData.textContent);
    let currentIndex = 0;
    
    function switchSection() {
        // Update current index
        currentIndex = (currentIndex + 1) % sections.length;
        const nextSection = sections[currentIndex];
        
        // console.log(`Switching to section: ${nextSection}`);
        
        // Update UI
        document.querySelectorAll('.section-name').forEach(el => {
            el.textContent = nextSection;
        });
        document.getElementById('current-section-display').textContent = nextSection;
        
        // Load new section data
        fetch(`/section/${encodeURIComponent(nextSection)}`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Check if there's a holiday message first
                const holidayMessage = doc.querySelector('.holiday-message');
                if (holidayMessage) {
                    // console.log(`Holiday detected for section: ${nextSection}`);
                    // If there's a holiday message, show it in both sections
                    const currentHolidayHTML = holidayMessage.outerHTML;
                    document.querySelector('.current-classes .section-content').innerHTML = currentHolidayHTML;
                    document.querySelector('.upcoming-classes .section-content').innerHTML = currentHolidayHTML;
                } else {
                    // console.log(`No holiday for section: ${nextSection}, showing normal classes`);
                    // Update current classes
                    const currentClassesContent = doc.querySelector('.current-classes .section-content');
                    if (currentClassesContent) {
                        document.querySelector('.current-classes .section-content').innerHTML = currentClassesContent.innerHTML;
                    }
                    
                    // Update upcoming classes
                    const upcomingClassesContent = doc.querySelector('.upcoming-classes .section-content');
                    if (upcomingClassesContent) {
                        document.querySelector('.upcoming-classes .section-content').innerHTML = upcomingClassesContent.innerHTML;
                    }
                }
            })
            .catch(error => {
                console.error('Error loading section:', error);
                // On error, show a message
                const errorMessage = `
                    <div class="no-items-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        Error loading section data. Please refresh the page.
                    </div>
                `;
                document.querySelector('.current-classes .section-content').innerHTML = errorMessage;
                document.querySelector('.upcoming-classes .section-content').innerHTML = errorMessage;
            });
    }
    
    // Switch sections every 10 seconds (as per user request)
    setInterval(switchSection, 10000);
    
    // Auto-refresh the page every 5 minutes to keep class information updated
    setInterval(function() {
        window.location.reload();
    }, 5 * 60 * 1000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSectionSwitcher); 