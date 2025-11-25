# # #!/usr/bin/env python3
# # """
# # Advanced CAPTCHA Bot Attacker - Playwright Async Implementation
# # Intelligently solves all 3 CAPTCHA types: Candy Match, Maze, and Slider
# # Usage: python3 advanced_captcha_attacker_playwright.py --url https://exam-portal-captcha-test.web.app/
# # """

# # import argparse
# # import time
# # import asyncio
# # import json
# # from collections import deque
# # from playwright.async_api import async_playwright

# # GRID_DIM = 3  # 3x3 for Candy Crush


# # class AdvancedCAPTCHAAttacker:
# #     def __init__(self, url):
# #         self.url = url
# #         self.browser = None
# #         self.page = None
# #         self.stats = {
# #             'attempts': 0,
# #             'candy_solved': 0,
# #             'maze_solved': 0,
# #             'slider_solved': 0,
# #             'total_success': 0,
# #             'failures': 0,
# #             'start_time': time.time()
# #         }

# #     async def init(self):
# #         """Initialize browser with stealth settings"""
# #         print("🤖 Initializing Advanced CAPTCHA Attacker (Playwright Async)...")
        
# #         p = await async_playwright().start()
        
# #         # Use Chromium for best compatibility
# #         self.browser = await p.chromium.launch(
# #             headless=False,
# #             slow_mo=50,
# #             args=[
# #                 "--start-maximized",
# #                 "--disable-blink-features=AutomationControlled"
# #             ]
# #         )
        
# #         self.page = await self.browser.new_page()
        
# #         # Apply stealth: change navigator.webdriver
# #         await self.page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
# #         print(f"🌐 Navigating to: {self.url}")
# #         await self.page.goto(self.url)
        
# #         # Wait for page load
# #         await self.page.wait_for_selector("#verifyBtn", timeout=10000)
# #         await asyncio.sleep(2)
# #         print("✅ CAPTCHA system loaded")

# #     async def check_and_submit_final_verification(self):
# #         """
# #         Performs the final verification check and attempts to submit the form.
# #         This must be called after all 3 individual CAPTCHAs are solved.
# #         """
        
# #         # 1. Attempt to find and click the FINAL submit/verify button
# #         print("\n🏁 Attempting final verification...")
        
# #         # Common IDs for the final button (adjust if your target uses a different ID)
# #         final_submit_selectors = [
# #             "#finalSubmitButton", 
# #             "#verifyButton", 
# #             "button:has-text('Verify')"
# #         ]
        
# #         final_button = None
# #         for selector in final_submit_selectors:
# #             try:
# #                 locator = self.page.locator(selector).first
# #                 if await locator.is_visible(timeout=1000):
# #                     final_button = locator
# #                     break
# #             except:
# #                 continue

# #         if final_button:
# #             print("   ✅ Found final verification button. Clicking...")
# #             await final_button.click()
# #             await asyncio.sleep(2) # Wait for server response/page update
# #         else:
# #             print("   ⚠️ No explicit final verification button found. Proceeding to status check.")
        
# #         # 2. Check for overall success message/state
        
# #         # Common success indicators (adjust if your target page uses different text)
# #         success_indicators = [
# #             self.page.locator("text=Verification Succeeded!"),
# #             self.page.locator("text=Form Submitted Successfully"),
# #             self.page.locator("#verificationStatus[data-status='success']"),
# #             self.page.locator("text=You are verified")
# #         ]
        
# #         is_succeeded = False
# #         for locator in success_indicators:
# #             try:
# #                 if await locator.is_visible(timeout=3000):
# #                     is_succeeded = True
# #                     break
# #             except:
# #                 pass

# #         if is_succeeded:
# #             print("\n\n🎉🎉 ALL CAPTCHAS SOLVED AND VERIFICATION SUCCEEDED! 🎉🎉")
# #             # Assuming you have a stat for overall success
# #             if 'total_success' in self.stats:
# #                 self.stats['total_success'] += 1
            
# #             # Close the page/browser (if not handled by the main loop cleanup)
# #             # You can decide to close the page immediately here, or let the main loop handle it.
# #             # Example to close page: await self.page.close() 
            
# #             return True
# #         else:
# #             print("\n\n❌ VERIFICATION INCOMPLETE: Final success status not confirmed.")
# #             # If you have a separate failure stat, update it here
# #             return False

# #     # ==================== CANDY CRUSH SOLVER ====================
    
# #     # ==================== CANDY CRUSH SOLVER ====================
    
# #     async def find_grid_cells(self):
# #         """Find the 3x3 grid structure and its symbols using Playwright locators."""
# #         try:
# #             # 1. Locate all 9 grid cells first
# #             all_cells_locator = self.page.locator("#gridContainer .grid-row .grid-cell")
# #             cells_count = await all_cells_locator.count()

# #             if cells_count != GRID_DIM * GRID_DIM:
# #                 print(f"   ⚠️ Expected 9 cells, found {cells_count}.")
# #                 return None, None
            
# #             # 2. Structure the locators into a 3x3 array
# #             grid_cells = []
# #             for r in range(GRID_DIM):
# #                 row = []
# #                 for c in range(GRID_DIM):
# #                     # Playwright locators are zero-indexed, CSS nth-child is one-indexed
# #                     locator = self.page.locator(f".grid-row:nth-child({r + 1}) > .grid-cell:nth-child({c + 1})")
# #                     row.append(locator)
# #                 grid_cells.append(row)
            
# #             # 3. Read symbols and classes by evaluating attributes on all cells
# #             symbols = []
# #             for r in range(GRID_DIM):
# #                 row_symbols = []
# #                 for c in range(GRID_DIM):
# #                     cell_locator = grid_cells[r][c]
                    
# #                     # Fetch text and class using a single async operation per cell
# #                     cell_data = await cell_locator.evaluate("""
# #                         (el) => ({
# #                             text: el.textContent.trim() || '?',
# #                             classes: el.className
# #                         })
# #                     """)
                    
# #                     if "hidden-cell" in cell_data['classes']:
# #                         row_symbols.append("?")
# #                     else:
# #                         row_symbols.append(cell_data['text'])

# #                 symbols.append(row_symbols)
            
# #             return grid_cells, symbols
        
# #         except Exception as e:
# #             print(f"   ❌ Error in find_grid_cells: {e}")
# #             return None, None

# #     async def reveal_all_hidden_cells(self):
# #         """Click all cells with '?' to reveal them"""
# #         print("   🔍 Revealing hidden cells...")
# #         max_attempts = 10
        
# #         for attempt in range(max_attempts):
            
# #             # Find all currently hidden cells in one go
# #             hidden_cells_count = await self.page.evaluate("""
# #                 () => {
# #                     const hiddenCells = document.querySelectorAll(".grid-cell.hidden-cell");
# #                     if (hiddenCells.length > 0) {
# #                         // Click the first one found
# #                         hiddenCells[0].click();
# #                         return hiddenCells.length;
# #                     }
# #                     return 0;
# #                 }
# #             """)

# #             if hidden_cells_count == 0:
# #                 print("   ✅ All cells revealed")
# #                 return

# #             await asyncio.sleep(0.3) # Wait for animation

# #         print("   ⚠️  Some cells may remain hidden")

# #     def has_three_in_row(self, grid):
# #         """Check if grid has 3 in a row (horizontal or vertical)"""
# #         # Check rows
# #         for r in range(GRID_DIM):
# #             if grid[r][0] == grid[r][1] == grid[r][2] and grid[r][0] != "?":
# #                 return True
        
# #         # Check columns
# #         for c in range(GRID_DIM):
# #             if grid[0][c] == grid[1][c] == grid[2][c] and grid[0][c] != "?":
# #                 return True
        
# #         return False

# #     def find_candy_solution_bfs(self, symbols, max_depth=5):
# #         """Use BFS to find shortest swap sequence (synchronous logic, as it's computation)"""
# #         def flatten(mat):
# #             return tuple(x for row in mat for x in row)
        
# #         def unflatten(f):
# #             return [list(f[i * GRID_DIM:(i + 1) * GRID_DIM]) for i in range(GRID_DIM)]
        
# #         start = flatten(symbols)
        
# #         # Generate all valid adjacent pairs
# #         neighbors = []
# #         for r in range(GRID_DIM):
# #             for c in range(GRID_DIM):
# #                 idx = r * GRID_DIM + c
# #                 # Right
# #                 if c + 1 < GRID_DIM:
# #                     neighbors.append((idx, idx + 1))
# #                 # Down
# #                 if r + 1 < GRID_DIM:
# #                     neighbors.append((idx, idx + GRID_DIM))
        
# #         if self.has_three_in_row(symbols):
# #             return []
        
# #         queue = deque()
# #         queue.append((start, []))
# #         seen = {start}
        
# #         while queue:
# #             current, moves = queue.popleft()
            
# #             if len(moves) >= max_depth:
# #                 continue
            
# #             for a, b in neighbors:
# #                 # Swap
# #                 lst = list(current)
# #                 lst[a], lst[b] = lst[b], lst[a]
# #                 new_state = tuple(lst)
                
# #                 if new_state in seen:
# #                     continue
                
# #                 seen.add(new_state)
# #                 new_moves = moves + [(a, b)]
# #                 new_grid = unflatten(new_state)
                
# #                 if self.has_three_in_row(new_grid):
# #                     return new_moves
                
# #                 queue.append((new_state, new_moves))
        
# #         raise RuntimeError("No solution found within depth limit")

# #     async def execute_swap(self, a, b):
# #         """Execute a swap between two cells using Playwright locator clicks"""
# #         r1, c1 = divmod(a, GRID_DIM)
# #         r2, c2 = divmod(b, GRID_DIM)
        
# #         grid_cells, _ = await self.find_grid_cells()
# #         if not grid_cells:
# #             raise RuntimeError("Grid disappeared")
        
# #         cell1 = grid_cells[r1][c1]
        
# #         # Check for locked cells via class attribute
# #         if 'locked-cell' in await cell1.get_attribute('class'):
# #              raise RuntimeError(f"Cell ({r1},{c1}) is locked")

# #         # Click first cell
# #         await cell1.click()
# #         await asyncio.sleep(0.3)
        
# #         # Re-read grid elements as they might have been re-rendered/repositioned after the first click
# #         grid_cells, _ = await self.find_grid_cells()
# #         if not grid_cells:
# #             raise RuntimeError("Grid disappeared after first click")

# #         cell2 = grid_cells[r2][c2]
        
# #         if 'locked-cell' in await cell2.get_attribute('class'):
# #             raise RuntimeError(f"Cell ({r2},{c2}) is locked")

# #         # Click second cell
# #         await cell2.click()
# #         await asyncio.sleep(0.5)

# #     async def solve_candy_crush(self):
# #         """Main candy crush solving logic"""
# #         print("\n🍬 Solving Candy Match CAPTCHA...")
        
# #         try:
# #             # Wait for modal to be visible
# #             await self.page.wait_for_selector("#verificationModal:visible", timeout=10000)
            
# #             await asyncio.sleep(1)
            
# #             # Reveal all hidden cells
# #             await self.reveal_all_hidden_cells()
            
# #             # Read grid
# #             _, symbols = await self.find_grid_cells()
# #             if not symbols:
# #                 print("❌ Grid not found or is malformed")
# #                 return False
            
# #             print("   Initial grid:")
# #             for row in symbols:
# #                 print(f"   {row}")
            
# #             # Find solution
# #             print("   🧠 Computing optimal solution...")
# #             moves = self.find_candy_solution_bfs(symbols, max_depth=5)
            
# #             print(f"   📋 Solution found: {len(moves)} moves")
# #             print(f"   Swap sequence: {moves}")
            
# #             for i, (a, b) in enumerate(moves):
# #                 print(f" Move {i+1}/{len(moves)}: Swap cells {a} ↔ {b}")
# #                 try:
# #                     await self.execute_swap(a, b)
# #                 except RuntimeError as e:
# #                     print(f" ⚠️ {e}, trying alternative...")
# #                     await self.page.click("#refreshBtn")
# #                     await asyncio.sleep(1)
# #                     return await self.solve_candy_crush()

# #                 # Early success check after each move to catch website response before CAPTCHA closes
# #                 try:
# #                     await self.page.wait_for_selector("#successMessage", timeout=3000)
# #                     print(f" 🎉 CAPTCHA solved early after move {i+1}")
# #                     self.stats['candy_solved'] += 1
# #                     await asyncio.sleep(2)
# #                     return True
# #                 except Exception:
# #                     # If no success message yet, continue with next move
# #                     pass

# #                 await asyncio.sleep(0.5)  # short pause for stability

# #             # Final verification after all moves
# #             try:
# #                 success_msg = self.page.locator("#successMessage:visible")
# #                 await success_msg.wait_for(timeout=3000)
# #                 print(" ✅ Candy Match SOLVED on final verification!")
# #                 self.stats['candy_solved'] += 1
# #                 await asyncio.sleep(2)
# #                 return True
# #             except Exception:
# #                 # fallback: check for 3-in-a-row in grid state as last resort
# #                 _, symbols = await self.find_grid_cells()
# #                 if symbols and self.has_three_in_row(symbols):
# #                     print(" ✅ Grid has 3-in-a-row! Assuming success on fallback...")
# #                     self.stats['candy_solved'] += 1
# #                     return True
# #         except Exception:
# #             print(" ❌ Candy Match failed after all verification attempts")
# #             return False


# #     # ==================== MAZE SOLVER ====================
    
# #     # ==================== MAZE SOLVER (REVERTED TO JS INJECTION) ====================

# #     async def get_maze_state(self):
# #         """Extract complete game state from JavaScript using Playwright's evaluate."""
# #         await asyncio.sleep(0.1) 
        
# #         # NOTE: Using 'mazeCaptcha' instance name as derived from previous turns, 
# #         # but the JS below also checks 'captchaInstance' from your old working code.
# #         script = """
# #         () => {
# #             const captcha = window.mazeCaptcha || window.captchaInstance;
            
# #             if (!captcha) return null;
            
# #             // Ensure necessary properties exist (e.g., if we hit a loading state)
# #             if (!captcha.player || !captcha.goal || !captcha.gameState) return null;

# #             return {
# #                 player: { x: captcha.player.x, y: captcha.player.y },
# #                 checkpoints: captcha.checkpoints.map(cp => ({
# #                     x: cp.x, y: cp.y, reached: cp.reached
# #                 })),
# #                 goal: { x: captcha.goal.x, y: captcha.goal.y },
# #                 inversionLevel: captcha.gameState.invertionLevel
# #                 // Add any other properties your logic requires, like obstacles
# #             };
# #         }
# #         """
        
# #         try:
# #             # Wait for the maze object to be initialized
# #             await self.page.wait_for_function(
# #                 "window.mazeCaptcha || window.captchaInstance", 
# #                 timeout=5000
# #             )
# #             result = await self.page.evaluate(script)
# #             return result
# #         except Exception as e:
# #             print(f"   ⚠️  JS state access error: {str(e)[:50]}")
# #             return None
    
# #     def apply_inversion(self, move_x, move_y, inversion_level):
# #         """Apply control inversion (synchronous helper)"""
# #         if inversion_level == 1: move_x *= -1
# #         elif inversion_level == 2: move_y *= -1
# #         elif inversion_level == 3:
# #             move_x *= -1
# #             move_y *= -1
# #         return move_x, move_y

# #     async def move_player_js(self, move_x, move_y, duration=100):
# #         """
# #         Move player using direct JavaScript key control (Ported from working Selenium code).
# #         This directly manipulates the game engine's internal key state.
# #         """
# #         keys_to_press = []
# #         if move_x > 0: keys_to_press.append('arrowright')
# #         elif move_x < 0: keys_to_press.append('arrowleft')
        
# #         if move_y > 0: keys_to_press.append('arrowdown')
# #         elif move_y < 0: keys_to_press.append('arrowup')
        
# #         if not keys_to_press:
# #             return

# #         # Build JavaScript to hold keys and then release them after 'duration'
# #         keys_str = "', '".join(keys_to_press)
        
# #         script = f"""
# #         (duration) => {{
# #             const captcha = window.mazeCaptcha || window.captchaInstance;
# #             if (!captcha || !captcha.keys) return;

# #             const keys = ['{keys_str}'];
            
# #             // Add all keys (press and hold)
# #             keys.forEach(key => captcha.keys.add(key));
            
# #             // Hold for duration then release
# #             setTimeout(() => {{
# #                 keys.forEach(key => captcha.keys.delete(key));
# #             }}, duration);
# #         }}
# #         """
        
# #         # Execute the script asynchronously
# #         await self.page.evaluate(script, duration)

# #     async def navigate_to_target(self, target, game_state, max_steps=400):
# #         """Navigate player to target position using direct JS key control"""
# #         steps = 0
# #         last_distance = float('inf')
# #         stuck_count = 0
        
# #         print(f"   Starting navigation to ({target['x']:.0f}, {target['y']:.0f})")
        
# #         while steps < max_steps:
# #             current_state = await self.get_maze_state()
# #             if not current_state:
# #                 print("⚠️ Could not read game state, aborting navigation")
# #                 return False
            
# #             player = current_state['player']
            
# #             # Check if reached target
# #             dx = target['x'] - player['x']
# #             dy = target['y'] - player['y']
# #             distance = (dx**2 + dy**2)**0.5
            
# #             if distance < 25:
# #                 print(f"✅ Reached target at ({target['x']:.0f}, {target['y']:.0f})")
# #                 return True
            
# #             # Progress update
# #             if steps % 30 == 0 and steps > 0:
# #                 print(f"   Step {steps}: Player at ({player['x']:.0f}, {player['y']:.0f}), distance = {distance:.1f}px")
            
# #             # Detect if stuck
# #             if abs(distance - last_distance) < 1:
# #                 stuck_count += 1
# #                 if stuck_count > 20:
# #                     print(f"⚠️ Stuck! Trying escape angle...")
# #                     # Perform a small temporary perpendicular movement (e.g., UP and RIGHT)
# #                     # We inject a specific script to move up/right for 100ms
# #                     await self.page.evaluate("""
# #                         () => {
# #                             const captcha = window.mazeCaptcha || window.captchaInstance;
# #                             if (!captcha || !captcha.keys) return;
# #                             captcha.keys.add('arrowup');
# #                             captcha.keys.add('arrowright');
# #                             setTimeout(() => {
# #                                 captcha.keys.clear();
# #                             }, 100);
# #                         }
# #                     """)
# #                     await asyncio.sleep(0.15) # Wait for movement to finish
# #                     stuck_count = 0
# #                     continue
# #             else:
# #                 stuck_count = 0
            
# #             last_distance = distance
            
# #             # Calculate movement direction
# #             move_x = 1 if dx > 10 else (-1 if dx < -10 else 0)
# #             move_y = 1 if dy > 10 else (-1 if dy < -10 else 0)
            
# #             # Apply inversion
# #             move_x, move_y = self.apply_inversion(
# #                 move_x, 
# #                 move_y, 
# #                 current_state['inversionLevel']
# #             )
            
# #             # Direct control via JavaScript
# #             await self.move_player_js(move_x, move_y, duration=100)
            
# #             await asyncio.sleep(0.05)
# #             steps += 1
        
# #         print(f"❌ Navigation timeout after {max_steps} steps")
# #         return False

# #     async def solve_maze(self):
# #         """Solve the entire maze intelligently using Playwright"""
# #         print("\n🎮 Starting intelligent maze solving...")
        
# #         self.stats['attempts'] += 1
        
# #         try:
# #             await self.page.wait_for_selector("#mazeCanvas", timeout=10000)
            
# #             # Focus the canvas for good measure, though direct JS manipulation shouldn't need it
# #             await self.page.focus("#mazeCanvas")
# #             await asyncio.sleep(2)
            
# #             game_state = await self.get_maze_state()
            
# #             if not game_state:
# #                 print("❌ Could not access game state")
# #                 self.stats['failures'] += 1
# #                 return False
            
# #             print(f"📊 Game State: {len(game_state['checkpoints'])} checkpoints")
            
# #             # Navigate to each checkpoint
# #             for i, checkpoint in enumerate(game_state['checkpoints']):
# #                 print(f"\n🚩 Checkpoint {i+1}/{len(game_state['checkpoints'])}: ({checkpoint['x']:.0f}, {checkpoint['y']:.0f})")
                
# #                 if not await self.navigate_to_target(checkpoint, game_state, max_steps=400):
# #                     print(f"❌ Failed to reach checkpoint {i+1}")
# #                     self.stats['failures'] += 1
# #                     return False
                
# #                 await asyncio.sleep(0.5)
                
# #                 # Update game state after each checkpoint
# #                 game_state = await self.get_maze_state()
# #                 if not game_state: return False
# #                 print(f"🔄 Inversion level now: {game_state['inversionLevel']}")
            
# #             # Navigate to goal
# #             print(f"\n🏁 Final Goal: ({game_state['goal']['x']:.0f}, {game_state['goal']['y']:.0f})")
            
# #             if not await self.navigate_to_target(game_state['goal'], game_state, max_steps=400):
# #                 print("❌ Failed to reach goal")
# #                 self.stats['failures'] += 1
# #                 return False
            
# #             await asyncio.sleep(1)
            
# #             # Check completion using the same status element
# #             status = await self.page.locator("#statusValue").inner_text(timeout=5000)
            
# #             if status == "Complete":
# #                 print("✅ MAZE SOLVED! Clicking submit...")
# #                 submit_btn = self.page.locator("#mazeSubmitBtn")
# #                 await submit_btn.click()
                
# #                 self.stats['total_success'] += 1 # Assuming this is the stat you use for successful CAPTCHA solves
# #                 return True
# #             else:
# #                 print("❌ Maze not marked as complete")
# #                 self.stats['failures'] += 1
# #                 return False
                
# #         except Exception as e:
# #             print(f"❌ Error in solve_maze: {str(e)}")
# #             self.stats['failures'] += 1
# #             return False

# #     # The blind navigation fallback is removed as the direct JS injection is the most robust method.
# #     # ==================== SLIDER SOLVER ====================

# #     async def get_slider_data_js(self):
# #         """Extract slider state from JavaScript asynchronously"""
# #         # Wait for the sliderState to be initialized
# #         await self.page.wait_for_function(
# #             "() => typeof sliderState !== 'undefined' && sliderState.targets && sliderState.targets.length === 3",
# #             timeout=10000
# #         )
# #         await asyncio.sleep(0.5)
        
# #         script = """
# #         () => {
# #             return {
# #                 targets: sliderState.targets.map(t => ({x: t.x, y: t.y})),
# #                 order: sliderState.sliderOrder.map(c => c.name.toLowerCase()),
# #                 sliders: sliderState.sliders.map(s => s.dataset.colorName)
# #             };
# #         }
# #         """
        
# #         return await self.page.evaluate(script)

# #     # async def drag_slider_to_target(self, slider_id, target_x):
# #     #     """Drag slider to specific target X coordinate using mouse actions"""
        
# #     #     # Get the slider element
# #     #     slider = self.page.locator(f"#{slider_id}")

# #     #     # The bounding box of the slider element (the handle)
# #     #     box = await slider.bounding_box()
# #     #     if not box:
# #     #         raise RuntimeError("Slider element not found or invisible.")

# #     #     # Center of the slider handle is the start point
# #     #     start_x = box["x"] + box["width"] / 2
# #     #     start_y = box["y"] + box["height"] / 2

# #     #     # To calculate the end_x on the screen, we need the container's position.
# #     #     # The sliderState.targets are relative to the *container*.
# #     #     container_id = slider_id.replace("slider", "sliderContainer")
# #     #     container = self.page.locator(f"#{container_id}")
# #     #     container_box = await container.bounding_box()
        
# #     #     if not container_box:
# #     #         raise RuntimeError("Slider container not found.")
            
# #     #     # target_x is relative to the container's left edge.
# #     #     # End X = Container's Left Edge + Target X + Half Slider Width
# #     #     end_x = container_box["x"] + target_x + box["width"] / 2
# #     #     end_y = start_y
        
# #     #     print(f"      Start X: {start_x:.1f}, End X: {end_x:.1f}, Offset: {end_x - start_x:.1f}")

# #     #     # Perform the drag operation
# #     #     await self.page.mouse.move(start_x, start_y)
# #     #     await self.page.mouse.down()
# #     #     # Move in steps for a more natural-looking drag
# #     #     await self.page.mouse.move(end_x, end_y, steps=30)
# #     #     await self.page.mouse.up()
        
# #     #     await asyncio.sleep(0.5)
# #     #     return True
# #     async def drag_slider_to_target(self, slider_id, target_x):
# #         """Drag slider to specific target X coordinate using mouse actions"""
        
# #         # Get the slider element
# #         slider = self.page.locator(f"#{slider_id}")

# #         # The bounding box of the slider element (the handle)
# #         box = await slider.bounding_box()
# #         if not box:
# #             raise RuntimeError("Slider element not found or invisible.")

# #         # Get the slider container's position
# #         container_id = slider_id.replace("slider", "sliderContainer")
# #         container = self.page.locator(f"#{container_id}")
# #         container_box = await container.bounding_box()
        
# #         if not container_box:
# #             raise RuntimeError("Slider container not found.")
        
# #         # The JavaScript validation checks:
# #         # let px = e.clientX - rect.left - slider.offsetWidth / 2;
# #         # const dx = Math.abs(px - sliderState.targets[index].x);
# #         # if (dx < 10) { ... }
# #         # 
# #         # This means 'px' is the LEFT EDGE of the slider relative to container
# #         # We need to position our mouse so that when released:
# #         # mouseX - container.left - (slider.width / 2) = target_x
# #         # Therefore: mouseX = container.left + target_x + (slider.width / 2)
        
# #         start_x = box["x"] + box["width"] / 2
# #         start_y = box["y"] + box["height"] / 2
        
# #         end_x = container_box["x"] + target_x + (box["width"] / 2)
# #         end_y = start_y
        
# #         print(f"      Slider width: {box['width']:.1f}px")
# #         print(f"      Container left: {container_box['x']:.1f}px")
# #         print(f"      Target X (slider left edge): {target_x:.1f}px")
# #         print(f"      Mouse start: ({start_x:.1f}, {start_y:.1f})")
# #         print(f"      Mouse end: ({end_x:.1f}, {end_y:.1f})")
# #         print(f"      Movement distance: {end_x - start_x:.1f}px")

# #         # Perform the drag operation with precise control
# #         await self.page.mouse.move(start_x, start_y)
# #         await asyncio.sleep(0.1)
# #         await self.page.mouse.down()
# #         await asyncio.sleep(0.15)

# #         # human‑like horizontal drag with tiny jitter
# #         mid_x = start_x + (end_x - start_x) * 0.7
# #         await self.page.mouse.move(mid_x, end_y + 1, steps=15)
# #         await self.page.mouse.move(end_x, end_y, steps=15)
 
# #         await asyncio.sleep(0.1)
# #         await self.page.mouse.up()
# #         await asyncio.sleep(0.4)  # let site process and lock slider


# #     async def solve_slider(self):
# #         """Main slider solving logic using the exact order/position from sliderState"""
# #         print("\n🧩 Solving Slider Puzzle CAPTCHA...")
        
# #         try:
# #             await asyncio.sleep(2)
            
# #             # 1. Get state
# #             data = await self.get_slider_data_js()
# #             if not data:
# #                 print("   ❌ Could not access sliderState in JavaScript")
# #                 return False
            
# #             targets = data["targets"]
# #             correct_order = data["order"]
# #             slider_colors = data["sliders"]
            
# #             print(f"   📋 Target positions: {[t['x'] for t in targets]}")
# #             print(f"   📋 Expected order: {correct_order}")
# #             print(f"   📋 Slider colors: {slider_colors}")
            
# #             # 2. Iterate through the correct color order
# #             for i, required_color in enumerate(correct_order):
# #                 try:
# #                     # Find the index of the slider with this color
# #                     slider_index = slider_colors.index(required_color)
# #                 except ValueError:
# #                     print(f"   ❌ Color '{required_color}' not found in sliders")
# #                     return False
                
# #                 # Slider IDs are slider1, slider2, slider3 (1-indexed)
# #                 slider_id = f"slider{slider_index + 1}"
# #                 target_x = targets[slider_index]["x"]
                
# #                 print(f"   ➡️ Move {i+1}: Matching color '{required_color}' ({slider_id}) to X={target_x:.1f}")
                
# #                 if not await self.drag_slider_to_target(slider_id, target_x):
# #                     print(f"   ❌ Failed to drag slider {slider_id}")
# #                     return False
                
# #                 await asyncio.sleep(0.5)
            
# #             # 3. Final verification check
# #             print("   ⏳ Waiting for success verification...")
# #             await asyncio.sleep(1.5)
            
# #             try:
# #                 # Check for the active class on the final success indicator
# #                 final_success = self.page.locator("#finalSuccess")
# #                 if "active" in await final_success.get_attribute("class"):
# #                     print("   ✅ Slider SOLVED!")
# #                     self.stats['slider_solved'] += 1
# #                     await asyncio.sleep(1)
# #                     return True
# #             except:
# #                 pass
            
# #             print("   ❌ Slider solving failed (Verification not detected)")
# #             return False
            
# #         except Exception as e:
# #             print(f"   ❌ Slider error: {str(e)}")
# #             return False

# #     # ==================== MAIN FLOW ====================
    
# #     async def detect_active_captcha(self):
# #         """Intelligently detect which CAPTCHA type is currently active"""
# #         await asyncio.sleep(1)
        
# #         current_url = self.page.url
        
# #         if "mode=maze" in current_url:
# #             return "maze"
# #         elif "mode=slider" in current_url:
# #             return "slider"
        
# #         # Check for candy modal
# #         try:
# #             if await self.page.locator("#verificationModal").is_visible():
# #                 return "candy"
# #         except:
# #             pass
        
# #         # Check for maze canvas
# #         try:
# #             if await self.page.locator("#mazeCanvas").is_visible():
# #                 return "maze"
# #         except:
# #             pass
        
# #         # Check for slider elements
# #         try:
# #             if await self.page.locator("#slider1").is_visible():
# #                 return "slider"
# #         except:
# #             pass
        
# #         return "unknown"

# #     async def solve_full_captcha_system(self):
# #         """Solve all 3 CAPTCHAs in sequence (handles random order)"""
# #         print("\n" + "="*60)
# #         print("🎯 STARTING FULL CAPTCHA CHALLENGE")
# #         print("="*60)
# #         print("⚠️  Note: CAPTCHA order is randomized by the system")
        
# #         self.stats['attempts'] += 1
        
# #         try:
# #             # Click start button
# #             verify_btn = self.page.locator("#verifyBtn")
# #             await verify_btn.click()
# #             print("✅ Started verification process")
# #             await asyncio.sleep(2)
            
# #             # Check for progress indicator
# #             try:
# #                 order_text = await self.page.locator("#progressSubtitle").inner_text()
# #                 print(f"📋 System info: {order_text}")
# #             except:
# #                 pass
            
# #             # Solve CAPTCHAs until all 3 are complete
# #             captchas_solved = 0
# #             max_captchas = 3
            
# #             while captchas_solved < max_captchas:
# #                 captcha_num = captchas_solved + 1
                
# #                 print(f"\n{'='*60}")
# #                 print(f"CAPTCHA {captcha_num}/3 - Detecting type...")
# #                 print('='*60)
                
# #                 # Detect which CAPTCHA is active
# #                 captcha_type = await self.detect_active_captcha()
# #                 print(f"🔍 Detected: {captcha_type.upper()}")
                
# #                 success = False
                
# #                 # Solve based on type
# #                 if captcha_type == "maze":
# #                     success = await self.solve_maze()
# #                 elif captcha_type == "slider":
# #                     success = await self.solve_slider()
# #                 elif captcha_type == "candy":
# #                     success = await self.solve_candy_crush()
# #                 else:
# #                     print(f"   ❌ Unknown CAPTCHA type!")
# #                     success = False

# #                 if not success:
# #                     print(f"\n❌ Failed at CAPTCHA {captcha_num}/3 ({captcha_type})")
# #                     self.stats['failures'] += 1
# #                     return False
                
# #                 captchas_solved += 1
                
# #                 # Handle alerts that may appear
# #                 try:
# #                     async with self.page.expect_event('dialog', timeout=2000) as dialog_info:
# #                         alert = await dialog_info.value
# #                         print(f"   📢 Alert: {alert.message[:80]}...")
# #                         await alert.accept()
# #                         await asyncio.sleep(1)
# #                 except:
# #                     pass
                
# #                 # Check if we're done (back on index page)
# #                 if "verified=1" in self.page.url:
# #                     print(f"\n🎉 All CAPTCHAs completed! Returned to index page.")
# #                     break
                
# #                 # Click continue button if on success page
# #                 if captchas_solved < max_captchas:
# #                     await asyncio.sleep(1.5)
# #                     try:
# #                         continue_btn = self.page.locator("#continueBtn")
# #                         await continue_btn.click(timeout=8000)
# #                         print(f"✅ CAPTCHA {captcha_num}/3 complete, continuing...")
# #                         await asyncio.sleep(2)
# #                     except Exception as e:
# #                         print(f"   ⚠️  Continue button not found: {str(e)[:50]}")
# #                         await asyncio.sleep(1)
            
# #             # Final verification check
# #             await asyncio.sleep(2)
            
# #             # Check if back on index with verified status
# #             if "verified=1" in self.page.url:
# #                 print("\n" + "="*60)
# #                 print("🎉 ALL 3 CAPTCHAS SOLVED SUCCESSFULLY!")
# #                 print("="*60)
# #                 self.stats['total_success'] += 1
                
# #                 # Click next button to go to exam
# #                 try:
# #                     next_btn = self.page.locator("#nextBtn")
# #                     await next_btn.click(timeout=5000)
# #                     await asyncio.sleep(2)
                    
# #                     print("✅ Successfully bypassed CAPTCHA system!")
# #                     return True
# #                 except:
# #                     print("✅ Verification complete (next button not found)")
# #                     return True
# #             else:
# #                 print("\n⚠️  Verification may be incomplete")
# #                 print(f"   Current URL: {self.page.url}")
                
# #                 self.stats['failures'] += 1
# #                 return False
            
# #         except Exception as e:
# #             print(f"\n❌ Critical error: {str(e)}")
# #             self.stats['failures'] += 1
# #             return False

# #     def print_stats(self):
# #         """Print attack statistics (synchronous)"""
# #         elapsed = time.time() - self.stats['start_time']
        
# #         print("\n" + "="*60)
# #         print("📊 ATTACK STATISTICS")
# #         print("="*60)
# #         print(f"Total Attempts:       {self.stats['attempts']}")
# #         print(f"Full Success:         {self.stats['total_success']}")
# #         print(f"Candy Solved:         {self.stats['candy_solved']}")
# #         print(f"Maze Solved:          {self.stats['maze_solved']}")
# #         print(f"Slider Solved:        {self.stats['slider_solved']}")
# #         print(f"Failures:             {self.stats['failures']}")
# #         print(f"Time Elapsed:         {elapsed:.2f}s")
        
# #         if self.stats['total_success'] > 0:
# #             success_rate = (self.stats['total_success'] / self.stats['attempts']) * 100
# #             avg_time = elapsed / self.stats['total_success']
# #             print(f"Success Rate:         {success_rate:.1f}%")
# #             print(f"Avg Time/Success:     {avg_time:.2f}s")
        
# #         print("="*60)

# #     async def close(self):
# #         """Close browser asynchronously"""
# #         if self.browser:
# #             await asyncio.sleep(3)  # Keep open briefly to see result
# #             await self.browser.close()
# #             print("🛑 Browser closed")


# # async def run_attacker_async(args):
# #     """Main async execution wrapper"""
# #     print("\n" + "="*60)
# #     print("🔓 ADVANCED CAPTCHA ATTACKER v2.0 (Playwright)")
# #     print("="*60)
# #     print("Targets: Candy Match + Maze + Slider (All 3)")
# #     print("Methods: Async DOM Manipulation, Mouse Simulation, BFS")
# #     print("="*60 + "\n")
    
# #     attacker = AdvancedCAPTCHAAttacker(args.url)
    
# #     try:
# #         await attacker.init()
        
# #         for attempt in range(args.attempts):
# #             if attempt > 0:
# #                 print(f"\n\n{'='*60}")
# #                 print(f"STARTING ATTEMPT {attempt + 1}/{args.attempts}")
# #                 print('='*60)
# #                 await attacker.page.goto(args.url)
# #                 await asyncio.sleep(2)
            
# #             await attacker.solve_full_captcha_system()
            
# #             if attempt < args.attempts - 1:
# #                 await asyncio.sleep(3)
        
# #         attacker.print_stats()
        
# #     except Exception as e:
# #         print(f"\n❌ Fatal error during run: {e}")
# #         attacker.print_stats()
# #     finally:
# #         await attacker.close()


# # def main():
# #     parser = argparse.ArgumentParser(description='Advanced CAPTCHA Bot Attacker')
# #     parser.add_argument('--url', default='http://127.0.0.1:5500/index.html', 
# #                        help='Target URL') # Default changed to local dev URL for testing Playwright scripts
# #     parser.add_argument('--attempts', type=int, default=1, 
# #                        help='Number of full attempts')
    
# #     args = parser.parse_args()
    
# #     try:
# #         asyncio.run(run_attacker_async(args))
# #     except KeyboardInterrupt:
# #         print("\n⚠️  Interrupted by user")
# #     except Exception as e:
# #         print(f"\n❌ Global error in main execution: {e}")


# # if __name__ == '__main__':
# #     main()
# #!/usr/bin/env python3
# #!/usr/bin/env python3
# #!/usr/bin/env python3
# #!/usr/bin/env python3
# """
# Advanced CAPTCHA Bot Attacker - Playwright Async Implementation
# Intelligently solves all 3 CAPTCHA types: Candy Match, Maze, and Slider
# Usage: python3 advanced_captcha_attacker_playwright.py --url https://exam-portal-captcha-test.web.app/
# """

# import argparse
# import time
# import asyncio
# import json
# from collections import deque
# from playwright.async_api import async_playwright

# GRID_DIM = 3  # 3x3 for Candy Crush


# class AdvancedCAPTCHAAttacker:
#     def __init__(self, url):
#         self.url = url
#         self.browser = None
#         self.page = None
#         self.stats = {
#             'attempts': 0,
#             'candy_solved': 0,
#             'maze_solved': 0,
#             'slider_solved': 0,
#             'total_success': 0,
#             'failures': 0,
#             'start_time': time.time()
#         }

#     async def init(self):
#         """Initialize browser with stealth settings"""
#         print("🤖 Initializing Advanced CAPTCHA Attacker (Playwright Async)...")
        
#         p = await async_playwright().start()
        
#         # Use Chromium for best compatibility
#         self.browser = await p.chromium.launch(
#             headless=False,
#             slow_mo=50,
#             args=[
#                 "--start-maximized",
#                 "--disable-blink-features=AutomationControlled"
#             ]
#         )
        
#         self.page = await self.browser.new_page()
        
#         # Apply stealth: change navigator.webdriver
#         await self.page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"🌐 Navigating to: {self.url}")
#         await self.page.goto(self.url)
        
#         # Wait for page load
#         await self.page.wait_for_selector("#verifyBtn", timeout=10000)
#         await asyncio.sleep(2)
#         print("✅ CAPTCHA system loaded")

#     async def check_and_submit_final_verification(self):
#         """
#         Performs the final verification check and attempts to submit the form.
#         This must be called after all 3 individual CAPTCHAs are solved.
#         """
        
#         # 1. Attempt to find and click the FINAL submit/verify button
#         print("\n🏁 Attempting final verification...")
        
#         # Common IDs for the final button (adjust if your target uses a different ID)
#         final_submit_selectors = [
#             "#finalSubmitButton", 
#             "#verifyButton", 
#             "button:has-text('Verify')"
#         ]
        
#         final_button = None
#         for selector in final_submit_selectors:
#             try:
#                 locator = self.page.locator(selector).first
#                 if await locator.is_visible(timeout=1000):
#                     final_button = locator
#                     break
#             except:
#                 continue

#         if final_button:
#             print("   ✅ Found final verification button. Clicking...")
#             await final_button.click()
#             await asyncio.sleep(2) # Wait for server response/page update
#         else:
#             print("   ⚠️ No explicit final verification button found. Proceeding to status check.")
        
#         # 2. Check for overall success message/state
        
#         # Common success indicators (adjust if your target page uses different text)
#         success_indicators = [
#             self.page.locator("text=Verification Succeeded!"),
#             self.page.locator("text=Form Submitted Successfully"),
#             self.page.locator("#verificationStatus[data-status='success']"),
#             self.page.locator("text=You are verified")
#         ]
        
#         is_succeeded = False
#         for locator in success_indicators:
#             try:
#                 if await locator.is_visible(timeout=3000):
#                     is_succeeded = True
#                     break
#             except:
#                 pass

#         if is_succeeded:
#             print("\n\n🎉🎉 ALL CAPTCHAS SOLVED AND VERIFICATION SUCCEEDED! 🎉🎉")
#             # Assuming you have a stat for overall success
#             if 'total_success' in self.stats:
#                 self.stats['total_success'] += 1
            
#             # Close the page/browser (if not handled by the main loop cleanup)
#             # You can decide to close the page immediately here, or let the main loop handle it.
#             # Example to close page: await self.page.close() 
            
#             return True
#         else:
#             print("\n\n❌ VERIFICATION INCOMPLETE: Final success status not confirmed.")
#             # If you have a separate failure stat, update it here
#             return False

#     # ==================== CANDY CRUSH SOLVER ====================
    
#     # ==================== CANDY CRUSH SOLVER ====================
    
#     async def find_grid_cells(self):
#         """Find the 3x3 grid structure and its symbols using Playwright locators."""
#         try:
#             # 1. Locate all 9 grid cells first
#             all_cells_locator = self.page.locator("#gridContainer .grid-row .grid-cell")
#             cells_count = await all_cells_locator.count()

#             if cells_count != GRID_DIM * GRID_DIM:
#                 print(f"   ⚠️ Expected 9 cells, found {cells_count}.")
#                 return None, None
            
#             # 2. Structure the locators into a 3x3 array
#             grid_cells = []
#             for r in range(GRID_DIM):
#                 row = []
#                 for c in range(GRID_DIM):
#                     # Playwright locators are zero-indexed, CSS nth-child is one-indexed
#                     locator = self.page.locator(f".grid-row:nth-child({r + 1}) > .grid-cell:nth-child({c + 1})")
#                     row.append(locator)
#                 grid_cells.append(row)
            
#             # 3. Read symbols and classes by evaluating attributes on all cells
#             symbols = []
#             for r in range(GRID_DIM):
#                 row_symbols = []
#                 for c in range(GRID_DIM):
#                     cell_locator = grid_cells[r][c]
                    
#                     # Fetch text and class using a single async operation per cell
#                     cell_data = await cell_locator.evaluate("""
#                         (el) => ({
#                             text: el.textContent.trim() || '?',
#                             classes: el.className
#                         })
#                     """)
                    
#                     if "hidden-cell" in cell_data['classes']:
#                         row_symbols.append("?")
#                     else:
#                         row_symbols.append(cell_data['text'])

#                 symbols.append(row_symbols)
            
#             return grid_cells, symbols
        
#         except Exception as e:
#             print(f"   ❌ Error in find_grid_cells: {e}")
#             return None, None

#     async def reveal_all_hidden_cells(self):
#         """Click all cells with '?' to reveal them"""
#         print("   🔍 Revealing hidden cells...")
#         max_attempts = 10
        
#         for attempt in range(max_attempts):
            
#             # Find all currently hidden cells in one go
#             hidden_cells_count = await self.page.evaluate("""
#                 () => {
#                     const hiddenCells = document.querySelectorAll(".grid-cell.hidden-cell");
#                     if (hiddenCells.length > 0) {
#                         // Click the first one found
#                         hiddenCells[0].click();
#                         return hiddenCells.length;
#                     }
#                     return 0;
#                 }
#             """)

#             if hidden_cells_count == 0:
#                 print("   ✅ All cells revealed")
#                 return

#             await asyncio.sleep(0.3) # Wait for animation

#         print("   ⚠️  Some cells may remain hidden")

#     def has_three_in_row(self, grid):
#         """Check if grid has 3 in a row (horizontal or vertical)"""
#         # Check rows
#         for r in range(GRID_DIM):
#             if grid[r][0] == grid[r][1] == grid[r][2] and grid[r][0] != "?":
#                 return True
        
#         # Check columns
#         for c in range(GRID_DIM):
#             if grid[0][c] == grid[1][c] == grid[2][c] and grid[0][c] != "?":
#                 return True
        
#         return False

#     def find_candy_solution_bfs(self, symbols, max_depth=5):
#         """Use BFS to find shortest swap sequence (synchronous logic, as it's computation)"""
#         def flatten(mat):
#             return tuple(x for row in mat for x in row)
        
#         def unflatten(f):
#             return [list(f[i * GRID_DIM:(i + 1) * GRID_DIM]) for i in range(GRID_DIM)]
        
#         start = flatten(symbols)
        
#         # Generate all valid adjacent pairs
#         neighbors = []
#         for r in range(GRID_DIM):
#             for c in range(GRID_DIM):
#                 idx = r * GRID_DIM + c
#                 # Right
#                 if c + 1 < GRID_DIM:
#                     neighbors.append((idx, idx + 1))
#                 # Down
#                 if r + 1 < GRID_DIM:
#                     neighbors.append((idx, idx + GRID_DIM))
        
#         if self.has_three_in_row(symbols):
#             return []
        
#         queue = deque()
#         queue.append((start, []))
#         seen = {start}
        
#         while queue:
#             current, moves = queue.popleft()
            
#             if len(moves) >= max_depth:
#                 continue
            
#             for a, b in neighbors:
#                 # Swap
#                 lst = list(current)
#                 lst[a], lst[b] = lst[b], lst[a]
#                 new_state = tuple(lst)
                
#                 if new_state in seen:
#                     continue
                
#                 seen.add(new_state)
#                 new_moves = moves + [(a, b)]
#                 new_grid = unflatten(new_state)
                
#                 if self.has_three_in_row(new_grid):
#                     return new_moves
                
#                 queue.append((new_state, new_moves))
        
#         raise RuntimeError("No solution found within depth limit")

#     async def execute_swap(self, a, b):
#         """Execute a swap between two cells using Playwright locator clicks"""
#         r1, c1 = divmod(a, GRID_DIM)
#         r2, c2 = divmod(b, GRID_DIM)
        
#         grid_cells, _ = await self.find_grid_cells()
#         if not grid_cells:
#             raise RuntimeError("Grid disappeared")
        
#         cell1 = grid_cells[r1][c1]
        
#         # Check for locked cells via class attribute
#         if 'locked-cell' in await cell1.get_attribute('class'):
#              raise RuntimeError(f"Cell ({r1},{c1}) is locked")

#         # Click first cell
#         await cell1.click()
#         await asyncio.sleep(0.3)
        
#         # Re-read grid elements as they might have been re-rendered/repositioned after the first click
#         grid_cells, _ = await self.find_grid_cells()
#         if not grid_cells:
#             raise RuntimeError("Grid disappeared after first click")

#         cell2 = grid_cells[r2][c2]
        
#         if 'locked-cell' in await cell2.get_attribute('class'):
#             raise RuntimeError(f"Cell ({r2},{c2}) is locked")

#         # Click second cell
#         await cell2.click()
#         await asyncio.sleep(0.5)

#     async def solve_candy_crush(self):
#         """Main candy crush solving logic"""
#         print("\n🍬 Solving Candy Match CAPTCHA...")
        
#         try:
#             # Wait for modal to be visible
#             await self.page.wait_for_selector("#verificationModal:visible", timeout=10000)
            
#             await asyncio.sleep(1)
            
#             # Reveal all hidden cells
#             await self.reveal_all_hidden_cells()
            
#             # Read grid
#             _, symbols = await self.find_grid_cells()
#             if not symbols:
#                 print("❌ Grid not found or is malformed")
#                 return False
            
#             print("   Initial grid:")
#             for row in symbols:
#                 print(f"   {row}")
            
#             # Find solution
#             print("   🧠 Computing optimal solution...")
#             moves = self.find_candy_solution_bfs(symbols, max_depth=5)
            
#             print(f"   📋 Solution found: {len(moves)} moves")
#             print(f"   Swap sequence: {moves}")
            
#             for i, (a, b) in enumerate(moves):
#                 print(f" Move {i+1}/{len(moves)}: Swap cells {a} ↔ {b}")
#                 try:
#                     await self.execute_swap(a, b)
#                 except RuntimeError as e:
#                     print(f" ⚠️ {e}, trying alternative...")
#                     await self.page.click("#refreshBtn")
#                     await asyncio.sleep(1)
#                     return await self.solve_candy_crush()

#                 # Early success check after each move to catch website response before CAPTCHA closes
#                 try:
#                     await self.page.wait_for_selector("#successMessage", timeout=3000)
#                     print(f" 🎉 CAPTCHA solved early after move {i+1}")
#                     self.stats['candy_solved'] += 1
#                     await asyncio.sleep(2)
#                     return True
#                 except Exception:
#                     # If no success message yet, continue with next move
#                     pass

#                 await asyncio.sleep(0.5)  # short pause for stability

#             # Final verification after all moves
#             try:
#                 success_msg = self.page.locator("#successMessage:visible")
#                 await success_msg.wait_for(timeout=3000)
#                 print(" ✅ Candy Match SOLVED on final verification!")
#                 self.stats['candy_solved'] += 1
#                 await asyncio.sleep(2)
#                 return True
#             except Exception:
#                 # fallback: check for 3-in-a-row in grid state as last resort
#                 _, symbols = await self.find_grid_cells()
#                 if symbols and self.has_three_in_row(symbols):
#                     print(" ✅ Grid has 3-in-a-row! Assuming success on fallback...")
#                     self.stats['candy_solved'] += 1
#                     return True
#         except Exception:
#             print(" ❌ Candy Match failed after all verification attempts")
#             return False


#     # ==================== MAZE SOLVER ====================
    
#     # ==================== MAZE SOLVER (REVERTED TO JS INJECTION) ====================

#     async def get_maze_state(self):
#         """Extract complete game state from JavaScript using Playwright's evaluate."""
#         await asyncio.sleep(0.1) 
        
#         # NOTE: Using 'mazeCaptcha' instance name as derived from previous turns, 
#         # but the JS below also checks 'captchaInstance' from your old working code.
#         script = """
#         () => {
#             const captcha = window.mazeCaptcha || window.captchaInstance;
            
#             if (!captcha) return null;
            
#             // Ensure necessary properties exist (e.g., if we hit a loading state)
#             if (!captcha.player || !captcha.goal || !captcha.gameState) return null;

#             return {
#                 player: { x: captcha.player.x, y: captcha.player.y },
#                 checkpoints: captcha.checkpoints.map(cp => ({
#                     x: cp.x, y: cp.y, reached: cp.reached
#                 })),
#                 goal: { x: captcha.goal.x, y: captcha.goal.y },
#                 inversionLevel: captcha.gameState.invertionLevel
#                 // Add any other properties your logic requires, like obstacles
#             };
#         }
#         """
        
#         try:
#             # Wait for the maze object to be initialized
#             await self.page.wait_for_function(
#                 "window.mazeCaptcha || window.captchaInstance", 
#                 timeout=5000
#             )
#             result = await self.page.evaluate(script)
#             return result
#         except Exception as e:
#             print(f"   ⚠️  JS state access error: {str(e)[:50]}")
#             return None
    
#     def apply_inversion(self, move_x, move_y, inversion_level):
#         """Apply control inversion (synchronous helper)"""
#         if inversion_level == 1: move_x *= -1
#         elif inversion_level == 2: move_y *= -1
#         elif inversion_level == 3:
#             move_x *= -1
#             move_y *= -1
#         return move_x, move_y

#     async def move_player_js(self, move_x, move_y, duration=100):
#         """
#         Move player using direct JavaScript key control (Ported from working Selenium code).
#         This directly manipulates the game engine's internal key state.
#         """
#         keys_to_press = []
#         if move_x > 0: keys_to_press.append('arrowright')
#         elif move_x < 0: keys_to_press.append('arrowleft')
        
#         if move_y > 0: keys_to_press.append('arrowdown')
#         elif move_y < 0: keys_to_press.append('arrowup')
        
#         if not keys_to_press:
#             return

#         # Build JavaScript to hold keys and then release them after 'duration'
#         keys_str = "', '".join(keys_to_press)
        
#         script = f"""
#         (duration) => {{
#             const captcha = window.mazeCaptcha || window.captchaInstance;
#             if (!captcha || !captcha.keys) return;

#             const keys = ['{keys_str}'];
            
#             // Add all keys (press and hold)
#             keys.forEach(key => captcha.keys.add(key));
            
#             // Hold for duration then release
#             setTimeout(() => {{
#                 keys.forEach(key => captcha.keys.delete(key));
#             }}, duration);
#         }}
#         """
        
#         # Execute the script asynchronously
#         await self.page.evaluate(script, duration)

#     async def navigate_to_target(self, target, game_state, max_steps=400):
#         """Navigate player to target position using direct JS key control"""
#         steps = 0
#         last_distance = float('inf')
#         stuck_count = 0
        
#         print(f"   Starting navigation to ({target['x']:.0f}, {target['y']:.0f})")
        
#         while steps < max_steps:
#             current_state = await self.get_maze_state()
#             if not current_state:
#                 print("⚠️ Could not read game state, aborting navigation")
#                 return False
            
#             player = current_state['player']
            
#             # Check if reached target
#             dx = target['x'] - player['x']
#             dy = target['y'] - player['y']
#             distance = (dx**2 + dy**2)**0.5
            
#             if distance < 25:
#                 print(f"✅ Reached target at ({target['x']:.0f}, {target['y']:.0f})")
#                 return True
            
#             # Progress update
#             if steps % 30 == 0 and steps > 0:
#                 print(f"   Step {steps}: Player at ({player['x']:.0f}, {player['y']:.0f}), distance = {distance:.1f}px")
            
#             # Detect if stuck
#             if abs(distance - last_distance) < 1:
#                 stuck_count += 1
#                 if stuck_count > 20:
#                     print(f"⚠️ Stuck! Trying escape angle...")
#                     # Perform a small temporary perpendicular movement (e.g., UP and RIGHT)
#                     # We inject a specific script to move up/right for 100ms
#                     await self.page.evaluate("""
#                         () => {
#                             const captcha = window.mazeCaptcha || window.captchaInstance;
#                             if (!captcha || !captcha.keys) return;
#                             captcha.keys.add('arrowup');
#                             captcha.keys.add('arrowright');
#                             setTimeout(() => {
#                                 captcha.keys.clear();
#                             }, 100);
#                         }
#                     """)
#                     await asyncio.sleep(0.15) # Wait for movement to finish
#                     stuck_count = 0
#                     continue
#             else:
#                 stuck_count = 0
            
#             last_distance = distance
            
#             # Calculate movement direction
#             move_x = 1 if dx > 10 else (-1 if dx < -10 else 0)
#             move_y = 1 if dy > 10 else (-1 if dy < -10 else 0)
            
#             # Apply inversion
#             move_x, move_y = self.apply_inversion(
#                 move_x, 
#                 move_y, 
#                 current_state['inversionLevel']
#             )
            
#             # Direct control via JavaScript
#             await self.move_player_js(move_x, move_y, duration=100)
            
#             await asyncio.sleep(0.05)
#             steps += 1
        
#         print(f"❌ Navigation timeout after {max_steps} steps")
#         return False

#     async def solve_maze(self):
#         """Solve the entire maze intelligently using Playwright"""
#         print("\n🎮 Starting intelligent maze solving...")
        
#         self.stats['attempts'] += 1
        
#         try:
#             await self.page.wait_for_selector("#mazeCanvas", timeout=10000)
            
#             # Focus the canvas for good measure, though direct JS manipulation shouldn't need it
#             await self.page.focus("#mazeCanvas")
#             await asyncio.sleep(2)
            
#             game_state = await self.get_maze_state()
            
#             if not game_state:
#                 print("❌ Could not access game state")
#                 self.stats['failures'] += 1
#                 return False
            
#             print(f"📊 Game State: {len(game_state['checkpoints'])} checkpoints")
            
#             # Navigate to each checkpoint
#             for i, checkpoint in enumerate(game_state['checkpoints']):
#                 print(f"\n🚩 Checkpoint {i+1}/{len(game_state['checkpoints'])}: ({checkpoint['x']:.0f}, {checkpoint['y']:.0f})")
                
#                 if not await self.navigate_to_target(checkpoint, game_state, max_steps=400):
#                     print(f"❌ Failed to reach checkpoint {i+1}")
#                     self.stats['failures'] += 1
#                     return False
                
#                 await asyncio.sleep(0.5)
                
#                 # Update game state after each checkpoint
#                 game_state = await self.get_maze_state()
#                 if not game_state: return False
#                 print(f"🔄 Inversion level now: {game_state['inversionLevel']}")
            
#             # Navigate to goal
#             print(f"\n🏁 Final Goal: ({game_state['goal']['x']:.0f}, {game_state['goal']['y']:.0f})")
            
#             if not await self.navigate_to_target(game_state['goal'], game_state, max_steps=400):
#                 print("❌ Failed to reach goal")
#                 self.stats['failures'] += 1
#                 return False
            
#             await asyncio.sleep(1)
            
#             # Check completion using the same status element
#             status = await self.page.locator("#statusValue").inner_text(timeout=5000)
            
#             if status == "Complete":
#                 print("✅ MAZE SOLVED! Clicking submit...")
#                 submit_btn = self.page.locator("#mazeSubmitBtn")
#                 await submit_btn.click()
                
#                 self.stats['maze_solved'] += 1
#                 return True
#             else:
#                 print("❌ Maze not marked as complete")
#                 self.stats['failures'] += 1
#                 return False
                
#         except Exception as e:
#             print(f"❌ Error in solve_maze: {str(e)}")
#             self.stats['failures'] += 1
#             return False

#     # ==================== SLIDER SOLVER (FIXED) ====================

#     async def get_slider_data_js(self):
#         """Extract slider state from JavaScript asynchronously"""
#         # Wait for the sliderState to be initialized
#         await self.page.wait_for_function(
#             "() => typeof sliderState !== 'undefined' && sliderState.targets && sliderState.targets.length === 3",
#             timeout=10000
#         )
#         await asyncio.sleep(0.5)
        
#         script = """
#         () => {
#             return {
#                 targets: sliderState.targets.map(t => ({x: t.x, y: t.y})),
#                 order: sliderState.sliderOrder.map(c => c.name.toLowerCase()),
#                 sliders: sliderState.sliders.map(s => s.dataset.colorName)
#             };
#         }
#         """
        
#         return await self.page.evaluate(script)

#     async def drag_slider_to_target(self, slider_id, target_x):
#         """Drag slider to specific target X coordinate - positions LEFT EDGE of slider at target_x"""
        
#         # Get the slider element
#         slider = self.page.locator(f"#{slider_id}")
#         box = await slider.bounding_box()
#         if not box:
#             raise RuntimeError(f"Slider {slider_id} not found")

#         # Get the container position
#         container_id = slider_id.replace("slider", "sliderContainer")
#         container = self.page.locator(f"#{container_id}")
#         container_box = await container.bounding_box()
        
#         if not container_box:
#             raise RuntimeError(f"Container {container_id} not found")
        
#         # Calculate positions
#         # Current slider center position
#         start_x = box["x"] + box["width"] / 2
#         start_y = box["y"] + box["height"] / 2
        
#         # Target: Place slider's LEFT EDGE at target_x pixels from container's left
#         # So slider CENTER should be at: container_left + target_x + (slider_width / 2)
#         end_x = container_box["x"] + target_x + box["width"] / 2
#         end_y = start_y
        
#         print(f"      Moving {slider_id}:")
#         print(f"        Start: ({start_x:.0f}, {start_y:.0f})")
#         print(f"        End:   ({end_x:.0f}, {end_y:.0f})")
#         print(f"        Delta: {end_x - start_x:.0f}px")

#         # Perform drag
#         await self.page.mouse.move(start_x, start_y)
#         await asyncio.sleep(0.05)
#         await self.page.mouse.down()
#         await asyncio.sleep(0.05)
#         await self.page.mouse.move(end_x, end_y, steps=20)
#         await asyncio.sleep(0.05)
#         await self.page.mouse.up()
        
#         # Critical: Wait for validation to complete
#         await asyncio.sleep(0.3)
        
#         return True

#     async def solve_slider(self):
#         """Main slider solving logic - moves sliders in CORRECT ORDER"""
#         print("\n🧩 Solving Slider Puzzle CAPTCHA...")
        
#         try:
#             await asyncio.sleep(2)
            
#             # Get state from JavaScript
#             data = await self.get_slider_data_js()
#             if not data:
#                 print("   ❌ Could not access sliderState")
#                 return False
            
#             targets = data["targets"]
#             correct_order = data["order"]
#             slider_colors = data["sliders"]
            
#             print(f"   📋 Target positions: {[t['x'] for t in targets]}")
#             print(f"   📋 Required order: {correct_order}")
#             print(f"   📋 Slider colors: {slider_colors}")
            
#             # CRITICAL: Move sliders in the EXACT ORDER required by sliderState.sliderOrder
#             # Each slider must be placed correctly before moving the next one
#             for move_num, required_color in enumerate(correct_order, 1):
#                 # Find which slider has this color
#                 try:
#                     slider_index = slider_colors.index(required_color)
#                 except ValueError:
#                     print(f"   ❌ Color '{required_color}' not found in sliders")
#                     return False
                
#                 # Get the target position for THIS slider (not the move number!)
#                 slider_id = f"slider{slider_index + 1}"
#                 target_x = targets[slider_index]["x"]
                
#                 print(f"\n   Move {move_num}/3: Place {required_color.upper()} ({slider_id}) at X={target_x:.0f}px")
                
#                 # Drag the slider
#                 if not await self.drag_slider_to_target(slider_id, target_x):
#                     print(f"   ❌ Failed to drag {slider_id}")
#                     return False
                
#                 # Check if puzzle was reset (validation failed)
#                 is_reset = await self.page.evaluate("""
#                     () => {
#                         // Check if completedOrder was cleared (indicates reset)
#                         return sliderState.completedOrder.length === 0 && sliderState.placed.every(p => !p);
#                     }
#                 """)
                
#                 if is_reset and move_num > 0:
#                     print(f"   ❌ Puzzle was reset after move {move_num} - order violation detected")
#                     return False
                
#                 # Verify this move was accepted
#                 completed_count = await self.page.evaluate("() => sliderState.completedOrder.length")
#                 print(f"      ✅ Move accepted ({completed_count}/{len(correct_order)} completed)")
                
#                 # Wait before next move
#                 await asyncio.sleep(0.5)
            
#             # Final verification
#             print("\n   ⏳ Waiting for final validation...")
#             await asyncio.sleep(1.0)
            
#             # Check completion status
#             is_completed = await self.page.evaluate("""
#                 () => {
#                     return {
#                         completed: sliderState.completed,
#                         placedCount: sliderState.placed.filter(p => p).length,
#                         orderCount: sliderState.completedOrder.length
#                     };
#                 }
#             """)
            
#             print(f"   Status: completed={is_completed['completed']}, " +
#                 f"placed={is_completed['placedCount']}/3, " +
#                 f"order={is_completed['orderCount']}/3")
            
#             if is_completed['completed']:
#                 print("   ✅ SLIDER SOLVED!")
#                 self.stats['slider_solved'] += 1
#                 await asyncio.sleep(1)
#                 return True
            
#             # Check for final success screen as fallback
#             try:
#                 final_success = self.page.locator("#finalSuccess")
#                 if await final_success.is_visible(timeout=2000):
#                     class_attr = await final_success.get_attribute("class")
#                     if "active" in class_attr:
#                         print("   ✅ SLIDER SOLVED! (Final success screen)")
#                         self.stats['slider_solved'] += 1
#                         await asyncio.sleep(1)
#                         return True
#             except:
#                 pass
            
#             print("   ❌ Slider puzzle not completed")
#             return False
                
#         except Exception as e:
#             print(f"   ❌ Slider error: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return False

#     # ==================== MAIN FLOW ====================
    
#     async def detect_active_captcha(self):
#         """Intelligently detect which CAPTCHA type is currently active"""
#         await asyncio.sleep(1)
        
#         current_url = self.page.url
        
#         if "mode=maze" in current_url:
#             return "maze"
#         elif "mode=slider" in current_url:
#             return "slider"
        
#         # Check for candy modal
#         try:
#             if await self.page.locator("#verificationModal").is_visible():
#                 return "candy"
#         except:
#             pass
        
#         # Check for maze canvas
#         try:
#             if await self.page.locator("#mazeCanvas").is_visible():
#                 return "maze"
#         except:
#             pass
        
#         # Check for slider elements
#         try:
#             if await self.page.locator("#slider1").is_visible():
#                 return "slider"
#         except:
#             pass
        
#         return "unknown"

#     async def solve_full_captcha_system(self):
#         """Solve all 3 CAPTCHAs in sequence (handles random order)"""
#         print("\n" + "="*60)
#         print("🎯 STARTING FULL CAPTCHA CHALLENGE")
#         print("="*60)
#         print("⚠️  Note: CAPTCHA order is randomized by the system")
        
#         self.stats['attempts'] += 1
        
#         try:
#             # Click start button
#             verify_btn = self.page.locator("#verifyBtn")
#             await verify_btn.click()
#             print("✅ Started verification process")
#             await asyncio.sleep(2)
            
#             # Check for progress indicator
#             try:
#                 order_text = await self.page.locator("#progressSubtitle").inner_text()
#                 print(f"📋 System info: {order_text}")
#             except:
#                 pass
            
#             # Solve CAPTCHAs until all 3 are complete
#             captchas_solved = 0
#             max_captchas = 3
            
#             while captchas_solved < max_captchas:
#                 captcha_num = captchas_solved + 1
                
#                 print(f"\n{'='*60}")
#                 print(f"CAPTCHA {captcha_num}/3 - Detecting type...")
#                 print('='*60)
                
#                 # Detect which CAPTCHA is active
#                 captcha_type = await self.detect_active_captcha()
#                 print(f"🔍 Detected: {captcha_type.upper()}")
                
#                 success = False
                
#                 # Solve based on type
#                 if captcha_type == "maze":
#                     success = await self.solve_maze()
#                 elif captcha_type == "slider":
#                     success = await self.solve_slider()
#                 elif captcha_type == "candy":
#                     success = await self.solve_candy_crush()
#                 else:
#                     print(f"   ❌ Unknown CAPTCHA type!")
#                     success = False

#                 if not success:
#                     print(f"\n❌ Failed at CAPTCHA {captcha_num}/3 ({captcha_type})")
#                     self.stats['failures'] += 1
#                     return False
                
#                 captchas_solved += 1
                
#                 # Handle alerts that may appear
#                 try:
#                     async with self.page.expect_event('dialog', timeout=2000) as dialog_info:
#                         alert = await dialog_info.value
#                         print(f"   📢 Alert: {alert.message[:80]}...")
#                         await alert.accept()
#                         await asyncio.sleep(1)
#                 except:
#                     pass
                
#                 # Check if we're done (back on index page)
#                 if "verified=1" in self.page.url:
#                     print(f"\n🎉 All CAPTCHAs completed! Returned to index page.")
#                     break
                
#                 # Click continue button if on success page
#                 if captchas_solved < max_captchas:
#                     await asyncio.sleep(1.5)
#                     try:
#                         continue_btn = self.page.locator("#continueBtn")
#                         await continue_btn.click(timeout=8000)
#                         print(f"✅ CAPTCHA {captcha_num}/3 complete, continuing...")
#                         await asyncio.sleep(2)
#                     except Exception as e:
#                         print(f"   ⚠️  Continue button not found: {str(e)[:50]}")
#                         await asyncio.sleep(1)
            
#             # Final verification check
#             await asyncio.sleep(2)
            
#             # Check if back on index with verified status
#             if "verified=1" in self.page.url:
#                 print("\n" + "="*60)
#                 print("🎉 ALL 3 CAPTCHAS SOLVED SUCCESSFULLY!")
#                 print("="*60)
#                 self.stats['total_success'] += 1
                
#                 # Click next button to go to exam
#                 try:
#                     next_btn = self.page.locator("#nextBtn")
#                     await next_btn.click(timeout=5000)
#                     await asyncio.sleep(2)
                    
#                     print("✅ Successfully bypassed CAPTCHA system!")
#                     return True
#                 except:
#                     print("✅ Verification complete (next button not found)")
#                     return True
#             else:
#                 print("\n⚠️  Verification may be incomplete")
#                 print(f"   Current URL: {self.page.url}")
                
#                 self.stats['failures'] += 1
#                 return False
            
#         except Exception as e:
#             print(f"\n❌ Critical error: {str(e)}")
#             self.stats['failures'] += 1
#             return False

#     def print_stats(self):
#         """Print attack statistics (synchronous)"""
#         elapsed = time.time() - self.stats['start_time']
        
#         print("\n" + "="*60)
#         print("📊 ATTACK STATISTICS")
#         print("="*60)
#         print(f"Total Attempts:       {self.stats['attempts']}")
#         print(f"Full Success:         {self.stats['total_success']}")
#         print(f"Candy Solved:         {self.stats['candy_solved']}")
#         print(f"Maze Solved:          {self.stats['maze_solved']}")
#         print(f"Slider Solved:        {self.stats['slider_solved']}")
#         print(f"Failures:             {self.stats['failures']}")
#         print(f"Time Elapsed:         {elapsed:.2f}s")
        
#         if self.stats['total_success'] > 0:
#             success_rate = (self.stats['total_success'] / self.stats['attempts']) * 100
#             avg_time = elapsed / self.stats['total_success']
#             print(f"Success Rate:         {success_rate:.1f}%")
#             print(f"Avg Time/Success:     {avg_time:.2f}s")
        
#         print("="*60)

#     async def close(self):
#         """Close browser asynchronously"""
#         if self.browser:
#             await asyncio.sleep(3)  # Keep open briefly to see result
#             await self.browser.close()
#             print("🛑 Browser closed")


# async def run_attacker_async(args):
#     """Main async execution wrapper"""
#     print("\n" + "="*60)
#     print("🔓 ADVANCED CAPTCHA ATTACKER v2.0 (Playwright)")
#     print("="*60)
#     print("Targets: Candy Match + Maze + Slider (All 3)")
#     print("Methods: Async DOM Manipulation, Mouse Simulation, BFS")
#     print("="*60 + "\n")
    
#     attacker = AdvancedCAPTCHAAttacker(args.url)
    
#     try:
#         await attacker.init()
        
#         for attempt in range(args.attempts):
#             if attempt > 0:
#                 print(f"\n\n{'='*60}")
#                 print(f"STARTING ATTEMPT {attempt + 1}/{args.attempts}")
#                 print('='*60)
#                 await attacker.page.goto(args.url)
#                 await asyncio.sleep(2)
            
#             await attacker.solve_full_captcha_system()
            
#             if attempt < args.attempts - 1:
#                 await asyncio.sleep(3)
        
#         attacker.print_stats()
        
#     except Exception as e:
#         print(f"\n❌ Fatal error during run: {e}")
#         attacker.print_stats()
#     finally:
#         await attacker.close()


# def main():
#     parser = argparse.ArgumentParser(description='Advanced CAPTCHA Bot Attacker')
#     parser.add_argument('--url', default='http://127.0.0.1:5500/index.html', 
#                        help='Target URL')
#     parser.add_argument('--attempts', type=int, default=1, 
#                        help='Number of full attempts')
    
#     args = parser.parse_args()
    
#     try:
#         asyncio.run(run_attacker_async(args))
#     except KeyboardInterrupt:
#         print("\n⚠️  Interrupted by user")
#     except Exception as e:
#         print(f"\n❌ Global error in main execution: {e}")


# if __name__ == '__main__':
#     main()
#!/usr/bin/env python3
#!/usr/bin/env python3
# """
# Advanced CAPTCHA Bot Attacker - Playwright Async Implementation (FIXED SLIDER LOGIC)
# Intelligently solves all 3 CAPTCHA types: Candy Match, Maze, and Slider
# Usage: python3 advanced_captcha_attacker_FIXED.py --url https://exam-portal-captcha-test.web.app/
# """

# import argparse
# import time
# import asyncio
# from collections import deque
# from playwright.async_api import async_playwright

# GRID_DIM = 3  # 3x3 for Candy Crush


# class AdvancedCAPTCHAAttacker:
#     def __init__(self, url):
#         self.url = url
#         self.browser = None
#         self.page = None
#         self.stats = {
#             'attempts': 0,
#             'candy_solved': 0,
#             'maze_solved': 0,
#             'slider_solved': 0,
#             'total_success': 0,
#             'failures': 0,
#             'start_time': time.time()
#         }

#     async def init(self):
#         """Initialize browser with stealth settings"""
#         print("🤖 Initializing Advanced CAPTCHA Attacker (Playwright Async)...")
        
#         p = await async_playwright().start()
        
#         # Use Chromium for best compatibility
#         self.browser = await p.chromium.launch(
#             headless=False,
#             slow_mo=50,
#             args=[
#                 "--start-maximized",
#                 "--disable-blink-features=AutomationControlled"
#             ]
#         )
        
#         self.page = await self.browser.new_page()
        
#         # Apply stealth: change navigator.webdriver
#         await self.page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"🌐 Navigating to: {self.url}")
#         await self.page.goto(self.url)
        
#         # Wait for page load
#         await self.page.wait_for_selector("#verifyBtn", timeout=10000)
#         await asyncio.sleep(2)
#         print("✅ CAPTCHA system loaded")

#     # ==================== CANDY CRUSH SOLVER ====================
    
#     async def find_grid_cells(self):
#         """Find the 3x3 grid structure and its symbols using Playwright locators."""
#         try:
#             # 1. Locate all 9 grid cells first
#             all_cells_locator = self.page.locator("#gridContainer .grid-row .grid-cell")
#             cells_count = await all_cells_locator.count()

#             if cells_count != GRID_DIM * GRID_DIM:
#                 print(f"   ⚠️ Expected 9 cells, found {cells_count}.")
#                 return None, None
            
#             # 2. Structure the locators into a 3x3 array
#             grid_cells = []
#             for r in range(GRID_DIM):
#                 row = []
#                 for c in range(GRID_DIM):
#                     locator = self.page.locator(f".grid-row:nth-child({r + 1}) > .grid-cell:nth-child({c + 1})")
#                     row.append(locator)
#                 grid_cells.append(row)
            
#             # 3. Read symbols and classes
#             symbols = []
#             for r in range(GRID_DIM):
#                 row_symbols = []
#                 for c in range(GRID_DIM):
#                     cell_locator = grid_cells[r][c]
                    
#                     cell_data = await cell_locator.evaluate("""
#                         (el) => ({
#                             text: el.textContent.trim() || '?',
#                             classes: el.className
#                         })
#                     """)
                    
#                     if "hidden-cell" in cell_data['classes']:
#                         row_symbols.append("?")
#                     else:
#                         row_symbols.append(cell_data['text'])

#                 symbols.append(row_symbols)
            
#             return grid_cells, symbols
        
#         except Exception as e:
#             print(f"   ❌ Error in find_grid_cells: {e}")
#             return None, None

#     async def reveal_all_hidden_cells(self):
#         """Click all cells with '?' to reveal them"""
#         print("   🔍 Revealing hidden cells...")
#         max_attempts = 10
        
#         for attempt in range(max_attempts):
#             hidden_cells_count = await self.page.evaluate("""
#                 () => {
#                     const hiddenCells = document.querySelectorAll(".grid-cell.hidden-cell");
#                     if (hiddenCells.length > 0) {
#                         hiddenCells[0].click();
#                         return hiddenCells.length;
#                     }
#                     return 0;
#                 }
#             """)

#             if hidden_cells_count == 0:
#                 print("   ✅ All cells revealed")
#                 return

#             await asyncio.sleep(0.3)

#         print("   ⚠️  Some cells may remain hidden")

#     def has_three_in_row(self, grid):
#         """Check if grid has 3 in a row (horizontal or vertical)"""
#         # Check rows
#         for r in range(GRID_DIM):
#             if grid[r][0] == grid[r][1] == grid[r][2] and grid[r][0] != "?":
#                 return True
        
#         # Check columns
#         for c in range(GRID_DIM):
#             if grid[0][c] == grid[1][c] == grid[2][c] and grid[0][c] != "?":
#                 return True
        
#         return False

#     def find_candy_solution_bfs(self, symbols, max_depth=5):
#         """Use BFS to find shortest swap sequence"""
#         def flatten(mat):
#             return tuple(x for row in mat for x in row)
        
#         def unflatten(f):
#             return [list(f[i * GRID_DIM:(i + 1) * GRID_DIM]) for i in range(GRID_DIM)]
        
#         start = flatten(symbols)
        
#         # Generate all valid adjacent pairs
#         neighbors = []
#         for r in range(GRID_DIM):
#             for c in range(GRID_DIM):
#                 idx = r * GRID_DIM + c
#                 if c + 1 < GRID_DIM:
#                     neighbors.append((idx, idx + 1))
#                 if r + 1 < GRID_DIM:
#                     neighbors.append((idx, idx + GRID_DIM))
        
#         if self.has_three_in_row(symbols):
#             return []
        
#         queue = deque()
#         queue.append((start, []))
#         seen = {start}
        
#         while queue:
#             current, moves = queue.popleft()
            
#             if len(moves) >= max_depth:
#                 continue
            
#             for a, b in neighbors:
#                 lst = list(current)
#                 lst[a], lst[b] = lst[b], lst[a]
#                 new_state = tuple(lst)
                
#                 if new_state in seen:
#                     continue
                
#                 seen.add(new_state)
#                 new_moves = moves + [(a, b)]
#                 new_grid = unflatten(new_state)
                
#                 if self.has_three_in_row(new_grid):
#                     return new_moves
                
#                 queue.append((new_state, new_moves))
        
#         raise RuntimeError("No solution found within depth limit")

#     async def execute_swap(self, a, b):
#         """Execute a swap between two cells"""
#         r1, c1 = divmod(a, GRID_DIM)
#         r2, c2 = divmod(b, GRID_DIM)
        
#         grid_cells, _ = await self.find_grid_cells()
#         if not grid_cells:
#             raise RuntimeError("Grid disappeared")
        
#         cell1 = grid_cells[r1][c1]
        
#         if 'locked-cell' in await cell1.get_attribute('class'):
#              raise RuntimeError(f"Cell ({r1},{c1}) is locked")

#         await cell1.click()
#         await asyncio.sleep(0.3)
        
#         grid_cells, _ = await self.find_grid_cells()
#         if not grid_cells:
#             raise RuntimeError("Grid disappeared after first click")

#         cell2 = grid_cells[r2][c2]
        
#         if 'locked-cell' in await cell2.get_attribute('class'):
#             raise RuntimeError(f"Cell ({r2},{c2}) is locked")

#         await cell2.click()
#         await asyncio.sleep(0.5)

#     async def solve_candy_crush(self):
#         """Main candy crush solving logic"""
#         print("\n🍬 Solving Candy Match CAPTCHA...")
        
#         try:
#             await self.page.wait_for_selector("#verificationModal:visible", timeout=10000)
#             await asyncio.sleep(1)
            
#             await self.reveal_all_hidden_cells()
            
#             _, symbols = await self.find_grid_cells()
#             if not symbols:
#                 print("❌ Grid not found or is malformed")
#                 return False
            
#             print("   Initial grid:")
#             for row in symbols:
#                 print(f"   {row}")
            
#             print("   🧠 Computing optimal solution...")
#             moves = self.find_candy_solution_bfs(symbols, max_depth=5)
            
#             print(f"   📋 Solution found: {len(moves)} moves")
#             print(f"   Swap sequence: {moves}")
            
#             for i, (a, b) in enumerate(moves):
#                 print(f" Move {i+1}/{len(moves)}: Swap cells {a} ↔ {b}")
#                 try:
#                     await self.execute_swap(a, b)
#                 except RuntimeError as e:
#                     print(f" ⚠️ {e}, trying alternative...")
#                     await self.page.click("#refreshBtn")
#                     await asyncio.sleep(1)
#                     return await self.solve_candy_crush()

#                 try:
#                     await self.page.wait_for_selector("#successMessage", timeout=3000)
#                     print(f" 🎉 CAPTCHA solved early after move {i+1}")
#                     self.stats['candy_solved'] += 1
#                     await asyncio.sleep(2)
#                     return True
#                 except Exception:
#                     pass

#                 await asyncio.sleep(0.5)

#             try:
#                 success_msg = self.page.locator("#successMessage:visible")
#                 await success_msg.wait_for(timeout=3000)
#                 print(" ✅ Candy Match SOLVED!")
#                 self.stats['candy_solved'] += 1
#                 await asyncio.sleep(2)
#                 return True
#             except Exception:
#                 _, symbols = await self.find_grid_cells()
#                 if symbols and self.has_three_in_row(symbols):
#                     print(" ✅ Grid has 3-in-a-row! Success!")
#                     self.stats['candy_solved'] += 1
#                     return True
#         except Exception:
#             print(" ❌ Candy Match failed")
#             return False

#     # ==================== MAZE SOLVER ====================

#     async def get_maze_state(self):
#         """Extract complete game state from JavaScript"""
#         await asyncio.sleep(0.1) 
        
#         script = """
#         () => {
#             const captcha = window.mazeCaptcha || window.captchaInstance;
            
#             if (!captcha) return null;
            
#             if (!captcha.player || !captcha.goal || !captcha.gameState) return null;

#             return {
#                 player: { x: captcha.player.x, y: captcha.player.y },
#                 checkpoints: captcha.checkpoints.map(cp => ({
#                     x: cp.x, y: cp.y, reached: cp.reached
#                 })),
#                 goal: { x: captcha.goal.x, y: captcha.goal.y },
#                 inversionLevel: captcha.gameState.invertionLevel
#             };
#         }
#         """
        
#         try:
#             await self.page.wait_for_function(
#                 "window.mazeCaptcha || window.captchaInstance", 
#                 timeout=5000
#             )
#             result = await self.page.evaluate(script)
#             return result
#         except Exception as e:
#             print(f"   ⚠️  JS state access error: {str(e)[:50]}")
#             return None
    
#     def apply_inversion(self, move_x, move_y, inversion_level):
#         """Apply control inversion"""
#         if inversion_level == 1: move_x *= -1
#         elif inversion_level == 2: move_y *= -1
#         elif inversion_level == 3:
#             move_x *= -1
#             move_y *= -1
#         return move_x, move_y

#     async def move_player_js(self, move_x, move_y, duration=100):
#         """Move player using direct JavaScript key control"""
#         keys_to_press = []
#         if move_x > 0: keys_to_press.append('arrowright')
#         elif move_x < 0: keys_to_press.append('arrowleft')
        
#         if move_y > 0: keys_to_press.append('arrowdown')
#         elif move_y < 0: keys_to_press.append('arrowup')
        
#         if not keys_to_press:
#             return

#         keys_str = "', '".join(keys_to_press)
        
#         script = f"""
#         (duration) => {{
#             const captcha = window.mazeCaptcha || window.captchaInstance;
#             if (!captcha || !captcha.keys) return;

#             const keys = ['{keys_str}'];
            
#             keys.forEach(key => captcha.keys.add(key));
            
#             setTimeout(() => {{
#                 keys.forEach(key => captcha.keys.delete(key));
#             }}, duration);
#         }}
#         """
        
#         await self.page.evaluate(script, duration)

#     async def navigate_to_target(self, target, game_state, max_steps=400):
#         """Navigate player to target position"""
#         steps = 0
#         last_distance = float('inf')
#         stuck_count = 0
        
#         print(f"   Starting navigation to ({target['x']:.0f}, {target['y']:.0f})")
        
#         while steps < max_steps:
#             current_state = await self.get_maze_state()
#             if not current_state:
#                 print("⚠️ Could not read game state, aborting navigation")
#                 return False
            
#             player = current_state['player']
            
#             dx = target['x'] - player['x']
#             dy = target['y'] - player['y']
#             distance = (dx**2 + dy**2)**0.5
            
#             if distance < 25:
#                 print(f"✅ Reached target at ({target['x']:.0f}, {target['y']:.0f})")
#                 return True
            
#             if steps % 30 == 0 and steps > 0:
#                 print(f"   Step {steps}: Player at ({player['x']:.0f}, {player['y']:.0f}), distance = {distance:.1f}px")
            
#             if abs(distance - last_distance) < 1:
#                 stuck_count += 1
#                 if stuck_count > 20:
#                     print(f"⚠️ Stuck! Trying escape angle...")
#                     await self.page.evaluate("""
#                         () => {
#                             const captcha = window.mazeCaptcha || window.captchaInstance;
#                             if (!captcha || !captcha.keys) return;
#                             captcha.keys.add('arrowup');
#                             captcha.keys.add('arrowright');
#                             setTimeout(() => {
#                                 captcha.keys.clear();
#                             }, 100);
#                         }
#                     """)
#                     await asyncio.sleep(0.15)
#                     stuck_count = 0
#                     continue
#             else:
#                 stuck_count = 0
            
#             last_distance = distance
            
#             move_x = 1 if dx > 10 else (-1 if dx < -10 else 0)
#             move_y = 1 if dy > 10 else (-1 if dy < -10 else 0)
            
#             move_x, move_y = self.apply_inversion(
#                 move_x, 
#                 move_y, 
#                 current_state['inversionLevel']
#             )
            
#             await self.move_player_js(move_x, move_y, duration=100)
            
#             await asyncio.sleep(0.05)
#             steps += 1
        
#         print(f"❌ Navigation timeout after {max_steps} steps")
#         return False

#     async def solve_maze(self):
#         """Solve the entire maze intelligently"""
#         print("\n🎮 Starting intelligent maze solving...")
        
#         self.stats['attempts'] += 1
        
#         try:
#             await self.page.wait_for_selector("#mazeCanvas", timeout=10000)
#             await self.page.focus("#mazeCanvas")
#             await asyncio.sleep(2)
            
#             game_state = await self.get_maze_state()
            
#             if not game_state:
#                 print("❌ Could not access game state")
#                 self.stats['failures'] += 1
#                 return False
            
#             print(f"📊 Game State: {len(game_state['checkpoints'])} checkpoints")
            
#             for i, checkpoint in enumerate(game_state['checkpoints']):
#                 print(f"\n🚩 Checkpoint {i+1}/{len(game_state['checkpoints'])}: ({checkpoint['x']:.0f}, {checkpoint['y']:.0f})")
                
#                 if not await self.navigate_to_target(checkpoint, game_state, max_steps=400):
#                     print(f"❌ Failed to reach checkpoint {i+1}")
#                     self.stats['failures'] += 1
#                     return False
                
#                 await asyncio.sleep(0.5)
                
#                 game_state = await self.get_maze_state()
#                 if not game_state: return False
#                 print(f"🔄 Inversion level now: {game_state['inversionLevel']}")
            
#             print(f"\n🏁 Final Goal: ({game_state['goal']['x']:.0f}, {game_state['goal']['y']:.0f})")
            
#             if not await self.navigate_to_target(game_state['goal'], game_state, max_steps=400):
#                 print("❌ Failed to reach goal")
#                 self.stats['failures'] += 1
#                 return False
            
#             await asyncio.sleep(1)
            
#             status = await self.page.locator("#statusValue").inner_text(timeout=5000)
            
#             if status == "Complete":
#                 print("✅ MAZE SOLVED! Clicking submit...")
#                 submit_btn = self.page.locator("#mazeSubmitBtn")
#                 await submit_btn.click()
                
#                 self.stats['maze_solved'] += 1
#                 return True
#             else:
#                 print("❌ Maze not marked as complete")
#                 self.stats['failures'] += 1
#                 return False
                
#         except Exception as e:
#             print(f"❌ Error in solve_maze: {str(e)}")
#             self.stats['failures'] += 1
#             return False

#     # ==================== SLIDER SOLVER (FIXED) ====================

#     async def get_slider_data_js(self):
#         """Extract slider state from JavaScript"""
#         await self.page.wait_for_function(
#             "() => typeof sliderState !== 'undefined' && sliderState.targets && sliderState.targets.length === 3",
#             timeout=10000
#         )
#         await asyncio.sleep(0.5)
        
#         script = """
#         () => {
#             return {
#                 targets: sliderState.targets.map(t => ({x: t.x, y: t.y})),
#                 order: sliderState.sliderOrder.map(c => c.name.toLowerCase()),
#                 sliders: sliderState.sliders.map(s => s.dataset.colorName)
#             };
#         }
#         """
        
#         return await self.page.evaluate(script)

#     async def drag_slider_to_target(self, slider_id, target_x):
#         """Drag slider to specific target X coordinate - positions LEFT EDGE at target_x"""
        
#         slider = self.page.locator(f"#{slider_id}")
#         box = await slider.bounding_box()
#         if not box:
#             raise RuntimeError(f"Slider {slider_id} not found")

#         container_id = slider_id.replace("slider", "sliderContainer")
#         container = self.page.locator(f"#{container_id}")
#         container_box = await container.bounding_box()
        
#         if not container_box:
#             raise RuntimeError(f"Container {container_id} not found")
        
#         # Current slider center position
#         start_x = box["x"] + box["width"] / 2
#         start_y = box["y"] + box["height"] / 2
        
#         # The validation calculates: px = mouseX - container.left - slider.width/2
#         # We want px = target_x
#         # So: mouseX - container.left - slider.width/2 = target_x
#         # Therefore: mouseX = container.left + target_x + slider.width/2
#         end_x = container_box["x"] + target_x + box["width"] / 2
#         end_y = start_y
        
#         print(f"      Moving {slider_id}:")
#         print(f"        Container left: {container_box['x']:.1f}px")
#         print(f"        Target X (left edge): {target_x:.1f}px")
#         print(f"        Slider width: {box['width']:.1f}px")
#         print(f"        Current center: ({start_x:.1f}, {start_y:.1f})")
#         print(f"        Target center: ({end_x:.1f}, {end_y:.1f})")
#         print(f"        Movement: {end_x - start_x:.1f}px")

#         # Perform precise drag
#         await self.page.mouse.move(start_x, start_y)
#         await asyncio.sleep(0.1)
#         await self.page.mouse.down()
#         await asyncio.sleep(0.1)
        
#         # Drag in stages for better precision
#         steps = 20
#         for step in range(1, steps + 1):
#             progress = step / steps
#             # Ease-out motion for final precision
#             eased_progress = 1 - (1 - progress) ** 2
#             intermediate_x = start_x + (end_x - start_x) * eased_progress
#             await self.page.mouse.move(intermediate_x, end_y, steps=1)
#             await asyncio.sleep(0.02)
        
#         # Final precise positioning
#         await self.page.mouse.move(end_x, end_y, steps=1)
#         await asyncio.sleep(0.1)
#         await self.page.mouse.up()
        
#         # Wait for validation to complete
#         await asyncio.sleep(0.4)
        
#         # Verify the slider position after drag
#         final_box = await slider.bounding_box()
#         if final_box:
#             # Calculate where the left edge ended up
#             actual_left_edge = final_box["x"] - container_box["x"]
#             error = abs(actual_left_edge - target_x)
#             print(f"        Actual left edge: {actual_left_edge:.1f}px (error: {error:.1f}px)")
            
#             if error > 15:
#                 print(f"        ⚠️  Large positioning error detected!")
#                 # Try a correction drag
#                 correction_x = container_box["x"] + target_x + box["width"] / 2
#                 correction_start_x = final_box["x"] + final_box["width"] / 2
                
#                 if abs(correction_x - correction_start_x) > 5:
#                     print(f"        🔧 Applying correction: {correction_start_x:.1f} → {correction_x:.1f}")
#                     await self.page.mouse.move(correction_start_x, end_y)
#                     await asyncio.sleep(0.05)
#                     await self.page.mouse.down()
#                     await asyncio.sleep(0.05)
#                     await self.page.mouse.move(correction_x, end_y, steps=10)
#                     await asyncio.sleep(0.05)
#                     await self.page.mouse.up()
#                     await asyncio.sleep(0.3)
        
#         return True

#     async def solve_slider(self):
#         """FIXED: Moves sliders in correct ORDER, each to its OWN target position"""
#         print("\n🧩 Solving Slider Puzzle CAPTCHA...")
        
#         try:
#             await asyncio.sleep(2)
            
#             # Get state from JavaScript
#             data = await self.get_slider_data_js()
#             if not data:
#                 print("   ❌ Could not access sliderState")
#                 return False
            
#             targets = data["targets"]  # [x1, x2, x3] - target positions indexed by slider ID
#             correct_order = data["order"]  # ['purple', 'red', 'yellow'] - ORDER they must be placed
#             slider_colors = data["sliders"]  # ['red', 'purple', 'yellow'] - colors indexed by slider ID
            
#             print(f"   📋 Target positions (indexed by slider ID 1-3): {[t['x'] for t in targets]}")
#             print(f"   📋 Required placement ORDER: {correct_order}")
#             print(f"   📋 Slider colors (indexed by slider ID 1-3): {slider_colors}")
#             print()
#             print("   🔑 KEY INSIGHT: Each slider must be placed IN ORDER at its OWN target position")
#             print(f"      - Slider with color '{correct_order[0]}' must be placed first")
#             print(f"      - Slider with color '{correct_order[1]}' must be placed second")
#             print(f"      - Slider with color '{correct_order[2]}' must be placed third")
            
#             # Move sliders in the ORDER specified by correct_order
#             for move_num, required_color in enumerate(correct_order, 1):
#                 # Find which slider ID (0, 1, or 2) has this color
#                 try:
#                     slider_index = slider_colors.index(required_color)
#                 except ValueError:
#                     print(f"   ❌ Color '{required_color}' not found in sliders")
#                     return False
                
#                 # This slider needs to go to targets[slider_index] (its own target)
#                 slider_id = f"slider{slider_index + 1}"
#                 target_x = targets[slider_index]["x"]
                
#                 print(f"\n   ➡️  Move {move_num}/3: Place {required_color.upper()} ({slider_id}) at X={target_x:.0f}px")
                
#                 # Drag the slider to its target
#                 if not await self.drag_slider_to_target(slider_id, target_x):
#                     print(f"   ❌ Failed to drag {slider_id}")
#                     return False
                
#                 # Wait for JavaScript validation to process
#                 await asyncio.sleep(0.4)
                
#                 # Get detailed validation state
#                 validation_data = await self.page.evaluate("""
#                     (sliderIndex) => {
#                         const slider = sliderState.sliders[sliderIndex];
#                         const rect = slider.parentElement.getBoundingClientRect();
#                         const sliderRect = slider.getBoundingClientRect();
                        
#                         // Calculate px the same way the validation does
#                         const currentLeft = sliderRect.left - rect.left;
#                         const targetX = sliderState.targets[sliderIndex].x;
#                         const error = Math.abs(currentLeft - targetX);
                        
#                         return {
#                             currentLeft: currentLeft,
#                             targetX: targetX,
#                             error: error,
#                             isWithinTolerance: error < 10,
#                             completedOrder: sliderState.completedOrder,
#                             placed: sliderState.placed,
#                             completed: sliderState.completed
#                         };
#                     }
#                 """, slider_index)
                
#                 print(f"      📊 Validation check:")
#                 print(f"         Current left edge: {validation_data['currentLeft']:.1f}px")
#                 print(f"         Target position: {validation_data['targetX']:.1f}px")
#                 print(f"         Error: {validation_data['error']:.1f}px (tolerance: <10px)")
#                 print(f"         Within tolerance: {validation_data['isWithinTolerance']}")
                
#                 completed_count = len(validation_data['completedOrder'])
                
#                 # Check if positioning was accurate enough
#                 if not validation_data['isWithinTolerance']:
#                     print(f"   ❌ Slider not positioned accurately enough!")
#                     print(f"      Error {validation_data['error']:.1f}px exceeds 10px tolerance")
                    
#                     # Try one more time with direct style manipulation as fallback
#                     print(f"   🔧 Attempting direct positioning fallback...")
#                     await self.page.evaluate(f"""
#                         (sliderIndex, targetX) => {{
#                             const slider = sliderState.sliders[sliderIndex];
#                             slider.style.left = targetX + 'px';
                            
#                             // Trigger the validation manually
#                             sliderState.placed[sliderIndex] = true;
#                             sliderState.completedOrder.push(slider.dataset.colorName);
                            
#                             const expectedOrder = sliderState.sliderOrder.map(c => c.name.toLowerCase()).slice(0, sliderState.completedOrder.length);
#                             if (sliderState.completedOrder.join(',') !== expectedOrder.join(',')) {{
#                                 // Reset if wrong order
#                                 sliderState.placed = [false, false, false];
#                                 sliderState.completedOrder = [];
#                             }}
#                         }}
#                     """, slider_index, target_x)
                    
#                     await asyncio.sleep(0.3)
                    
#                     # Re-check
#                     validation_data = await self.page.evaluate("""
#                         () => ({
#                             completedOrder: sliderState.completedOrder,
#                             placed: sliderState.placed,
#                             completed: sliderState.completed
#                         })
#                     """)
#                     completed_count = len(validation_data['completedOrder'])
                
#                 # Verify the move was accepted
#                 if completed_count != move_num:
#                     print(f"   ❌ Move rejected! Expected {move_num} completed, got {completed_count}")
#                     print(f"      Completed order: {validation_data['completedOrder']}")
#                     print(f"      Expected order: {correct_order[:move_num]}")
#                     return False
                
#                 # Check if puzzle was reset
#                 if not any(validation_data['placed']) and move_num > 0:
#                     print(f"   ❌ Puzzle was reset - order violation!")
#                     return False
                
#                 print(f"      ✅ Move accepted! ({completed_count}/3 completed)")
#                 print(f"         Order so far: {validation_data['completedOrder']}")
                
#                 # Check if we're done early
#                 if validation_data['completed']:
#                     print(f"\n   🎉 Puzzle completed after move {move_num}!")
#                     self.stats['slider_solved'] += 1
#                     await asyncio.sleep(1)
#                     return True
                
#                 # Wait before next move
#                 await asyncio.sleep(0.5)
            
#             # Final verification
#             print("\n   ⏳ Final verification...")
#             await asyncio.sleep(1.0)
            
#             # Check completion status
#             final_status = await self.page.evaluate("""
#                 () => ({
#                     completed: sliderState.completed,
#                     placed: sliderState.placed,
#                     completedOrder: sliderState.completedOrder
#                 })
#             """)
            
#             print(f"   Final status:")
#             print(f"     - Completed: {final_status['completed']}")
#             print(f"     - Placed count: {sum(final_status['placed'])}/3")
#             print(f"     - Order: {final_status['completedOrder']}")
            
#             if final_status['completed']:
#                 print("   ✅ SLIDER SOLVED!")
#                 self.stats['slider_solved'] += 1
#                 await asyncio.sleep(1)
#                 return True
            
#             # Fallback: Check for visual success indicator
#             try:
#                 final_success = self.page.locator("#finalSuccess.active")
#                 if await final_success.is_visible(timeout=2000):
#                     print("   ✅ SLIDER SOLVED! (Visual confirmation)")
#                     self.stats['slider_solved'] += 1
#                     await asyncio.sleep(1)
#                     return True
#             except:
#                 pass
            
#             print("   ❌ Slider verification failed")
#             return False
                
#         except Exception as e:
#             print(f"   ❌ Slider error: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             return False

#     # ==================== MAIN FLOW ====================
    
#     async def detect_active_captcha(self):
#         """Detect which CAPTCHA type is currently active"""
#         await asyncio.sleep(1)
        
#         current_url = self.page.url
        
#         if "mode=maze" in current_url:
#             return "maze"
#         elif "mode=slider" in current_url:
#             return "slider"
        
#         try:
#             if await self.page.locator("#verificationModal").is_visible():
#                 return "candy"
#         except:
#             pass
        
#         try:
#             if await self.page.locator("#mazeCanvas").is_visible():
#                 return "maze"
#         except:
#             pass
        
#         try:
#             if await self.page.locator("#slider1").is_visible():
#                 return "slider"
#         except:
#             pass
        
#         return "unknown"

#     async def solve_full_captcha_system(self):
#         """Solve all 3 CAPTCHAs in sequence"""
#         print("\n" + "="*60)
#         print("🎯 STARTING FULL CAPTCHA CHALLENGE")
#         print("="*60)
#         print("⚠️  Note: CAPTCHA order is randomized by the system")
        
#         self.stats['attempts'] += 1
        
#         try:
#             verify_btn = self.page.locator("#verifyBtn")
#             await verify_btn.click()
#             print("✅ Started verification process")
#             await asyncio.sleep(2)
            
#             try:
#                 order_text = await self.page.locator("#progressSubtitle").inner_text()
#                 print(f"📋 System info: {order_text}")
#             except:
#                 pass
            
#             captchas_solved = 0
#             max_captchas = 3
            
#             while captchas_solved < max_captchas:
#                 captcha_num = captchas_solved + 1
                
#                 print(f"\n{'='*60}")
#                 print(f"CAPTCHA {captcha_num}/3 - Detecting type...")
#                 print('='*60)
                
#                 captcha_type = await self.detect_active_captcha()
#                 print(f"🔍 Detected: {captcha_type.upper()}")
                
#                 success = False
                
#                 if captcha_type == "maze":
#                     success = await self.solve_maze()
#                 elif captcha_type == "slider":
#                     success = await self.solve_slider()
#                 elif captcha_type == "candy":
#                     success = await self.solve_candy_crush()
#                 else:
#                     print(f"   ❌ Unknown CAPTCHA type!")
#                     success = False

#                 if not success:
#                     print(f"\n❌ Failed at CAPTCHA {captcha_num}/3 ({captcha_type})")
#                     self.stats['failures'] += 1
#                     return False
                
#                 captchas_solved += 1
                
#                 try:
#                     async with self.page.expect_event('dialog', timeout=2000) as dialog_info:
#                         alert = await dialog_info.value
#                         print(f"   📢 Alert: {alert.message[:80]}...")
#                         await alert.accept()
#                         await asyncio.sleep(1)
#                 except:
#                     pass
                
#                 if "verified=1" in self.page.url:
#                     print(f"\n🎉 All CAPTCHAs completed! Returned to index page.")
#                     break
                
#                 if captchas_solved < max_captchas:
#                     await asyncio.sleep(1.5)
#                     try:
#                         continue_btn = self.page.locator("#continueBtn")
#                         await continue_btn.click(timeout=8000)
#                         print(f"✅ CAPTCHA {captcha_num}/3 complete, continuing...")
#                         await asyncio.sleep(2)
#                     except Exception as e:
#                         print(f"   ⚠️  Continue button not found: {str(e)[:50]}")
#                         await asyncio.sleep(1)
            
#             await asyncio.sleep(2)
            
#             if "verified=1" in self.page.url:
#                 print("\n" + "="*60)
#                 print("🎉 ALL 3 CAPTCHAS SOLVED SUCCESSFULLY!")
#                 print("="*60)
#                 self.stats['total_success'] += 1
                
#                 try:
#                     next_btn = self.page.locator("#nextBtn")
#                     await next_btn.click(timeout=5000)
#                     await asyncio.sleep(2)
                    
#                     print("✅ Successfully bypassed CAPTCHA system!")
#                     return True
#                 except:
#                     print("✅ Verification complete (next button not found)")
#                     return True
#             else:
#                 print("\n⚠️  Verification may be incomplete")
#                 print(f"   Current URL: {self.page.url}")
                
#                 self.stats['failures'] += 1
#                 return False
            
#         except Exception as e:
#             print(f"\n❌ Critical error: {str(e)}")
#             self.stats['failures'] += 1
#             return False

#     def print_stats(self):
#         """Print attack statistics"""
#         elapsed = time.time() - self.stats['start_time']
        
#         print("\n" + "="*60)
#         print("📊 ATTACK STATISTICS")
#         print("="*60)
#         print(f"Total Attempts:       {self.stats['attempts']}")
#         print(f"Full Success:         {self.stats['total_success']}")
#         print(f"Candy Solved:         {self.stats['candy_solved']}")
#         print(f"Maze Solved:          {self.stats['maze_solved']}")
#         print(f"Slider Solved:        {self.stats['slider_solved']}")
#         print(f"Failures:             {self.stats['failures']}")
#         print(f"Time Elapsed:         {elapsed:.2f}s")
        
#         if self.stats['total_success'] > 0:
#             success_rate = (self.stats['total_success'] / self.stats['attempts']) * 100
#             avg_time = elapsed / self.stats['total_success']
#             print(f"Success Rate:         {success_rate:.1f}%")
#             print(f"Avg Time/Success:     {avg_time:.2f}s")
        
#         print("="*60)

#     async def close(self):
#         """Close browser"""
#         if self.browser:
#             await asyncio.sleep(3)
#             await self.browser.close()
#             print("🛑 Browser closed")


# async def run_attacker_async(args):
#     """Main async execution wrapper"""
#     print("\n" + "="*60)
#     print("🔓 ADVANCED CAPTCHA ATTACKER v2.1 (FIXED SLIDER)")
#     print("="*60)
#     print("Targets: Candy Match + Maze + Slider (All 3)")
#     print("FIX: Slider now places tiles in CORRECT ORDER")
#     print("="*60 + "\n")
    
#     attacker = AdvancedCAPTCHAAttacker(args.url)
    
#     try:
#         await attacker.init()
        
#         for attempt in range(args.attempts):
#             if attempt > 0:
#                 print(f"\n\n{'='*60}")
#                 print(f"STARTING ATTEMPT {attempt + 1}/{args.attempts}")
#                 print('='*60)
#                 await attacker.page.goto(args.url)
#                 await asyncio.sleep(2)
            
#             await attacker.solve_full_captcha_system()
            
#             if attempt < args.attempts - 1:
#                 await asyncio.sleep(3)
        
#         attacker.print_stats()
        
#     except Exception as e:
#         print(f"\n❌ Fatal error during run: {e}")
#         attacker.print_stats()
#     finally:
#         await attacker.close()


# def main():
#     parser = argparse.ArgumentParser(description='Advanced CAPTCHA Bot Attacker (FIXED)')
#     parser.add_argument('--url', default='http://127.0.0.1:5500/index.html', 
#                        help='Target URL')
#     parser.add_argument('--attempts', type=int, default=1, 
#                        help='Number of full attempts')
    
#     args = parser.parse_args()
    
#     try:
#         asyncio.run(run_attacker_async(args))
#     except KeyboardInterrupt:
#         print("\n⚠️  Interrupted by user")
#     except Exception as e:
#         print(f"\n❌ Global error in main execution: {e}")


# if __name__ == '__main__':
#     main()
#!/usr/bin/env python3
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