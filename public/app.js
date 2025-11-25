// let isVerified = false;
// let showModal = false;
// let captchaProgress = 0; // Track how many CAPTCHAs have been completed
// const TOTAL_CAPTCHAS = 3; // Require 3 CAPTCHAs to be solved

// // Shuffle the CAPTCHA types to create a random order
// function shuffleArray(array) {
//     const shuffled = [...array];
//     for (let i = shuffled.length - 1; i > 0; i--) {
//         const j = Math.floor(Math.random() * (i + 1));
//         [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
//     }
//     return shuffled;
// }

// // Create a random order of all three CAPTCHA types
// let CAPTCHA_ORDER = shuffleArray(['candy', 'maze', 'slider']);

// const verifyBtn = document.getElementById('verifyBtn');
// const nextBtn = document.getElementById('nextBtn');
// const verificationModal = document.getElementById('verificationModal');
// const closeBtn = document.getElementById('closeBtn');
// const progressContainer = document.getElementById('progressContainer');
// const progressBar = document.getElementById('progressBar');
// const progressText = document.getElementById('progressText');

// function getCaptchaMethod() {
//     // Get the CAPTCHA type based on current progress
//     const method = CAPTCHA_ORDER[captchaProgress];
//     console.log(`CAPTCHA ${captchaProgress + 1}: ${method} (Order: ${CAPTCHA_ORDER.join(' → ')})`);
//     return method;
// }

// function updateProgress() {
//     // Update progress bar
//     const progressPercentage = (captchaProgress / TOTAL_CAPTCHAS) * 100;
//     progressBar.style.width = progressPercentage + '%';
    
//     // Show which CAPTCHAs have been completed and which is next
//     let completedText = '';
//     if (captchaProgress > 0) {
//         const completed = CAPTCHA_ORDER.slice(0, captchaProgress).map(type => 
//             type.charAt(0).toUpperCase() + type.slice(1)
//         ).join(', ');
//         completedText = ` - Completed: ${completed}`;
//     }
    
//     progressText.textContent = `CAPTCHA ${captchaProgress} of ${TOTAL_CAPTCHAS} completed${completedText}`;
    
//     if (progressContainer) {
//         progressContainer.style.display = 'block';
//     }
// }

// document.addEventListener('DOMContentLoaded', function () {
//     // Hide progress container initially
//     if (progressContainer) {
//         progressContainer.style.display = 'none';
//     }

//     const params = new URLSearchParams(window.location.search);
//     const verifiedParam = params.get('verified');
//     const progressParam = params.get('progress');
//     const orderParam = params.get('order'); // Get the CAPTCHA order from URL
    
//     // If there's an order in the URL, use it (for continuing after page reload)
//     if (orderParam) {
//         CAPTCHA_ORDER = orderParam.split(',');
//         console.log('Resumed CAPTCHA order from URL:', CAPTCHA_ORDER);
//     }
    
//     if (verifiedParam === '1') {
//         // Final verification complete
//         isVerified = true;
//         captchaProgress = TOTAL_CAPTCHAS;

//         verifyBtn.textContent = 'Verified ✓';
//         verifyBtn.disabled = true;
//         verifyBtn.classList.add('verified');

//         nextBtn.classList.remove('disabled');
//         nextBtn.disabled = false;
        
//         updateProgress();
//     } else if (progressParam) {
//         // Continuing from a previous CAPTCHA
//         captchaProgress = parseInt(progressParam) || 0;
//         updateProgress();
        
//         // Automatically start next CAPTCHA
//         if (captchaProgress < TOTAL_CAPTCHAS) {
//             setTimeout(() => {
//                 handleStartVerification();
//             }, 500);
//         }
//     }

//     verifyBtn.addEventListener('click', handleStartVerification);
//     nextBtn.addEventListener('click', handleNextPage);
//     if (closeBtn) {
//         closeBtn.addEventListener('click', closeModal);
//     }

//     if (typeof initVerificationGame === 'function') {
//         initVerificationGame(onVerificationSuccess);
//     }
// });

// function handleStartVerification() {
//     if (isVerified) return;

//     const method = getCaptchaMethod();
//     const orderParam = CAPTCHA_ORDER.join(','); // Pass the order as a comma-separated string
    
//     console.log(`Starting CAPTCHA ${captchaProgress + 1} of ${TOTAL_CAPTCHAS}: ${method}`);

//     if (method === 'candy') {
//         showModal = true;
//         verificationModal.style.display = 'flex';

//         if (typeof resetVerificationGame === 'function') {
//             resetVerificationGame();
//         }
//     } else if (method === 'maze') {
//         window.location.href = `captcha-updated.html?mode=maze&progress=${captchaProgress}&order=${orderParam}`;
//     } else {
//         window.location.href = `captcha-updated.html?mode=slider&progress=${captchaProgress}&order=${orderParam}`;
//     }
// }

// function closeModal() {
//     // Don't allow closing modal until all CAPTCHAs are done
//     if (captchaProgress >= TOTAL_CAPTCHAS) {
//         showModal = false;
//         verificationModal.style.display = 'none';
//     } else {
//         alert(`Please complete all ${TOTAL_CAPTCHAS} CAPTCHAs to verify you're human. (${captchaProgress}/${TOTAL_CAPTCHAS} completed)`);
//     }
// }

// function onVerificationSuccess() {
//     const completedType = CAPTCHA_ORDER[captchaProgress];
//     const completedName = completedType.charAt(0).toUpperCase() + completedType.slice(1);
    
//     // Increment progress
//     captchaProgress++;
//     updateProgress();
    
//     console.log(`CAPTCHA ${captchaProgress} of ${TOTAL_CAPTCHAS} completed: ${completedName}`);

//     if (captchaProgress >= TOTAL_CAPTCHAS) {
//         // All CAPTCHAs completed!
//         closeModal();
//         isVerified = true;

//         verifyBtn.textContent = 'Verified ✓';
//         verifyBtn.disabled = true;
//         verifyBtn.classList.add('verified');

//         nextBtn.classList.remove('disabled');
//         nextBtn.disabled = false;

//         const allCompleted = CAPTCHA_ORDER.map(type => 
//             type.charAt(0).toUpperCase() + type.slice(1)
//         ).join(' → ');
        
//         alert(`🎉 Verification complete!\n\nYou successfully completed all 3 CAPTCHAs:\n${allCompleted}\n\nYou have been verified as a human user.`);
//     } else {
//         // More CAPTCHAs to go
//         const nextType = CAPTCHA_ORDER[captchaProgress];
//         const nextName = nextType.charAt(0).toUpperCase() + nextType.slice(1);
        
//         closeModal();
//         alert(`✓ ${completedName} CAPTCHA completed!\n\nProgress: ${captchaProgress}/${TOTAL_CAPTCHAS}\n\nNext: ${nextName} CAPTCHA`);
        
//         // Start next CAPTCHA after a short delay
//         setTimeout(() => {
//             handleStartVerification();
//         }, 1000);
//     }
// }

// function handleNextPage() {
//     if (isVerified) {
//         alert('Verification successful! Proceeding to next page...');
//         // You can redirect to your actual next page here
//         window.location.href = 'exam.html';
//     } else {
//         alert('Please complete all CAPTCHAs before proceeding.');
//     }
// }
let isVerified = false;
let showModal = false;
let captchaProgress = 0; // Track how many CAPTCHAs have been completed
const TOTAL_CAPTCHAS = 3; // Require 3 CAPTCHAs to be solved

// Shuffle the CAPTCHA types to create a random order
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// Create a random order of all three CAPTCHA types
let CAPTCHA_ORDER = shuffleArray(['candy', 'maze', 'slider']);

const verifyBtn = document.getElementById('verifyBtn');
const nextBtn = document.getElementById('nextBtn');
const verificationModal = document.getElementById('verificationModal');
const closeBtn = document.getElementById('closeBtn');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');

function getCaptchaMethod() {
    // Get the CAPTCHA type based on current progress
    const method = CAPTCHA_ORDER[captchaProgress];
    console.log(`CAPTCHA ${captchaProgress + 1}: ${method} (Order: ${CAPTCHA_ORDER.join(' → ')})`);
    return method;
}

function updateProgress() {
    // Update progress bar
    const progressPercentage = (captchaProgress / TOTAL_CAPTCHAS) * 100;
    progressBar.style.width = progressPercentage + '%';
    
    // Show which CAPTCHAs have been completed and which is next
    let completedText = '';
    if (captchaProgress > 0) {
        const completed = CAPTCHA_ORDER.slice(0, captchaProgress).map(type => 
            type.charAt(0).toUpperCase() + type.slice(1)
        ).join(', ');
        completedText = ` - Completed: ${completed}`;
    }
    
    progressText.textContent = `CAPTCHA ${captchaProgress} of ${TOTAL_CAPTCHAS} completed${completedText}`;
    
    if (progressContainer) {
        progressContainer.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Hide progress container initially
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }

    const params = new URLSearchParams(window.location.search);
    const verifiedParam = params.get('verified');
    const progressParam = params.get('progress');
    const orderParam = params.get('order'); // Get the CAPTCHA order from URL
    
    // If there's an order in the URL, use it (for continuing after page reload)
    if (orderParam) {
        CAPTCHA_ORDER = orderParam.split(',');
        console.log('Resumed CAPTCHA order from URL:', CAPTCHA_ORDER);
    }
    
    if (verifiedParam === '1') {
        // Final verification complete
        isVerified = true;
        captchaProgress = TOTAL_CAPTCHAS;

        verifyBtn.textContent = 'Verified ✓';
        verifyBtn.disabled = true;
        verifyBtn.classList.add('verified');

        nextBtn.classList.remove('disabled');
        nextBtn.disabled = false;
        
        updateProgress();
    } else if (progressParam) {
        // Continuing from a previous CAPTCHA
        captchaProgress = parseInt(progressParam) || 0;
        updateProgress();
        
        // Automatically start next CAPTCHA
        if (captchaProgress < TOTAL_CAPTCHAS) {
            setTimeout(() => {
                handleStartVerification();
            }, 500);
        }
    }

    verifyBtn.addEventListener('click', handleStartVerification);
    nextBtn.addEventListener('click', handleNextPage);
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    if (typeof initVerificationGame === 'function') {
        // Protect the verification callback with bot detection
        const protectedCallback = window.BotDetectionIntegration 
            ? window.BotDetectionIntegration.createProtectedVerificationCallback(onVerificationSuccess)
            : onVerificationSuccess;
        
        initVerificationGame(protectedCallback);
    }
});

function handleStartVerification() {
    if (isVerified) return;

    const method = getCaptchaMethod();
    const orderParam = CAPTCHA_ORDER.join(','); // Pass the order as a comma-separated string
    
    console.log(`Starting CAPTCHA ${captchaProgress + 1} of ${TOTAL_CAPTCHAS}: ${method}`);

    if (method === 'candy') {
        showModal = true;
        verificationModal.style.display = 'flex';

        if (typeof resetVerificationGame === 'function') {
            resetVerificationGame();
        }
    } else if (method === 'maze') {
        window.location.href = `captcha-updated.html?mode=maze&progress=${captchaProgress}&order=${orderParam}`;
    } else {
        window.location.href = `captcha-updated.html?mode=slider&progress=${captchaProgress}&order=${orderParam}`;
    }
}

function closeModal() {
    // Don't allow closing modal until all CAPTCHAs are done
    if (captchaProgress >= TOTAL_CAPTCHAS) {
        showModal = false;
        verificationModal.style.display = 'none';
    } else {
        alert(`Please complete all ${TOTAL_CAPTCHAS} CAPTCHAs to verify you're human. (${captchaProgress}/${TOTAL_CAPTCHAS} completed)`);
    }
}

function onVerificationSuccess() {
    const completedType = CAPTCHA_ORDER[captchaProgress];
    const completedName = completedType.charAt(0).toUpperCase() + completedType.slice(1);
    
    // Increment progress
    captchaProgress++;
    updateProgress();
    
    console.log(`CAPTCHA ${captchaProgress} of ${TOTAL_CAPTCHAS} completed: ${completedName}`);

    if (captchaProgress >= TOTAL_CAPTCHAS) {
        // All CAPTCHAs completed!
        closeModal();
        isVerified = true;

        verifyBtn.textContent = 'Verified ✓';
        verifyBtn.disabled = true;
        verifyBtn.classList.add('verified');

        nextBtn.classList.remove('disabled');
        nextBtn.disabled = false;

        const allCompleted = CAPTCHA_ORDER.map(type => 
            type.charAt(0).toUpperCase() + type.slice(1)
        ).join(' → ');
        
        alert(`🎉 Verification complete!\n\nYou successfully completed all 3 CAPTCHAs:\n${allCompleted}\n\nYou have been verified as a human user.`);
    } else {
        // More CAPTCHAs to go
        const nextType = CAPTCHA_ORDER[captchaProgress];
        const nextName = nextType.charAt(0).toUpperCase() + nextType.slice(1);
        
        closeModal();
        alert(`✓ ${completedName} CAPTCHA completed!\n\nProgress: ${captchaProgress}/${TOTAL_CAPTCHAS}\n\nNext: ${nextName} CAPTCHA`);
        
        // Start next CAPTCHA after a short delay
        setTimeout(() => {
            handleStartVerification();
        }, 1000);
    }
}

function handleNextPage() {
    if (isVerified) {
        alert('Verification successful! Proceeding to next page...');
        // You can redirect to your actual next page here
        window.location.href = 'exam.html';
    } else {
        alert('Please complete all CAPTCHAs before proceeding.');
    }
}