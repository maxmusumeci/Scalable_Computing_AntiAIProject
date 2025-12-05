#!/usr/bin/env python3
# Authors - Yuxin and Liwei
"""
Advanced CAPTCHA Bot Attacker - Playwright Async Implementation
Intelligently solves all 3 CAPTCHA types: Candy Match, Maze, and Slider
Usage: python3 advanced_captcha_attacker_playwright.py --url https://exam-portal-captcha-test.web.app/
"""

import argparse
import time
import asyncio
import json
from collections import deque
from playwright.async_api import async_playwright
import os
import aiohttp  # Requires additional installation: pip install aiohttp
import re
from dashscope import MultiModalConversation
import dashscope
import base64

GRID_DIM = 3  # 3x3 for Candy Crush

MAX_ATTEMPTS = 10  # Maximum number of attempts to solve the CAPTCHA
SUCCESS_CHECK_DELAY = 1.5  # Delay to wait for verification animation (seconds)

dashscope.api_key = "sk-47699cd41a90450f9664a387d00b9883"
URL = "http://127.0.0.1:5500/public/index.html"

class AdvancedCAPTCHAAttacker:
    def __init__(self, url):
        self.url = url
        self.browser = None
        self.page = None
        # Qwen related configuration
        self.qwen_api_key = os.getenv("QWEN_API_KEY", "sk-47699cd41a90450f9664a387d00b9883")  # Priority from environment variable
        self.qwen_api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
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

    async def check_and_submit_final_verification(self):
        """
        Performs the final verification check and attempts to submit the form.
        This must be called after all 3 individual CAPTCHAs are solved.
        """
        
        # 1. Attempt to find and click the FINAL submit/verify button
        print("\n🏁 Attempting final verification...")
        
        # Common IDs for the final button (adjust if your target uses a different ID)
        final_submit_selectors = [
            "#finalSubmitButton", 
            "#verifyButton", 
            "button:has-text('Verify')"
        ]
        
        final_button = None
        for selector in final_submit_selectors:
            try:
                locator = self.page.locator(selector).first
                if await locator.is_visible(timeout=1000):
                    final_button = locator
                    break
            except:
                continue

        if final_button:
            print("   ✅ Found final verification button. Clicking...")
            await final_button.click()
            await asyncio.sleep(2)  # Wait for server response/page update
        else:
            print("   ⚠️ No explicit final verification button found. Proceeding to status check.")
        
        # 2. Check for overall success message/state
        success_indicators = [
            self.page.locator("text=Verification Succeeded!"),
            self.page.locator("text=Form Submitted Successfully"),
            self.page.locator("#verificationStatus[data-status='success']"),
            self.page.locator("text=You are verified")
        ]
        
        is_succeeded = False
        for locator in success_indicators:
            try:
                if await locator.is_visible(timeout=3000):
                    is_succeeded = True
                    break
            except:
                pass

        if is_succeeded:
            print("\n\n🎉🎉 ALL CAPTCHAS SOLVED AND VERIFICATION SUCCEEDED! 🎉🎉")
            if 'total_success' in self.stats:
                self.stats['total_success'] += 1
            return True
        else:
            print("\n\n❌ VERIFICATION INCOMPLETE: Final success status not confirmed.")
            return False

   # ==================== CANDY CRUSH SOLVER ====================
    async def is_verification_success(self):
        """Check if CAPTCHA verification is successful (adapts to actual page indicators)"""
        try:
            success_selectors = [
                "#successMessage:visible",
                ".winning:visible",
                "[data-status='success']"
            ]
            for selector in success_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=SUCCESS_CHECK_DELAY * 1000)
                    return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"⚠️ Verification status check error: {str(e)}")
            return False

    async def get_candy_moves_from_screenshot(self, page, attempt):
        """Capture fresh screenshot for each attempt to ensure model uses latest grid state"""
        await page.wait_for_selector(".grid-cell")
        await asyncio.sleep(0.8)

        modal = await page.query_selector(".modal-container")
        if not modal:
            modal = await page.query_selector(".grid-container")
        if not modal:
            print("❌ Failed to find screenshot target")
            return [], [], []

        screenshot_bytes = await modal.screenshot(type="png")
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
        image_uri = f"data:image/png;base64,{screenshot_base64}"

        prompt = f"""
        This is a 3x3 candy CAPTCHA (Attempt {attempt}), analyze based on the LATEST state in the current screenshot:
        Rules:
        1. Hidden cells display "?" and need to be clicked to reveal; locked cells have special styles and cannot be operated
        2. Goal: Swap adjacent cells to form 3 identical symbols in a row or column
        3. Note: Must make decisions based on the actual state of the current screenshot

        Output strictly in this JSON format:
        {{
            "locked_cells": [[0,0]],
            "reveal_cells": [[0,1], [2,2]],
            "swap_cells": [[0,1], [0,2]]
        }}
        """

        messages = [
            {
                "role": "user",
                "content": [{"image": image_uri}, {"text": prompt}]
            }
        ]

        try:
            response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=messages,
                result_format='message'
            )

            raw_text = ""
            if hasattr(response, 'output') and response.output:
                if hasattr(response.output, 'choices') and response.output.choices:
                    choice = response.output.choices[0]
                    if hasattr(choice, 'message') and choice.message:
                        content = choice.message.content
                        if isinstance(content, str):
                            raw_text = content
                        elif isinstance(content, list):
                            for item in content:
                                raw_text += item.get('text', '') if isinstance(item, dict) else str(item)

            if not raw_text:
                raw_text = str(response)
            print(f"🤖 Attempt {attempt} - Model output: {raw_text}")

        except Exception as e:
            print(f"❌ Model call error: {str(e)}")
            return [], [], []

        try:
            raw_text = re.sub(r'```(?:json)?\s*|\s*```', '', raw_text, flags=re.IGNORECASE)
            json_match = re.search(r'\{[\s\S]*\}', raw_text)
            if not json_match:
                raise ValueError("No JSON data found")
            raw_json = re.sub(r'\((\d+)\s*,\s*(\d+)\)', r'[\1,\2]', json_match.group())
            result = json.loads(raw_json)

            locked_cells = [(int(cell[0]), int(cell[1])) for cell in result.get("locked_cells", []) if len(cell) == 2]
            reveal_cells = [(int(cell[0]), int(cell[1])) for cell in result.get("reveal_cells", []) if len(cell) == 2]
            swap_cells = [(int(cell[0]), int(cell[1])) for cell in result.get("swap_cells", []) if len(cell) == 2]

            return locked_cells, reveal_cells, swap_cells

        except Exception as e:
            print(f"⚠️ Parsing failed: {str(e)}, using fallback extraction")
            locked_match = re.search(r'locked_cells\s*:\s*\[(.*?)\]', raw_text, re.DOTALL)
            reveal_match = re.search(r'reveal_cells\s*:\s*\[(.*?)\]', raw_text, re.DOTALL)
            swap_match = re.search(r'swap_cells\s*:\s*\[(.*?)\]', raw_text, re.DOTALL)

            parse_cells = lambda match: [(int(m[0]), int(m[1])) for m in re.findall(r'(\d+)\s*,\s*(\d+)', match.group(1))] if match else []
            return parse_cells(locked_match), parse_cells(reveal_match), parse_cells(swap_match)

    async def click_cell(self, page, row, col, locked_cells):
        """Click a cell at specified coordinates (0-indexed), skip locked/invalid cells"""
        if (row, col) in locked_cells:
            print(f"⚠️ Skipping locked cell ({row},{col})")
            return False

        try:
            selector = f".grid-row:nth-child({row+1}) > .grid-cell:nth-child({col+1})"
            cell = await page.query_selector(selector)
            if not cell:
                print(f"❌ Cell not found: ({row},{col})")
                return False
            await cell.click()
            await asyncio.sleep(0.5)
            return True
        except Exception as e:
            print(f"❌ Cell click error: {str(e)}")
            return False

    async def solve_candy_crush(self):
        """Main function to run the candy CAPTCHA attacker"""
        async with async_playwright() as p:
            print("✅ Candy CAPTCHA detected, starting solving attempts...")
            verification_success = False

            for attempt in range(1, MAX_ATTEMPTS + 1):
                print(f"\n===== Attempt {attempt}/{MAX_ATTEMPTS} =====")
                locked_cells, reveal_cells, swap_cells = await self.get_candy_moves_from_screenshot(self.page, attempt)
                print(f"📊 Analysis result - Locked: {locked_cells}, Reveal: {reveal_cells}, Swap: {swap_cells}")

                # Reveal hidden cells
                for (row, col) in reveal_cells:
                    await self.click_cell(self.page, row, col, locked_cells)

                # Perform swap
                if len(swap_cells) >= 2:
                    (r1, c1), (r2, c2) = swap_cells[:2]
                    if (r1, c1) not in locked_cells and (r2, c2) not in locked_cells:
                        print(f"🔄 Performing swap: ({r1},{c1}) ↔ ({r2},{c2})")
                        await self.click_cell(self.page, r1, c1, locked_cells)
                        await self.click_cell(self.page, r2, c2, locked_cells)
                        await asyncio.sleep(SUCCESS_CHECK_DELAY)
                        verification_success = await self.is_verification_success()
                        if verification_success:
                            print("🎉 Verification successful!")
                            break
                    else:
                        print("⚠️ Swap includes locked cells, skipping")
                else:
                    print("⚠️ No valid swap pair received, attempting refresh")
                    try:
                        refresh_btn = await self.page.query_selector("#refreshBtn")
                        if refresh_btn:
                            await refresh_btn.click()
                            await asyncio.sleep(1)
                            print("✅ Grid refreshed")
                    except:
                        pass

            if not verification_success:
                print(f"\n❌ Maximum attempts ({MAX_ATTEMPTS}) reached, failed to complete verification")


    # ==================== MAZE SOLVER (QWEN INTEGRATION) ====================
    # ==================== MAZE SOLVER (QWEN INTEGRATION) ====================
    async def get_maze_state(self):
        """Get maze state"""
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
                // Note: This is invertionLevel (spelled as such in frontend)
                inversionLevel: captcha.gameState.invertionLevel,
                obstacles: captcha.obstacles ? captcha.obstacles.map(o => ({
                    x: o.x, y: o.y, width: o.width, height: o.height
                })) : []
            };
        }
        """
        
        try:
            await self.page.wait_for_function(
                "window.mazeCaptcha || window.captchaInstance", 
                timeout=5000
            )
            return await self.page.evaluate(script)
        except Exception as e:
            print(f"   ⚠️  JS state access error: {str(e)[:50]}")
            return None

    async def query_qwen_for_move(self, game_state, target, recent_positions=None):
        """Query Qwen model for next move direction (including recent trajectory to avoid back-and-forth oscillation)"""
        if not self.qwen_api_key:
            raise ValueError("Please set QWEN_API_KEY environment variable")

        # Recent positions for提示"不要在几个点之间来回"
        recent_str = "[]"
        if recent_positions:
            recent_str = "[" + ", ".join(
                f"({x:.1f},{y:.1f})" for (x, y) in list(recent_positions)
            ) + "]"

        # Format maze state information
        state_desc = f"""
        Maze state:
        - Player position: (x={game_state['player']['x']:.1f}, y={game_state['player']['y']:.1f})
        - Target position: (x={target['x']:.1f}, y={target['y']:.1f})
        - Direction inversion level: {game_state['inversionLevel']} (handled automatically by system, think in normal directions)
        - Unreached checkpoints: {[f"({cp['x']:.1f},{cp['y']:.1f})" for cp in game_state['checkpoints'] if not cp['reached']]}
        - Recent position sequence: {recent_str}
        """

        # Build prompt: no longer requires model to handle inversion, just use up/down/left/right normally
        prompt = f"""
        You are a maze navigation assistant. Please help the player complete the following tasks:
        1. First reach all incomplete checkpoints in order (must reach checkpoint 1 first, then checkpoint 2, finally checkpoint 3).
        2. Only proceed to the final goal after all checkpoints are reached.
        3. You only need to assume normal controls: up=up, down=down, left=left, right=right.
           "Direction inversion is handled automatically by the system, do not reverse directions in your answer".
        4. Try to choose directions that gradually move the player closer to the current target.
        5. If this would cause the player to move back and forth between recent positions (e.g., A-B-A-B), please try a different direction to avoid looping between 2-3 coordinates.

        Current target coordinates to move to: (x={target['x']:.1f}, y={target['y']:.1f})

        {state_desc}

        Please return only one English word: up / down / left / right. Do not add any additional explanations or punctuation.
        """

        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "qwen-plus",
                "input": {"prompt": prompt},
                "parameters": {"temperature": 0.1}
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.qwen_api_key}"
            }

            async with session.post(self.qwen_api_url, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise RuntimeError(f"Qwen API call failed: {await response.text()}")
                
                result = await response.json()
                move = result.get("output", {}).get("text", "").strip().lower()
                
                if move not in ["up", "down", "left", "right"]:
                    raise RuntimeError(f"Invalid move command: {move}")
                return move

    def convert_move_to_coordinates(self, move):
        """Convert text move command to coordinate changes (logic remains unchanged)"""
        move_map = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }
        return move_map.get(move, (0, 0))

    def apply_inversion(self, move_x, move_y, inversion_level):
        """Apply direction inversion (frontend uses inversionLevel, handled according to original rules)"""
        if inversion_level == 1:
            return (-move_x, move_y)
        elif inversion_level == 2:
            return (move_x, -move_y)
        elif inversion_level == 3:
            return (-move_x, -move_y)
        return (move_x, move_y)

    async def move_player_js(self, move_x, move_y, duration=100):
        """Execute movement"""
        keys_to_press = []
        if move_x > 0: 
            keys_to_press.append('arrowright')
        elif move_x < 0: 
            keys_to_press.append('arrowleft')
        
        if move_y > 0: 
            keys_to_press.append('arrowdown')
        elif move_y < 0: 
            keys_to_press.append('arrowup')
        
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

    async def navigate_to_target(self, target, max_steps=400):
        """Use Qwen model to navigate to target position (enhanced stuck and small loop detection)"""
        steps = 0
        last_positions = deque(maxlen=8)   # Record recent positions
        best_distance = float('inf')       # Historical minimum distance to target
        no_improve_steps = 0               # How long with no significant improvement

        print(f"   Starting navigation to target ({target['x']:.0f}, {target['y']:.0f})")
        
        while steps < max_steps:
            current_state = await self.get_maze_state()
            if not current_state:
                print("⚠️ Unable to get maze state, terminating navigation")
                return False
            
            player = current_state['player']
            pos = (round(player['x'], 1), round(player['y'], 1))
            last_positions.append(pos)
            
            # Calculate distance to target
            dx = target['x'] - player['x']
            dy = target['y'] - player['y']
            distance = (dx**2 + dy**2) ** 0.5
            
            # Update "best distance" and "no improvement count"
            if distance + 1 < best_distance:  # Allow some tolerance
                best_distance = distance
                no_improve_steps = 0
            else:
                no_improve_steps += 1
            
            # Reached target
            if distance < 25:
                print(f"✅ Reached target position ({target['x']:.0f}, {target['y']:.0f})")
                return True
            
            # Print progress
            if steps % 10 == 0:
                print(f"   Step {steps}: Position ({player['x']:.0f}, {player['y']:.0f}), Distance to target: {distance:.1f}px")
            
            # ---------- Enhanced stuck / small loop detection ----------
            is_stuck = (
                len(last_positions) == last_positions.maxlen and
                all(p == last_positions[0] for p in last_positions)
            )
            # Moving back and forth between 2-3 points, e.g., A-B-A-B or A-B-C-A...
            is_loop = (
                len(last_positions) == last_positions.maxlen and
                1 < len(set(last_positions)) <= 3
            )
            # No significant progress towards target for a long time
            no_progress = no_improve_steps > 30

            if is_stuck or is_loop or no_progress:
                reason = "completely stuck" if is_stuck else ("small loop" if is_loop else "no significant progress for a long time")
                print(f"⚠️ Detected {reason}, attempting random movement to break the situation")
                
                # Use original style random key JS
                await self.page.evaluate("""
                    () => {
                        const captcha = window.mazeCaptcha || window.captchaInstance;
                        if (!captcha || !captcha.keys) return;
                        const dirs = ['arrowup', 'arrowdown', 'arrowleft', 'arrowright'];
                        const key = dirs[Math.floor(Math.random() * dirs.length)];
                        captcha.keys.add(key);
                        setTimeout(() => captcha.keys.delete(key), 100);
                    }
                """)
                await asyncio.sleep(0.2)
                
                last_positions.clear()
                no_improve_steps = 0
                steps += 1
                continue
            # ---------- End stuck detection ----------
            
            try:
                # Query Qwen for next move, passing recent path to reduce back-and-forth jitter
                move = await self.query_qwen_for_move(current_state, target, last_positions)
                print(f"   Qwen suggested move: {move}")
                
                # Convert to coordinate movement
                move_x, move_y = self.convert_move_to_coordinates(move)
                
                # Apply direction inversion (Qwen thinks in normal directions, handled uniformly here)
                move_x, move_y = self.apply_inversion(move_x, move_y, current_state['inversionLevel'])
                
                # Execute movement
                await self.move_player_js(move_x, move_y, duration=100)
                
            except Exception as e:
                print(f"   ⚠️ Movement decision error: {str(e)}, using fallback strategy ({str(e)})")
                # Fallback strategy: move directly towards target
                move_x = 1 if dx > 10 else (-1 if dx < -10 else 0)
                move_y = 1 if dy > 10 else (-1 if dy < -10 else 0)
                move_x, move_y = self.apply_inversion(move_x, move_y, current_state['inversionLevel'])
                await self.move_player_js(move_x, move_y, duration=100)
            
            await asyncio.sleep(0.1)
            steps += 1
        
        print(f"❌ Exceeded maximum steps ({max_steps}), navigation failed")
        return False

    async def solve_maze(self):
        """Main maze solving function using Qwen model"""
        print("\n🎮 Starting Qwen intelligent maze solving...")
        
        self.stats['attempts'] += 1
        
        try:
            await self.page.wait_for_selector("#mazeCanvas", timeout=10000)
            await self.page.focus("#mazeCanvas")
            await asyncio.sleep(2)
            
            game_state = await self.get_maze_state()
            if not game_state:
                print("❌ Unable to get maze state")
                self.stats['failures'] += 1
                return False
            
            print(f"📊 Maze state: {len(game_state['checkpoints'])} checkpoints")
            
            # Navigate to each checkpoint
            for i, checkpoint in enumerate(game_state['checkpoints']):
                if checkpoint['reached']:
                    print(f"   Checkpoint {i+1} already reached, skipping")
                    continue
                    
                print(f"\n🚩 Navigating to checkpoint {i+1}/{len(game_state['checkpoints'])}: ({checkpoint['x']:.0f}, {checkpoint['y']:.0f})")
                
                if not await self.navigate_to_target(checkpoint, max_steps=300):
                    print(f"❌ Unable to reach checkpoint {i+1}")
                    self.stats['failures'] += 1
                    return False
                
                await asyncio.sleep(0.5)
                game_state = await self.get_maze_state()
                if not game_state: 
                    return False
                print(f"🔄 Current inversion level: {game_state['inversionLevel']}")
            
            # Navigate to goal
            print(f"\n🏁 Navigating to final goal: ({game_state['goal']['x']:.0f}, {game_state['goal']['y']:.0f})")
            if not await self.navigate_to_target(game_state['goal'], max_steps=300):
                print("❌ Unable to reach final goal")
                self.stats['failures'] += 1
                return False
            
            await asyncio.sleep(1)
            
            # Check completion status
            status = await self.page.locator("#statusValue").inner_text(timeout=5000)
            if status == "Complete":
                print("✅ Maze solved successfully! Clicking submit...")
                submit_btn = self.page.locator("#mazeSubmitBtn")
                await submit_btn.click()
                self.stats['maze_solved'] += 1
                return True
            else:
                print("❌ Maze not marked as complete")
                self.stats['failures'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Maze solving error: {str(e)}")
            self.stats['failures'] += 1
            return False


    # ==================== SLIDER SOLVER ====================
    async def get_color_order_from_screenshot(self):
        """
        Capture a screenshot and use the model to detect only color_order
        """
        await asyncio.sleep(2)

        # Take a screenshot
        screenshot_bytes = await self.page.screenshot(type="png")
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
        image_uri = f"data:image/png;base64,{screenshot_base64}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"image": image_uri},
                    {"text":
                    "Please read the image and output both the slider_colors (the initial color order on screen) "
                    "and the color_order (the correct order after 'Drag sliders in order:'). "
                    "Output as a JSON object like this:\n"
                    "{\"slider_colors\": [\"yellow\",\"red\",\"purple\"], \"color_order\": [\"red\",\"yellow\",\"purple\"]}\n"
                    "Do not output anything else, just a valid JSON object."}
                ]
            }
        ]

        response = MultiModalConversation.call(
            model="qwen3-vl-plus",
            messages=messages
        )

        raw_text = response.output.choices[0].message.content[0]["text"].strip()
        print("Model raw output:", raw_text)

        try:
            result = json.loads(raw_text)
            slider_colors = result.get("slider_colors", [])
            color_order = result.get("color_order", [])
            print("Parsed slider_colors:", slider_colors)
            print("Parsed color_order:", color_order)
            return slider_colors, color_order
        except json.JSONDecodeError:
            print("⚠ JSON parsing failed, using fallback")
            # Fallback: extract colors with regex
            colors = re.findall(r"[A-Za-z]+", raw_text)
            print("Fallback colors:", colors)
            return colors, colors
    
    async def get_slider_data_js(self):
        """Extract slider state from JavaScript asynchronously"""
        await self.page.wait_for_function(
            "() => typeof sliderState !== 'undefined' && "
            "sliderState.targets && sliderState.targets.length === 3",
            timeout=10000
        )
        await asyncio.sleep(0.5)

        script = """
        () => {
            return {
                targets: sliderState.targets.map(t => ({x: t.x, y: t.y})),
            };
        }
        """

        return await self.page.evaluate(script)

    async def drag_slider_to_target(self, slider_id, target_x):
        """Drag slider to specific target X coordinate using mouse actions"""

        slider = self.page.locator(f"#{slider_id}")
        box = await slider.bounding_box()
        if not box:
            raise RuntimeError("Slider element not found or invisible.")

        start_x = box["x"] + box["width"] / 2
        start_y = box["y"] + box["height"] / 2

        container_id = slider_id.replace("slider", "sliderContainer")
        container = self.page.locator(f"#{container_id}")
        container_box = await container.bounding_box()

        if not container_box:
            raise RuntimeError("Slider container not found.")

        end_x = container_box["x"] + target_x + box["width"] / 2
        end_y = start_y

        print(f"      Start X: {start_x:.1f}, End X: {end_x:.1f}, Offset: {end_x - start_x:.1f}")

        await self.page.mouse.move(start_x, start_y)
        await self.page.mouse.down()
        await self.page.mouse.move(end_x, end_y, steps=30)
        await self.page.mouse.up()

        await asyncio.sleep(0.5)
        return True

    async def solve_slider(self):

        print("\nSolving Slider Puzzle CAPTCHA...")

        try:
            await asyncio.sleep(2)

            data = await self.get_slider_data_js()
            if not data:
                print("Could not access sliderState")
                return False

            targets = data["targets"]
            slider_colors,  correct_order = await self.get_color_order_from_screenshot()

            print(f"Slider initial colors: {slider_colors}")
            print(f"Target positions: {[t['x'] for t in targets]}")
            print(f"Expected order: {correct_order}")

            for target_index, required_color in enumerate(correct_order):

                try:
                    slider_index = slider_colors.index(required_color)
                except ValueError:
                    print(f"   ❌ Color '{required_color}' not found in sliders")
                    return False

                slider_id = f"slider{slider_index + 1}"
                target_x = targets[slider_index]["x"]

                print(f"Move {target_index+1}: '{required_color}' ({slider_id}) → {target_x:.1f}")

                if not await self.drag_slider_to_target(slider_id, target_x):
                    print(f"   ❌ Failed dragging {slider_id}")
                    return False

                await asyncio.sleep(0.5)


            try:
                final_success = self.page.locator("#finalSuccess")
                if "active" in await final_success.get_attribute("class"):
                    print("   ✅ Slider SOLVED!")
                    self.stats['slider_solved'] += 1
                    await asyncio.sleep(1)
                    return True
            except:
                pass

            print("   ❌ Slider solving failed (verification missing)")
            return False

        except Exception as e:
            print(f"   ❌ Slider error: {str(e)}")
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
        
        # Check for candy modal
        try:
            if await self.page.locator("#verificationModal").is_visible():
                return "candy"
        except:
            pass
        
        # Check for maze canvas
        try:
            if await self.page.locator("#mazeCanvas").is_visible():
                return "maze"
        except:
            pass
        
        # Check for slider elements
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
            # Click start button
            verify_btn = self.page.locator("#verifyBtn")
            await verify_btn.click()
            print("✅ Started verification process")
            await asyncio.sleep(2)
            
            # Check for progress indicator
            try:
                order_text = await self.page.locator("#progressSubtitle").inner_text()
                print(f"📋 System info: {order_text}")
            except:
                pass
            
            # Solve CAPTCHAs until all 3 are complete
            captchas_solved = 0
            max_captchas = 3
            
            while captchas_solved < max_captchas:
                captcha_num = captchas_solved + 1
                
                print(f"\n{'='*60}")
                print(f"CAPTCHA {captcha_num}/3 - Detecting type...")
                print('='*60)
                
                # Detect which CAPTCHA is active
                captcha_type = await self.detect_active_captcha()
                print(f"🔍 Detected: {captcha_type.upper()}")
                
                success = False
                
                # Solve based on type
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
                
                # Handle alerts
                try:
                    async with self.page.expect_event('dialog', timeout=2000) as dialog_info:
                        alert = await dialog_info.value
                        print(f"   📢 Alert: {alert.message[:80]}...")
                        await alert.accept()
                        await asyncio.sleep(1)
                except:
                    pass
                
                # Check if done
                if "verified=1" in self.page.url:
                    print(f"\n🎉 All CAPTCHAs completed! Returned to index page.")
                    break
                
                # Click continue button
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
            
            # Final verification check
            await asyncio.sleep(2)
            
            # Check if back on index with verified status
            if "verified=1" in self.page.url:
                print("\n" + "="*60)
                print("🎉 ALL 3 CAPTCHAS SOLVED SUCCESSFULLY!")
                print("="*60)
                self.stats['total_success'] += 1
                
                # Click next button to go to exam
                try:
                    next_btn = self.page.locator("#nextToExamBtn")
                    await next_btn.click()
                    print("✅ Proceeding to exam...")
                except:
                    pass
                return True
            else:
                # Final verification attempt
                return await self.check_and_submit_final_verification()
                
        except Exception as e:
            print(f"❌ Critical error in full challenge flow: {str(e)}")
            self.stats['failures'] += 1
            return False

    async def run(self, max_attempts=3):
        """Main runner with retry logic"""
        try:
            await self.init()
            
            for attempt in range(1, max_attempts + 1):
                print(f"\n{'='*60}")
                print(f"ATTEMPT {attempt}/{max_attempts}")
                print(f"{'='*60}")
                
                success = await self.solve_full_captcha_system()
                
                if success:
                    print("\n🏆 Challenge completed successfully!")
                    break
                
                if attempt < max_attempts:
                    print(f"\n🔄 Retrying ({attempt}/{max_attempts} failed)...")
                    await self.page.reload()
                    await asyncio.sleep(2)
            
            # Print final stats
            elapsed = time.time() - self.stats['start_time']
            print("\n" + "="*60)
            print("📊 FINAL STATISTICS")
            print("="*60)
            print(f"Total Attempts:       {self.stats['attempts']}")
            print(f"Full Success:         {self.stats['total_success']}")
            print(f"Candy Solved:         {self.stats['candy_solved']}")
            print(f"Maze Solved:          {self.stats['maze_solved']}")
            print(f"Slider Solved:        {self.stats['slider_solved']}")
            print(f"Failures:             {self.stats['failures']}")
            print(f"Time Elapsed:         {elapsed:.2f}s")
            print("="*60)
            
        finally:
            if self.browser:
                print("\n🔌 Closing browser...")
                await self.browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Advanced CAPTCHA Bot Attacker')
    parser.add_argument('--url', default='http://127.0.0.1:5500/index.html', 
                       help='Target URL') # Default changed to local dev URL for testing Playwright scripts
    parser.add_argument('--attempts', type=int, default=1, 
                       help='Number of full attempts')
    args = parser.parse_args()

    attacker = AdvancedCAPTCHAAttacker(args.url)
    asyncio.run(attacker.run(max_attempts=args.attempts))
