document.addEventListener('DOMContentLoaded', function() {
    const feedbackForm = document.getElementById('feedbackForm');
    
    feedbackForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const feedback = document.getElementById('feedback').value;
        
        // You would typically send this data to a server endpoint
        // For now, we'll just display a success message
        alert(`Thank you for your feedback, ${name}!\n\nWe've received your message and will review it shortly.`);
        
        // Reset the form
        feedbackForm.reset();
    });
});
