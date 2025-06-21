
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
    const jobDescription = document.getElementById('jobDescriptionInput').value; //user input
    // For now, we'll just log it and show an alert.
    // You can replace this with your actual resume generation logic.
    console.log('Job Description:', jobDescription);
    alert('Generating resume based on: ' + jobDescription);
  });
  
}); 
