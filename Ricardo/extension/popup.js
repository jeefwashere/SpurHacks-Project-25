document.addEventListener('DOMContentLoaded', function() {
  const navGenerate = document.getElementById('navGenerate');
  const navProfile = document.getElementById('navProfile');
  const generateView = document.getElementById('generateView');
  const profileView = document.getElementById('profileView');

  // Function to switch views
  function switchView(viewToShow) {
    if (viewToShow === 'generate') {
      generateView.classList.add('active');
      profileView.classList.remove('active');
      navGenerate.classList.add('active');
      navProfile.classList.remove('active');
    } else {
      profileView.classList.add('active');
      generateView.classList.remove('active');
      navProfile.classList.add('active');
      navGenerate.classList.remove('active');
    }
  }

  // Event listeners for navigation buttons
  navGenerate.addEventListener('click', () => switchView('generate'));
  navProfile.addEventListener('click', () => switchView('profile'));

  // Functionality for the "Generate" button inside the generate view
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.addEventListener('click', () => {
    const jobDescription = document.getElementById('jobDescriptionInput').value;
    
    if (!jobDescription) {
      alert("Please enter a job description.");
      return;
    }

    // Use fetch to send data to the Flask server
    fetch('http://127.0.0.1:5000/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ jobDescription: jobDescription }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);// Show the success message from the server
    })
    .catch((error) => {
      console.error('Error:', error);
      alert('Failed to send data to server. Make sure the Flask server is running.');
    });
  });
  
}); 
