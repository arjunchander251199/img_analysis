// Global state
let currentFile = null;
let currentFilename = null;
let extractedData = null;
let isEditing = false;

// DOM Elements
const uploadSection = document.getElementById("uploadSection");
const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const filePreview = document.getElementById("filePreview");
const previewContent = document.getElementById("previewContent");
const fileName = document.getElementById("fileName");
const removeFileBtn = document.getElementById("removeFile");
const analyzeBtn = document.getElementById("analyzeBtn");
const progressBar = document.getElementById("progressBar");
const loadingText = document.getElementById("loadingText");
const extractedContent = document.getElementById("extractedContent");
const resultImagePreview = document.getElementById("resultImagePreview");
const editBtn = document.getElementById("editBtn");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const newAnalysisBtn = document.getElementById("newAnalysis");
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toastMessage");

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
});

function setupEventListeners() {
  // Drag and drop
  dropZone.addEventListener("dragover", handleDragOver);
  dropZone.addEventListener("dragleave", handleDragLeave);
  dropZone.addEventListener("drop", handleDrop);

  // File input
  fileInput.addEventListener("change", handleFileSelect);

  // Buttons
  removeFileBtn.addEventListener("click", resetUpload);
  analyzeBtn.addEventListener("click", analyzeFile);
  editBtn.addEventListener("click", toggleEdit);
  copyBtn.addEventListener("click", copyToClipboard);
  downloadBtn.addEventListener("click", downloadAsText);
  newAnalysisBtn.addEventListener("click", resetAll);
}

// Drag and drop handlers
function handleDragOver(e) {
  e.preventDefault();
  dropZone.classList.add("border-primary-600", "bg-primary-200");
}

function handleDragLeave(e) {
  e.preventDefault();
  dropZone.classList.remove("border-primary-600", "bg-primary-200");
}

function handleDrop(e) {
  e.preventDefault();
  dropZone.classList.remove("border-primary-600", "bg-primary-200");

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFile(files[0]);
  }
}

function handleFileSelect(e) {
  const files = e.target.files;
  if (files.length > 0) {
    handleFile(files[0]);
  }
}

function handleFile(file) {
  // Validate file size
  const maxSize = 16 * 1024 * 1024; // 16MB
  if (file.size > maxSize) {
    showToast("File too large. Maximum size is 16MB.", "error");
    return;
  }

  // Validate file type
  const allowedTypes = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/bmp",
    "image/webp",
  ];
  if (!allowedTypes.includes(file.type)) {
    showToast("Invalid file type. Please upload an image.", "error");
    return;
  }

  currentFile = file;
  displayFilePreview(file);
}

function displayFilePreview(file) {
  fileName.textContent = `📄 ${file.name} (${formatFileSize(file.size)})`;

  // Show preview
  previewContent.innerHTML = "";

  const reader = new FileReader();
  reader.onload = (e) => {
    previewContent.innerHTML = `
        <img src="${e.target.result}" alt="Preview" class="max-w-full h-auto rounded-lg shadow-md mx-auto" style="max-height: 300px;">
    `;
  };
  reader.readAsDataURL(file);

  filePreview.classList.remove("hidden");
}

function resetUpload() {
  currentFile = null;
  fileInput.value = "";
  filePreview.classList.add("hidden");
  previewContent.innerHTML = "";
  fileName.textContent = "";
}

async function analyzeFile() {
  if (!currentFile) {
    showToast("Please select a file first.", "error");
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML =
    '<i class="fas fa-spinner fa-spin mr-2"></i>Uploading...';

  try {
    // Upload file
    const formData = new FormData();
    formData.append("file", currentFile);

    const uploadResponse = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const uploadData = await uploadResponse.json();

    if (!uploadResponse.ok) {
      throw new Error(uploadData.error || "Upload failed");
    }

    currentFilename = uploadData.filename;

    // Show loading section
    uploadSection.classList.add("hidden");
    loadingSection.classList.remove("hidden");

    // Animate progress bar
    animateProgress();

    // Analyze file
    const analyzeResponse = await fetch("/api/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ filename: currentFilename }),
    });

    const analyzeData = await analyzeResponse.json();

    if (!analyzeResponse.ok) {
      throw new Error(analyzeData.error || "Analysis failed");
    }

    extractedData = analyzeData.result;

    // Show results
    setTimeout(() => {
      displayResults(extractedData);
    }, 500);
  } catch (error) {
    console.error("Error:", error);
    showToast(error.message, "error");
    resetAll();
  }
}

function animateProgress() {
  let progress = 0;
  const texts = [
    "Uploading file...",
    "Initializing AI model...",
    "Analyzing content...",
    "Extracting text...",
    "Processing handwriting...",
    "Finalizing results...",
  ];

  const interval = setInterval(() => {
    progress += 2;
    progressBar.style.width = `${Math.min(progress, 95)}%`;

    const textIndex = Math.floor(progress / 16);
    if (textIndex < texts.length) {
      loadingText.textContent = texts[textIndex];
    }

    if (progress >= 95) {
      clearInterval(interval);
    }
  }, 100);
}

function displayResults(data) {
  loadingSection.classList.add("hidden");
  resultsSection.classList.remove("hidden");

  // Display the uploaded image
  const reader = new FileReader();
  reader.onload = (e) => {
    resultImagePreview.innerHTML = `
      <img src="${e.target.result}" alt="Uploaded Image" class="max-w-full h-auto rounded-lg shadow-md mx-auto" style="max-height: 500px;">
    `;
  };
  reader.readAsDataURL(currentFile);

  extractedContent.innerHTML = "";

  const contentDiv = createContentBlock(
    "Extracted Content",
    data.content,
    "single"
  );
  extractedContent.appendChild(contentDiv);

  progressBar.style.width = "100%";
  showToast("Analysis completed successfully!", "success");
}

function createContentBlock(title, content, id) {
  // Clean up content - remove markdown formatting
  let cleanContent = content
    .replace(/\*\*/g, "") // Remove bold markers
    .replace(/\*/g, "") // Remove asterisks
    .replace(/#{1,6}\s/g, "") // Remove markdown headers
    .replace(/`{1,3}/g, "") // Remove code markers
    .trim();

  const div = document.createElement("div");
  div.className = "bg-gray-50 rounded-lg p-6";
  div.innerHTML = `
        <h3 class="text-xl font-semibold text-gray-800 mb-4">
            <i class="fas fa-file-text text-primary-600 mr-2"></i>${title}
        </h3>
        <div class="content-editable bg-white rounded-lg p-4 border border-gray-200 min-h-[200px] whitespace-pre-wrap font-mono text-sm" 
             id="content-${id}" 
             contenteditable="false">${escapeHtml(cleanContent)}</div>
    `;
  return div;
}

function toggleEdit() {
  isEditing = !isEditing;
  const editableElements = document.querySelectorAll(".content-editable");

  editableElements.forEach((el) => {
    el.contentEditable = isEditing;
    if (isEditing) {
      el.classList.add("ring-2", "ring-primary-500");
    } else {
      el.classList.remove("ring-2", "ring-primary-500");
    }
  });

  if (isEditing) {
    editBtn.innerHTML = '<i class="fas fa-save mr-2"></i>Save Changes';
    editBtn.classList.add("bg-green-600", "hover:bg-green-700");
    editBtn.classList.remove("bg-primary-600", "hover:bg-primary-700");
    showToast("Edit mode enabled. Click Save when done.", "info");
  } else {
    editBtn.innerHTML = '<i class="fas fa-edit mr-2"></i>Edit Content';
    editBtn.classList.remove("bg-green-600", "hover:bg-green-700");
    editBtn.classList.add("bg-primary-600", "hover:bg-primary-700");
    showToast("Changes saved!", "success");
  }
}

function copyToClipboard() {
  const editableElements = document.querySelectorAll(".content-editable");
  let allText = "";

  editableElements.forEach((el) => {
    allText += el.textContent + "\n\n";
  });

  navigator.clipboard
    .writeText(allText)
    .then(() => {
      showToast("Copied to clipboard!", "success");
    })
    .catch((err) => {
      showToast("Failed to copy to clipboard.", "error");
    });
}

function downloadAsText() {
  const editableElements = document.querySelectorAll(".content-editable");
  let allText = "";

  editableElements.forEach((el) => {
    allText += el.textContent + "\n\n";
  });

  const blob = new Blob([allText], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "extracted_content.txt";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast("Downloaded successfully!", "success");
}

function resetAll() {
  // Delete file from server if exists
  if (currentFilename) {
    fetch(`/api/delete/${currentFilename}`, { method: "DELETE" }).catch((err) =>
      console.error("Error deleting file:", err)
    );
  }

  // Reset state
  currentFile = null;
  currentFilename = null;
  extractedData = null;
  isEditing = false;

  // Reset UI
  fileInput.value = "";
  filePreview.classList.add("hidden");
  loadingSection.classList.add("hidden");
  resultsSection.classList.add("hidden");
  uploadSection.classList.remove("hidden");
  progressBar.style.width = "0%";
  analyzeBtn.disabled = false;
  analyzeBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Analyze with AI';
}

// Utility functions
function showToast(message, type = "info") {
  toastMessage.textContent = message;

  // Set color based on type
  if (type === "success") {
    toast.classList.add("bg-green-600");
    toast.classList.remove("bg-gray-800", "bg-red-600", "bg-blue-600");
  } else if (type === "error") {
    toast.classList.add("bg-red-600");
    toast.classList.remove("bg-gray-800", "bg-green-600", "bg-blue-600");
  } else if (type === "info") {
    toast.classList.add("bg-blue-600");
    toast.classList.remove("bg-gray-800", "bg-green-600", "bg-red-600");
  }

  toast.style.transform = "translateY(0)";

  setTimeout(() => {
    toast.style.transform = "translateY(8rem)";
  }, 3000);
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
