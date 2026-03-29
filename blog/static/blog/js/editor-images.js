const DRAG_OVER_CLASS = "blog-editor__textarea--dragover";
const SUCCESS_FLASH_DELAY_MS = 2200;

function clearUploadFlash(uploadFlash) {
    uploadFlash.hidden = true;
    uploadFlash.textContent = "";
    uploadFlash.className = "blog-flash";
}

function showUploadFlash(uploadFlash, message, tone) {
    uploadFlash.hidden = false;
    uploadFlash.textContent = message;
    uploadFlash.className = `blog-flash blog-flash--${tone}`;
}

function insertMarkdownImage(textarea, imageUrl) {
    const start = textarea.selectionStart ?? textarea.value.length;
    const end = textarea.selectionEnd ?? start;
    const before = textarea.value.slice(0, start);
    const after = textarea.value.slice(end);
    const prefix = before && !before.endsWith("\n") ? "\n" : "";
    const suffix = after && !after.startsWith("\n") ? "\n" : "";
    const markdown = `${prefix}![alt text](${imageUrl})${suffix}`;

    textarea.value = `${before}${markdown}${after}`;

    const cursor = before.length + markdown.length;
    textarea.focus();
    textarea.setSelectionRange(cursor, cursor);
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
}

async function uploadImage(file, uploadUrl, csrfToken) {
    const payload = new FormData();
    payload.append("image", file, file.name || `pasted-image-${Date.now()}.png`);

    const response = await fetch(uploadUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
        body: payload,
        credentials: "same-origin",
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || "Image upload failed.");
    }

    return data.imageUrl;
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("blog-editor-form");
    const textarea = document.getElementById("id_markdown_body");
    const uploadFlash = document.getElementById("blog-editor-upload-flash");
    const csrfInput = form?.querySelector("input[name='csrfmiddlewaretoken']");
    const uploadUrl = form?.dataset.uploadUrl;
    const csrfToken = csrfInput?.value;

    if (!form || !textarea || !uploadFlash || !uploadUrl || !csrfToken) {
        return;
    }

    let flashTimerId = null;

    const setFlash = (message, tone, clearAfterMs = null) => {
        if (flashTimerId) {
            window.clearTimeout(flashTimerId);
            flashTimerId = null;
        }

        showUploadFlash(uploadFlash, message, tone);
        if (clearAfterMs) {
            flashTimerId = window.setTimeout(() => clearUploadFlash(uploadFlash), clearAfterMs);
        }
    };

    const uploadFiles = async (files) => {
        const imageFiles = files.filter((file) => file && file.type.startsWith("image/"));
        if (!imageFiles.length) {
            return;
        }

        setFlash(imageFiles.length > 1 ? "Uploading images..." : "Uploading image...", "working");

        try {
            for (const file of imageFiles) {
                const imageUrl = await uploadImage(file, uploadUrl, csrfToken);
                insertMarkdownImage(textarea, imageUrl);
            }
            setFlash(imageFiles.length > 1 ? "Images inserted." : "Image inserted.", "success", SUCCESS_FLASH_DELAY_MS);
        } catch (error) {
            setFlash(error.message || "Image upload failed.", "error");
        }
    };

    textarea.addEventListener("paste", (event) => {
        const files = Array.from(event.clipboardData?.items || [])
            .filter((item) => item.kind === "file")
            .map((item) => item.getAsFile())
            .filter(Boolean);

        if (!files.length) {
            return;
        }

        event.preventDefault();
        uploadFiles(files);
    });

    textarea.addEventListener("dragover", (event) => {
        event.preventDefault();
        textarea.classList.add(DRAG_OVER_CLASS);
    });

    textarea.addEventListener("dragleave", () => {
        textarea.classList.remove(DRAG_OVER_CLASS);
    });

    textarea.addEventListener("drop", (event) => {
        event.preventDefault();
        textarea.classList.remove(DRAG_OVER_CLASS);
        uploadFiles(Array.from(event.dataTransfer?.files || []));
    });
});
