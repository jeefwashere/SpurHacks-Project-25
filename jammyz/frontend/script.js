
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
        tabContainer.querySelector(".tabs__sidebar .tabs__button").click();
    })
    
});

// adding jobs bullshit
let jobData = [];

// [{
//   title: '',
//   skills: [ {name: '',  description: ''} ]
// }]

function createJob(index) {
  const container = document.createElement("div");
  container.classList.add("job-entry");

  container.innerHTML = `
    <label>Job title:</label>
    <input type="text" class="jobtitle" placeholder="Titan Slayer">
    <button class="remove-job" type="button"><img src="/assets/images/garbage.png" height = 15px></button>
    <br>
    <label>Select Skill:</label>
    <select class="skill-select"></select>

    <div class="active-skill-editor"></div>

    <button class="add-skill" type="button">Add Skill</button>
    <hr>
  `;


   // Hook up removal
   container.querySelector(".remove-job").addEventListener("click", () => {
       jobData.splice(index, 1);
       container.remove();
   });

   
    //init
    jobData.push({ title: "", skills: [] });

    //  sync job title input to jobData
    const titleInput = container.querySelector(".jobtitle");
    titleInput.addEventListener("input", () => {
        jobData[index].title = titleInput.value;
    });
        
    // Hook up skill-related event garbage
    const addSkillBtn = container.querySelector(".add-skill");
    const skillSelect = container.querySelector(".skill-select");
    const jobSkills = jobData[index].skills;

    addSkillBtn.addEventListener("click", () => {
        addSkill(jobSkills, container);
    });

    skillSelect.addEventListener("change", () => {
        switchToSkill(jobSkills, container);
    });
 
    
  return container;
}


function addSkill(skillData, container){
    skillSelect = container.querySelector(".skill-select")
    skillData.push({name: '', description: '' });
    updateSkillSelect(skillData, skillSelect);
    skillSelect.selectedIndex = skillData.length - 1;
    switchToSkill(skillData, container);

}

// refresh the dropdown skill select
function updateSkillSelect(skillData, skillSelect){
    skillSelect.innerHTML = '';
    skillData.forEach((skill, index) => {
        const option = document.createElement("option");
        option.value = index;
        option.textContent = skill.name || `Skill ${index + 1}`;
        skillSelect.appendChild(option);
    });
}

// switch to a skill
function switchToSkill(skillData, container){
    const skillSelect = container.querySelector(".skill-select");
    const index = skillSelect.selectedIndex;
    const skill = skillData[index];
    const editor = container.querySelector(".active-skill-editor")
    editor.innerHTML = `
        <input class="skill-name" type="text" placeholder="Skill name" value="${skill.name}">
        <textarea class="skill-description" placeholder="Describe how you used this skill" >${skill.description}</textarea>
        <button class="remove-skill" type="button">Remove Skill</button>
    `;

    const skillName = editor.querySelector(".skill-name")
    const skillDesc = editor.querySelector(".skill-description")
    const removeSkillBtn = editor.querySelector(".remove-skill")
    
    skillName.addEventListener("input", () => {
        skillData[index].name = skillName.value;
        updateSkillSelect(skillData, skillSelect);
        skillSelect.selectedIndex = index;
    });
    skillDesc.addEventListener("input", () => {
        updateSkillDesc(skillData, index, skillDesc.value)
    })
    removeSkillBtn.addEventListener("click", () => {
        removeSkill(skillData, container)
    })
}

// Update skill name
function updateSkillName(skillData, skillSelect, newName) {
    const index = skillSelect.selectedIndex;
    skillData[index].name = newName;
    updateSkillSelect(skillData, skillSelect);
    skillSelect.selectedIndex = index
  }
  
// Update skill description
function updateSkillDesc(skillData, index, newDesc) {
    skillData[index].description = newDesc;
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

// Remove a skill
function removeSkill(skillData, container) {
    const editor = container.querySelector(".active-skill-editor")
    const skillSelect = container.querySelector(".skill-select")
    const index = skillSelect.selectedIndex
    skillData.splice(index, 1);
    updateSkillSelect(skillData, skillSelect);
    if (skillData.length > 0) {
        skillSelect.selectedIndex = Math.max(0, index - 1);
        switchToSkill(skillData, container);
    } else {
        editor.innerHTML = '';
    }
}



document.addEventListener("DOMContentLoaded", () => {
    const jobTab = document.querySelector('[data-tab="2"]');
    const addJobBtn = jobTab.querySelector(".add-job");
    const jobForm = jobTab.querySelector("#job-form");

    addJobBtn.addEventListener("click", () => {
        const index = jobData.length;
        const jobEntry = createJob(index);
        jobForm.appendChild(jobEntry);
    });

    // Default job entry
    addJobBtn.click();
    document.getElementById("submit-all").addEventListener("click", () => {
        const finalData = collectAllData();
    
        fetch("http://127.0.0.1:5000/submit-jobs", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(finalData)
        })
        .then(res => res.json())
        .then(data => {
            alert("All data submitted!");
            console.log(data);
        })
        .catch(err => {
            console.error("Error submitting data:", err);
        });
    });
    
});

function collectAllData() {
    const personalInfo = {
        fullName: document.getElementById("username").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        birthdate: document.getElementById("birthdate").value,
        linkedin: document.getElementById("linkedin").value
    };

    const education = {
        schoolName: document.getElementById("schoolname").value,
        major: document.getElementById("major").value,
        degreeType: document.getElementById("degreetype").value,
        gpa: document.getElementById("gpa").value,
        startDate: document.getElementById("startdate").value,
        endDate: document.getElementById("enddate").value
    };

    const finalData = {
        personalInfo,
        jobExperience: jobData,
        projects: projectData,
        education
    };

    console.log(finalData);
    return finalData;
}




