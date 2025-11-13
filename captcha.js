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

        setTimeout(() => {
            this.resizeCanvas();
            this.generateMaze();
            this.setupEventListeners();
            this.gameLoop();
            console.log('Maze initialized with', this.checkpoints.length, 'checkpoints');
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

    generateMaze() {
        this.obstacles = [];
        this.dangerZones = [];
        this.checkpoints = [];

        const padding = 60;
        const usableWidth = this.canvas.width - padding * 2;
        const usableHeight = this.canvas.height - padding * 2;

        // Generate obstacles
        for (let i = 0; i < 10; i++) {
            let obstacle;
            let valid = true;
            let attempts = 0;

            do {
                obstacle = {
                    x: Math.random() * (usableWidth - 60) + padding,
                    y: Math.random() * (usableHeight - 60) + padding,
                    width: Math.random() * 40 + 30,
                    height: Math.random() * 40 + 30
                };

                const distToStart = Math.hypot(obstacle.x - 40, obstacle.y - this.canvas.height / 2);
                const distToEnd = Math.hypot(obstacle.x - (this.canvas.width - 40), obstacle.y - this.canvas.height / 2);

                if (distToStart < 80 || distToEnd < 80) {
                    valid = false;
                } else {
                    valid = true;
                }

                attempts++;
            } while (!valid && attempts < 5);

            if (valid) {
                this.obstacles.push(obstacle);
            }
        }

        // Generate danger zones
        for (let i = 0; i < 3; i++) {
            let danger;
            let valid = true;
            let attempts = 0;

            do {
                danger = {
                    x: Math.random() * (usableWidth - 100) + padding + 50,
                    y: Math.random() * (usableHeight - 100) + padding + 50,
                    radius: Math.random() * 30 + 20,
                    angle: 0
                };

                valid = true;
                for (let obstacle of this.obstacles) {
                    const distX = Math.abs(danger.x - (obstacle.x + obstacle.width / 2));
                    const distY = Math.abs(danger.y - (obstacle.y + obstacle.height / 2));
                    const minDist = danger.radius + Math.max(obstacle.width, obstacle.height) / 2 + 30;

                    if (distX < minDist && distY < minDist) {
                        valid = false;
                        break;
                    }
                }

                attempts++;
            } while (!valid && attempts < 5);

            if (valid) {
                this.dangerZones.push(danger);
            }
        }

        // Generate exactly 3 checkpoints at specific positions
        const checkpointXPositions = [
            this.canvas.width * 0.25,
            this.canvas.width * 0.5,
            this.canvas.width * 0.75
        ];

        for (let i = 0; i < 3; i++) {
            let checkpoint;
            let valid = false;
            let attempts = 0;
            const maxAttempts = 20; // Increase attempts to ensure creation

            do {
                // Create variation in Y position
                const yVariation = (Math.random() - 0.5) * (this.canvas.height * 0.4);
                checkpoint = {
                    x: checkpointXPositions[i],
                    y: this.canvas.height / 2 + yVariation,
                    reached: false,
                    index: i
                };

                // Clamp Y to valid range
                checkpoint.y = Math.max(50, Math.min(this.canvas.height - 50, checkpoint.y));

                valid = true;

                // Check collision with obstacles
                for (let obstacle of this.obstacles) {
                    const distX = Math.abs(checkpoint.x - (obstacle.x + obstacle.width / 2));
                    const distY = Math.abs(checkpoint.y - (obstacle.y + obstacle.height / 2));
                    const minDist = 30 + Math.max(obstacle.width, obstacle.height) / 2;

                    if (distX < minDist && distY < minDist) {
                        valid = false;
                        break;
                    }
                }

                // Check collision with danger zones
                if (valid) {
                    for (let danger of this.dangerZones) {
                        const dist = Math.hypot(checkpoint.x - danger.x, checkpoint.y - danger.y);
                        if (dist < danger.radius + 40) {
                            valid = false;
                            break;
                        }
                    }
                }

                attempts++;
            } while (!valid && attempts < maxAttempts);

            // Force add checkpoint if all attempts fail (to guarantee 3 checkpoints)
            if (!valid) {
                checkpoint = {
                    x: checkpointXPositions[i],
                    y: this.canvas.height / 2 + (Math.random() - 0.5) * 100,
                    reached: false,
                    index: i
                };
                checkpoint.y = Math.max(50, Math.min(this.canvas.height - 50, checkpoint.y));
            }

            this.checkpoints.push(checkpoint);
        }

        console.log('Generated checkpoints:', this.checkpoints);
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'w', 'a', 's', 'd'].includes(key)) {
                this.keys.add(key);
                e.preventDefault();
            }
        });

        document.addEventListener('keyup', (e) => {
            const key = e.key.toLowerCase();
            this.keys.delete(key);
        });

        window.addEventListener('resize', () => this.resizeCanvas());
    }

    getInvertedMovement(moveX, moveY) {
        if (this.gameState.invertionLevel >= 1) {
            moveX *= -1;
        }
        if (this.gameState.invertionLevel >= 2) {
            moveY *= -1;
        }

        return { moveX, moveY };
    }

    updatePlayer() {
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
                    'Checkpoint 1 reached! Inversion Level 1 (X-axis inverted).',
                    'Checkpoint 2 reached! Inversion Level 2 (Y-axis also inverted).',
                    'Checkpoint 3 reached! Inversion Level 3 (Full chaos!).'
                ];

                if (this.gameState.currentCheckpoint <= 3) {
                    document.getElementById('quirkMessage').textContent = invertionMessages[this.gameState.currentCheckpoint - 1];
                }

                if (this.gameState.currentCheckpoint === 3) {
                    document.getElementById('quirkMessage').textContent = 'All 3 checkpoints reached! Navigate to END with full inversion!';
                }
            }
        }

        // Check goal - only reachable after all 3 checkpoints
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

    completeGame() {
        this.gameState.completed = true;
        document.getElementById('status').textContent = 'Maze completed successfully';
        document.getElementById('status').className = 'message-area success';
        document.getElementById('statusValue').textContent = 'Complete';
        document.getElementById('submitBtn').disabled = false;
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

        // Draw checkpoints
        for (let i = 0; i < this.checkpoints.length; i++) {
            const checkpoint = this.checkpoints[i];
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

        // Inversion level indicator
        this.ctx.fillStyle = '#2563eb';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'right';
        this.ctx.textBaseline = 'top';
        const invertionText = ['Normal', 'Inverted X', 'Inverted X+Y', 'Fully Inverted'];
        this.ctx.fillText('Mode: ' + invertionText[this.gameState.invertionLevel], this.canvas.width - 10, 10);

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

    document.getElementById('submitBtn').addEventListener('click', () => {
        alert(`Verification Complete\n\nAttempts: ${captcha.gameState.deaths}\n\nForm submitted successfully.`);
    });
});