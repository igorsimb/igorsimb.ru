const DRAG_OVER_CLASS = "blog-editor__textarea--dragover";
const SUCCESS_FLASH_DELAY_MS = 2200;

function syncScrollPosition(source, target) {
    const maxSourceScroll = source.scrollHeight - source.clientHeight;
    const maxTargetScroll = target.scrollHeight - target.clientHeight;

    if (maxSourceScroll <= 0 || maxTargetScroll <= 0) {
        target.scrollTop = 0;
        return;
    }

    target.scrollTop = (source.scrollTop / maxSourceScroll) * maxTargetScroll;
}

function setupEditorPreviewScrollSync(textarea, previewMount) {
    let syncing = false;

    const sync = (source, target) => {
        if (syncing) {
            return;
        }

        syncing = true;
        syncScrollPosition(source, target);
        requestAnimationFrame(() => {
            syncing = false;
        });
    };

    textarea.addEventListener("scroll", () => sync(textarea, previewMount));
    previewMount.addEventListener("scroll", () => sync(previewMount, textarea));

    const observer = new MutationObserver(() => {
        sync(textarea, previewMount);
    });
    observer.observe(previewMount, { childList: true, subtree: true, characterData: true });

    requestAnimationFrame(() => syncScrollPosition(textarea, previewMount));
}

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

async function uploadImage(file, uploadUrl, csrfToken, failureMessage) {
    const payload = new FormData();
    payload.append("image", file, file.name || `pasted-image-${Date.now()}.png`);

    const response = await fetch(uploadUrl, {
        method: "POST",
        headers: { "Accept": "application/json", "X-CSRFToken": csrfToken },
        body: payload,
        credentials: "same-origin",
    });

    const isJson = response.headers.get("content-type")?.includes("application/json");
    const data = isJson ? await response.json().catch(() => ({})) : {};
    if (response.redirected || !response.ok || !isJson || !data.imageUrl) {
        throw new Error(data.error || failureMessage);
    }

    return data.imageUrl;
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("blog-editor-form");
    const textarea = document.getElementById("id_markdown_body");
    const previewMount = document.querySelector("[data-sync-scroll='preview']");
    const uploadFlash = document.getElementById("blog-editor-upload-flash");
    const csrfInput = form?.querySelector("input[name='csrfmiddlewaretoken']");
    const uploadUrl = form?.dataset.uploadUrl;
    const csrfToken = csrfInput?.value;

    if (!form || !textarea || !previewMount || !uploadFlash || !uploadUrl || !csrfToken) {
        return;
    }

    setupEditorPreviewScrollSync(textarea, previewMount);

    const uploadMessages = {
        oneWorking: form.dataset.uploadOneWorking,
        manyWorking: form.dataset.uploadManyWorking,
        oneSuccess: form.dataset.uploadOneSuccess,
        manySuccess: form.dataset.uploadManySuccess,
        failed: form.dataset.uploadFailed,
    };

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

        setFlash(imageFiles.length > 1 ? uploadMessages.manyWorking : uploadMessages.oneWorking, "working");

        try {
            for (const file of imageFiles) {
                const imageUrl = await uploadImage(file, uploadUrl, csrfToken, uploadMessages.failed);
                insertMarkdownImage(textarea, imageUrl);
            }
            const successMessage = imageFiles.length > 1 ? uploadMessages.manySuccess : uploadMessages.oneSuccess;
            setFlash(successMessage, "success", SUCCESS_FLASH_DELAY_MS);
        } catch (error) {
            setFlash(error.message || uploadMessages.failed, "error");
        }
    };

    textarea.addEventListener("paste", (event) => {
        const files = Array.from(event.clipboardData?.items || [])
            .filter((item) => item.kind === "file")
            .map((item) => item.getAsFile())
            .filter((file) => file && file.type.startsWith("image/"));

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
