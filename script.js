
// tab switching garbage
function setupTabs(){
    document.querySelectorAll(".tabs__button").forEach(button => {
        button.addEventListener("click", () => {
            const sideBar = button.parentElement
            const tabsContainer = sideBar.parentElement
            const tabNumber = button.dataset.forTab
            const tabToActivate = tabsContainer.querySelector(`.tabs__content[data-tab="${tabNumber}"]`);
        
            sideBar.querySelectorAll(".tabs__button").forEach(button => {
                button.classList.remove("tabs__button--active")
            })

            tabsContainer.querySelectorAll(".tabs__content").forEach(content => {
                content.classList.remove("tabs__content--active")
            })

            button.classList.add("tabs_button--active");
            tabToActivate.classList.add("tabs__content--active");
        })
    })
}

document.addEventListener("DOMContentLoaded", () => {
    setupTabs();

    document.querySelectorAll(".tabs").forEach(tabContainer => {
        //tabContainer.querySelector(".tabs__sidebar .tabs__button").click();
        const buttons = tabContainer.querySelectorAll(".tabs__sidebar .tabs__button");
    
        if (buttons.length >= 2) {
            buttons[1].click(); // 👈 Index 1 is the second button
        }
    })
});

// adding jobs bullshit
let jobData = [];

function createJob(index) {
  const container = document.createElement("div");
  container.classList.add("job-entry");

  container.innerHTML = `
    <label>Job title:</label>
    <input type="text" class="jobtitle" placeholder="Titan Slayer">

    <br>
    <label>Select Skill:</label>
    <select class="skill-select"></select>

    <div class="active-skill-editor"></div>

    <button class="add-skill" type="button">Add Skill</button>
    <hr>
  `;

  jobData.push({ title: "" });

  return container;
}

// remove job from fucking the job-entries
function removeJob() {
    const jobForm = document.querySelector("#job-form");
    const jobEntries = jobForm.querySelectorAll(".job-entry");
  
    if (jobEntries.length > 1) {
      jobForm.removeChild(jobEntries[jobEntries.length - 1]);
      jobData.pop();
    }
  }

document.addEventListener("DOMContentLoaded", () => {

  const jobTab = document.querySelector('[data-tab="2"]');
  const addJobBtn = jobTab.querySelector(".add-job");
  const removeJobBtn = jobTab.querySelector(".remove-job")
  const jobForm = jobTab.querySelector("#job-form");

  // Event listener to add jobs
  addJobBtn.addEventListener("click", () => {
    const index = jobData.length;
    const jobEntry = createJob(index);
    jobForm.appendChild(jobEntry);
  });

  removeJobBtn.addEventListener("click", () => {
    removeJob();
  })

  // Add one default job entry on load
  addJobBtn.click();

});
