document.addEventListener("DOMContentLoaded", function () {

let originalEntities = [];
let maskedEntities = [];

let originalTextGlobal = "";
let maskedTextGlobal = "";

// Clear on reload
window.addEventListener("load", function () {
    resetAll();
});

// ================= FILE NAME DISPLAY =================
function showFileName(input) {
    const file = input.files[0];
    document.getElementById("fileName").innerText =
        file ? file.name : "No file chosen";
}
window.showFileName = showFileName; // expose to HTML

// ================= FILE UPLOAD =================
document.getElementById("fileInput").addEventListener("change", async function (event) {
    const file = event.target.files[0];

    // backup update (in case onchange not used)
    document.getElementById("fileName").innerText = file
        ? file.name
        : "No file chosen";

    if (!file) return;

    const fileName = file.name.toLowerCase();

    // TEXT FILES
    if (file.type === "text/plain" || fileName.endsWith(".txt")) {
        const reader = new FileReader();
        reader.onload = e => document.getElementById("inputText").value = e.target.result;
        reader.readAsText(file);
    }

    // PDF FILES
    else if (file.type === "application/pdf" || fileName.endsWith(".pdf")) {
        const reader = new FileReader();
        reader.onload = async function () {
            const typedarray = new Uint8Array(this.result);
            const pdf = await pdfjsLib.getDocument(typedarray).promise;

            let fullText = "";
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const content = await page.getTextContent();
                const strings = content.items.map(item => item.str).join(" ");
                fullText += strings + "\n";
            }

            document.getElementById("inputText").value = fullText;
        };
        reader.readAsArrayBuffer(file);
    }

    // OTHER FILE TYPES
    else {
        document.getElementById("inputText").value =
            `File "${file.name}" uploaded successfully.\n\n` +
            `⚠ Text extraction is not supported in the browser for this file type.\n` +
            `Send this file to the backend for processing.`;
    }
});

// ================= ANALYZE =================
async function analyzeText() {
    const text = document.getElementById("inputText").value.trim();
    if (!text) return alert("Please enter text first!");

    originalTextGlobal = text;

    const response = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });

    const data = await response.json();
    originalEntities = data.entities || [];

    highlightText(originalTextGlobal, originalEntities);
    populateTable(originalTextGlobal, originalEntities);
}

// ================= HIGHLIGHT =================
function highlightText(text, entities) {
    let result = "";
    let lastIndex = 0;

    const sorted = [...entities].sort((a, b) => a.start - b.start);

    sorted.forEach(e => {
        result += text.substring(lastIndex, e.start);
        const entityClass = getEntityClass(e.entity);
        result += `<mark class="${entityClass}">${text.substring(e.start, e.end)}</mark>`;
        lastIndex = e.end;
    });

    result += text.substring(lastIndex);
    document.getElementById("outputText").innerHTML = result;
}

function getEntityClass(entityType) {
    const classMap = {
        'PERSON': 'person',
        'LOCATION': 'location',
        'PHONE_NUMBER': 'phone',
        'PAN': 'pan',
        'AADHAAR': 'aadhaar',
        'CREDIT_CARD': 'credit_card',
        'VOTER_ID': 'voter_id',
        'IBANK': 'ibank',
        'EMAIL': 'email'
    };
    return classMap[entityType] || 'default';
}

// ================= TABLE =================
function populateTable(text, entities) {
    const tableBody = document.getElementById("resultBody");
    tableBody.innerHTML = "";

    entities.forEach(e => {
        const value = text.substring(e.start, e.end);
        const confidence = (e.score * 100).toFixed(0);
        tableBody.innerHTML += `<tr>
            <td>${e.entity}</td>
            <td>${value}</td>
            <td>${e.start}</td>
            <td>${e.end}</td>
            <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div class="confidence-bar">
                        <div class="confidence-bar-fill" style="width: ${confidence}%"></div>
                    </div>
                    <span>${confidence}%</span>
                </div>
            </td>
        </tr>`;
    });
}

// ================= MASK =================
function maskSensitive() {
    if (!originalEntities.length) return alert("Analyze text first!");

    let newText = "";
    let lastIndex = 0;
    maskedEntities = [];

    const sorted = [...originalEntities].sort((a, b) => a.start - b.start);

    sorted.forEach(e => {
        newText += originalTextGlobal.substring(lastIndex, e.start);
        const originalValue = originalTextGlobal.substring(e.start, e.end);
        const maskedValue = maskByType(e.entity, originalValue);

        const newStart = newText.length;
        newText += maskedValue;
        const newEnd = newText.length;

        maskedEntities.push({ entity: e.entity, start: newStart, end: newEnd, score: e.score });
        lastIndex = e.end;
    });

    newText += originalTextGlobal.substring(lastIndex);
    maskedTextGlobal = newText;

    document.getElementById("inputText").value = maskedTextGlobal;
    highlightText(maskedTextGlobal, maskedEntities);
    populateTable(maskedTextGlobal, maskedEntities);
}

// ================= UNMASK =================
function unmaskSensitive() {
    document.getElementById("inputText").value = originalTextGlobal;
    highlightText(originalTextGlobal, originalEntities);
    populateTable(originalTextGlobal, originalEntities);
}

// ================= MASK RULES =================
function maskByType(entity, value) {
    switch (entity) {
        case "AADHAAR_NUMBER": return value.replace(/\d/g, "X").slice(0, -4) + value.slice(-4);
        case "PAN_NUMBER": return value.slice(0, 5).replace(/[A-Z]/g, "X") + value.slice(5);
        case "PHONE_NUMBER": return value.slice(0, 2) + "*".repeat(value.length - 4) + value.slice(-2);
        case "CREDIT_CARD": return value.replace(/\d/g, "X").slice(0, -4) + value.slice(-4);
        case "IBAN_CODE": return value.slice(0, 4) + "X".repeat(value.length - 8) + value.slice(-4);
        case "VOTER_ID": return value.slice(0, 3) + "X".repeat(value.length - 6) + value.slice(-3);
        case "EMAIL_ADDRESS":
            const parts = value.split("@");
            return parts[0][0] + "X".repeat(parts[0].length - 1) + "@" + parts[1];
        case "LOCATION": return "[ADDRESS]";
        default: return "█".repeat(value.length);
    }
}

// ================= RESET =================
function resetAll() {
    document.getElementById("inputText").value = "";
    document.getElementById("outputText").innerHTML = "";
    document.getElementById("resultBody").innerHTML = "";
    document.getElementById("fileInput").value = "";
    document.getElementById("fileName").innerText = "No file chosen";
    originalEntities = [];
    maskedEntities = [];
    originalTextGlobal = "";
    maskedTextGlobal = "";
}

// ================= DOWNLOAD =================
function downloadJSON() {
    if (!maskedEntities.length && !originalEntities.length)
        return alert("No results to download!");

    const dataToDownload = maskedEntities.length ? maskedEntities : originalEntities;

    const blob = new Blob([JSON.stringify({ entities: dataToDownload }, null, 2)], { type: "application/json" });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "pii_results.json";
    a.click();
    URL.revokeObjectURL(url);
}

// 🔥 Expose functions to HTML buttons
window.analyzeText = analyzeText;
window.maskSensitive = maskSensitive;
window.unmaskSensitive = unmaskSensitive;
window.downloadJSON = downloadJSON;
window.resetAll = resetAll;

});
