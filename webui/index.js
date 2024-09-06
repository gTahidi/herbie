import * as msgs from "./messages.js"

const splitter = document.getElementById('splitter');
const leftPanel = document.getElementById('left-panel');
const container = document.querySelector('.container');
const chatInput = document.getElementById('chat-input');
const chatHistory = document.getElementById('chat-history');
const sendButton = document.getElementById('send-button');
const inputSection = document.getElementById('input-section');
const statusSection = document.getElementById('status-section');
const chatsSection = document.getElementById('chats-section');

let isResizing = false;
let autoScroll = true;

let context = "";


splitter.addEventListener('mousedown', (e) => {
    isResizing = true;
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
});

function resize(e) {
    if (isResizing) {
        const newWidth = e.clientX - container.offsetLeft;
        leftPanel.style.width = `${newWidth}px`;
    }
}

function stopResize() {
    isResizing = false;
    document.removeEventListener('mousemove', resize);
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {

        const response = await sendJsonData("/msg", { text: message, context });

        //setMessage('user', message);
        chatInput.value = '';
        adjustTextareaHeight();
    }
}

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendButton.addEventListener('click', sendMessage);

function setMessage(id, type, heading, content, kvps = null) {
    // Search for the existing message container by id
    let messageContainer = document.getElementById(`message-${id}`);

    if (messageContainer) {
        // Clear the existing container's content if found
        messageContainer.innerHTML = '';
    } else {
        // Create a new container if not found
        const sender = type === 'user' ? 'user' : 'ai';
        messageContainer = document.createElement('div');
        messageContainer.id = `message-${id}`;
        messageContainer.classList.add('message-container', `${sender}-container`);
    }

    const handler = msgs.getHandler(type);
    handler(messageContainer, id, type, heading, content, kvps);

    // If the container was found, it was already in the DOM, no need to append again
    if (!document.getElementById(`message-${id}`)) {
        chatHistory.appendChild(messageContainer);
    }

    if (autoScroll) chatHistory.scrollTop = chatHistory.scrollHeight;
}


function adjustTextareaHeight() {
    chatInput.style.height = 'auto';
    chatInput.style.height = (chatInput.scrollHeight) + 'px';
}

async function sendJsonData(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    const jsonResponse = await response.json();
    return jsonResponse;
}

function generateGUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0;
        var v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

let lastLogVersion = 0;
let lastLogGuid = ""

async function poll() {
    try {
        const response = await sendJsonData("/poll", { log_from: lastLogVersion, context });
        // console.log(response)

        if (response.ok) {

            setContext(response.context)

            if (lastLogGuid != response.log_guid) {
                chatHistory.innerHTML = ""
                lastLogVersion = 0
            }

            if (lastLogVersion != response.log_version) {
                for (const log of response.logs) {
                    setMessage(log.no, log.type, log.heading, log.content, log.kvps);
                }
            }

            //set ui model vars from backend
            const inputAD = Alpine.$data(inputSection);
            inputAD.paused = response.paused;
            const statusAD = Alpine.$data(statusSection);
            statusAD.connected = response.ok;
            const chatsAD = Alpine.$data(chatsSection);
            chatsAD.contexts = response.contexts;

            lastLogVersion = response.log_version;
            lastLogGuid = response.log_guid;


        }

    } catch (error) {
        console.error('Error:', error);
        const statusAD = Alpine.$data(statusSection);
        statusAD.connected = false;
    }
}

window.pauseAgent = async function (paused) {
    const resp = await sendJsonData("/pause", { paused: paused, context });
}

window.resetChat = async function () {
    const resp = await sendJsonData("/reset", { context });
}

window.newChat = async function () {
    setContext(generateGUID());
}

window.killChat = async function (id) {


    const chatsAD = Alpine.$data(chatsSection);
    let found, other
    for (let i = 0; i < chatsAD.contexts.length; i++) {
        if (chatsAD.contexts[i].id == id) {
            found = true
        } else {
            other = chatsAD.contexts[i]
        }
        if (found && other) break
    }

    if (context == id && found) {
        if (other) setContext(other.id)
        else setContext(generateGUID())
    }
    
    if (found) sendJsonData("/remove", { context: id });
}

window.selectChat = async function (id) {
    setContext(id)
}

const setContext = function (id) {
    if (id == context) return
    context = id
    lastLogGuid = ""
    lastLogVersion = 0
    const chatsAD = Alpine.$data(chatsSection);
    chatsAD.selected = id
}


window.toggleAutoScroll = async function (_autoScroll) {
    autoScroll = _autoScroll;
}

window.toggleJson = async function (showJson) {
    // add display:none to .msg-json class definition
    toggleCssProperty('.msg-json', 'display', showJson ? 'block' : 'none');
}

window.toggleThoughts = async function (showThoughts) {
    // add display:none to .msg-json class definition
    toggleCssProperty('.msg-thoughts', 'display', showThoughts ? undefined : 'none');
}


function toggleCssProperty(selector, property, value) {
    // Get the stylesheet that contains the class
    const styleSheets = document.styleSheets;

    // Iterate through all stylesheets to find the class
    for (let i = 0; i < styleSheets.length; i++) {
        const styleSheet = styleSheets[i];
        const rules = styleSheet.cssRules || styleSheet.rules;

        for (let j = 0; j < rules.length; j++) {
            const rule = rules[j];
            if (rule.selectorText == selector) {
                // Check if the property is already applied
                if (value === undefined) {
                    rule.style.removeProperty(property);  // Remove the property
                } else {
                    rule.style.setProperty(property, value);  // Add the property (you can customize the value)
                }
                return;
            }
        }
    }
}

// Templates functionality
const templatesSection = document.getElementById('templates-section');
const templateList = templatesSection.querySelector('.template-list');
const addTemplateButton = templatesSection.querySelector('#addTemplateBtn');
const modal = templatesSection.querySelector('#templateModal');
const modalContent = modal.querySelector('.modal-content');

let templates = [];
let currentTemplate = null;

function renderTemplates() {
    templateList.innerHTML = '';
    templates.forEach(template => {
        const li = document.createElement('li');
        li.className = 'template-item';
        li.innerHTML = `
            <span class="template-name">${template.name}</span>
            <div class="template-actions">
                <button class="edit-button">Edit</button>
                <button class="delete-button">Delete</button>
            </div>
        `;
        li.querySelector('.template-name').addEventListener('click', () => useTemplate(template.id));
        li.querySelector('.edit-button').addEventListener('click', () => editTemplate(template));
        li.querySelector('.delete-button').addEventListener('click', () => deleteTemplate(template.id));
        templateList.appendChild(li);
    });
}

async function loadTemplates() {
    try {
        const response = await sendJsonData("/templates", {});
        if (response.ok) {
            templates = response.templates;
            renderTemplates();
        } else {
            console.error("Failed to load templates:", response.message);
        }
    } catch (error) {
        console.error("Error loading templates:", error);
    }
}

function openModal(template = null) {
    currentTemplate = template || { id: '', name: '', url: '', navigation_goal: '', data_extraction_goal: '' };
    modalContent.innerHTML = `
        <h2>${currentTemplate.id ? 'Edit Template' : 'New Template'}</h2>
        <input type="text" id="templateName" placeholder="Template Name" value="${currentTemplate.name}">
        <input type="text" id="templateUrl" placeholder="URL" value="${currentTemplate.url}">
        <textarea id="navigationGoal" placeholder="Navigation Goal">${currentTemplate.navigation_goal}</textarea>
        <textarea id="dataExtractionGoal" placeholder="Data Extraction Goal">${currentTemplate.data_extraction_goal}</textarea>
        <div class="modal-actions">
            <button class="save-button">Save</button>
            <button class="cancel-button">Cancel</button>
        </div>
    `;
    modalContent.querySelector('.save-button').addEventListener('click', saveTemplate);
    modalContent.querySelector('.cancel-button').addEventListener('click', closeModal);
    modal.style.display = 'block';
}

function closeModal() {
    modal.style.display = 'none';
}

async function saveTemplate() {
    currentTemplate.name = modalContent.querySelector('#templateName').value;
    currentTemplate.url = modalContent.querySelector('#templateUrl').value;
    currentTemplate.navigation_goal = modalContent.querySelector('#navigationGoal').value;
    currentTemplate.data_extraction_goal = modalContent.querySelector('#dataExtractionGoal').value;

    const response = await sendJsonData("/save_template", currentTemplate);
    if (response.ok) {
        await loadTemplates();
        closeModal();
    } else {
        alert("Error saving template: " + response.message);
    }
}

function editTemplate(template) {
    openModal(template);
}

async function deleteTemplate(templateId) {
    if (confirm("Are you sure you want to delete this template?")) {
        const response = await sendJsonData("/delete_template", { id: templateId });
        if (response.ok) {
            await loadTemplates();
        } else {
            alert("Error deleting template: " + response.message);
        }
    }
}

async function useTemplate(templateId) {
    const response = await sendJsonData("/use_template", { template_id: templateId, context });
    if (response.ok) {
        console.log("Template applied successfully");
    } else {
        alert("Error using template: " + response.message);
    }
}

addTemplateButton.addEventListener('click', () => openModal());

// Initialize templates
loadTemplates();
chatInput.addEventListener('input', adjustTextareaHeight);

setInterval(poll, 250);
