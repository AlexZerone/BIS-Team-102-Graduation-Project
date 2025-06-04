document.addEventListener('DOMContentLoaded', function() {
    // Password strength
    const passwordInput = document.getElementById('password');
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            let strength = 0;
            const password = passwordInput.value;
            
            if (password.length >= 8) strength += 25;
            if (password.match(/[a-z]+/)) strength += 25;
            if (password.match(/[A-Z]+/)) strength += 25;
            if (password.match(/[0-9]+/)) strength += 25;
            
            strengthBar.style.width = strength + '%';
            
            if (strength < 25) {
                strengthBar.className = 'progress-bar bg-danger';
                strengthText.textContent = 'Weak';
            } else if (strength < 50) {
                strengthBar.className = 'progress-bar bg-warning';
                strengthText.textContent = 'Fair';
            } else if (strength < 75) {
                strengthBar.className = 'progress-bar bg-info';
                strengthText.textContent = 'Good';
            } else {
                strengthBar.className = 'progress-bar bg-success';
                strengthText.textContent = 'Strong';
            }
        });
    }
    
    // Show/hide fields based on user type selection
    const userTypeSelect = document.getElementById('user_type');
    const studentFields = document.getElementById('student-fields');
    const instructorFields = document.getElementById('instructor-fields');
    const companyFields = document.getElementById('company-fields');
    
    if (userTypeSelect) {
        userTypeSelect.addEventListener('change', function() {
            console.log("User type changed to: " + this.value); // Debug log
            
            // Hide all fields first
            if (studentFields) studentFields.style.display = 'none';
            if (instructorFields) instructorFields.style.display = 'none';
            if (companyFields) companyFields.style.display = 'none';
            
            // Show relevant fields based on selection
            switch(this.value) {
                case 'student':
                    if (studentFields) studentFields.style.display = 'block';
                    break;
                case 'instructor':
                    if (instructorFields) instructorFields.style.display = 'block';
                    break;
                case 'company':
                    if (companyFields) companyFields.style.display = 'block';
                    break;
            }
        });
    }
    
    // Form validation
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(event) {
            // Get the correct user_type element
            const userType = document.getElementById('user_type').value;
            let isValid = true;
            
            // Basic validation example
            if (userType === 'student') {
                const gpa = document.getElementById('gpa').value;
                if (gpa && (gpa < 0 || gpa > 4)) {
                    alert('GPA must be between 0 and 4');
                    isValid = false;
                }
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Update progress bar as user fills form
    const formInputs = document.querySelectorAll('#signupForm input, #signupForm select, #signupForm textarea');
    const progressBar = document.getElementById('formProgress');
    
    if (formInputs.length > 0 && progressBar) {
        const updateProgress = function() {
            const filledInputs = Array.from(formInputs).filter(input => 
                (input.type === 'checkbox' || input.type === 'radio') ? input.checked : input.value.trim() !== ''
            );
            const progress = (filledInputs.length / formInputs.length) * 100;
            progressBar.style.width = progress + '%';
        };
        
        formInputs.forEach(input => {
            input.addEventListener('input', updateProgress);
            input.addEventListener('change', updateProgress);
        });
        
        // Initial progress calculation
        updateProgress();
    }
});