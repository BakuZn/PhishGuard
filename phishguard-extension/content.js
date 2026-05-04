
console.log("PhishGuard content script loaded");

let lastUrl = location.href;

//extract email data
function extractEmailData() {

    const subjectElement = document.querySelector('h2.hP');
    const bodyElement = document.querySelector('div.a3s.aiL');

    if (subjectElement && bodyElement) {
        const subject = subjectElement.innerText.trim();
        const body = bodyElement.innerText.trim();
        const cleanBody = body.replace(/\s+/g, ' ').trim();

        console.log("📨 Extracted Subject:", subject);
        console.log("📝 Body Preview:", cleanBody.substring(0, 120) + "...");
        console.log("📏 Body Length:", cleanBody.length);


    } else {
        console.log("Elements not found yet, Gmail might still be loading...");
    }
}

const observer = new MutationObserver(() => {
    if (location.href !== lastUrl) {
        lastUrl = location.href;

        // Only extracts if looking at an email (hash contains /inbox/)
        if (location.hash.includes("#inbox/") && location.hash.length > 10) {
            console.log("New email opened:", location.href);
            // Wait 1.5 seconds
            setTimeout(extractEmailData, 1500);
        }
    }
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
