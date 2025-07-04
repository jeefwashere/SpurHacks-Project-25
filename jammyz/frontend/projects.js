// adding jobs bullshit
let projectData = [];
// [{
//   title: '',
//   skills: [ {name: '',  description: ''} ]
// }]
function createProject(index) {
    const container = document.createElement("div");
    container.classList.add("project-entry");
    container.innerHTML = `
        <label class="entry-title">Project Title</label>
        <input type="text" class="projecttitle styled" placeholder="Name of Project">
        <button class="remove-project button" id="delete-button" type="button"><img src="/assets/images/trash.png" id="garbagePNG"></button>
        <br>
        <label class="subEntry-title">Select Skill:</label>
        <select class="skill-select"></select>
        <div class="active-skill-editor"></div>
        <button class="add-skill button" id="skill-button" type="button">Add Skill</button>
        <hr>
    `;
    // Hook up removal
    container.querySelector(".remove-project").addEventListener("click", () => {
        projectData.splice(index, 1);
        container.remove();
    });
    //init
    projectData.push({ title: "", skills: [] });
    //  sync job title input to jobData
    const titleInput = container.querySelector(".projecttitle");
    titleInput.addEventListener("input", () => {
        projectData[index].title = titleInput.value;
    });
    // Hook up skill-related event 
    const addSkillBtn = container.querySelector(".add-skill");
    const skillSelect = container.querySelector(".skill-select");
    const projectSkills = projectData[index].skills;
    addSkillBtn.addEventListener("click", () => {
        addSkill(projectSkills, container);
    });
    skillSelect.addEventListener("change", () => {
        switchToProjectSkill(projectSkills, container);
    });
  return container;
}
function addSkill(skillData, container){
    skillSelect = container.querySelector(".skill-select")
    skillData.push({name: '', description: '' });
    updateProjectSkillSelect(skillData, skillSelect);
    skillSelect.selectedIndex = skillData.length - 1;
    switchToProjectSkill(skillData, container);

}
// refresh the dropdown skill select
function updateProjectSkillSelect(skillData, skillSelect){
    skillSelect.innerHTML = '';
    skillData.forEach((skill, index) => {
        const option = document.createElement("option");
        option.value = index;
        option.textContent = skill.name || `Skill ${index + 1}`;
        skillSelect.appendChild(option);
    });
}
// switch to a skill
function switchToProjectSkill(skillData, container){
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
        updateProjectSkillSelect(skillData, skillSelect);
        skillSelect.selectedIndex = index;
    });
    skillDesc.addEventListener("input", () => {
        updateProjectSkillDesc(skillData, index, skillDesc.value)
    })
    removeSkillBtn.addEventListener("click", () => {
        removeProjectSkill(skillData, container)
    })
}

// Update skill name
function updateProjectSkillName(skillData, skillSelect, newName) {
    const index = skillSelect.selectedIndex;
    skillData[index].name = newName;
    updateProjectSkillSelect(skillData, skillSelect);
    skillSelect.selectedIndex = index
  }
// Update skill description
function updateProjectSkillDesc(skillData, index, newDesc) {
    skillData[index].description = newDesc;
}
// remove project from fucking the project-entries
function removeProject() {
    const projectForm = document.querySelector("#job-form");
    const projectEntries = projectForm.querySelectorAll(".job-entry");
  
    if (projectEntries.length > 1) {
      projectForm.removeChild(projectEntries[projectEntries.length - 1]);
      projectData.pop();
    }   
}
// Remove a skill
function removeProjectSkill(skillData, container) {
    const editor = container.querySelector(".active-skill-editor")
    const skillSelect = container.querySelector(".skill-select")
    const index = skillSelect.selectedIndex
    skillData.splice(index, 1);
    updateProjectSkillSelect(skillData, skillSelect);
    if (skillData.length > 0) {
        skillSelect.selectedIndex = Math.max(0, index - 1);
        switchToProjectSkill(skillData, container);
    } else {
        editor.innerHTML = '';
    }
}
document.addEventListener("DOMContentLoaded", () => {

    const projectTab = document.querySelector('[data-tab="3"]');
    const addProjectBtn = projectTab.querySelector(".add-project");
    const removeProjectBtn = projectTab.querySelector(".remove-project")
    const projectForm = projectTab.querySelector("#project-form");
    // Event listener to add jobs
    addProjectBtn.addEventListener("click", () => {
        const index = projectData.length;
        const jobEntry = createProject(index);
        projectForm.appendChild(jobEntry);
    });
    // Add one default job entry on load
    addProjectBtn.click();
    removeProjectBtn.addEventListener("click", () => {
        removeProject();
    })
});
