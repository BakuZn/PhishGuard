
console.log("PhishGuard content script loaded");

let lastUrl = location.href;

function showWarningBanner(isPhishing, confidence, message) {
    // 1. Remove any existing banner if the user clicks between emails quickly
    const existingBanner = document.getElementById("phishguard-banner");
    if (existingBanner) existingBanner.remove();

    // 2. Create the new banner element
    const banner = document.createElement("div");
    banner.id = "phishguard-banner";
    
    // 3. Style it dynamically based on the prediction
    banner.style.padding = "10px 15px";
    banner.style.margin = "10px 0";
    banner.style.borderRadius = "5px";
    banner.style.fontWeight = "bold";
    banner.style.color = "white";
    banner.style.zIndex = "9999";
    banner.style.textAlign = "center";
    
    if (isPhishing) {
        banner.style.backgroundColor = "#d93025"; // Google Red
        banner.innerHTML = `⚠️ <b>WARNING:</b> ${message} (Confidence: ${(confidence * 100).toFixed(1)}%)`;
    } else {
        banner.style.backgroundColor = "#188038"; // Google Green
        banner.innerHTML = `✅ <b>SAFE:</b> ${message} (Confidence: ${(confidence * 100).toFixed(1)}%)`;
    }

    // 4. Inject it into the Gmail UI (at the top of the email container)
    // 'h2.hP' is the subject line container. We'll insert our banner right before it.
    const subjectLine = document.querySelector('h2.hP');
    if (subjectLine && subjectLine.parentElement) {
        subjectLine.parentElement.insertBefore(banner, subjectLine);
    }
}

async function sendToBackend(subject, body) {
    try {
        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                subject: subject,
                body: body
            })
        });

        const data = await response.json();

        console.log("🧠 Prediction:", data.is_phishing ? "Phishing" : "Safe");
        console.log("📊 Confidence:", data.confidence);
        console.log("💬 Message:", data.message);

        // Show the UI Banner
        showWarningBanner(data.is_phishing, data.confidence, data.message);

    } catch (error) {
        console.error("❌ Backend error:", error);
    }
}

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

        sendToBackend(subject, cleanBody);

    } else {
        console.log("Elements not found yet, Gmail might still be loading...");
    }
}

const observer = new MutationObserver(() => {
    if (location.href !== lastUrl) {
        lastUrl = location.href;

        // Extracts if looking at an email in any folder (inbox, spam, trash, etc.)
        const isEmailView = location.hash.match(/#(inbox|spam|all|trash|sent|important|starred)\//) && location.hash.length > 10;
        
        if (isEmailView) {
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
