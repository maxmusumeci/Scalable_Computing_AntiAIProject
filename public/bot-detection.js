/**
 * Advanced Bot Detection System v2.0
 * Specifically designed to catch Playwright, Selenium, and Puppeteer bots
 * Even when they use stealth/evasion techniques
 */

class VelocityProfileAnalyzer {
    constructor() {
        this.positions = [];
        this.samplingRate = 16; // every 16 milliseconds
        this.minSamplesForAnalysis = 20;
    }

    recordPosition(x, y, timestamp= Date.now()) {
        this.positions.push({x, y, timestamp});

        if (this.positions.length > 200) {
            this.positions.shift();
        }
    }

    calculateVelocity(pos1, pos2) {
        const dx = pos2.x - pos1.x;
        const dy = pos2.y - pos1.y;
        const dt = (pos2.timestamp - pos1.timestamp) / 1000;

        if (dt == 0) return {vx: 0, vy: 0, speed: 0};

        const vx = dx / dt;
        const vy = dy / dt;

        const speed = Math.sqrt((vx * vx) + (vy * vy))

        return {vx, vy, speed};
    }

    calculateAcceleration(v1, v2, dt) {
        if (dt == 0) return 0;
        const ax = (v2.vx - v1.vx) / dt;
        const ay = (v2.vy - v1.vy) / dt;

        return Math.sqrt((ax * ax) + (ay * ay));
    }

    velocityProfileAnalysis()  {
        if (this.positions.length < this.minSamplesForAnalysis) {
            return {
                score: 0,
                reason: 'Insufficient data',
                flags: [],
                insufficient: true
            };
        }

        let flags = [];
        let suspicionScore = 0;

        const accelerations = [];
        const velocities = [];

        for (let i = 1; i < this.positions.length; ++i) {
            const v = this.calculateVelocity(this.positions[i - 1], this.positions[i]);
            velocities.push(v);
            if (i > 1) { // off by 1 for acceleration
                const dt = (this.positions[i].timestamp - this.positions[i - 1.].timestamp) / 1000;
                const acc = this.calculateAcceleration(velocities[i - 2], velocities[i - 1], dt);
                accelerations.push(acc)
            }

        }

        // start with simple acc check
        const maxHumanAcceleration = 10000; // conservative estimate of max mouse movement acc
        const impossibleAcceleration = accelerations.filter(a => a > maxHumanAcceleration).length;

        if (impossibleAcceleration > 0) {
            suspicionScore += 40;
            flags.push('IMPOSSIBLE_ACCELERATION');
        }

        const speeds = velocities.map(v => v.speed);
        const avgSpeed = speeds.reduce((a, b) => a + b, 0) / speeds.length;
        // variance = sum over s(s_i - avgSpeed)^2/num_samples
        const variance = speeds.reduce((sum, s) => sum + Math.pow(s - avgSpeed, 2));
        const stdDev = Math.sqrt(variance);

        if (avgSpeed > 50) { // 50 pixels
            const coefficientOfVariation = stdDev / avgSpeed;
            if (coefficientOfVariation < 0.05) {
                suspicionScore += 30;
                flags.push("NO_VELOCITY_JITTER")
            }
        }

        let teleported = false;
        const movements = [];

        for (let i = 1; i < this.positions.length; ++i) {
            const distance = Math.hypot(this.positions[i].x, this.positions[i - 1].x, 
                this.positions[i].y, this.positions[i - 1].y
            );
            
            const dt = (this.positions[i].timestamp - this.positions[i - 1].timestamp);
            if (distance > 500 && dt < 0.05) {
                teleported = true;
            }

            // we use this for fitt's law later
            const v = velocities[i - 1];
            if (distance > 50) {
                movements.push({distance, speed: v.speed});
            }
        }
        if (teleported) {
            suspicionScore += 0.15;
            flags.push("POSITION_TELEPORTED");
        }

        // main one: fitt's law violation
        if (movements.length > 5) {
            const distanceGroups = {
                short: movements.filter(m => m.distance < 100),
                medium: movements.filter(m => m.distance >= 100 && m.distance < 300),
                long: movements.filter(m => m.distance >= 300)
            };

            const avgSpeed = {};
            for (const [key, group] of Object.entries(distanceGroups)) {
                if (group.length > 0) {
                    avgSpeed[key] = group.reduce((sum, m) => sum + m.speed, 0) / group.length;
                }
            }

            if (avgSpeeds.short && avgSpeeds.long) {
                // if we're reaching speeds that are far in distance in similar speeds
                //that we reach for small distance, then it violates fitt's law
                const speedRatio = avgSpeeds.long / avgSpeeds.short;
                if (speedRatio < 1.2) {
                    suspicionScore += 20;
                    flags.push("FITTS_LAW_VIOLATION");
                }
            }
        }

        suspicionScore = Math.min(100, suspicionScore);

        return {
            score: Math.round(suspicionScore),
            insufficient: false,
            flags: flags
        };
    }

    reset() {
        this.positions = [];
    }
}

class DistanceAngleAnalyzer {
    constructor() {
        this.movements = [];
        this.minMovementsForAnalysis = 15;
    }

    recordMovement(x1, x2, y1, y2) {
        const dx = x2 - x1;
        const dy = y2 - y1;

        const distance = Math.sqrt((dx * dx) + (dy * dy));

        if (distance > 5) {
            const angle = Math.atan2(dy, dx); // instead of atan which finds pi to -pi, we find -pi to pi
            this.movements.push({distance, angle});

            if (this.movements.length > 100) {
                this.movements.shift();
            }
        }
    }

    analyzeAngularDistribution() {
        if (this.movements.length < this.minMovementsForAnalysis) {
            return {
                score: 0, 
                reason: "Insufficient data", 
                flags: [], 
                insufficient: true
            };
        }

        const bins = new Array(8).fill(0);

        for (const movement of this.movements) {
            const normalizedAngle = (movement.angle + Math.PI) % (2 * Math.PI);
            const binIndex = Math.floor(normalizedAngle / (Math.PI / 4)) % 8;
            bins[binIndex]++;
        }

        const cardinalCount = bins[0] + bins[2] + bins[4] + bins[6];
        const cardinalRatio = cardinalCount / this.movements.length;

        let suspicionScore = 0;
        let flags = [];

        if (cardinalRatio < 0.45 || cardinalRatio > 0.85) {
            suspicionScore += 30;
            flags.push("UNNATURAL_ANGLE_DISTRIBUTION")
        }

        const expectedCount = this.movements.length / 8;
        const chiSquare = bins.reduce((sum, count) => {
            return sum + Math.pow(count - expectedCount, 2) / expectedCount;
        }, 0);

        if (chiSquare < 2) {
            suspicionScore += 40;
            flags("ANGLES_TOO_UNIFORM");
        }

        return {
            score: suspicionScore,
            flags: flags,
            insufficient: false
        };
    }

    analyzeDistanceDistribution() {
        if (this.movements.length < this.minMovementsForAnalysis) {
            return { score: 0, reason: 'Insufficient data', flags: [] };
        }

        const distances = this.movements.map(m => m.distance);
        const avgDistance = distances.reduce((a, b) => a + b, 0) / distances.length;
        const variance = distances.reduce((sum, d) => sum + Math.pow(d - avgDistance, 2), 0) / distances.length;
        const stdDev = Math.sqrt(variance);

        let suspicionScore = 0;
        let flags = [];

        const coefficientOfVariation = stdDev / avgDistance;
        if (coefficientOfVariation < 0.15) {
            suspicionScore += 35;
            flags.push('UNIFORM_MOVEMENT_DISTANCES');
        }

        const bins = { short: 0, medium: 0, long: 0 };
        for (const d of distances) {
            if (d < 50) bins.short++;
            else if (d < 150) bins.medium++;
            else bins.long++;
        }

        const shortRatio = bins.short / distances.length;
        if (shortRatio < 0.3) {
            suspicionScore += 25;
            flags.push('TOO_FEW_SHORT_MOVEMENTS');
        }

        return {
            score: suspicionScore,
            avgDistance: Math.round(avgDistance),
            coefficientOfVariation: Math.round(coefficientOfVariation * 100),
            bins,
            flags
        };
    }

    analyzeDistanceAndAngle() {

        const angleAnalysis = this.analyzeAngularDistribution();
        const distanceAnalysis = this.analyzeDistanceDistribution();

        const totalScore = Math.min(100, angleAnalysis.score + distanceAnalysis.score);
        const allFlags = [...angleAnalysis.flags, ...distanceAnalysis.flags];

        return {
            score: Math.round(totalScore),
            flags: allFlags,
            insufficient: this.movements.length < this.minMovementsForAnalysis,
            details: {
                movementCount: this.movements.length,
                cardinalRatio: Math.round(angleAnalysis.cardinalRatio * 100),
                avgDistance: distanceAnalysis.avgDistance,
                distanceVariation: distanceAnalysis.coefficientOfVariation
            }
        };
    }

    reset() {
        this.movements = [];
    }
}

class BotDetector {
    constructor(options = {}) {
        this.config = {
            suspicionThreshold: 50,
            reportInterval: 2000,
            analysisWindow: 30000,
            onSuspicion: options.onSuspicion || this.defaultSuspicionHandler,
            onClear: options.onClear || (() => {}),
            debug: options.debug || false,
            ...options
        };

        // Data stores
        this.mouseData = {
            movements: [], // array of x, y, timestamp?
            clicks: [],
            rawEvents: [], // Store raw event data for analysis
            lastPosition: null,
            totalDistance: 0
        };
        
        this.velocityAnalyzer = new VelocityProfileAnalyzer();
        this.distanceAngleAnalyzer = new DistanceAngleAnalyzer();

        this.keyboardData = {
            keyDownTimes: {},
            keyDurations: [],
            interKeyIntervals: [],
            lastKeyTime: null,
            keystrokePattern: [],
            hasRealKeyboard: false
        };

        this.clickData = {
            clickTimes: [],
            clickPositions: [],
            clickTimingPattern: []
        };

        this.interactionData = {
            firstInteraction: null,
            lastInteraction: null,
            totalEvents: 0,
            eventTimestamps: []
        };

        // Advanced detection data
        this.advancedData = {
            mouseEventTrust: [],      // isTrusted flag
            clickEventTrust: [],
            keyEventTrust: [],
            pointerTypes: [],         // mouse, pen, touch
            eventSourceTypes: [],     // Track how events are generated
            movementPatterns: [],     // Detect synthetic movement
            bezierScore: 0,           // Human movements follow bezier curves
            jitterAnalysis: [],
            accelerationChanges: []
        };

        this.scores = {
            mouse: 0,
            keyboard: 0,
            timing: 0,
            environment: 0,
            behavior: 0,
            advanced: 0
        };

        this.isRunning = false;
        this.suspicionLevel = 0;
        this.flags = [];
        this.analysisInterval = null;

        // Bind methods
        this.handleMouseMove = this.handleMouseMove.bind(this);
        this.handleMouseDown = this.handleMouseDown.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleKeyUp = this.handleKeyUp.bind(this);
        this.handlePointerMove = this.handlePointerMove.bind(this);
        this.handlePointerDown = this.handlePointerDown.bind(this);

        this.pointerData = {
        sequences: [],           // Track pointer event sequences
        lastPointerDown: null,
        lastPointerMove: null,
        moveBeforeDown: false,   // Did pointer move before down?
        downWithoutHover: 0,     // Pointer downs without hover
        perfectSteps: [],        // Track if movements are too perfect
        pressureValues: [],      // Track all pressure values
        timingDeltas: []         // Time between pointer events
        };
    }

    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.interactionData.firstInteraction = Date.now();
        
        // Use capture phase to get events before they can be stopped
        document.addEventListener('mousemove', this.handleMouseMove, { capture: true, passive: true });
        document.addEventListener('mousedown', this.handleMouseDown, { capture: true, passive: true });
        document.addEventListener('click', this.handleClick, { capture: true, passive: true });
        document.addEventListener('keydown', this.handleKeyDown, { capture: true, passive: true });
        document.addEventListener('keyup', this.handleKeyUp, { capture: true, passive: true });
        
        // Pointer events (more detailed than mouse events)
        document.addEventListener('pointermove', this.handlePointerMove, { capture: true, passive: true });
        document.addEventListener('pointerdown', this.handlePointerDown, { capture: true, passive: true });

        // Run environment checks immediately
        this.runEnvironmentChecks();

        // Start periodic analysis
        this.analysisInterval = setInterval(() => {
            this.analyzeAndReport();
        }, this.config.reportInterval);

        // Inject detection traps
        this.injectDetectionTraps();

        this.log('Bot detection started');
    }

    stop() {
        if (!this.isRunning) return;
        
        this.isRunning = false;
        
        document.removeEventListener('mousemove', this.handleMouseMove, { capture: true });
        document.removeEventListener('mousedown', this.handleMouseDown, { capture: true });
        document.removeEventListener('click', this.handleClick, { capture: true });
        document.removeEventListener('keydown', this.handleKeyDown, { capture: true });
        document.removeEventListener('keyup', this.handleKeyUp, { capture: true });
        document.removeEventListener('pointermove', this.handlePointerMove, { capture: true });
        document.removeEventListener('pointerdown', this.handlePointerDown, { capture: true });

        if (this.analysisInterval) {
            clearInterval(this.analysisInterval);
        }

        this.log('Bot detection stopped');
    }

    // ==================== EVENT HANDLERS ====================

    handleMouseMove(event) {
        const now = Date.now();
        
        // CRITICAL: Check if event is trusted (not synthesized)
        this.advancedData.mouseEventTrust.push(event.isTrusted);
        
        const position = {
            x: event.clientX,
            y: event.clientY,
            time: now,
            isTrusted: event.isTrusted,
            movementX: event.movementX,
            movementY: event.movementY,
            screenX: event.screenX,
            screenY: event.screenY
        };

        this.velocityAnalyzer.recordPosition(position.x, position.y, now);

        if (this.mouseData.lastPosition) {
            const last = this.mouseData.lastPosition;
            const dx = position.x - last.x;
            const dy = position.y - last.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const timeDelta = now - last.time;
            
            position.distance = distance;
            position.speed = timeDelta > 0 ? distance / timeDelta : 0;
            position.timeDelta = timeDelta;
            position.angle = Math.atan2(dy, dx);
            
            // Calculate acceleration
            if (last.speed !== undefined) {
                position.acceleration = timeDelta > 0 ? (position.speed - last.speed) / timeDelta : 0;
                this.advancedData.accelerationChanges.push(position.acceleration);
            }

            this.distanceAngleAnalyzer.recordMovement(last.x, last.y, position.x, position.y);

            // Check for synthetic movement patterns
            this.analyzeMovementPattern(position, last);
            
            this.mouseData.totalDistance += distance;
        }

        this.mouseData.movements.push(position);
        this.mouseData.lastPosition = position;
        this.interactionData.lastInteraction = now;
        this.interactionData.totalEvents++;
        this.interactionData.eventTimestamps.push(now);

        this.pruneOldData();
    }

    handleMouseDown(event) {
        this.advancedData.clickEventTrust.push(event.isTrusted);
    }

    handleClick(event) {
        const now = Date.now();
        
        this.clickData.clickTimes.push(now);
        this.clickData.clickPositions.push({ x: event.clientX, y: event.clientY });
        
        // Track click timing patterns
        if (this.clickData.clickTimes.length > 1) {
            const interval = now - this.clickData.clickTimes[this.clickData.clickTimes.length - 2];
            this.clickData.clickTimingPattern.push(interval);
        }

        this.mouseData.clicks.push({
            x: event.clientX,
            y: event.clientY,
            time: now,
            isTrusted: event.isTrusted,
            button: event.button
        });

        this.interactionData.lastInteraction = now;
    }

    handleKeyDown(event) {
        const now = Date.now();
        const key = event.code;

        this.advancedData.keyEventTrust.push(event.isTrusted);
        this.keyboardData.hasRealKeyboard = true;

        if (!this.keyboardData.keyDownTimes[key]) {
            this.keyboardData.keyDownTimes[key] = now;
        }

        if (this.keyboardData.lastKeyTime) {
            const interval = now - this.keyboardData.lastKeyTime;
            this.keyboardData.interKeyIntervals.push(interval);
        }

        this.keyboardData.lastKeyTime = now;
        this.keyboardData.keystrokePattern.push({ 
            key, 
            time: now, 
            type: 'down',
            isTrusted: event.isTrusted
        });
        
        this.interactionData.lastInteraction = now;
    }

    handleKeyUp(event) {
        const now = Date.now();
        const key = event.code;

        if (this.keyboardData.keyDownTimes[key]) {
            const duration = now - this.keyboardData.keyDownTimes[key];
            this.keyboardData.keyDurations.push(duration);
            delete this.keyboardData.keyDownTimes[key];
        }

        this.keyboardData.keystrokePattern.push({ 
            key, 
            time: now, 
            type: 'up',
            isTrusted: event.isTrusted
        });
    }

    // handlePointerMove(event) {
    //     // Pointer events give us more info about input type
    //     this.advancedData.pointerTypes.push(event.pointerType);
        
    //     // Check for pressure (real devices have varying pressure)
    //     if (event.pressure !== undefined) {
    //         // Synthetic events often have pressure of 0 or exactly 0.5
    //         if (event.pressure === 0 || event.pressure === 0.5) {
    //             this.advancedData.eventSourceTypes.push('synthetic_pressure');
    //         } else {
    //             this.advancedData.eventSourceTypes.push('real_pressure');
    //         }
    //     }
    // }

    handlePointerDown(event) {
        this.advancedData.pointerTypes.push(event.pointerType);
    }

    handlePointerMove(event) {
        const now = Date.now();
        
        // CRITICAL: Track pointer event trust
        this.advancedData.mouseEventTrust.push(event.isTrusted);
        this.advancedData.pointerTypes.push(event.pointerType);
        
        // Track if this is the first move (suspicious if no hover first)
        if (!this.pointerData.lastPointerMove && !this.pointerData.lastPointerDown) {
            this.pointerData.moveBeforeDown = true;
        }
        
        // Store detailed pointer data
        const position = {
            x: event.clientX,
            y: event.clientY,
            time: now,
            isTrusted: event.isTrusted,
            pointerType: event.pointerType,
            pressure: event.pressure,
            tiltX: event.tiltX,
            tiltY: event.tiltY,
            twist: event.twist,
            width: event.width,
            height: event.height,
            buttons: event.buttons,
            isPrimary: event.isPrimary
        };
        
        // CRITICAL: Track pressure values
        if (event.pressure !== undefined) {
            this.pointerData.pressureValues.push(event.pressure);
            
            if (event.pressure === 0 || event.pressure === 0.5) {
                this.advancedData.eventSourceTypes.push('synthetic_pressure');
            } else {
                this.advancedData.eventSourceTypes.push('real_pressure');
            }
        }
        
        // Track timing between events
        if (this.pointerData.lastPointerMove) {
            const delta = now - this.pointerData.lastPointerMove.time;
            this.pointerData.timingDeltas.push(delta);
            
            // Check for suspiciously regular timing (20ms, 30ms, 50ms intervals)
            if (this.pointerData.timingDeltas.length > 10) {
                const recent = this.pointerData.timingDeltas.slice(-10);
                const variance = this.calculateVariance(recent);
                if (variance < 5) {  // Very consistent timing
                    this.advancedData.eventSourceTypes.push('regular_timing');
                }
            }
        }
        
        // Do the same movement analysis as mouse events
        if (this.mouseData.lastPosition) {
            const last = this.mouseData.lastPosition;
            const dx = position.x - last.x;
            const dy = position.y - last.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const timeDelta = now - last.time;
            
            position.distance = distance;
            position.speed = timeDelta > 0 ? distance / timeDelta : 0;
            position.timeDelta = timeDelta;
            position.angle = Math.atan2(dy, dx);
            
            // CRITICAL: Check if distance is too uniform (bot uses fixed steps)
            if (distance > 0) {
                this.pointerData.perfectSteps.push(distance);
                
                if (this.pointerData.perfectSteps.length > 15) {
                    const recentSteps = this.pointerData.perfectSteps.slice(-15);
                    const stepVariance = this.calculateVariance(recentSteps);
                    const avgStep = recentSteps.reduce((a,b) => a+b) / recentSteps.length;
                    
                    // If steps are very uniform, it's a bot
                    if (stepVariance < avgStep * 0.05 && avgStep > 5) {
                        this.advancedData.eventSourceTypes.push('uniform_steps');
                    }
                }
            }
            
            if (last.speed !== undefined) {
                position.acceleration = timeDelta > 0 ? (position.speed - last.speed) / timeDelta : 0;
                this.advancedData.accelerationChanges.push(position.acceleration);
            }
            
            this.analyzeMovementPattern(position, last);
            this.mouseData.totalDistance += distance;
        }
        
        this.pointerData.lastPointerMove = position;
        this.mouseData.movements.push(position);
        this.mouseData.lastPosition = position;
        this.interactionData.lastInteraction = now;
        this.interactionData.totalEvents++;
        this.interactionData.eventTimestamps.push(now);
        
        this.pruneOldData();
    }

    handlePointerDown(event) {
        const now = Date.now();
        
        this.advancedData.pointerTypes.push(event.pointerType);
        this.advancedData.clickEventTrust.push(event.isTrusted);
        
        // CRITICAL: Check if pointer down happened without hover
        // Real users hover before clicking
        if (!this.pointerData.lastPointerMove) {
            this.pointerData.downWithoutHover++;
        }
        
        // Track pointer down with full details
        this.pointerData.lastPointerDown = {
            x: event.clientX,
            y: event.clientY,
            time: now,
            pressure: event.pressure
        };
        
        this.mouseData.clicks.push({
            x: event.clientX,
            y: event.clientY,
            time: now,
            isTrusted: event.isTrusted,
            pointerType: event.pointerType,
            pressure: event.pressure
        });
    }

    // Add this new analysis method
    analyzePointerBehavior() {
        if (this.pointerData.timingDeltas.length < 10) {
            return { score: 0, flags: [], insufficient: true };
        }

        const flags = [];
        let score = 0;

        // 1. Check for uniform step distances (CRITICAL for your bot)
        const uniformSteps = this.advancedData.eventSourceTypes.filter(
            t => t === 'uniform_steps'
        ).length;
        
        if (uniformSteps > 5) {
            score += 50;
            flags.push('UNIFORM_POINTER_STEPS');
        }

        // 2. Check for regular timing (20ms intervals from your bot's asyncio.sleep(0.02))
        const regularTiming = this.advancedData.eventSourceTypes.filter(
            t => t === 'regular_timing'
        ).length;
        
        if (regularTiming > 5) {
            score += 45;
            flags.push('REGULAR_POINTER_TIMING');
        }

        // 3. Check timing variance directly
        if (this.pointerData.timingDeltas.length > 15) {
            const variance = this.calculateVariance(this.pointerData.timingDeltas);
            if (variance < 10) {  // Less than 10ms variance
                score += 40;
                flags.push('MACHINE_POINTER_TIMING');
            }
        }

        // 4. Check for synthetic pressure
        const syntheticPressure = this.advancedData.eventSourceTypes.filter(
            t => t === 'synthetic_pressure'
        ).length;
        const totalPressureEvents = this.advancedData.eventSourceTypes.filter(
            t => t === 'synthetic_pressure' || t === 'real_pressure'
        ).length;
        
        if (totalPressureEvents > 10) {
            const syntheticRatio = syntheticPressure / totalPressureEvents;
            if (syntheticRatio > 0.8) {
                score += 35;
                flags.push('SYNTHETIC_POINTER_PRESSURE');
            }
        }

        // 5. Check pressure variance (real hands have varying pressure)
        if (this.pointerData.pressureValues.length > 20) {
            const pressureVariance = this.calculateVariance(this.pointerData.pressureValues);
            if (pressureVariance < 0.001) {  // Essentially constant
                score += 35;
                flags.push('CONSTANT_POINTER_PRESSURE');
            }
        }

        // 6. Check if pointer down happened without prior movement
        if (this.pointerData.downWithoutHover > 2) {
            score += 25;
            flags.push('POINTER_DOWN_WITHOUT_HOVER');
        }

        // 7. Check perfect step distances
        if (this.pointerData.perfectSteps.length > 20) {
            const stepVariance = this.calculateVariance(this.pointerData.perfectSteps);
            const avgStep = this.pointerData.perfectSteps.reduce((a,b) => a+b) / this.pointerData.perfectSteps.length;
            
            if (stepVariance < avgStep * 0.1 && avgStep > 5) {
                score += 40;
                flags.push('PERFECT_STEP_DISTANCES');
            }
        }

        // 8. Check for missing tilt/twist data (real stylus/touch has these)
        const movementsWithTilt = this.mouseData.movements.filter(
            m => m.tiltX !== undefined && m.tiltX !== 0
        ).length;
        
        if (this.mouseData.movements.length > 30 && movementsWithTilt === 0) {
            score += 15;
            flags.push('NO_POINTER_TILT_DATA');
        }

        return { score: Math.min(score, 100), flags };
    }

    // Update analyzeAndReport to include pointer analysis
    analyzeAndReport() {
        const mouseAnalysis = this.analyzeMouseBehavior();
        const clickAnalysis = this.analyzeClickBehavior();
        const keyboardAnalysis = this.analyzeKeyboardBehavior();
        const timingAnalysis = this.analyzeTimingBehavior();
        const pointerAnalysis = this.analyzePointerBehavior(); // ADD THIS

        const velocityAnalysis = this.velocityAnalyzer.velocityProfileAnalysis();
        const distanceAngleAnalysis = this.distanceAngleAnalyzer.analyzeDistanceAndAngle();

        // Update scores
        this.scores.mouse = mouseAnalysis.score;
        this.scores.behavior = clickAnalysis.score;
        this.scores.keyboard = keyboardAnalysis.score;
        this.scores.timing = timingAnalysis.score;
        this.scores.pointer = pointerAnalysis.score; // ADD THIS

        this.scores.velocity = velocityAnalyzer.score;
        this.scores.distanceAngle = distanceAngleAnalyzer.score;

        // Calculate weighted suspicion level
        let totalWeight = 0;
        let weightedScore = 0;

        weightedScore += this.scores.environment * 0.30;
        totalWeight += 0.30;

        weightedScore += this.scores.advanced * 0.10;
        totalWeight += 0.10;

        if (!mouseAnalysis.insufficient) {
            weightedScore += this.scores.mouse * 0.15;
            totalWeight += 0.15;
        }

        if (!pointerAnalysis.insufficient) {  // ADD THIS
            weightedScore += this.scores.pointer * 0.20;  // High weight!
            totalWeight += 0.20;
        }

        if (!velocityAnalysis.insufficient) {
            weightedScore += this.scores.velocity * 0.20;
            totalWeight += 0.20;
        }

        if (!distanceAngleAnalysis.insufficient) {
            weightedScore += this.scores.distanceAngle * 0.12;
            totalWeight += 0.12;
        }

        if (!clickAnalysis.insufficient) {
            weightedScore += this.scores.behavior * 0.15;
            totalWeight += 0.15;
        }

        if (!keyboardAnalysis.insufficient) {
            weightedScore += this.scores.keyboard * 0.05;
            totalWeight += 0.05;
        }

        weightedScore += this.scores.timing * 0.05;
        totalWeight += 0.05;

        this.suspicionLevel = totalWeight > 0 ? Math.round(weightedScore / totalWeight) : 0;

        // Collect all flags
        this.flags = [
            ...new Set([
                ...this.flags,
                ...mouseAnalysis.flags,
                ...clickAnalysis.flags,
                ...keyboardAnalysis.flags,
                ...timingAnalysis.flags,
                ...pointerAnalysis.flags,  // ADD THIS
                ...velocityAnalysis.flags,
                ...distanceAngleAnalysis.flags
            ])
        ];

        const result = this.getReport();
        this.log('Analysis complete:', result);

        if (this.suspicionLevel >= this.config.suspicionThreshold) {
            this.config.onSuspicion(result);
        } else {
            this.config.onClear(result);
        }

        return result;
    }

    // ==================== ADVANCED DETECTION ====================

    analyzeMovementPattern(current, last) {
        if (this.mouseData.movements.length >= 3) {
            const prev = this.mouseData.movements[this.mouseData.movements.length - 2];
            
            // Calculate angle change
            const angle1 = Math.atan2(last.y - prev.y, last.x - prev.x);
            const angle2 = Math.atan2(current.y - last.y, current.x - last.x);
            const angleDiff = Math.abs(angle1 - angle2);
            
            this.advancedData.movementPatterns.push({
                angleDiff,
                isLinear: angleDiff < 0.05 || angleDiff > Math.PI * 2 - 0.05,
                speed: current.speed,
                timeDelta: current.timeDelta
            });
        }

        // Analyze jitter (micro-movements from hand tremor)
        if (current.distance < 5 && current.distance > 0) {
            this.advancedData.jitterAnalysis.push({
                distance: current.distance,
                time: current.time
            });
        }
    }

    injectDetectionTraps() {
        // Trap 1: Detect if someone is overriding navigator.webdriver
        try {
            const descriptor = Object.getOwnPropertyDescriptor(navigator, 'webdriver');
            if (descriptor && (descriptor.get || descriptor.configurable === false)) {
                this.flags.push('WEBDRIVER_TAMPERED');
                this.scores.environment += 40;
            }
        } catch (e) {
            // Error accessing property often indicates tampering
            this.flags.push('WEBDRIVER_ACCESS_ERROR');
            this.scores.environment += 30;
        }

        // Trap 2: Check if webdriver was deleted/undefined but automation exists
        if (navigator.webdriver === undefined) {
            // Check for other automation indicators
            if (window.cdc_adoQpoasnfa76pfcZLmcfl_ ||
                document.$cdc_asdjflasutopfhvcZLmcfl_ ||
                window.__playwright ||
                window.__selenium_evaluate ||
                window.__driver_evaluate) {
                this.flags.push('HIDDEN_AUTOMATION_DETECTED');
                this.scores.environment += 50;
            }
        }

        // Trap 3: Monitor for programmatic function calls
        this.monitorProgrammaticCalls();

        // Trap 4: Detect Playwright's evaluate() calls
        this.detectPlaywrightEvaluate();
    }

    monitorProgrammaticCalls() {
        // Override click to detect programmatic clicks
        const originalClick = HTMLElement.prototype.click;
        const self = this;
        
        HTMLElement.prototype.click = function() {
            // Check call stack for automation signatures
            const stack = new Error().stack || '';
            if (stack.includes('evaluate') || 
                stack.includes('Runtime.evaluate') ||
                stack.includes('puppeteer') ||
                stack.includes('playwright')) {
                self.flags.push('PROGRAMMATIC_CLICK_DETECTED');
                self.scores.advanced += 30;
            }
            return originalClick.apply(this, arguments);
        };

        // Monitor for suspicious setTimeout patterns (bots use fixed delays)
        const originalSetTimeout = window.setTimeout;
        let timeoutDelays = [];
        
        window.setTimeout = function(callback, delay) {
            timeoutDelays.push(delay);
            
            // Check for suspiciously regular delays
            if (timeoutDelays.length > 5) {
                const recentDelays = timeoutDelays.slice(-5);
                const allSame = recentDelays.every(d => d === recentDelays[0]);
                if (allSame && delay > 0) {
                    self.flags.push('REGULAR_TIMEOUT_PATTERN');
                    self.scores.advanced += 10;
                }
                timeoutDelays = timeoutDelays.slice(-20);
            }
            
            return originalSetTimeout.apply(this, arguments);
        };
    }

    detectPlaywrightEvaluate() {
        // Playwright's evaluate() leaves traces
        // Check for specific global variables it might create
        
        const suspiciousGlobals = [
            '__playwright',
            '__pw_manual',
            '__pwInitScripts',
            '__REACT_DEVTOOLS_GLOBAL_HOOK__', // Often disabled in automation
        ];

        for (const global of suspiciousGlobals) {
            if (window[global] !== undefined) {
                this.flags.push(`SUSPICIOUS_GLOBAL_${global}`);
                this.scores.environment += 20;
            }
        }

        // Check for modified prototype chain
        if (Document.prototype.hasOwnProperty('$cdc_asdjflasutopfhvcZLmcfl_')) {
            this.flags.push('CHROMEDRIVER_DETECTED');
            this.scores.environment += 50;
        }
    }

    runEnvironmentChecks() {
        // 1. Comprehensive webdriver detection
        this.checkWebdriver();
        
        // 2. Headless browser detection
        this.checkHeadless();
        
        // 3. Automation framework detection
        this.checkAutomationFrameworks();
        
        // 4. Browser fingerprint anomalies
        this.checkBrowserAnomalies();
        
        // 5. Check for DevTools protocol
        this.checkDevToolsProtocol();
    }

    checkWebdriver() {
        // Multiple ways to detect webdriver
        const checks = [
            () => navigator.webdriver === true,
            () => {
                try {
                    const desc = Object.getOwnPropertyDescriptor(navigator, 'webdriver');
                    return desc && typeof desc.get === 'function';
                } catch { return false; }
            },
            () => 'webdriver' in navigator && navigator.webdriver !== false,
            () => document.documentElement.getAttribute('webdriver') !== null,
            () => window.callPhantom !== undefined,
            () => window._phantom !== undefined,
        ];

        let webdriverScore = 0;
        for (const check of checks) {
            try {
                if (check()) webdriverScore += 15;
            } catch {}
        }

        if (webdriverScore > 0) {
            this.flags.push('WEBDRIVER_INDICATORS');
            this.scores.environment += Math.min(webdriverScore, 50);
        }
    }

    checkHeadless() {
        const checks = [
            // User agent checks
            /HeadlessChrome/.test(navigator.userAgent),
            /Headless/.test(navigator.userAgent),
            
            // Plugin checks
            navigator.plugins.length === 0,
            
            // Language checks
            !navigator.languages || navigator.languages.length === 0,
            
            // WebGL checks
            (() => {
                try {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl');
                    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                    return renderer.includes('SwiftShader') || renderer.includes('llvmpipe');
                } catch { return false; }
            })(),
            
            // Chrome without chrome object
            navigator.userAgent.includes('Chrome') && !window.chrome,
            
            // Permissions API
            navigator.permissions === undefined,
            
            // Missing browser features
            !window.Notification,
        ];

        const headlessScore = checks.filter(Boolean).length * 10;
        if (headlessScore > 20) {
            this.flags.push('HEADLESS_BROWSER_INDICATORS');
            this.scores.environment += Math.min(headlessScore, 40);
        }
    }

    checkAutomationFrameworks() {
        const automationIndicators = {
            // Selenium
            'document.__selenium_unwrapped': document.__selenium_unwrapped,
            'document.__webdriver_evaluate': document.__webdriver_evaluate,
            'document.__driver_evaluate': document.__driver_evaluate,
            'document.$cdc_asdjflasutopfhvcZLmcfl_': document.$cdc_asdjflasutopfhvcZLmcfl_,
            
            // Puppeteer
            'window.puppeteer': window.puppeteer,
            
            // Playwright
            'window.__playwright': window.__playwright,
            'window.__pw_manual': window.__pw_manual,
            
            // Cypress
            'window.Cypress': window.Cypress,
            
            // Generic automation
            'window.domAutomation': window.domAutomation,
            'window.domAutomationController': window.domAutomationController,
            
            // Nightmare
            'window.__nightmare': window.__nightmare,
        };

        for (const [name, value] of Object.entries(automationIndicators)) {
            if (value !== undefined) {
                this.flags.push(`AUTOMATION_${name.split('.').pop().toUpperCase()}`);
                this.scores.environment += 40;
            }
        }
    }

    checkBrowserAnomalies() {
        // Screen dimension anomalies
        if (window.outerWidth === 0 || window.outerHeight === 0) {
            this.flags.push('ZERO_WINDOW_DIMENSIONS');
            this.scores.environment += 30;
        }

        // Check for unusual screen dimensions typical of headless
        if (screen.width === 800 && screen.height === 600) {
            this.flags.push('DEFAULT_HEADLESS_DIMENSIONS');
            this.scores.environment += 20;
        }

        // Chrome-specific checks
        if (window.chrome) {
            if (!window.chrome.runtime) {
                this.flags.push('MISSING_CHROME_RUNTIME');
                this.scores.environment += 15;
            }
        }

        // Check for consistent timing (bots often have very precise timing)
        const now = performance.now();
        const times = [];
        for (let i = 0; i < 10; i++) {
            times.push(performance.now() - now);
        }
        const variance = this.calculateVariance(times);
        if (variance === 0) {
            this.flags.push('ZERO_TIMING_VARIANCE');
            this.scores.environment += 15;
        }
    }

    checkDevToolsProtocol() {
        // Check if CDP (Chrome DevTools Protocol) is being used
        try {
            // Debugger statement detection
            const start = performance.now();
            // debugger;
            const end = performance.now();
            
            // If debugger was hit (DevTools open), this takes time
            // But automation tools might skip it
            if (end - start < 0.1) {
                // Extremely fast = possibly automation
                this.advancedData.eventSourceTypes.push('fast_debugger');
            }
        } catch {}
    }

    // ==================== ANALYSIS METHODS ====================

    analyzeMouseBehavior() {
        const movements = this.mouseData.movements;
        if (movements.length < 10) {
            return { score: 0, flags: [], insufficient: true };
        }

        const flags = [];
        let score = 0;

        // 1. Check event trust ratio
        const trustedCount = this.advancedData.mouseEventTrust.filter(t => t).length;
        const totalEvents = this.advancedData.mouseEventTrust.length;
        const trustRatio = totalEvents > 0 ? trustedCount / totalEvents : 1;
        
        if (trustRatio < 0.9 && totalEvents > 20) {
            score += 40;
            flags.push('LOW_TRUSTED_EVENTS');
        }

        // 2. Check for missing micro-movements (jitter)
        const jitterCount = this.advancedData.jitterAnalysis.length;
        const jitterRatio = movements.length > 0 ? jitterCount / movements.length : 0;
        
        if (jitterRatio < 0.05 && movements.length > 50) {
            score += 25;
            flags.push('NO_NATURAL_JITTER');
        }

        // 3. Check for linear movement patterns
        const linearMoves = this.advancedData.movementPatterns.filter(p => p.isLinear).length;
        const linearRatio = this.advancedData.movementPatterns.length > 0 
            ? linearMoves / this.advancedData.movementPatterns.length : 0;
        
        if (linearRatio > 0.7 && this.advancedData.movementPatterns.length > 20) {
            score += 30;
            flags.push('TOO_LINEAR_MOVEMENT');
        }

        // 4. Check acceleration variance
        if (this.advancedData.accelerationChanges.length > 10) {
            const accVariance = this.calculateVariance(this.advancedData.accelerationChanges);
            if (accVariance < 0.0001) {
                score += 20;
                flags.push('CONSTANT_ACCELERATION');
            }
        }

        // 5. Check for perfectly stepped movements (Playwright uses steps parameter)
        const distances = movements.filter(m => m.distance).map(m => m.distance);
        if (distances.length > 10) {
            const distanceVariance = this.calculateVariance(distances);
            const avgDistance = distances.reduce((a, b) => a + b, 0) / distances.length;
            
            // Very low variance in step distances is suspicious
            if (distanceVariance < avgDistance * 0.1 && avgDistance > 5) {
                score += 25;
                flags.push('UNIFORM_STEP_DISTANCE');
            }
        }

        // 6. Check speed patterns
        const speeds = movements.filter(m => m.speed).map(m => m.speed);
        if (speeds.length > 10) {
            const speedVariance = this.calculateVariance(speeds);
            if (speedVariance < 0.01) {
                score += 20;
                flags.push('CONSTANT_SPEED');
            }
        }

        return { score: Math.min(score, 100), flags };
    }

    analyzeClickBehavior() {
        const clicks = this.mouseData.clicks;
        if (clicks.length < 3) {
            return { score: 0, flags: [], insufficient: true };
        }

        const flags = [];
        let score = 0;

        // 1. Check click trust
        const trustedClicks = this.advancedData.clickEventTrust.filter(t => t).length;
        const clickTrustRatio = this.advancedData.clickEventTrust.length > 0 
            ? trustedClicks / this.advancedData.clickEventTrust.length : 1;
        
        if (clickTrustRatio < 0.9 && clicks.length > 5) {
            score += 35;
            flags.push('UNTRUSTED_CLICKS');
        }

        // 2. Check click timing regularity
        if (this.clickData.clickTimingPattern.length > 3) {
            const timingVariance = this.calculateVariance(this.clickData.clickTimingPattern);
            if (timingVariance < 1000) {
                score += 25;
                flags.push('REGULAR_CLICK_TIMING');
            }
        }

        // 3. Check for clicks without preceding mouse movement
        let clicksWithoutMovement = 0;
        for (const click of clicks) {
            const precedingMovements = this.mouseData.movements.filter(
                m => m.time < click.time && m.time > click.time - 500
            );
            if (precedingMovements.length < 3) {
                clicksWithoutMovement++;
            }
        }
        
        const teleportRatio = clicksWithoutMovement / clicks.length;
        if (teleportRatio > 0.5 && clicks.length > 5) {
            score += 30;
            flags.push('TELEPORTING_CLICKS');
        }

        return { score: Math.min(score, 100), flags };
    }

    analyzeKeyboardBehavior() {
        if (!this.keyboardData.hasRealKeyboard || this.keyboardData.keystrokePattern.length < 5) {
            // No keyboard interaction might be suspicious for CAPTCHA
            if (this.interactionData.totalEvents > 50 && !this.keyboardData.hasRealKeyboard) {
                return { 
                    score: 15, 
                    flags: ['NO_KEYBOARD_INTERACTION'],
                    insufficient: false 
                };
            }
            return { score: 0, flags: [], insufficient: true };
        }

        const flags = [];
        let score = 0;

        // Check key event trust
        const trustedKeys = this.advancedData.keyEventTrust.filter(t => t).length;
        const keyTrustRatio = this.advancedData.keyEventTrust.length > 0
            ? trustedKeys / this.advancedData.keyEventTrust.length : 1;
        
        if (keyTrustRatio < 0.9) {
            score += 30;
            flags.push('UNTRUSTED_KEY_EVENTS');
        }

        // Check timing patterns
        if (this.keyboardData.interKeyIntervals.length > 5) {
            const variance = this.calculateVariance(this.keyboardData.interKeyIntervals);
            if (variance < 100) {
                score += 25;
                flags.push('ROBOTIC_TYPING');
            }
        }

        return { score: Math.min(score, 100), flags };
    }

    analyzeTimingBehavior() {
        const flags = [];
        let score = 0;

        // Check event timing regularity
        if (this.interactionData.eventTimestamps.length > 20) {
            const intervals = [];
            for (let i = 1; i < this.interactionData.eventTimestamps.length; i++) {
                intervals.push(
                    this.interactionData.eventTimestamps[i] - 
                    this.interactionData.eventTimestamps[i-1]
                );
            }
            
            const variance = this.calculateVariance(intervals);
            if (variance < 10) {
                score += 30;
                flags.push('MACHINE_TIMING');
            }
        }

        // Check for suspicious session patterns
        const sessionDuration = Date.now() - this.interactionData.firstInteraction;
        const eventsPerSecond = this.interactionData.totalEvents / (sessionDuration / 1000);
        
        // Very consistent event rate is suspicious
        if (eventsPerSecond > 50) {
            score += 20;
            flags.push('HIGH_EVENT_RATE');
        }

        return { score: Math.min(score, 100), flags };
    }

    // ==================== HELPERS ====================

    calculateVariance(values) {
        if (values.length < 2) return 0;
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const squaredDiffs = values.map(v => Math.pow(v - mean, 2));
        return squaredDiffs.reduce((a, b) => a + b, 0) / values.length;
    }

    pruneOldData() {
        const cutoff = Date.now() - this.config.analysisWindow;
        this.mouseData.movements = this.mouseData.movements.filter(m => m.time > cutoff);
        this.mouseData.clicks = this.mouseData.clicks.filter(c => c.time > cutoff);
        this.interactionData.eventTimestamps = this.interactionData.eventTimestamps.filter(t => t > cutoff);
    }

    // ==================== REPORTING ====================

    analyzeAndReport() {
        const mouseAnalysis = this.analyzeMouseBehavior();
        const clickAnalysis = this.analyzeClickBehavior();
        const keyboardAnalysis = this.analyzeKeyboardBehavior();
        const timingAnalysis = this.analyzeTimingBehavior();

        // Update scores
        this.scores.mouse = mouseAnalysis.score;
        this.scores.behavior = clickAnalysis.score;
        this.scores.keyboard = keyboardAnalysis.score;
        this.scores.timing = timingAnalysis.score;

        // Calculate weighted suspicion level
        let totalWeight = 0;
        let weightedScore = 0;

        // Environment is always weighted heavily
        weightedScore += this.scores.environment * 0.35;
        totalWeight += 0.35;

        // Advanced detection
        weightedScore += this.scores.advanced * 0.15;
        totalWeight += 0.15;

        if (!mouseAnalysis.insufficient) {
            weightedScore += this.scores.mouse * 0.20;
            totalWeight += 0.20;
        }

        if (!clickAnalysis.insufficient) {
            weightedScore += this.scores.behavior * 0.15;
            totalWeight += 0.15;
        }

        if (!keyboardAnalysis.insufficient) {
            weightedScore += this.scores.keyboard * 0.10;
            totalWeight += 0.10;
        }

        weightedScore += this.scores.timing * 0.05;
        totalWeight += 0.05;

        this.suspicionLevel = totalWeight > 0 ? Math.round(weightedScore / totalWeight) : 0;

        // Collect all flags
        this.flags = [
            ...new Set([
                ...this.flags,
                ...mouseAnalysis.flags,
                ...clickAnalysis.flags,
                ...keyboardAnalysis.flags,
                ...timingAnalysis.flags
            ])
        ];

        const result = this.getReport();
        this.log('Analysis complete:', result);

        if (this.suspicionLevel >= this.config.suspicionThreshold) {
            this.config.onSuspicion(result);
        } else {
            this.config.onClear(result);
        }

        return result;
    }

    getReport() {
        return {
            isBot: this.suspicionLevel >= this.config.suspicionThreshold,
            suspicionLevel: this.suspicionLevel,
            scores: { ...this.scores },
            flags: [...this.flags],
            dataPoints: {
                mouseMovements: this.mouseData.movements.length,
                clicks: this.mouseData.clicks.length,
                keystrokes: this.keyboardData.keystrokePattern.length,
                trustedEvents: this.advancedData.mouseEventTrust.filter(t => t).length,
                untrustedEvents: this.advancedData.mouseEventTrust.filter(t => !t).length
            },
            sessionDuration: Date.now() - this.interactionData.firstInteraction,
            timestamp: Date.now()
        };
    }

    forceAnalysis() {
        return this.analyzeAndReport();
    }

    getSuspicionLevel() {
        return this.suspicionLevel;
    }

    isBot() {
        return this.suspicionLevel >= this.config.suspicionThreshold;
    }

    defaultSuspicionHandler(report) {
        console.warn('🤖 Bot detected!', report);
    }

    log(...args) {
        if (this.config.debug) {
            console.log('[BotDetector]', ...args);
        }
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BotDetector;
}
window.BotDetector = BotDetector;