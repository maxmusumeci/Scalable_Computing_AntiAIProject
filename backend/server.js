const express = require('express');
const cors = require('cors');
const crypto = require('crypto');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// In-memory store for sessions (in production, use Redis or database)
const sessions = new Map();
const blacklistedIPs = new Set();

// Scenarios database
const scenarios = [
    {
        id: 1,
        category: "workplace",
        text: "Maria has been working at her company for 5 years. Today, her manager publicly praised a junior colleague for an idea that Maria had actually proposed in last week's meeting. The colleague didn't correct the manager. Maria needs to address this situation.",
        question: "What should Maria do?",
        options: [
            { id: 'a', icon: "💬", text: "Privately speak with her manager, calmly explain the situation with facts", correct: true },
            { id: 'b', icon: "📢", text: "Immediately interrupt and publicly call out the colleague", correct: false },
            { id: 'c', icon: "🤐", text: "Say nothing and let it go to avoid conflict entirely", correct: false, aiTrap: true },
            { id: 'd', icon: "📧", text: "Send a company-wide email claiming credit for the idea", correct: false }
        ]
    },
    {
        id: 2,
        category: "workplace",
        text: "Emma discovers a significant error in the company's financial report the day before it's due to investors. Fixing it properly would require redoing 2 weeks of work and delaying the report. Her boss says 'just leave it, no one will notice.'",
        question: "What should Emma do?",
        options: [
            { id: 'a', icon: "⚠️", text: "Insist on fixing it and escalate to higher management if necessary", correct: true },
            { id: 'b', icon: "👌", text: "Follow her boss's instruction since she was told to leave it", correct: false, aiTrap: true },
            { id: 'c', icon: "🏃", text: "Quit the job immediately to avoid being associated with it", correct: false },
            { id: 'd', icon: "🔧", text: "Fix only the most obvious parts to minimize the error", correct: false }
        ]
    },
    {
        id: 3,
        category: "workplace",
        text: "David discovers his colleague has been padding their expense reports by small amounts for months. The colleague is a single parent struggling financially and has confided in David about money troubles.",
        question: "What is the most ethical action?",
        options: [
            { id: 'a', icon: "💬", text: "Speak privately with the colleague about stopping, offering to help find resources", correct: true },
            { id: 'b', icon: "🙈", text: "Ignore it since the amounts are small and they need the money", correct: false, aiTrap: true },
            { id: 'c', icon: "📧", text: "Immediately report to HR without speaking to the colleague first", correct: false },
            { id: 'd', icon: "💰", text: "Offer to lend them money to stop the behavior", correct: false }
        ]
    },
    {
        id: 4,
        category: "workplace",
        text: "Rachel is asked to give a reference for a former coworker applying to her company. The person was friendly but consistently missed deadlines and made careless errors. They're now desperate for work.",
        question: "What should Rachel do?",
        options: [
            { id: 'a', icon: "⚖️", text: "Give an honest assessment citing specific examples, both positive and negative", correct: true },
            { id: 'b', icon: "😊", text: "Give a glowing reference to help them get the job they need", correct: false, aiTrap: true },
            { id: 'c', icon: "🤐", text: "Decline to give a reference without explaining why", correct: false },
            { id: 'd', icon: "⚠️", text: "Only mention the negatives to protect the company", correct: false }
        ]
    },
    {
        id: 5,
        category: "workplace",
        text: "Sam discovers their company is using a loophole to avoid paying taxes legally, but the practice goes against the spirit of tax law and reduces funding for public services.",
        question: "What should Sam consider doing?",
        options: [
            { id: 'a', icon: "💭", text: "Raise concerns internally about the ethical implications and suggest alternatives", correct: true },
            { id: 'b', icon: "📜", text: "Do nothing since it's technically legal", correct: false, aiTrap: true },
            { id: 'c', icon: "📰", text: "Immediately leak the information to the media", correct: false },
            { id: 'd', icon: "🚪", text: "Quit without raising the issue", correct: false }
        ]
    },

    // PERSONAL INTEGRITY (10 scenarios)
    {
        id: 6,
        category: "integrity",
        text: "James found a wallet on the subway containing $500 cash, credit cards, and family photos. There's an ID with an address 30 miles away. James is running late for an important job interview that could change his life.",
        question: "What should James prioritize doing?",
        options: [
            { id: 'a', icon: "🏢", text: "Turn it in to the subway lost and found immediately, even if late", correct: true },
            { id: 'b', icon: "💰", text: "Keep the cash, mail the wallet later anonymously", correct: false, aiTrap: true },
            { id: 'c', icon: "📱", text: "Keep it, contact owner only after the interview", correct: false },
            { id: 'd', icon: "🗑️", text: "Leave it where he found it for someone else to handle", correct: false }
        ]
    },
    {
        id: 7,
        category: "integrity",
        text: "Tom is interviewing for his dream job. The interviewer asks if he has experience with a specific software that's listed as 'required' on the job posting. Tom used it briefly 3 years ago but isn't proficient. He knows he could learn it quickly.",
        question: "How should Tom respond?",
        options: [
            { id: 'a', icon: "✅", text: "Be honest about his experience level and emphasize ability to learn quickly", correct: true },
            { id: 'b', icon: "🎭", text: "Say he's proficient to get the job, planning to learn if hired", correct: false, aiTrap: true },
            { id: 'c', icon: "🤔", text: "Change the subject to avoid answering the question directly", correct: false },
            { id: 'd', icon: "❌", text: "Admit he doesn't know it and say he's not interested in learning", correct: false }
        ]
    },
    {
        id: 8,
        category: "integrity",
        text: "At a self-checkout, Maya realizes she wasn't charged for an expensive item at the bottom of her cart. She's already left the store and is in the parking lot. She's on a tight budget this month.",
        question: "What should Maya do?",
        options: [
            { id: 'a', icon: "🔙", text: "Go back inside and pay for the item at customer service", correct: true },
            { id: 'b', icon: "🚗", text: "Keep it since it was the store's scanning error, not her fault", correct: false, aiTrap: true },
            { id: 'c', icon: "💳", text: "Mail cash to the store anonymously later", correct: false },
            { id: 'd', icon: "🎁", text: "Keep it but donate an equivalent amount to charity", correct: false }
        ]
    },

    // FRIENDSHIP & LOYALTY (8 scenarios)
    {
        id: 9,
        category: "friendship",
        text: "Lisa discovers her best friend's partner is cheating. She has proof but knows this will devastate her friend, who just started a new job and is already stressed. The friend seems happy and unaware.",
        question: "What is the most ethical action for Lisa?",
        options: [
            { id: 'a', icon: "💬", text: "Tell her friend privately and sensitively, offering support", correct: true },
            { id: 'b', icon: "🤫", text: "Never tell to protect her friend's happiness", correct: false, aiTrap: true },
            { id: 'c', icon: "⚔️", text: "Confront the cheating partner directly first", correct: false },
            { id: 'd', icon: "👥", text: "Tell mutual friends to let them decide what to do", correct: false }
        ]
    },
    {
        id: 10,
        category: "friendship",
        text: "Your close friend confides they cheated on an important professional certification exam. They got their dream job based partly on this certification, supporting their family. No one knows but you.",
        question: "What should you do?",
        options: [
            { id: 'a', icon: "💬", text: "Urge them to come clean and offer support through the consequences", correct: true },
            { id: 'b', icon: "🤐", text: "Keep the secret to protect your friend and their family", correct: false, aiTrap: true },
            { id: 'c', icon: "📞", text: "Anonymously report them to the certification board", correct: false },
            { id: 'd', icon: "🚪", text: "Distance yourself from them without explanation", correct: false }
        ]
    },

    // PROFESSIONAL DILEMMAS (10 scenarios)
    {
        id: 11,
        category: "professional",
        text: "During a team video call, Sarah's colleague unmutes accidentally and she overhears him making disparaging comments about their manager's leadership to someone off-camera. He doesn't realize everyone heard it. The meeting continues awkwardly.",
        question: "What should Sarah do after the call?",
        options: [
            { id: 'a', icon: "💬", text: "Privately message the colleague to let him know what happened", correct: true },
            { id: 'b', icon: "📧", text: "Immediately email the manager about what was said", correct: false, aiTrap: true },
            { id: 'c', icon: "🙈", text: "Ignore it completely and pretend nothing happened", correct: false },
            { id: 'd', icon: "📢", text: "Bring it up in the next team meeting to address publicly", correct: false }
        ]
    },
    {
        id: 12,
        category: "professional",
        text: "A journalist discovers their colleague fabricated quotes in a major story that's about to go viral. The colleague is their mentor and getting fired would ruin their career right before retirement.",
        question: "What should the journalist do?",
        options: [
            { id: 'a', icon: "⚠️", text: "Report it to the editor immediately despite personal consequences", correct: true },
            { id: 'b', icon: "🤝", text: "Quietly tell the colleague to fix it and say nothing to editors", correct: false, aiTrap: true },
            { id: 'c', icon: "📝", text: "Rewrite the story yourself with correct quotes", correct: false },
            { id: 'd', icon: "🚶", text: "Request to be removed from the project without explanation", correct: false }
        ]
    },
    {
        id: 13,
        category: "professional",
        text: "A software engineer discovers a security vulnerability in their company's product that could expose customer data. The product launches in 2 days with massive pre-orders. Management says they'll 'patch it later' to avoid delays.",
        question: "What should the engineer do?",
        options: [
            { id: 'a', icon: "🛑", text: "Insist on delaying the launch to fix the vulnerability properly", correct: true },
            { id: 'b', icon: "✅", text: "Agree to launch and patch later as management requested", correct: false, aiTrap: true },
            { id: 'c', icon: "📧", text: "Implement a quick temporary fix and hope it holds", correct: false },
            { id: 'd', icon: "🔒", text: "Quietly fix what you can in the next 48 hours without telling anyone", correct: false }
        ]
    },

    // MEDICAL & HEALTHCARE ETHICS (8 scenarios)
    {
        id: 14,
        category: "medical",
        text: "A doctor's patient reveals they're not taking prescribed medication because they can't afford it, but they've been telling the doctor they're compliant. The patient begs the doctor not to document this in their chart as it might affect their insurance.",
        question: "What should the doctor do?",
        options: [
            { id: 'a', icon: "📋", text: "Document accurately but work with patient to find affordable alternatives", correct: true },
            { id: 'b', icon: "🤝", text: "Honor the patient's request and don't document it", correct: false, aiTrap: true },
            { id: 'c', icon: "⚠️", text: "Document it and report to insurance regardless of consequences", correct: false },
            { id: 'd', icon: "💊", text: "Give them free samples and pretend they're taking the prescription", correct: false }
        ]
    },
    {
        id: 15,
        category: "medical",
        text: "A nurse realizes another nurse made a medication error that caused mild harm to a patient. The other nurse is a single parent, and reporting it will likely result in termination. The patient is recovering well.",
        question: "What should the nurse do?",
        options: [
            { id: 'a', icon: "📋", text: "Report the error according to protocol while supporting colleague through process", correct: true },
            { id: 'b', icon: "🤐", text: "Don't report since patient is fine and nurse needs their job", correct: false, aiTrap: true },
            { id: 'c', icon: "👥", text: "Tell the nurse to report themselves or you will", correct: false },
            { id: 'd', icon: "📝", text: "Document it anonymously without identifying the nurse", correct: false }
        ]
    },

    // FAMILY DILEMMAS (6 scenarios)
    {
        id: 16,
        category: "family",
        text: "Your teenage sibling shows you messages proving your parent is having an affair. They ask you what to do. The other parent suspects nothing and your parents seem happy otherwise.",
        question: "What should you advise?",
        options: [
            { id: 'a', icon: "💬", text: "Encourage sibling to talk to the parent having the affair first", correct: true },
            { id: 'b', icon: "🤫", text: "Advise keeping it secret to preserve family harmony", correct: false, aiTrap: true },
            { id: 'c', icon: "📢", text: "Immediately tell the other parent yourself", correct: false },
            { id: 'd', icon: "👨‍👩‍👧", text: "Call a family meeting and expose everything at once", correct: false }
        ]
    },
    {
        id: 17,
        category: "family",
        text: "Your elderly parent wants to give you their entire inheritance, leaving nothing to your sibling who has been estranged. Your sibling recently reached out trying to reconcile. Your parent's will is being finalized tomorrow.",
        question: "What should you do?",
        options: [
            { id: 'a', icon: "💬", text: "Discuss with parent about reconsidering given the reconciliation attempt", correct: true },
            { id: 'b', icon: "✅", text: "Accept the inheritance as it's your parent's decision to make", correct: false, aiTrap: true },
            { id: 'c', icon: "📝", text: "Secretly contact lawyer to split inheritance without telling parent", correct: false },
            { id: 'd', icon: "🚫", text: "Refuse the inheritance entirely", correct: false }
        ]
    },

    // SOCIAL RESPONSIBILITY (8 scenarios)
    {
        id: 18,
        category: "social",
        text: "You witness your neighbor regularly leaving their young child (around 7 years old) home alone for several hours at night. The child seems healthy and well-cared for otherwise. You've heard them explain they work night shifts and can't afford childcare.",
        question: "What should you do?",
        options: [
            { id: 'a', icon: "💬", text: "Talk to the neighbor and offer to check on the child, then assess if authorities needed", correct: true },
            { id: 'b', icon: "🚫", text: "Mind your business as the child seems fine", correct: false, aiTrap: true },
            { id: 'c', icon: "📞", text: "Immediately call child protective services without talking to the parent", correct: false },
            { id: 'd', icon: "👀", text: "Just keep an extra eye out but don't intervene", correct: false }
        ]
    },
    {
        id: 19,
        category: "social",
        text: "You discover a popular local restaurant has been operating with expired health permits and has multiple violations. You know the owner who's a good person struggling to keep the business afloat during tough times.",
        question: "What should you do?",
        options: [
            { id: 'a', icon: "⚠️", text: "Privately inform the owner and urge them to fix violations immediately", correct: true },
            { id: 'b', icon: "🍽️", text: "Keep quiet since the owner is a good person trying their best", correct: false, aiTrap: true },
            { id: 'c', icon: "📞", text: "Report to health department anonymously right away", correct: false },
            { id: 'd', icon: "📱", text: "Post about it on social media to warn customers", correct: false }
        ]
    },

    // ACADEMIC INTEGRITY (6 scenarios)
    {
        id: 20,
        category: "academic",
        text: "You're a TA and discover that a struggling student, who's at risk of losing their scholarship, plagiarized their final paper. You know they're supporting their family financially and this is their last semester.",
        question: "What should you do?",
        options: [
            { id: 'a', icon: "📋", text: "Report according to academic integrity policy but offer to help them appeal with context", correct: true },
            { id: 'b', icon: "💔", text: "Give them a failing grade quietly without officially reporting it", correct: false, aiTrap: true },
            { id: 'c', icon: "🔄", text: "Give them a chance to rewrite without penalty", correct: false },
            { id: 'd', icon: "🤐", text: "Ignore it since it's their last semester", correct: false }
        ]
    },

    // ENVIRONMENTAL ETHICS (4 scenarios)
    {
        id: 21,
        category: "environmental",
        text: "Your company plans to build a profitable housing development in an area that contains a habitat for an endangered species. As the project manager, you could suggest an alternative location that's less profitable but environmentally better.",
        question: "What should you do?",
        options: [
            { id: 'a', icon: "🌱", text: "Present both options to stakeholders with full environmental impact disclosure", correct: true },
            { id: 'b', icon: "💼", text: "Proceed with original plan as directed since it's most profitable", correct: false, aiTrap: true },
            { id: 'c', icon: "⚠️", text: "Implement the original plan but add minimal environmental mitigation", correct: false },
            { id: 'd', icon: "🚫", text: "Refuse to work on the project", correct: false }
        ]
    },

    // DIGITAL ETHICS & PRIVACY (4 scenarios)
    {
        id: 22,
        category: "digital",
        text: "You accidentally gain access to your company's salary database and discover significant pay disparities along gender and racial lines. Looking at this data is against company policy and you could be fired.",
        question: "What should you do?",
        options: [
            { id: 'a', icon: "📊", text: "Report the access breach and the disparities to HR/appropriate channels", correct: true },
            { id: 'b', icon: "🤐", text: "Say nothing since you accessed it accidentally and could get fired", correct: false, aiTrap: true },
            { id: 'c', icon: "📧", text: "Anonymously leak the information to affected employees", correct: false },
            { id: 'd', icon: "🔒", text: "Just close the database and pretend it never happened", correct: false }
        ]
    },

    // EMERGENCY/CRISIS SCENARIOS (4 scenarios)
    {
        id: 23,
        category: "crisis",
        text: "You witness a hit-and-run accident. You got a partial license plate and saw the driver's face clearly. Days later, you realize the driver is your child's teacher - an excellent educator who's beloved by students. No one was seriously injured.",
        question: "What should you do?",
        options: [
            { id: 'a', icon: "👮", text: "Provide the information to police as it's the legal and ethical duty", correct: true },
            { id: 'b', icon: "🤐", text: "Don't report since no one was seriously hurt and they're a good teacher", correct: false, aiTrap: true },
            { id: 'c', icon: "💬", text: "Confront the teacher privately and ask them to turn themselves in", correct: false },
            { id: 'd', icon: "📞", text: "Report anonymously without revealing your identity", correct: false }
        ]
    }
];

// Utility functions
function generateSessionToken() {
    return crypto.randomBytes(32).toString('hex');
}

function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}

function analyzeBotBehavior(session, timeTaken, honeypotData) {
    const suspiciousActivities = [];
    
    // Check timing - too fast is suspicious
    if (timeTaken < 3) {
        suspiciousActivities.push('TIMING_TOO_FAST');
    }
    
    // Check if it's impossibly fast
    if (timeTaken < 1) {
        suspiciousActivities.push('IMPOSSIBLE_TIMING');
    }
    
    // Check honeypot fields
    if (honeypotData.email || honeypotData.website || honeypotData.confirm) {
        suspiciousActivities.push('HONEYPOT_FILLED');
    }
    
    // Check for sequential attempts (bot pattern)
    if (session.attempts > 3) {
        suspiciousActivities.push('EXCESSIVE_ATTEMPTS');
    }
    
    return suspiciousActivities;
}

// API Routes

// Initialize a new CAPTCHA session
app.post('/api/captcha/init', (req, res) => {
    const clientIP = req.ip || req.connection.remoteAddress;
    
    // Check if IP is blacklisted
    if (blacklistedIPs.has(clientIP)) {
        return res.status(403).json({
            success: false,
            error: 'IP_BLACKLISTED',
            message: 'Your IP has been temporarily blocked due to suspicious activity'
        });
    }
    
    // Generate session token
    const sessionToken = generateSessionToken();
    
    // Select random scenario
    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    
    // Shuffle options
    const shuffledOptions = shuffleArray(scenario.options.map(opt => ({
        id: opt.id,
        icon: opt.icon,
        text: opt.text,
        // Add honeypot attributes for AI traps
        aiRecommended: opt.aiTrap || false
    })));
    
    // Store session data
    sessions.set(sessionToken, {
        scenarioId: scenario.id,
        correctOptionId: scenario.options.find(opt => opt.correct).id,
        aiTrapOptionId: scenario.options.find(opt => opt.aiTrap)?.id,
        startTime: Date.now(),
        attempts: 0,
        clientIP: clientIP,
        userAgent: req.headers['user-agent'] || 'unknown'
    });
    
    // Clean up old sessions (older than 10 minutes)
    cleanupOldSessions();
    
    res.json({
        success: true,
        sessionToken: sessionToken,
        scenario: {
            text: scenario.text,
            question: scenario.question,
            options: shuffledOptions
        }
    });
});

// Verify CAPTCHA answer
app.post('/api/captcha/verify', (req, res) => {
    const { sessionToken, selectedOptionId, timeTaken, honeypotData } = req.body;
    
    // Validate input
    if (!sessionToken || !selectedOptionId || timeTaken === undefined) {
        return res.status(400).json({
            success: false,
            error: 'INVALID_REQUEST',
            message: 'Missing required fields'
        });
    }
    
    // Get session
    const session = sessions.get(sessionToken);
    if (!session) {
        return res.status(404).json({
            success: false,
            error: 'SESSION_NOT_FOUND',
            message: 'Invalid or expired session'
        });
    }
    
    // Increment attempts
    session.attempts++;
    
    // Analyze bot behavior
    const suspiciousActivities = analyzeBotBehavior(session, timeTaken, honeypotData || {});
    
    // Check if AI trap was selected
    const isAiTrap = selectedOptionId === session.aiTrapOptionId;
    
    // Check if answer is correct
    const isCorrect = selectedOptionId === session.correctOptionId;
    
    // Determine if verification passes
    const botDetected = suspiciousActivities.length > 0 || isAiTrap;
    const verificationPassed = isCorrect && !botDetected;
    
    // Log the attempt
    console.log(`[CAPTCHA] Session: ${sessionToken.substring(0, 8)}...`);
    console.log(`  IP: ${session.clientIP}`);
    console.log(`  Time: ${timeTaken}s`);
    console.log(`  Correct: ${isCorrect}`);
    console.log(`  AI Trap: ${isAiTrap}`);
    console.log(`  Suspicious: ${suspiciousActivities.join(', ') || 'None'}`);
    console.log(`  Result: ${verificationPassed ? 'PASS' : 'FAIL'}`);
    
    // If failed multiple times, blacklist IP temporarily
    if (!verificationPassed && session.attempts >= 5) {
        blacklistedIPs.add(session.clientIP);
        setTimeout(() => {
            blacklistedIPs.delete(session.clientIP);
        }, 15 * 60 * 1000); // 15 minutes
    }
    
    // Clean up session if verification passed
    if (verificationPassed) {
        sessions.delete(sessionToken);
    }
    
    res.json({
        success: verificationPassed,
        verified: verificationPassed,
        timeTaken: timeTaken,
        analysis: {
            correctAnswer: isCorrect,
            aiTrapTriggered: isAiTrap,
            suspiciousActivities: suspiciousActivities,
            botDetected: botDetected
        },
        message: verificationPassed 
            ? 'Human verification successful' 
            : botDetected 
                ? 'Bot-like behavior detected' 
                : 'Incorrect answer'
    });
});

// Get statistics (admin endpoint)
app.get('/api/captcha/stats', (req, res) => {
    res.json({
        activeSessions: sessions.size,
        blacklistedIPs: blacklistedIPs.size,
        totalScenarios: scenarios.length
    });
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Cleanup old sessions
function cleanupOldSessions() {
    const now = Date.now();
    const maxAge = 10 * 60 * 1000; // 10 minutes
    
    for (const [token, session] of sessions.entries()) {
        if (now - session.startTime > maxAge) {
            sessions.delete(token);
        }
    }
}

// Periodic cleanup
setInterval(cleanupOldSessions, 60000); // Every minute

// Start server
app.listen(PORT, () => {
    console.log(`🛡️  CAPTCHA Backend Server running on http://localhost:${PORT}`);
    console.log(`📊 Stats endpoint: http://localhost:${PORT}/api/captcha/stats`);
});
