// Wait for DOM and Matter.js to load
window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('puzzle-canvas');
    const submitBtn = document.getElementById('submit-btn');
    const statusMessage = document.getElementById('status-message');
    
    const width = 800;
    const height = 600;
    
    // Set canvas size
    canvas.width = width;
    canvas.height = height;

    // Matter.js aliases
    const Engine = Matter.Engine;
    const Render = Matter.Render;
    const World = Matter.World;
    const Bodies = Matter.Bodies;
    const Mouse = Matter.Mouse;
    const MouseConstraint = Matter.MouseConstraint;
    const Events = Matter.Events;
    const Constraint = Matter.Constraint;

    // Create engine with no gravity
    const engine = Engine.create({
        gravity: { x: 0, y: 0 }
    });

    // Create renderer
    const render = Render.create({
        canvas: canvas,
        engine: engine,
        options: {
            width: width,
            height: height,
            wireframes: false,
            background: '#f5f5f5'
        }
    });

    // Create boundaries (walls)
    const wallThickness = 50;
    const walls = [
        Bodies.rectangle(width / 2, -wallThickness / 2, width, wallThickness, {
            isStatic: true,
            render: { fillStyle: '#cccccc', visible: false }
        }),
        Bodies.rectangle(width / 2, height + wallThickness / 2, width, wallThickness, {
            isStatic: true,
            render: { fillStyle: '#cccccc', visible: false }
        }),
        Bodies.rectangle(-wallThickness / 2, height / 2, wallThickness, height, {
            isStatic: true,
            render: { fillStyle: '#cccccc', visible: false }
        }),
        Bodies.rectangle(width + wallThickness / 2, height / 2, wallThickness, height, {
            isStatic: true,
            render: { fillStyle: '#cccccc', visible: false }
        })
    ];

    World.add(engine.world, walls);

    // Target positions for a simple box (center-right)
    // Box is 100x100, made of 4 pieces (top, bottom, left, right)
    const targetX = 600;
    const targetY = 300;
    const pieceLength = 100;
    const pieceThickness = 10;
    
    const targets = {
        top: { x: targetX, y: targetY - 50, width: pieceLength, height: pieceThickness, color: '#8B4513', angle: 0 },
        bottom: { x: targetX, y: targetY + 50, width: pieceLength, height: pieceThickness, color: '#A0522D', angle: 0 },
        left: { x: targetX - 50, y: targetY, width: pieceThickness, height: pieceLength, color: '#654321', angle: 0 },
        right: { x: targetX + 50, y: targetY, width: pieceThickness, height: pieceLength, color: '#8B7355', angle: 0 }
    };

    // Rotation settings
    const ROTATION_INCREMENT = 15 * (Math.PI / 180); // 15 degrees in radians
    const CLICK_THRESHOLD = 200; // milliseconds - short click vs long click
    const MAGNETIC_DISTANCE = 40; // Distance at which edges start attracting
    const MAGNETIC_STRENGTH = 0.00015; // Strength of magnetic attraction

    // Helper function to snap angle to nearest increment
    function snapAngleToIncrement(angle) {
        const normalized = ((angle % (2 * Math.PI)) + (2 * Math.PI)) % (2 * Math.PI);
        const steps = Math.round(normalized / ROTATION_INCREMENT);
        return steps * ROTATION_INCREMENT;
    }

    // Create scattered box parts (left side) - all start with snapped angles
    const parts = [];
    
    const top = Bodies.rectangle(150, 150, pieceLength, pieceThickness, {
        render: { fillStyle: '#8B4513' },
        label: 'top',
        friction: 0.8,
        frictionAir: 0.05,
        frictionStatic: 1.0,
        restitution: 0.1,
        density: 0.001,
        inertia: Infinity
    });
    Matter.Body.setAngle(top, snapAngleToIncrement(Math.random() * Math.PI));
    parts.push({ body: top, target: targets.top, assembled: false });

    const bottom = Bodies.rectangle(200, 250, pieceLength, pieceThickness, {
        render: { fillStyle: '#A0522D' },
        label: 'bottom',
        friction: 0.8,
        frictionAir: 0.05,
        frictionStatic: 1.0,
        restitution: 0.1,
        density: 0.001,
        inertia: Infinity
    });
    Matter.Body.setAngle(bottom, snapAngleToIncrement(Math.random() * Math.PI));
    parts.push({ body: bottom, target: targets.bottom, assembled: false });

    const left = Bodies.rectangle(120, 350, pieceThickness, pieceLength, {
        render: { fillStyle: '#654321' },
        label: 'left',
        friction: 0.8,
        frictionAir: 0.05,
        frictionStatic: 1.0,
        restitution: 0.1,
        density: 0.001,
        inertia: Infinity
    });
    Matter.Body.setAngle(left, snapAngleToIncrement(Math.random() * Math.PI));
    parts.push({ body: left, target: targets.left, assembled: false });

    const right = Bodies.rectangle(180, 450, pieceThickness, pieceLength, {
        render: { fillStyle: '#8B7355' },
        label: 'right',
        friction: 0.8,
        frictionAir: 0.05,
        frictionStatic: 1.0,
        restitution: 0.1,
        density: 0.001,
        inertia: Infinity
    });
    Matter.Body.setAngle(right, snapAngleToIncrement(Math.random() * Math.PI));
    parts.push({ body: right, target: targets.right, assembled: false });

    // Add all parts to world
    World.add(engine.world, parts.map(p => p.body));

    // Mouse control - disabled by default, we'll handle clicks manually
    const mouse = Mouse.create(canvas);
    const mouseConstraint = MouseConstraint.create(engine, {
        mouse: mouse,
        constraint: {
            stiffness: 0.2,
            render: { visible: false }
        }
    });

    // Disable the mouse constraint initially
    mouseConstraint.constraint.stiffness = 0;
    World.add(engine.world, mouseConstraint);

    // Click handling
    let mouseDownTime = 0;
    let mouseDownPos = { x: 0, y: 0 };
    let clickedBody = null;
    let isDragging = false;

    canvas.addEventListener('mousedown', (event) => {
        mouseDownTime = Date.now();
        mouseDownPos = { x: event.offsetX, y: event.offsetY };
        
        // Check if clicking on a piece
        const bodies = Matter.Query.point(parts.map(p => p.body), { x: event.offsetX, y: event.offsetY });
        if (bodies.length > 0) {
            clickedBody = bodies[0];
        }
    });

    canvas.addEventListener('mousemove', (event) => {
        if (clickedBody && !isDragging) {
            const dx = event.offsetX - mouseDownPos.x;
            const dy = event.offsetY - mouseDownPos.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 5) {
                const elapsed = Date.now() - mouseDownTime;
                if (elapsed > CLICK_THRESHOLD) {
                    isDragging = true;
                    mouseConstraint.constraint.stiffness = 0.2;
                }
            }
        }
    });

    canvas.addEventListener('mouseup', (event) => {
        const clickDuration = Date.now() - mouseDownTime;
        const dx = event.offsetX - mouseDownPos.x;
        const dy = event.offsetY - mouseDownPos.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Short click with minimal movement = rotate
        if (clickedBody && !isDragging && clickDuration < CLICK_THRESHOLD && distance < 5) {
            const part = parts.find(p => p.body === clickedBody);
            if (part && !part.assembled) {
                const currentAngle = clickedBody.angle;
                const newAngle = snapAngleToIncrement(currentAngle + ROTATION_INCREMENT);
                Matter.Body.setAngle(clickedBody, newAngle);
                Matter.Body.setAngularVelocity(clickedBody, 0);
            }
        }

        isDragging = false;
        mouseConstraint.constraint.stiffness = 0;
        clickedBody = null;
    });

    // Magnetic edge snapping - apply forces to attract nearby edges
    Events.on(engine, 'beforeUpdate', () => {
        parts.forEach(part => {
            if (!part.assembled) {
                // Stop any angular velocity
                Matter.Body.setAngularVelocity(part.body, 0);
                
                // Snap angle if not being dragged
                if (!isDragging || clickedBody !== part.body) {
                    const snappedAngle = snapAngleToIncrement(part.body.angle);
                    if (Math.abs(part.body.angle - snappedAngle) > 0.01) {
                        Matter.Body.setAngle(part.body, snappedAngle);
                    }
                }

                // Apply magnetic forces between piece edges only
                if (clickedBody !== part.body) {
                    parts.forEach(otherPart => {
                        if (otherPart !== part && !otherPart.assembled) {
                            // Get the edges (endpoints) of each piece
                            const getEdges = (body) => {
                                const bounds = body.bounds;
                                const cos = Math.cos(body.angle);
                                const sin = Math.sin(body.angle);
                                
                                // For rectangles, get the 4 edge midpoints
                                const halfWidth = (bounds.max.x - bounds.min.x) / 2;
                                const halfHeight = (bounds.max.y - bounds.min.y) / 2;
                                
                                return [
                                    // Top edge
                                    { x: body.position.x - halfHeight * sin, y: body.position.y + halfHeight * cos },
                                    // Bottom edge
                                    { x: body.position.x + halfHeight * sin, y: body.position.y - halfHeight * cos },
                                    // Left edge
                                    { x: body.position.x - halfWidth * cos, y: body.position.y - halfWidth * sin },
                                    // Right edge
                                    { x: body.position.x + halfWidth * cos, y: body.position.y + halfWidth * sin }
                                ];
                            };
                            
                            const edges1 = getEdges(part.body);
                            const edges2 = getEdges(otherPart.body);
                            
                            // Check each edge of part against each edge of otherPart
                            let closestDistance = Infinity;
                            let closestForce = { x: 0, y: 0 };
                            
                            edges1.forEach(edge1 => {
                                edges2.forEach(edge2 => {
                                    const dx = edge2.x - edge1.x;
                                    const dy = edge2.y - edge1.y;
                                    const distance = Math.sqrt(dx * dx + dy * dy);
                                    
                                    // Only consider edges that are close enough
                                    if (distance < MAGNETIC_DISTANCE && distance < closestDistance) {
                                        closestDistance = distance;
                                        
                                        // Calculate magnetic force between these specific edges
                                        const forceMagnitude = MAGNETIC_STRENGTH * (MAGNETIC_DISTANCE - distance) / Math.max(distance, 1);
                                        closestForce = {
                                            x: dx * forceMagnitude,
                                            y: dy * forceMagnitude
                                        };
                                    }
                                });
                            });
                            
                            // Apply the strongest edge-to-edge force found
                            if (closestDistance < MAGNETIC_DISTANCE) {
                                Matter.Body.applyForce(part.body, part.body.position, closestForce);
                            }
                        }
                    });
                }
            }
        });
    });

    // Snap tolerance for final assembly
    const snapDistance = 25;
    const snapAngle = 0.3;

    let isComplete = false;

    // Check assembly on every update
    Events.on(engine, 'afterUpdate', () => {
        let allAssembled = true;

        parts.forEach(part => {
            const { body, target } = part;
            const dx = body.position.x - target.x;
            const dy = body.position.y - target.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            const normalizeAngle = (angle) => {
                while (angle > Math.PI) angle -= 2 * Math.PI;
                while (angle < -Math.PI) angle += 2 * Math.PI;
                return angle;
            };
            
            const angleDiff = Math.abs(normalizeAngle(body.angle - target.angle));

            if (distance < snapDistance && angleDiff < snapAngle) {
                Matter.Body.setPosition(body, { x: target.x, y: target.y });
                Matter.Body.setAngle(body, target.angle);
                Matter.Body.setStatic(body, true);
                body.render.fillStyle = '#228B22';
                part.assembled = true;
            } else {
                if (part.assembled) {
                    Matter.Body.setStatic(body, false);
                    body.render.fillStyle = target.color;
                    part.assembled = false;
                }
                allAssembled = false;
            }
        });

        if (allAssembled && !isComplete) {
            isComplete = true;
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit';
            statusMessage.textContent = '✓ Box assembled correctly!';
        } else if (!allAssembled && isComplete) {
            isComplete = false;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Complete Assembly First';
            statusMessage.textContent = '';
        }
    });

    // Submit button handler
    submitBtn.addEventListener('click', () => {
        if (isComplete) {
            window.location.href = '/success';
        }
    });

    // Run the engine and renderer
    Engine.run(engine);
    Render.run(render);
});