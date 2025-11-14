class MazeCapcha {
    constructor() {
        this.canvas = document.getElementById('mazeCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        this.gameState = {
            deaths: 0,
            completed: false,
            invertionLevel: 0,
            currentCheckpoint: 0
        };

        this.player = {
            x: 40,
            y: 0,
            radius: 6,
            vx: 0,
            vy: 0,
            friction: 0.82
        };

        this.goal = {
            radius: 10,
            x: 0,
            y: 0
        };

        this.checkpoints = [];
        this.obstacles = [];
        this.dangerZones = [];

        this.keys = new Set();
        this.animationId = null;

        // Bot detection system
        this.botDetection = {
            movements: [],
            keyPresses: [],
            perfectLineCount: 0,
            suspiciousPatterns: 0,
            startTime: Date.now(),
            lastPositions: [],
            directionChanges: 0,
            constantVelocityFrames: 0,
            isBot: false,
            botReasons: [],
            directManipulationDetected: false,
            keysSetSize: 0,
            totalFrames: 0,
            framesWithMovement: 0
        };

        setTimeout(() => {
            this.resizeCanvas();
            this.generateMaze();
            this.setupEventListeners();
            this.gameLoop();
        }, 100);
    }

    resizeCanvas() {
        const wrapper = this.canvas.parentElement;
        
        const width = wrapper.offsetWidth;
        const height = wrapper.offsetHeight;
        
        this.canvas.width = width;
        this.canvas.height = height;
        
        this.player.y = this.canvas.height / 2;
        this.goal.x = this.canvas.width - 40;
        this.goal.y = this.canvas.height / 2;
    }

    isPointClearOfObstacle(x, y, clearanceRadius = 80) {
        for (let obstacle of this.obstacles) {
            const closestX = Math.max(obstacle.x, Math.min(x, obstacle.x + obstacle.width));
            const closestY = Math.max(obstacle.y, Math.min(y, obstacle.y + obstacle.height));
            
            const distX = x - closestX;
            const distY = y - closestY;
            const distance = Math.sqrt(distX * distX + distY * distY);
            
            if (distance < clearanceRadius) {
                return false;
            }
        }

        for (let danger of this.dangerZones) {
            const dist = Math.hypot(x - danger.x, y - danger.y);
            if (dist < danger.radius + clearanceRadius) {
                return false;
            }
        }

        if (x < 50 || x > this.canvas.width - 50 || y < 50 || y > this.canvas.height - 50) {
            return false;
        }

        return true;
    }

    generateMaze() {
        this.obstacles = [];
        this.dangerZones = [];
        this.checkpoints = [];

        const padding = 60;
        const usableWidth = this.canvas.width - padding * 2;
        const usableHeight = this.canvas.height - padding * 2;

        for (let i = 0; i < 5; i++) {
            let obstacle;
            let valid = true;
            let attempts = 0;

            do {
                obstacle = {
                    x: Math.random() * (usableWidth - 80) + padding + 40,
                    y: Math.random() * (usableHeight - 80) + padding + 40,
                    width: Math.random() * 50 + 40,
                    height: Math.random() * 50 + 40
                };

                const distToStart = Math.hypot(obstacle.x - 40, obstacle.y - this.canvas.height / 2);
                const distToEnd = Math.hypot(obstacle.x - (this.canvas.width - 40), obstacle.y - this.canvas.height / 2);

                if (distToStart < 100 || distToEnd < 100) {
                    valid = false;
                } else {
                    valid = true;
                }

                attempts++;
            } while (!valid && attempts < 5);

            if (valid) {
                this.obstacles.push(obstacle);
                console.log(`📦 Obstacle ${i + 1} placed`);
            }
        }

        for (let i = 0; i < 2; i++) {
            let danger;
            let valid = true;
            let attempts = 0;

            do {
                danger = {
                    x: Math.random() * (usableWidth - 120) + padding + 60,
                    y: Math.random() * (usableHeight - 120) + padding + 60,
                    radius: Math.random() * 25 + 15,
                    angle: 0
                };

                valid = true;
                
                for (let obstacle of this.obstacles) {
                    const distX = Math.abs(danger.x - (obstacle.x + obstacle.width / 2));
                    const distY = Math.abs(danger.y - (obstacle.y + obstacle.height / 2));
                    const minDist = danger.radius + Math.max(obstacle.width, obstacle.height) / 2 + 50;

                    if (distX < minDist && distY < minDist) {
                        valid = false;
                        break;
                    }
                }

                attempts++;
            } while (!valid && attempts < 5);

            if (valid) {
                this.dangerZones.push(danger);
                console.log(`⚠️ Danger zone ${i + 1} placed`);
            }
        }

        const checkpointXPositions = [
            this.canvas.width * 0.25,
            this.canvas.width * 0.5,
            this.canvas.width * 0.75
        ];

        for (let checkpointIndex = 0; checkpointIndex < 3; checkpointIndex++) {
            let checkpoint = null;
            let foundValidSpot = false;
            let attempts = 0;
            const maxAttempts = 100;
            
            while (!foundValidSpot && attempts < maxAttempts) {
                const targetX = checkpointXPositions[checkpointIndex];
                const x = targetX + (Math.random() - 0.5) * 100;
                const y = Math.random() * (this.canvas.height - 100) + 50;
                
                checkpoint = {
                    x: Math.max(60, Math.min(this.canvas.width - 60, x)),
                    y: Math.max(60, Math.min(this.canvas.height - 60, y)),
                    reached: false,
                    index: checkpointIndex
                };

                if (this.isPointClearOfObstacle(checkpoint.x, checkpoint.y, 100)) {
                    foundValidSpot = true;
                    console.log(`✅ Checkpoint ${checkpointIndex + 1} placed at (${checkpoint.x.toFixed(0)}, ${checkpoint.y.toFixed(0)})`);
                } else {
                    attempts++;
                }
            }

            if (!foundValidSpot) {
                attempts = 0;
                while (!foundValidSpot && attempts < maxAttempts) {
                    const targetX = checkpointXPositions[checkpointIndex];
                    const x = targetX + (Math.random() - 0.5) * 150;
                    const y = Math.random() * (this.canvas.height - 100) + 50;
                    
                    checkpoint = {
                        x: Math.max(60, Math.min(this.canvas.width - 60, x)),
                        y: Math.max(60, Math.min(this.canvas.height - 60, y)),
                        reached: false,
                        index: checkpointIndex
                    };

                    if (this.isPointClearOfObstacle(checkpoint.x, checkpoint.y, 60)) {
                        foundValidSpot = true;
                        console.log(`⚠️ Checkpoint ${checkpointIndex + 1} placed with reduced clearance at (${checkpoint.x.toFixed(0)}, ${checkpoint.y.toFixed(0)})`);
                    } else {
                        attempts++;
                    }
                }
            }

            if (!foundValidSpot) {
                console.warn(`❌ Could not place checkpoint ${checkpointIndex + 1}. Regenerating maze...`);
                this.generateMaze();
                return;
            }

            this.checkpoints.push(checkpoint);
        }

        console.log(`✅ Maze generation complete - ${this.checkpoints.length} checkpoints placed`);
        console.log(`📦 Total obstacles: ${this.obstacles.length}`);
        console.log(`⚠️ Total danger zones: ${this.dangerZones.length}`);
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'w', 'a', 's', 'd'].includes(key)) {
                this.keys.add(key);
                e.preventDefault();
                
                // Track key press timing
                this.botDetection.keyPresses.push({
                    key: key,
                    time: Date.now(),
                    playerPos: {x: this.player.x, y: this.player.y}
                });
                
                // Debug log
                console.log('✅ Keyboard event:', key, '- Total:', this.botDetection.keyPresses.length);
            }
        });

        document.addEventListener('keyup', (e) => {
            const key = e.key.toLowerCase();
            this.keys.delete(key);
        });

        window.addEventListener('resize', () => this.resizeCanvas());
    }

    getInvertedMovement(moveX, moveY) {
        let newMoveX = moveX;
        let newMoveY = moveY;

        if (this.gameState.invertionLevel === 1) {
            newMoveX *= -1;
        }
        else if (this.gameState.invertionLevel === 2) {
            newMoveY *= -1;
        }
        else if (this.gameState.invertionLevel === 3) {
            newMoveX *= -1;
            newMoveY *= -1;
        }

        return { moveX: newMoveX, moveY: newMoveY };
    }

    updatePlayer() {
        // Bot detection - count frames
        this.botDetection.totalFrames++;
        
        // Check if player is actually moving
        if (Math.abs(this.player.vx) > 0.1 || Math.abs(this.player.vy) > 0.1) {
            this.botDetection.framesWithMovement++;
        }
        
        // Early detection at frame 50
        if (this.botDetection.totalFrames === 50) {
            console.log('🔍 BOT CHECK AT 50 FRAMES:');
            console.log('   Frames with movement:', this.botDetection.framesWithMovement);
            console.log('   Keyboard events recorded:', this.botDetection.keyPresses.length);
            
            // If player moved for more than 20 frames but has fewer than 5 keyboard events
            if (this.botDetection.framesWithMovement > 20 && this.botDetection.keyPresses.length < 5) {
                this.botDetection.directManipulationDetected = true;
                this.botDetection.isBot = true;
                this.botDetection.botReasons = [
                    `Movement in ${this.botDetection.framesWithMovement} frames but only ${this.botDetection.keyPresses.length} keyboard events`
                ];
                console.error('🚫 BOT DETECTED: Direct key manipulation');
            }
        }
        
        let moveX = 0;
        let moveY = 0;

        if (this.keys.has('arrowup') || this.keys.has('w')) moveY = -1;
        if (this.keys.has('arrowdown') || this.keys.has('s')) moveY = 1;
        if (this.keys.has('arrowleft') || this.keys.has('a')) moveX = -1;
        if (this.keys.has('arrowright') || this.keys.has('d')) moveX = 1;

        const inverted = this.getInvertedMovement(moveX, moveY);
        moveX = inverted.moveX;
        moveY = inverted.moveY;

        this.player.vx += moveX * 0.4;
        this.player.vy += moveY * 0.4;

        this.player.vx *= this.player.friction;
        this.player.vy *= this.player.friction;

        let newX = this.player.x + this.player.vx;
        let newY = this.player.y + this.player.vy;

        newX = Math.max(this.player.radius, Math.min(this.canvas.width - this.player.radius, newX));
        newY = Math.max(this.player.radius, Math.min(this.canvas.height - this.player.radius, newY));

        let hitObstacle = false;
        for (let obstacle of this.obstacles) {
            if (this.checkRectCircleCollision(obstacle, newX, newY)) {
                hitObstacle = true;
                break;
            }
        }

        let inDangerZone = false;
        for (let danger of this.dangerZones) {
            const dist = Math.hypot(newX - danger.x, newY - danger.y);
            if (dist < danger.radius + this.player.radius) {
                inDangerZone = true;
                break;
            }
        }

        if (!hitObstacle && !inDangerZone) {
            this.player.x = newX;
            this.player.y = newY;
        } else if (inDangerZone) {
            this.resetPlayer();
        }

        // Check checkpoint progression
        if (this.gameState.currentCheckpoint < this.checkpoints.length) {
            const nextCheckpoint = this.checkpoints[this.gameState.currentCheckpoint];
            const dist = Math.hypot(this.player.x - nextCheckpoint.x, this.player.y - nextCheckpoint.y);
            
            if (dist < 25) {
                nextCheckpoint.reached = true;
                this.gameState.currentCheckpoint++;
                this.gameState.invertionLevel++;
                
                const invertionMessages = [
                    '✅ Checkpoint 1 reached! LEFT & RIGHT controls inverted.',
                    '✅ Checkpoint 2 reached! UP & DOWN controls inverted.',
                    '✅ Checkpoint 3 reached! ALL controls inverted (LEFT↔RIGHT, UP↔DOWN).'
                ];

                if (this.gameState.currentCheckpoint <= 3) {
                    document.getElementById('quirkMessage').textContent = invertionMessages[this.gameState.currentCheckpoint - 1];
                }

                if (this.gameState.currentCheckpoint === 3) {
                    document.getElementById('quirkMessage').textContent = '⚠️ All checkpoints reached! Navigate to END with FULL inversion!';
                }
            }
        }

        // Check goal
        const distToGoal = Math.hypot(this.player.x - this.goal.x, this.player.y - this.goal.y);
        if (distToGoal < 25 && this.gameState.currentCheckpoint === 3) {
            this.completeGame();
        }

        const progress = Math.round((this.player.x / this.canvas.width) * 100);
        document.getElementById('progressValue').textContent = Math.min(progress, 100) + '%';
    }

    checkRectCircleCollision(rect, cx, cy) {
        const distX = Math.abs(cx - (rect.x + rect.width / 2));
        const distY = Math.abs(cy - (rect.y + rect.height / 2));

        if (distX > rect.width / 2 + this.player.radius) return false;
        if (distY > rect.height / 2 + this.player.radius) return false;

        if (distX <= rect.width / 2) return true;
        if (distY <= rect.height / 2) return true;

        const dx = distX - rect.width / 2;
        const dy = distY - rect.height / 2;
        return dx * dx + dy * dy <= this.player.radius * this.player.radius;
    }

    resetPlayer() {
        this.gameState.deaths++;
        document.getElementById('deathCounter').textContent = this.gameState.deaths;
        document.getElementById('status').textContent = 'Collision detected. Restarting...';
        document.getElementById('status').className = 'message-area error';
        
        setTimeout(() => {
            document.getElementById('status').textContent = '';
            document.getElementById('status').className = 'message-area';
        }, 1500);

        this.player.x = 40;
        this.player.y = this.canvas.height / 2;
        this.player.vx = 0;
        this.player.vy = 0;
        this.gameState.currentCheckpoint = 0;
        this.gameState.invertionLevel = 0;
        this.checkpoints.forEach(cp => cp.reached = false);
        document.getElementById('quirkMessage').textContent = 'Navigate to all 3 checkpoints, then to END...';
    }

    analyzeBotBehavior() {
        // Check for direct key manipulation
        if (this.botDetection.directManipulationDetected) {
            this.botDetection.isBot = true;
            console.warn('🤖 BOT DETECTED: Direct manipulation');
            return;
        }
        
        // Check key press timing
        if (this.botDetection.keyPresses.length >= 50) {
            const recentPresses = this.botDetection.keyPresses.slice(-50);
            const intervals = [];
            
            for (let i = 1; i < recentPresses.length; i++) {
                intervals.push(recentPresses[i].time - recentPresses[i-1].time);
            }
            
            const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
            const roboticIntervals = intervals.filter(i => 
                Math.abs(i - avgInterval) < 2
            ).length;
            
            const regularityPercent = (roboticIntervals / intervals.length) * 100;
            
            console.log('🔍 Key Timing Analysis:');
            console.log('   Regularity:', regularityPercent.toFixed(1), '%');
            
            if (regularityPercent > 90 && intervals.length > 40) {
                this.botDetection.isBot = true;
                this.botDetection.botReasons.push(`Robotic key timing: ${regularityPercent.toFixed(1)}%`);
                console.warn('🤖 BOT DETECTED: Key timing too perfect');
            }
        }
        
        // Check superhuman speed
        const timeElapsed = (Date.now() - this.botDetection.startTime) / 1000;
        
        if (this.gameState.currentCheckpoint === 3 && timeElapsed < 3) {
            this.botDetection.isBot = true;
            this.botDetection.botReasons.push(`Superhuman speed: ${timeElapsed.toFixed(1)}s`);
        }
    }

    completeGame() {
        // Final bot check
        console.log('🎯 FINAL BOT CHECK:');
        console.log('   Total frames:', this.botDetection.totalFrames);
        console.log('   Frames with movement:', this.botDetection.framesWithMovement);
        console.log('   Keyboard events:', this.botDetection.keyPresses.length);
        
        // If significant movement with very few keyboard events = BOT
        if (this.botDetection.framesWithMovement > 50 && this.botDetection.keyPresses.length < 20) {
            this.botDetection.isBot = true;
            this.botDetection.botReasons = [
                `Only ${this.botDetection.keyPresses.length} keyboard events for ${this.botDetection.framesWithMovement} frames (expected ~${this.botDetection.framesWithMovement})`
            ];
        }
        
        this.analyzeBotBehavior();
        
        console.log('=== FINAL BOT DETECTION REPORT ===');
        console.log('Is Bot:', this.botDetection.isBot);
        console.log('Reasons:', this.botDetection.botReasons);
        console.log('Time:', (Date.now() - this.botDetection.startTime) / 1000, 'seconds');
        console.log('================================');
        
        if (this.botDetection.isBot) {
            // BOT DETECTED
            this.gameState.completed = false;
            document.getElementById('status').textContent = '⚠️ Suspicious activity detected. Verification failed.';
            document.getElementById('status').className = 'message-area error';
            document.getElementById('statusValue').textContent = 'Failed';
            document.getElementById('submitBtn').disabled = true;
            
            console.error('🚫 BOT VERIFICATION FAILED');
            console.error('Reasons:', this.botDetection.botReasons);
            
            setTimeout(() => {
                document.getElementById('quirkMessage').textContent = 
                    '🤖 Bot behavior detected. Please solve manually.';
            }, 500);
            
        } else {
            // HUMAN VERIFIED
            this.gameState.completed = true;
            document.getElementById('status').textContent = 'Maze completed successfully ✅';
            document.getElementById('status').className = 'message-area success';
            document.getElementById('statusValue').textContent = 'Complete';
            document.getElementById('submitBtn').disabled = false;
            
            console.log('✅ HUMAN VERIFIED');
        }
    }

    draw() {
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Grid background
        this.ctx.strokeStyle = '#f0f0f0';
        this.ctx.lineWidth = 0.5;
        for (let x = 0; x < this.canvas.width; x += 40) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y < this.canvas.height; y += 40) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }

        // Start point
        this.ctx.fillStyle = '#16a34a';
        this.ctx.beginPath();
        this.ctx.arc(40, this.canvas.height / 2, 10, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = 'bold 12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('S', 40, this.canvas.height / 2);

        // End point
        this.ctx.fillStyle = '#dc2626';
        this.ctx.beginPath();
        this.ctx.arc(this.goal.x, this.goal.y, 10, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillText('E', this.goal.x, this.goal.y);

        // Obstacles
        this.ctx.fillStyle = '#d1d5db';
        this.ctx.strokeStyle = '#9ca3af';
        this.ctx.lineWidth = 1;
        for (let obstacle of this.obstacles) {
            this.ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
            this.ctx.strokeRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        }

        // Danger zones
        for (let danger of this.dangerZones) {
            danger.angle += 0.03;
            
            this.ctx.strokeStyle = '#fca5a5';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(danger.x, danger.y, danger.radius, 0, Math.PI * 2);
            this.ctx.stroke();

            const endX = danger.x + Math.cos(danger.angle) * danger.radius;
            const endY = danger.y + Math.sin(danger.angle) * danger.radius;
            this.ctx.strokeStyle = '#dc2626';
            this.ctx.lineWidth = 2.5;
            this.ctx.beginPath();
            this.ctx.moveTo(danger.x, danger.y);
            this.ctx.lineTo(endX, endY);
            this.ctx.stroke();
        }

        // Path connecting checkpoints
        if (this.checkpoints.length > 0) {
            this.ctx.strokeStyle = '#bfdbfe';
            this.ctx.lineWidth = 2;
            this.ctx.setLineDash([5, 5]);
            this.ctx.beginPath();
            this.ctx.moveTo(40, this.canvas.height / 2);
            
            for (let checkpoint of this.checkpoints) {
                this.ctx.lineTo(checkpoint.x, checkpoint.y);
            }
            
            this.ctx.lineTo(this.goal.x, this.goal.y);
            this.ctx.stroke();
            this.ctx.setLineDash([]);
        }

        // Draw checkpoints with numbers
        for (let i = 0; i < this.checkpoints.length; i++) {
            const checkpoint = this.checkpoints[i];
            
            this.ctx.fillStyle = checkpoint.reached ? 'rgba(22, 163, 74, 0.1)' : 'rgba(234, 179, 8, 0.1)';
            this.ctx.beginPath();
            this.ctx.arc(checkpoint.x, checkpoint.y, 20, 0, Math.PI * 2);
            this.ctx.fill();
            
            this.ctx.fillStyle = checkpoint.reached ? '#16a34a' : '#eab308';
            this.ctx.beginPath();
            this.ctx.arc(checkpoint.x, checkpoint.y, 8, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.strokeStyle = checkpoint.reached ? '#15803d' : '#ca8a04';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = 'bold 10px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(i + 1, checkpoint.x, checkpoint.y);
        }

        // Control mode indicator
        this.ctx.fillStyle = '#2563eb';
        this.ctx.font = '13px Arial';
        this.ctx.textAlign = 'right';
        this.ctx.textBaseline = 'top';
        
        const modeNames = [
            '🟢 NORMAL',
            '🔴 LEFT & RIGHT INVERTED',
            '🔴 UP & DOWN INVERTED',
            '🔴 ALL INVERTED'
        ];
        
        this.ctx.fillText(modeNames[this.gameState.invertionLevel], this.canvas.width - 10, 10);

        // Player
        this.ctx.fillStyle = '#2563eb';
        this.ctx.beginPath();
        this.ctx.arc(this.player.x, this.player.y, this.player.radius, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.strokeStyle = '#1d4ed8';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
    }

    gameLoop = () => {
        if (!this.gameState.completed) {
            this.updatePlayer();
        }
        this.draw();
        this.animationId = requestAnimationFrame(this.gameLoop);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const captcha = new MazeCapcha();
    
    window.captchaInstance = captcha;
    
    document.getElementById('submitBtn').addEventListener('click', () => {
        if (captcha.botDetection.isBot) {
            alert('⚠️ Verification Failed\n\nBot behavior was detected. Please complete the CAPTCHA manually.');
        } else {
            alert(`✅ Verification Complete\n\nAttempts: ${captcha.gameState.deaths}\n\nForm submitted successfully.`);
        }
    });
});