
let isVerified = false;
let showModal = false;


const CAPTCHA_METHODS = ['candy', 'maze', 'slider'];


const verifyBtn = document.getElementById('verifyBtn');
const nextBtn = document.getElementById('nextBtn');
const verificationModal = document.getElementById('verificationModal');
const closeBtn = document.getElementById('closeBtn');


function pickCaptchaMethod() {
    const idx = Math.floor(Math.random() * CAPTCHA_METHODS.length);
    const method = CAPTCHA_METHODS[idx];
    console.log('Selected CAPTCHA method:', method);
    return method;
}

document.addEventListener('DOMContentLoaded', function () {

    const params = new URLSearchParams(window.location.search);
    if (params.get('verified') === '1') {
        isVerified = true;

        verifyBtn.textContent = 'Verified';
        verifyBtn.disabled = true;

        nextBtn.classList.remove('disabled');
        nextBtn.disabled = false;
    }


    verifyBtn.addEventListener('click', handleStartVerification);
    nextBtn.addEventListener('click', handleNextPage);
    closeBtn.addEventListener('click', closeModal);


    if (typeof initVerificationGame === 'function') {
        initVerificationGame(onVerificationSuccess);
    }
});

function handleStartVerification() {
    if (isVerified) return;

    const method = pickCaptchaMethod();

    if (method === 'candy') {
        showModal = true;
        verificationModal.style.display = 'flex';

        if (typeof resetVerificationGame === 'function') {
            resetVerificationGame();
        }
    } else if (method === 'maze') {
        window.location.href = 'captcha-updated.html?mode=maze';
    } else {
        window.location.href = 'captcha-updated.html?mode=slider';
    }
}


function closeModal() {
    showModal = false;
    verificationModal.style.display = 'none';
}

function onVerificationSuccess() {
    closeModal();
    isVerified = true;

    verifyBtn.textContent = 'Verified';
    verifyBtn.disabled = true;

    nextBtn.classList.remove('disabled');
    nextBtn.disabled = false;

    alert('Verification complete! You have been identified as a human user.');
}

function handleNextPage() {
    if (isVerified) {
        alert('Next page!');
    }
}
