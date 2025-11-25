// /**
//  * Bot Detection Integration (background only)
//  * Runs bot detection without showing any UI to the user
//  */

// let botDetector = null;

// document.addEventListener('DOMContentLoaded', function() {
//   // Initialize bot detector (no status panel)
//   botDetector = new BotDetector({
//     suspicionThreshold: 40,      // Lower threshold to catch more bots
//     reportInterval: 1500,        // Check every 1.5 seconds
//     debug: false,                // Set to true if you want console logs
//     onSuspicion: handleBotSuspicion,
//     onClear: handleHumanBehavior
//   });

//   // Start detection
//   botDetector.start();
//   console.log('Bot detection v2.0 started (background mode)');
// });

// /**
//  * Handle bot suspicion (no visual banner)
//  * You can plug in server logging, blocking, etc. here.
//  */
// function handleBotSuspicion(report) {
//   console.warn('BOT DETECTED!', report);

//   // Example: prevent verification callbacks or mark session as suspicious.
//   // You can send this report to your backend here if needed.
// }

// /**
//  * Handle when behavior looks human again
//  */
// function handleHumanBehavior(report) {
//   console.log('Human behavior confirmed', report);
// }

// /**
//  * Safely get a snapshot of the current bot detection report
//  * without any UI.
//  */
// function getBotStatusReport() {
//   if (!botDetector) return null;
//   try {
//     return botDetector.getReport();
//   } catch (e) {
//     console.error('Error getting bot report', e);
//     return null;
//   }
// }

// /**
//  * Protected verification callback wrapper
//  * Use this to wrap your CAPTCHA verification logic.
//  *
//  * Example usage:
//  *   const protectedVerify = createProtectedVerificationCallback(actualVerify);
//  *   protectedVerify(resultFromCaptcha);
//  */
// function createProtectedVerificationCallback(originalCallback) {
//   return async function(result) {
//     if (!botDetector) {
//       console.warn('BotDetector not initialized, proceeding anyway');
//       return originalCallback(result);
//     }

//     try {
//       // Force a final analysis before allowing verification
//       const analysis = await botDetector.forceAnalysis();
//       console.log('Final bot analysis before verification:', analysis);

//       if (analysis.isBot || analysis.suspicionScore >= (botDetector.config?.suspicionThreshold || 40)) {
//         console.warn('Verification blocked due to suspected bot activity', analysis);
//         // Optionally call the original callback with a failure result or do nothing
//         return;
//       }

//       // If analysis looks human, proceed with original verification
//       return originalCallback(result);
//     } catch (err) {
//       console.error('Error during bot analysis before verification, proceeding cautiously', err);
//       // In case of error, you can decide to block or allow:
//       return originalCallback(result);
//     }
//   };
// }

// /**
//  * Optional: expose helper for manual checks from other scripts
//  */
// window.BotDetectionIntegration = {
//   getReport: getBotStatusReport,
//   isSuspicious: function() {
//     const report = getBotStatusReport();
//     if (!report) return false;
//     const threshold = botDetector?.config?.suspicionThreshold || 40;
//     return report.isBot || report.suspicionScore >= threshold;
//   },
//   createProtectedVerificationCallback
// };
/**
 * Bot Detection Integration (background only)
 * Runs bot detection without showing any UI to the user
 */

/**
 * Bot Detection Integration (background only)
 * Runs bot detection without showing any UI to the user
 */

let botDetector = null;

document.addEventListener('DOMContentLoaded', function() {
  // Initialize bot detector (no status panel)
  botDetector = new BotDetector({
    suspicionThreshold: 40,      // Lower threshold to catch more bots
    reportInterval: 1500,        // Check every 1.5 seconds
    debug: false,                // Set to true if you want console logs
    onSuspicion: handleBotSuspicion,
    onClear: handleHumanBehavior
  });

  // Start detection
  botDetector.start();
  console.log('Bot detection v2.0 started (background mode)');
});

/**
 * Handle bot suspicion - UPDATED TO ACTUALLY STOP THE CAPTCHA
 */
function handleBotSuspicion(report) {
  console.warn('BOT DETECTED!', report);

  // Stop maze game loop if it's running
  if (window.mazeCaptcha && window.mazeCaptcha.animationId) {
    cancelAnimationFrame(window.mazeCaptcha.animationId);
    window.mazeCaptcha.animationId = null;
    window.mazeCaptcha.gameState.completed = true; // Prevent further updates
    console.log('Maze game loop stopped due to bot detection');
  }

  // Close modal and reset if bot is detected (for candy crush)
  const modal = document.getElementById('verificationModal');
  if (modal && modal.style.display !== 'none') {
    modal.style.display = 'none';
    
    // Show alert to user
    alert('⚠️ Suspicious Activity Detected\n\nBot-like behavior has been detected. Please try again with natural mouse movements and interactions.');
    
    // Reset the verification game
    if (typeof resetVerificationGame === 'function') {
      resetVerificationGame();
    }
  }

  // For maze/slider CAPTCHA pages (captcha-updated.html)
  const timerContainer = document.getElementById('timerContainer');
  if (timerContainer) {
    // Stop the timer
    if (typeof stopTimer === 'function') {
      stopTimer();
    }
    
    // Hide timer
    timerContainer.style.display = 'none';
    
    // Show alert
    alert('⚠️ Bot Behavior Detected\n\nSuspicious activity detected during CAPTCHA. Returning to start.');
    
    // Redirect back to index
    setTimeout(() => {
      window.location.href = 'index.html';
    }, 1000);
  }

  // You can send this report to your backend here if needed.
}

/**
 * Handle when behavior looks human again
 */
function handleHumanBehavior(report) {
  console.log('Human behavior confirmed', report);
}

/**
 * Safely get a snapshot of the current bot detection report
 * without any UI.
 */
function getBotStatusReport() {
  if (!botDetector) return null;
  try {
    return botDetector.getReport();
  } catch (e) {
    console.error('Error getting bot report', e);
    return null;
  }
}

/**
 * Protected verification callback wrapper
 * Use this to wrap your CAPTCHA verification logic.
 *
 * Example usage:
 *   const protectedVerify = createProtectedVerificationCallback(actualVerify);
 *   protectedVerify(resultFromCaptcha);
 */
function createProtectedVerificationCallback(originalCallback) {
  return async function(result) {
    if (!botDetector) {
      console.warn('BotDetector not initialized, proceeding anyway');
      return originalCallback(result);
    }

    try {
      // Force a final analysis before allowing verification
      const analysis = await botDetector.forceAnalysis();
      console.log('Final bot analysis before verification:', analysis);

      const threshold = botDetector.config?.suspicionThreshold || 40;
      
      if (analysis.isBot || analysis.suspicionScore >= threshold) {
        console.warn('Verification blocked due to suspected bot activity', analysis);
        
        // Close the modal
        const modal = document.getElementById('verificationModal');
        if (modal) {
          modal.style.display = 'none';
        }
        
        // Show detailed alert to user
        alert(`🤖 Bot Behavior Detected\n\nYour verification was blocked due to suspicious activity.\n\nSuspicion Score: ${Math.round(analysis.suspicionScore)}%\nThreshold: ${threshold}%\n\nReason: ${analysis.reasons.join(', ')}\n\nPlease interact naturally and try again.`);
        
        // Reset the game
        if (typeof resetVerificationGame === 'function') {
          resetVerificationGame();
        }
        
        // Do NOT call the original callback - block verification
        return;
      }

      // If analysis looks human, proceed with original verification
      console.log('✓ Human behavior verified, proceeding with verification');
      return originalCallback(result);
    } catch (err) {
      console.error('Error during bot analysis before verification, proceeding cautiously', err);
      // In case of error, you can decide to block or allow:
      return originalCallback(result);
    }
  };
}

/**
 * Optional: expose helper for manual checks from other scripts
 */
window.BotDetectionIntegration = {
  getReport: getBotStatusReport,
  isSuspicious: function() {
    const report = getBotStatusReport();
    if (!report) return false;
    const threshold = botDetector?.config?.suspicionThreshold || 40;
    return report.isBot || report.suspicionScore >= threshold;
  },
  createProtectedVerificationCallback
};