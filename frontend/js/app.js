// User clicks "Login" button
async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Send request to backend API
    const response = await fetch('http://localhost:5001/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        alert('Login successful!');
        // Redirect to dashboard
        window.location.href = 'student_dashboard.html';
    } else {
        alert('Login failed!');
    }
}