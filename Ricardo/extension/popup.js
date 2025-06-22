document.addEventListener('DOMContentLoaded', function () {
  const navGenerate = document.getElementById('navGenerate');
  const navProfile = document.getElementById('navProfile');
  const generateView = document.getElementById('generateView');
  const profileView = document.getElementById('profileView');
  const resultsContainer = document.getElementById('resultsContainer');
  const loadingIndicator = document.getElementById('loadingIndicator');

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

  // Function to display the analysis results
  function displayResults(data) {
    resultsContainer.innerHTML = `
      <h3>Job Description Analysis</h3>
      <div class="job-description">
        <h4>Original Job Description:</h4>
        <p>${data.jobDescription}</p>
      </div>
      <div class="analysis-results">
        <h4>Key Skills Identified:</h4>
        <pre>${data.analysis}</pre>
      </div>
      <button id="generateResumeBtn" class="btn btn-primary">Generate Tailored Resume</button>
    `;

    // Add event listener for the new button
    document.getElementById('generateResumeBtn').addEventListener('click', () => {
      generateResume(data.jobDescription);
    });
  }

  // Function to generate the resume
  function generateResume(jobDescription) {
    loadingIndicator.style.display = 'block';

    fetch('http://127.0.0.1:5000/process_data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ jobDescription: jobDescription }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tailored_resume.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        loadingIndicator.style.display = 'none';
      })
      .catch(error => {
        console.error('Error:', error);
        loadingIndicator.style.display = 'none';
        alert('Failed to generate resume. Please try again.');
      });
  }

  // Functionality for the "Generate" button inside the generate view
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.addEventListener('click', () => {
    const jobDescription = document.getElementById('jobDescriptionInput').value.trim();

    if (!jobDescription) {
      alert("Please enter a job description.");
      return;
    }

    loadingIndicator.style.display = 'block';
    resultsContainer.innerHTML = '';

    fetch('http://127.0.0.1:5000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jobDescription })
    })
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
      })
      .then(data => {
        if (data.error) throw new Error(data.error);
        displayResults(data);
      })
      .catch(error => {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
      })
      .finally(() => {
        loadingIndicator.style.display = 'none';
      });
  });
});