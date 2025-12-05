#!/usr/bin/env python3
# Authors - Sriram, Yuxin and Liwei
"""
Advanced CAPTCHA Bot Attacker - Playwright Async Implementation (FIXED SLIDER LOGIC)
Intelligently solves all 3 CAPTCHA types: Candy Match, Maze, and Slider
Usage: python3 advanced_captcha_attacker_FIXED.py --url https://exam-portal-captcha-test.web.app/
"""

import argparse
import time
import asyncio
from collections import deque
from playwright.async_api import async_playwright

GRID_DIM = 3  # 3x3 for Candy Crush


class AdvancedCAPTCHAAttacker:
    def __init__(self, url):
        self.url = url
        self.browser = None
        self.page = None
        self.stats = {
            'attempts': 0,
            'candy_solved': 0,
            'maze_solved': 0,
            'slider_solved': 0,
            'total_success': 0,
            'failures': 0,
            'start_time': time.time()
        }

    async def init(self):
        """Initialize browser with stealth settings"""
        print("🤖 Initializing Advanced CAPTCHA Attacker (Playwright Async)...")
        
        p = await async_playwright().start()
        
        # Use Chromium for best compatibility
        self.browser = await p.chromium.launch(
            headless=False,
            slow_mo=50,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        self.page = await self.browser.new_page()
        
        # Apply stealth: change navigator.webdriver
        await self.page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"🌐 Navigating to: {self.url}")
        await self.page.goto(self.url)
        
        # Wait for page load
        await self.page.wait_for_selector("#verifyBtn", timeout=10000)
        await asyncio.sleep(2)
        print("✅ CAPTCHA system loaded")

    # ==================== CANDY CRUSH SOLVER ====================
    
    async def find_grid_cells(self):
        """Find the 3x3 grid structure and its symbols using Playwright locators."""
        try:
            # 1. Locate all 9 grid cells first
            all_cells_locator = self.page.locator("#gridContainer .grid-row .grid-cell")
            cells_count = await all_cells_locator.count()

            if cells_count != GRID_DIM * GRID_DIM:
                print(f"   ⚠️ Expected 9 cells, found {cells_count}.")
                return None, None
            
            # 2. Structure the locators into a 3x3 array
            grid_cells = []
            for r in range(GRID_DIM):
                row = []
                for c in range(GRID_DIM):
                    locator = self.page.locator(f".grid-row:nth-child({r + 1}) > .grid-cell:nth-child({c + 1})")
                    row.append(locator)
                grid_cells.append(row)
            
            # 3. Read symbols and classes
            symbols = []
            for r in range(GRID_DIM):
                row_symbols = []
                for c in range(GRID_DIM):
                    cell_locator = grid_cells[r][c]
                    
                    cell_data = await cell_locator.evaluate("""
                        (el) => ({
                            text: el.textContent.trim() || '?',
                            classes: el.className
                        })
                    """)
                    
                    if "hidden-cell" in cell_data['classes']:
                        row_symbols.append("?")
                    else:
                        row_symbols.append(cell_data['text'])

                symbols.append(row_symbols)
            
            return grid_cells, symbols
        
        except Exception as e:
            print(f"   ❌ Error in find_grid_cells: {e}")
            return None, None

    async def reveal_all_hidden_cells(self):
        """Click all cells with '?' to reveal them"""
        print("   🔍 Revealing hidden cells...")
        max_attempts = 10
        
        for attempt in range(max_attempts):
            hidden_cells_count = await self.page.evaluate("""
                () => {
                    const hiddenCells = document.querySelectorAll(".grid-cell.hidden-cell");
                    if (hiddenCells.length > 0) {
                        hiddenCells[0].click();
                        return hiddenCells.length;
                    }
                    return 0;
                }
            """)

            if hidden_cells_count == 0:
                print("   ✅ All cells revealed")
                return

            await asyncio.sleep(0.3)

        print("   ⚠️  Some cells may remain hidden")

    def has_three_in_row(self, grid):
        """Check if grid has 3 in a row (horizontal or vertical)"""
        # Check rows
        for r in range(GRID_DIM):
            if grid[r][0] == grid[r][1] == grid[r][2] and grid[r][0] != "?":
                return True
        
        # Check columns
        for c in range(GRID_DIM):
            if grid[0][c] == grid[1][c] == grid[2][c] and grid[0][c] != "?":
                return True
        
        return False

    def find_candy_solution_bfs(self, symbols, max_depth=5):
        """Use BFS to find shortest swap sequence"""
        def flatten(mat):
            return tuple(x for row in mat for x in row)
        
        def unflatten(f):
            return [list(f[i * GRID_DIM:(i + 1) * GRID_DIM]) for i in range(GRID_DIM)]
        
        start = flatten(symbols)
        
        # Generate all valid adjacent pairs
        neighbors = []
        for r in range(GRID_DIM):
            for c in range(GRID_DIM):
                idx = r * GRID_DIM + c
                if c + 1 < GRID_DIM:
                    neighbors.append((idx, idx + 1))
                if r + 1 < GRID_DIM:
                    neighbors.append((idx, idx + GRID_DIM))
        
        if self.has_three_in_row(symbols):
            return []
        
        queue = deque()
        queue.append((start, []))
        seen = {start}
        
        while queue:
            current, moves = queue.popleft()
            
            if len(moves) >= max_depth:
                continue
            
            for a, b in neighbors:
                lst = list(current)
                lst[a], lst[b] = lst[b], lst[a]
                new_state = tuple(lst)
                
                if new_state in seen:
                    continue
                
                seen.add(new_state)
                new_moves = moves + [(a, b)]
                new_grid = unflatten(new_state)
                
                if self.has_three_in_row(new_grid):
                    return new_moves
                
                queue.append((new_state, new_moves))
        
        raise RuntimeError("No solution found within depth limit")

    async def execute_swap(self, a, b):
        """Execute a swap between two cells"""
        r1, c1 = divmod(a, GRID_DIM)
        r2, c2 = divmod(b, GRID_DIM)
        
        grid_cells, _ = await self.find_grid_cells()
        if not grid_cells:
            raise RuntimeError("Grid disappeared")
        
        cell1 = grid_cells[r1][c1]
        
        if 'locked-cell' in await cell1.get_attribute('class'):
             raise RuntimeError(f"Cell ({r1},{c1}) is locked")

        await cell1.click()
        await asyncio.sleep(0.3)
        
        grid_cells, _ = await self.find_grid_cells()
        if not grid_cells:
            raise RuntimeError("Grid disappeared after first click")

        cell2 = grid_cells[r2][c2]
        
        if 'locked-cell' in await cell2.get_attribute('class'):
            raise RuntimeError(f"Cell ({r2},{c2}) is locked")

        await cell2.click()
        await asyncio.sleep(0.5)

    async def solve_candy_crush(self):
        """Main candy crush solving logic"""
        print("\n🍬 Solving Candy Match CAPTCHA...")
        
        try:
            await self.page.wait_for_selector("#verificationModal:visible", timeout=10000)
            await asyncio.sleep(1)
            
            await self.reveal_all_hidden_cells()
            
            _, symbols = await self.find_grid_cells()
            if not symbols:
                print("❌ Grid not found or is malformed")
                return False
            
            print("   Initial grid:")
            for row in symbols:
                print(f"   {row}")
            
            print("   🧠 Computing optimal solution...")
            moves = self.find_candy_solution_bfs(symbols, max_depth=5)
            
            print(f"   📋 Solution found: {len(moves)} moves")
            print(f"   Swap sequence: {moves}")
            
            for i, (a, b) in enumerate(moves):
                print(f" Move {i+1}/{len(moves)}: Swap cells {a} ↔ {b}")
                try:
                    await self.execute_swap(a, b)
                except RuntimeError as e:
                    print(f" ⚠️ {e}, trying alternative...")
                    await self.page.click("#refreshBtn")
                    await asyncio.sleep(1)
                    return await self.solve_candy_crush()

                try:
                    await self.page.wait_for_selector("#successMessage", timeout=3000)
                    print(f" 🎉 CAPTCHA solved early after move {i+1}")
                    self.stats['candy_solved'] += 1
                    await asyncio.sleep(2)
                    return True
                except Exception:
                    pass

                await asyncio.sleep(0.5)

            try:
                success_msg = self.page.locator("#successMessage:visible")
                await success_msg.wait_for(timeout=3000)
                print(" ✅ Candy Match SOLVED!")
                self.stats['candy_solved'] += 1
                await asyncio.sleep(2)
                return True
            except Exception:
                _, symbols = await self.find_grid_cells()
                if symbols and self.has_three_in_row(symbols):
                    print(" ✅ Grid has 3-in-a-row! Success!")
                    self.stats['candy_solved'] += 1
                    return True
        except Exception:
            print(" ❌ Candy Match failed")
            return False

    # ==================== MAZE SOLVER ====================

    async def get_maze_state(self):
        """Extract complete game state from JavaScript"""
        await asyncio.sleep(0.1) 
        
        script = """
        () => {
            const captcha = window.mazeCaptcha || window.captchaInstance;
            
            if (!captcha) return null;
            
            if (!captcha.player || !captcha.goal || !captcha.gameState) return null;

            return {
                player: { x: captcha.player.x, y: captcha.player.y },
                checkpoints: captcha.checkpoints.map(cp => ({
                    x: cp.x, y: cp.y, reached: cp.reached
                })),
                goal: { x: captcha.goal.x, y: captcha.goal.y },
                inversionLevel: captcha.gameState.invertionLevel
            };
        }
        """
        
        try:
            await self.page.wait_for_function(
                "window.mazeCaptcha || window.captchaInstance", 
                timeout=5000
            )
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            print(f"   ⚠️  JS state access error: {str(e)[:50]}")
            return None
    
    def apply_inversion(self, move_x, move_y, inversion_level):
        """Apply control inversion"""
        if inversion_level == 1: move_x *= -1
        elif inversion_level == 2: move_y *= -1
        elif inversion_level == 3:
            move_x *= -1
            move_y *= -1
        return move_x, move_y

    async def move_player_js(self, move_x, move_y, duration=100):
        """Move player using direct JavaScript key control"""
        keys_to_press = []
        if move_x > 0: keys_to_press.append('arrowright')
        elif move_x < 0: keys_to_press.append('arrowleft')
        
        if move_y > 0: keys_to_press.append('arrowdown')
        elif move_y < 0: keys_to_press.append('arrowup')
        
        if not keys_to_press:
            return

        keys_str = "', '".join(keys_to_press)
        
        script = f"""
        (duration) => {{
            const captcha = window.mazeCaptcha || window.captchaInstance;
            if (!captcha || !captcha.keys) return;

            const keys = ['{keys_str}'];
            
            keys.forEach(key => captcha.keys.add(key));
            
            setTimeout(() => {{
                keys.forEach(key => captcha.keys.delete(key));
            }}, duration);
        }}
        """
        
        await self.page.evaluate(script, duration)

    async def navigate_to_target(self, target, game_state, max_steps=400):
        """Navigate player to target position"""
        steps = 0
        last_distance = float('inf')
        stuck_count = 0
        
        print(f"   Starting navigation to ({target['x']:.0f}, {target['y']:.0f})")
        
        while steps < max_steps:
            current_state = await self.get_maze_state()
            if not current_state:
                print("⚠️ Could not read game state, aborting navigation")
                return False
            
            player = current_state['player']
            
            dx = target['x'] - player['x']
            dy = target['y'] - player['y']
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 25:
                print(f"✅ Reached target at ({target['x']:.0f}, {target['y']:.0f})")
                return True
            
            if steps % 30 == 0 and steps > 0:
                print(f"   Step {steps}: Player at ({player['x']:.0f}, {player['y']:.0f}), distance = {distance:.1f}px")
            
            if abs(distance - last_distance) < 1:
                stuck_count += 1
                if stuck_count > 20:
                    print(f"⚠️ Stuck! Trying escape angle...")
                    await self.page.evaluate("""
                        () => {
                            const captcha = window.mazeCaptcha || window.captchaInstance;
                            if (!captcha || !captcha.keys) return;
                            captcha.keys.add('arrowup');
                            captcha.keys.add('arrowright');
                            setTimeout(() => {
                                captcha.keys.clear();
                            }, 100);
                        }
                    """)
                    await asyncio.sleep(0.15)
                    stuck_count = 0
                    continue
            else:
                stuck_count = 0
            
            last_distance = distance
            
            move_x = 1 if dx > 10 else (-1 if dx < -10 else 0)
            move_y = 1 if dy > 10 else (-1 if dy < -10 else 0)
            
            move_x, move_y = self.apply_inversion(
                move_x, 
                move_y, 
                current_state['inversionLevel']
            )
            
            await self.move_player_js(move_x, move_y, duration=100)
            
            await asyncio.sleep(0.05)
            steps += 1
        
        print(f"❌ Navigation timeout after {max_steps} steps")
        return False

    async def solve_maze(self):
        """Solve the entire maze intelligently"""
        print("\n🎮 Starting intelligent maze solving...")
        
        self.stats['attempts'] += 1
        
        try:
            await self.page.wait_for_selector("#mazeCanvas", timeout=10000)
            await self.page.focus("#mazeCanvas")
            await asyncio.sleep(2)
            
            game_state = await self.get_maze_state()
            
            if not game_state:
                print("❌ Could not access game state")
                self.stats['failures'] += 1
                return False
            
            print(f"📊 Game State: {len(game_state['checkpoints'])} checkpoints")
            
            for i, checkpoint in enumerate(game_state['checkpoints']):
                print(f"\n🚩 Checkpoint {i+1}/{len(game_state['checkpoints'])}: ({checkpoint['x']:.0f}, {checkpoint['y']:.0f})")
                
                if not await self.navigate_to_target(checkpoint, game_state, max_steps=400):
                    print(f"❌ Failed to reach checkpoint {i+1}")
                    self.stats['failures'] += 1
                    return False
                
                await asyncio.sleep(0.5)
                
                game_state = await self.get_maze_state()
                if not game_state: return False
                print(f"🔄 Inversion level now: {game_state['inversionLevel']}")
            
            print(f"\n🏁 Final Goal: ({game_state['goal']['x']:.0f}, {game_state['goal']['y']:.0f})")
            
            if not await self.navigate_to_target(game_state['goal'], game_state, max_steps=400):
                print("❌ Failed to reach goal")
                self.stats['failures'] += 1
                return False
            
            await asyncio.sleep(1)
            
            status = await self.page.locator("#statusValue").inner_text(timeout=5000)
            
            if status == "Complete":
                print("✅ MAZE SOLVED! Clicking submit...")
                submit_btn = self.page.locator("#mazeSubmitBtn")
                await submit_btn.click()
                
                self.stats['maze_solved'] += 1
                return True
            else:
                print("❌ Maze not marked as complete")
                self.stats['failures'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Error in solve_maze: {str(e)}")
            self.stats['failures'] += 1
            return False

    # ==================== SLIDER SOLVER (FIXED) ====================

    async def get_slider_data_js(self):
        """Extract slider state from JavaScript"""
        await self.page.wait_for_function(
            "() => typeof sliderState !== 'undefined' && sliderState.targets && sliderState.targets.length === 3",
            timeout=10000
        )
        await asyncio.sleep(0.5)
        
        script = """
        () => {
            return {
                targets: sliderState.targets.map(t => ({x: t.x, y: t.y})),
                order: sliderState.sliderOrder.map(c => c.name.toLowerCase()),
                sliders: sliderState.sliders.map(s => s.dataset.colorName)
            };
        }
        """
        
        return await self.page.evaluate(script)

    async def drag_slider_to_target(self, slider_id, target_x):
        """Drag slider to target position using pointer events (not mouse events)"""
        
        slider_index = int(slider_id.replace("slider", "")) - 1
        container_id = f"sliderContainer{slider_index + 1}"
        
        print(f"      Dragging {slider_id} to target X={target_x:.0f}px...")
        
        try:
            slider = self.page.locator(f"#{slider_id}")
            container = self.page.locator(f"#{container_id}")
            
            await slider.wait_for(state="visible", timeout=5000)
            
            # Get bounding boxes
            slider_box = await slider.bounding_box()
            container_box = await container.bounding_box()
            
            if not slider_box or not container_box:
                print(f"      ❌ Could not get bounding boxes")
                return False
            
            # CRITICAL FIX: Calculate correct end position
            # The target_x is already in container-relative coordinates
            # We need to position the mouse so that when the event handler calculates:
            # px = e.clientX - rect.left - slider.offsetWidth / 2
            # it equals target_x
            
            # So: e.clientX = rect.left + target_x + slider.offsetWidth / 2
            end_x = container_box['x'] + target_x + (slider_box['width'] / 2)
            
            # Start from current slider position
            start_x = slider_box['x'] + slider_box['width'] / 2
            start_y = slider_box['y'] + slider_box['height'] / 2
            end_y = start_y
            
            print(f"        Container left: {container_box['x']:.0f}px")
            print(f"        Target X (relative): {target_x:.0f}px")
            print(f"        Slider width: {slider_box['width']:.0f}px")
            print(f"        Start: ({start_x:.0f}, {start_y:.0f})")
            print(f"        End: ({end_x:.0f}, {end_y:.0f})")
            print(f"        Distance: {abs(end_x - start_x):.0f}px")
            
            # Hover over slider first to ensure it's ready
            await slider.hover()
            await asyncio.sleep(0.1)
            
            # Dispatch pointerdown event
            await self.page.mouse.move(start_x, start_y)
            await asyncio.sleep(0.05)
            
            # Use pointer events instead of mouse events
            await self.page.evaluate("""
                ([x, y, sliderId]) => {
                    const slider = document.getElementById(sliderId);
                    const event = new PointerEvent('pointerdown', {
                        bubbles: true,
                        cancelable: true,
                        clientX: x,
                        clientY: y,
                        pointerId: 1,
                        pointerType: 'mouse'
                    });
                    slider.dispatchEvent(event);
                }
            """, [start_x, start_y, slider_id])
            
            await asyncio.sleep(0.1)
            
            # Move in smooth steps
            steps = 20
            for i in range(1, steps + 1):
                intermediate_x = start_x + (end_x - start_x) * (i / steps)
                
                await self.page.mouse.move(intermediate_x, end_y)
                
                # Dispatch pointermove events
                await self.page.evaluate("""
                    ([x, y]) => {
                        const event = new PointerEvent('pointermove', {
                            bubbles: true,
                            cancelable: true,
                            clientX: x,
                            clientY: y,
                            pointerId: 1,
                            pointerType: 'mouse'
                        });
                        window.dispatchEvent(event);
                    }
                """, [intermediate_x, end_y])
                
                await asyncio.sleep(0.02)
            
            # Dispatch pointerup event at final position
            await self.page.evaluate("""
                ([x, y]) => {
                    const event = new PointerEvent('pointerup', {
                        bubbles: true,
                        cancelable: true,
                        clientX: x,
                        clientY: y,
                        pointerId: 1,
                        pointerType: 'mouse'
                    });
                    window.dispatchEvent(event);
                }
            """, [end_x, end_y])
            
            await asyncio.sleep(0.4)
            
            # Verify placement
            result = await self.page.evaluate("""
                (sliderIndex) => {
                    if (!sliderState) return {success: false, reason: 'no_state'};
                    
                    const slider = sliderState.sliders[sliderIndex];
                    const actualPos = parseInt(slider.style.left) || 0;
                    const targetPos = sliderState.targets[sliderIndex].x;
                    const error = Math.abs(actualPos - targetPos);
                    
                    return {
                        success: sliderState.placed[sliderIndex] === true,
                        completed: sliderState.completed,
                        completedOrder: sliderState.completedOrder,
                        placed: sliderState.placed,
                        actualPos: actualPos,
                        targetPos: targetPos,
                        error: error,
                        tolerance: 10
                    };
                }
            """, slider_index)
            
            print(f"        Placement: {result['success']}")
            print(f"        Actual position: {result['actualPos']}px")
            print(f"        Target position: {result['targetPos']}px")
            print(f"        Error: {result['error']}px (tolerance: {result['tolerance']}px)")
            print(f"        Completed order: {result['completedOrder']}")
            
            if not result['success']:
                if result['error'] >= result['tolerance']:
                    print(f"        ❌ Position error too large!")
                else:
                    print(f"        ❌ Wrong order or other issue")
                return False
            
            if result.get('completed'):
                print(f"        🎉 Puzzle completed!")
            
            return True
            
        except Exception as e:
            print(f"        ❌ Drag error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    async def solve_slider(self):
        """FIXED: Moves sliders in correct ORDER, each to its OWN target position"""
        print("\n🧩 Solving Slider Puzzle CAPTCHA...")
        
        try:
            await asyncio.sleep(2)
            
            # Get state from JavaScript
            data = await self.get_slider_data_js()
            if not data:
                print("   ❌ Could not access sliderState")
                return False
            
            targets = data["targets"]  # [x1, x2, x3] - target positions indexed by slider ID
            correct_order = data["order"]  # ['purple', 'red', 'yellow'] - ORDER they must be placed
            slider_colors = data["sliders"]  # ['red', 'purple', 'yellow'] - colors indexed by slider ID
            
            print(f"   📋 Target positions (indexed by slider ID 1-3): {[t['x'] for t in targets]}")
            print(f"   📋 Required placement ORDER: {correct_order}")
            print(f"   📋 Slider colors (indexed by slider ID 1-3): {slider_colors}")
            print()
            print("   🔑 KEY INSIGHT: Each slider must be placed IN ORDER at its OWN target position")
            print(f"      - Slider with color '{correct_order[0]}' must be placed first")
            print(f"      - Slider with color '{correct_order[1]}' must be placed second")
            print(f"      - Slider with color '{correct_order[2]}' must be placed third")
            
            # Move sliders in the ORDER specified by correct_order
            for move_num, required_color in enumerate(correct_order, 1):
                # Find which slider ID (0, 1, or 2) has this color
                try:
                    slider_index = slider_colors.index(required_color)
                except ValueError:
                    print(f"   ❌ Color '{required_color}' not found in sliders")
                    return False
                
                # This slider needs to go to targets[slider_index] (its own target)
                slider_id = f"slider{slider_index + 1}"
                target_x = targets[slider_index]["x"]
                
                print(f"\n   ➡️  Move {move_num}/3: Place {required_color.upper()} ({slider_id}) at X={target_x:.0f}px")
                
                # Place the slider using direct JavaScript manipulation
                if not await self.drag_slider_to_target(slider_id, target_x):
                    print(f"   ❌ Failed to place {slider_id} at target")
                    return False
                
                # Wait for any animations
                await asyncio.sleep(0.3)
                
                # Get the current state
                validation_data = await self.page.evaluate("""
                    () => ({
                        completedOrder: sliderState.completedOrder,
                        placed: sliderState.placed,
                        completed: sliderState.completed
                    })
                """)
                
                completed_count = len(validation_data['completedOrder'])
                
                # Verify the move was accepted
                if completed_count != move_num:
                    print(f"   ❌ Move rejected! Expected {move_num} completed, got {completed_count}")
                    print(f"      Completed order: {validation_data['completedOrder']}")
                    print(f"      Expected order: {correct_order[:move_num]}")
                    return False
                
                # Check if puzzle was reset
                if not any(validation_data['placed']) and move_num > 0:
                    print(f"   ❌ Puzzle was reset - order violation!")
                    return False
                
                print(f"      ✅ Move accepted! ({completed_count}/3 completed)")
                print(f"         Order so far: {validation_data['completedOrder']}")
                
                # Check if we're done early
                if validation_data['completed']:
                    print(f"\n   🎉 Puzzle completed after move {move_num}!")
                    self.stats['slider_solved'] += 1
                    await asyncio.sleep(1)
                    return True
                
                # Wait before next move
                await asyncio.sleep(0.5)
            
            # Final verification
            print("\n   ⏳ Final verification...")
            await asyncio.sleep(1.0)
            
            # Check completion status
            final_status = await self.page.evaluate("""
                () => ({
                    completed: sliderState.completed,
                    placed: sliderState.placed,
                    completedOrder: sliderState.completedOrder
                })
            """)
            
            print(f"   Final status:")
            print(f"     - Completed: {final_status['completed']}")
            print(f"     - Placed count: {sum(final_status['placed'])}/3")
            print(f"     - Order: {final_status['completedOrder']}")
            
            if final_status['completed']:
                print("   ✅ SLIDER SOLVED!")
                self.stats['slider_solved'] += 1
                await asyncio.sleep(1)
                return True
            
            # Fallback: Check for visual success indicator
            try:
                final_success = self.page.locator("#finalSuccess.active")
                if await final_success.is_visible(timeout=2000):
                    print("   ✅ SLIDER SOLVED! (Visual confirmation)")
                    self.stats['slider_solved'] += 1
                    await asyncio.sleep(1)
                    return True
            except:
                pass
            
            print("   ❌ Slider verification failed")
            return False
                
        except Exception as e:
            print(f"   ❌ Slider error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    # ==================== MAIN FLOW ====================
    
    async def detect_active_captcha(self):
        """Detect which CAPTCHA type is currently active"""
        await asyncio.sleep(1)
        
        current_url = self.page.url
        
        if "mode=maze" in current_url:
            return "maze"
        elif "mode=slider" in current_url:
            return "slider"
        
        try:
            if await self.page.locator("#verificationModal").is_visible():
                return "candy"
        except:
            pass
        
        try:
            if await self.page.locator("#mazeCanvas").is_visible():
                return "maze"
        except:
            pass
        
        try:
            if await self.page.locator("#slider1").is_visible():
                return "slider"
        except:
            pass
        
        return "unknown"

    async def solve_full_captcha_system(self):
        """Solve all 3 CAPTCHAs in sequence"""
        print("\n" + "="*60)
        print("🎯 STARTING FULL CAPTCHA CHALLENGE")
        print("="*60)
        print("⚠️  Note: CAPTCHA order is randomized by the system")
        
        self.stats['attempts'] += 1
        
        try:
            verify_btn = self.page.locator("#verifyBtn")
            await verify_btn.click()
            print("✅ Started verification process")
            await asyncio.sleep(2)
            
            try:
                order_text = await self.page.locator("#progressSubtitle").inner_text()
                print(f"📋 System info: {order_text}")
            except:
                pass
            
            captchas_solved = 0
            max_captchas = 3
            
            while captchas_solved < max_captchas:
                captcha_num = captchas_solved + 1
                
                print(f"\n{'='*60}")
                print(f"CAPTCHA {captcha_num}/3 - Detecting type...")
                print('='*60)
                
                captcha_type = await self.detect_active_captcha()
                print(f"🔍 Detected: {captcha_type.upper()}")
                
                success = False
                
                if captcha_type == "maze":
                    success = await self.solve_maze()
                elif captcha_type == "slider":
                    success = await self.solve_slider()
                elif captcha_type == "candy":
                    success = await self.solve_candy_crush()
                else:
                    print(f"   ❌ Unknown CAPTCHA type!")
                    success = False

                if not success:
                    print(f"\n❌ Failed at CAPTCHA {captcha_num}/3 ({captcha_type})")
                    self.stats['failures'] += 1
                    return False
                
                captchas_solved += 1
                
                try:
                    async with self.page.expect_event('dialog', timeout=2000) as dialog_info:
                        alert = await dialog_info.value
                        print(f"   📢 Alert: {alert.message[:80]}...")
                        await alert.accept()
                        await asyncio.sleep(1)
                except:
                    pass
                
                if "verified=1" in self.page.url:
                    print(f"\n🎉 All CAPTCHAs completed! Returned to index page.")
                    break
                
                if captchas_solved < max_captchas:
                    await asyncio.sleep(1.5)
                    try:
                        continue_btn = self.page.locator("#continueBtn")
                        await continue_btn.click(timeout=8000)
                        print(f"✅ CAPTCHA {captcha_num}/3 complete, continuing...")
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"   ⚠️  Continue button not found: {str(e)[:50]}")
                        await asyncio.sleep(1)
            
            await asyncio.sleep(2)
            
            if "verified=1" in self.page.url:
                print("\n" + "="*60)
                print("🎉 ALL 3 CAPTCHAS SOLVED SUCCESSFULLY!")
                print("="*60)
                self.stats['total_success'] += 1
                
                try:
                    next_btn = self.page.locator("#nextBtn")
                    await next_btn.click(timeout=5000)
                    await asyncio.sleep(2)
                    
                    print("✅ Successfully bypassed CAPTCHA system!")
                    return True
                except:
                    print("✅ Verification complete (next button not found)")
                    return True
            else:
                print("\n⚠️  Verification may be incomplete")
                print(f"   Current URL: {self.page.url}")
                
                self.stats['failures'] += 1
                return False
            
        except Exception as e:
            print(f"\n❌ Critical error: {str(e)}")
            self.stats['failures'] += 1
            return False

    def print_stats(self):
        """Print attack statistics"""
        elapsed = time.time() - self.stats['start_time']
        
        print("\n" + "="*60)
        print("📊 ATTACK STATISTICS")
        print("="*60)
        print(f"Total Attempts:       {self.stats['attempts']}")
        print(f"Full Success:         {self.stats['total_success']}")
        print(f"Candy Solved:         {self.stats['candy_solved']}")
        print(f"Maze Solved:          {self.stats['maze_solved']}")
        print(f"Slider Solved:        {self.stats['slider_solved']}")
        print(f"Failures:             {self.stats['failures']}")
        print(f"Time Elapsed:         {elapsed:.2f}s")
        
        if self.stats['total_success'] > 0:
            success_rate = (self.stats['total_success'] / self.stats['attempts']) * 100
            avg_time = elapsed / self.stats['total_success']
            print(f"Success Rate:         {success_rate:.1f}%")
            print(f"Avg Time/Success:     {avg_time:.2f}s")
        
        print("="*60)

    async def close(self):
        """Close browser"""
        if self.browser:
            await asyncio.sleep(3)
            await self.browser.close()
            print("🛑 Browser closed")


async def run_attacker_async(args):
    """Main async execution wrapper"""
    print("\n" + "="*60)
    print("🔓 ADVANCED CAPTCHA ATTACKER v2.1 (FIXED SLIDER)")
    print("="*60)
    print("Targets: Candy Match + Maze + Slider (All 3)")
    print("FIX: Slider now places tiles in CORRECT ORDER")
    print("="*60 + "\n")
    
    attacker = AdvancedCAPTCHAAttacker(args.url)
    
    try:
        await attacker.init()
        
        for attempt in range(args.attempts):
            if attempt > 0:
                print(f"\n\n{'='*60}")
                print(f"STARTING ATTEMPT {attempt + 1}/{args.attempts}")
                print('='*60)
                await attacker.page.goto(args.url)
                await asyncio.sleep(2)
            
            await attacker.solve_full_captcha_system()
            
            if attempt < args.attempts - 1:
                await asyncio.sleep(3)
        
        attacker.print_stats()
        
    except Exception as e:
        print(f"\n❌ Fatal error during run: {e}")
        attacker.print_stats()
    finally:
        await attacker.close()


def main():
    parser = argparse.ArgumentParser(description='Advanced CAPTCHA Bot Attacker (FIXED)')
    parser.add_argument('--url', default='http://127.0.0.1:5500/index.html', 
                       help='Target URL')
    parser.add_argument('--attempts', type=int, default=1, 
                       help='Number of full attempts')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_attacker_async(args))
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Global error in main execution: {e}")


if __name__ == '__main__':
    main()