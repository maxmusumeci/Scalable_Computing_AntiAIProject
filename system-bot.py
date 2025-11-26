#!/usr/bin/env python3
"""
UNIFIED EXAM BOT - Complete Automation
Solves CAPTCHA challenges AND answers exam questions using local trained model
"""

import argparse
import time
import random
import asyncio
import sys
import json
import base64
from datetime import datetime
from collections import deque
from playwright.async_api import async_playwright

# Transformers for local LLM
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Qwen Vision API for CAPTCHA solving
from dashscope import MultiModalConversation
import dashscope
import regex as re

# ==================== CONFIGURATION ====================
GRID_DIM = 3  # 3x3 for Candy Crush
MAX_ATTEMPTS = 10
SUCCESS_CHECK_DELAY = 1.5
LOG_FILE = "unified_bot_log.txt"

# API Keys
dashscope.api_key = "sk-47699cd41a90450f9664a387d00b9883"  # Your Qwen API key

# Model paths
MODEL_PATH = "./exam_model_final"  # Your trained model path

# URLs
DEFAULT_URL = "http://127.0.0.1:5500/index.html"  # CAPTCHA page
EXAM_URL = "http://127.0.0.1:5500/exam.html"  # Exam page

# ==================== LOGGING ====================
def log_event(message):
    """Log events with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

# ==================== LLM SETUP ====================
print("\n🔧 Loading trained model for exam questions...")
print("="*60)

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float32,
    )
    model.eval()
    
    print(f"✅ Model loaded successfully from: {MODEL_PATH}")
    print(f"💾 Model size: ~82MB")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Failed to load model from {MODEL_PATH}")
    print(f"Error: {e}")
    print("\n💡 Train the model first: python train_model.py")
    sys.exit(1)

def get_ai_answer(question_text):
    """Generate answer using trained local model"""
    log_event(f"🧠 Generating answer for: {question_text[:50]}...")
    
    try:
        prompt = f"Question: {question_text}\nAnswer:"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=80,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.eos_token_id
            )
        
        full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "Answer:" in full_text:
            answer = full_text.split("Answer:")[-1].strip()
        else:
            answer = full_text.strip()
        
        answer = answer.split('\n')[0].strip()
        
        if len(answer) < 10:
            answer = "This requires careful analysis of the given context and its underlying principles."
        
        log_event(f"✅ Generated: {answer[:60]}...")
        return answer
        
    except Exception as e:
        log_event(f"❌ Generation Error: {e}")
        return "Error generating answer - requires further investigation."

# ==================== UNIFIED BOT CLASS ====================
class UnifiedExamBot:
    def __init__(self, url, headless=False):
        self.url = url
        self.headless = headless
        self.browser = None
        self.page = None
        self.context = None
        self.stats = {
            'attempts': 0,
            'candy_solved': 0,
            'maze_solved': 0,
            'slider_solved': 0,
            'total_captcha_success': 0,
            'exam_completed': False,
            'failures': 0,
            'start_time': time.time()
        }

    # ==================== BROWSER INITIALIZATION ====================
    async def init(self):
        """Initialize browser with stealth settings"""
        log_event("🤖 Initializing Unified Exam Bot...")
        
        p = await async_playwright().start()
        
        self.browser = await p.chromium.launch(
            headless=self.headless,
            slow_mo=50,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        
        self.page = await self.context.new_page()
        
        # Apply stealth
        await self.page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        log_event(f"🌐 Navigating to: {self.url}")
        await self.page.goto(self.url)
        await asyncio.sleep(2)

    # ==================== CAPTCHA SOLVING METHODS ====================
    
    async def get_candy_moves_from_screenshot(self, attempt):
        """Use Qwen Vision to analyze candy grid"""
        await self.page.wait_for_selector(".grid-cell")
        await asyncio.sleep(0.8)

        modal = await self.page.query_selector(".modal-container")
        if not modal:
            modal = await self.page.query_selector(".grid-container")
        if not modal:
            return [], [], []

        screenshot_bytes = await modal.screenshot(type="png")
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
        image_uri = f"data:image/png;base64,{screenshot_base64}"

        prompt = f"""
        This is a 3x3 candy CAPTCHA (Attempt {attempt}):
        Rules:
        1. Hidden cells show "?" and need clicking to reveal
        2. Goal: Swap adjacent cells to form 3 identical symbols in a row/column
        
        Output JSON format:
        {{
            "locked_cells": [[0,0]],
            "reveal_cells": [[0,1]],
            "swap_cells": [[0,1], [0,2]]
        }}
        """

        messages = [{"role": "user", "content": [{"image": image_uri}, {"text": prompt}]}]

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

            # Parse JSON from response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_text)
            if json_match:
                data = json.loads(json_match.group())
                locked = data.get("locked_cells", [])
                reveal = data.get("reveal_cells", [])
                swaps = data.get("swap_cells", [])
                return locked, reveal, swaps
                
        except Exception as e:
            log_event(f"Vision API error: {e}")
        
        return [], [], []

    async def solve_candy_crush(self):
        """Solve candy crush CAPTCHA"""
        log_event("🍬 Solving Candy Match CAPTCHA...")
        
        for attempt in range(1, MAX_ATTEMPTS + 1):
            log_event(f"   Attempt {attempt}/{MAX_ATTEMPTS}")
            
            locked, reveal, swaps = await self.get_candy_moves_from_screenshot(attempt)
            
            # Reveal hidden cells
            for pos in reveal:
                try:
                    cell = self.page.locator(f".grid-row:nth-child({pos[0]+1}) > .grid-cell:nth-child({pos[1]+1})")
                    await cell.click()
                    await asyncio.sleep(0.3)
                except:
                    pass
            
            await asyncio.sleep(1)
            
            # Perform swaps
            for swap_pair in swaps:
                if len(swap_pair) != 2:
                    continue
                
                r1, c1 = swap_pair[0]
                r2, c2 = swap_pair[1]
                
                try:
                    cell1 = self.page.locator(f".grid-row:nth-child({r1+1}) > .grid-cell:nth-child({c1+1})")
                    await cell1.click()
                    await asyncio.sleep(0.3)
                    
                    cell2 = self.page.locator(f".grid-row:nth-child({r2+1}) > .grid-cell:nth-child({c2+1})")
                    await cell2.click()
                    await asyncio.sleep(0.5)
                    
                    # Check for success
                    try:
                        await self.page.wait_for_selector("#successMessage", timeout=2000)
                        log_event("✅ Candy Match SOLVED!")
                        self.stats['candy_solved'] += 1
                        return True
                    except:
                        pass
                        
                except Exception as e:
                    log_event(f"Swap error: {e}")
            
            await asyncio.sleep(1)
        
        log_event("❌ Candy Match failed")
        return False

    async def solve_maze(self):
        """Solve maze CAPTCHA (simplified version)"""
        log_event("🎮 Solving Maze CAPTCHA...")
        
        try:
            await self.page.wait_for_selector("#mazeCanvas", timeout=10000)
            await self.page.focus("#mazeCanvas")
            await asyncio.sleep(2)
            
            # Simplified maze solving - just press arrow keys randomly
            # (You can implement proper pathfinding if needed)
            for _ in range(100):
                keys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']
                key = random.choice(keys)
                await self.page.keyboard.press(key)
                await asyncio.sleep(0.1)
            
            # Check for completion
            try:
                status = await self.page.locator("#statusValue").inner_text(timeout=2000)
                if status == "Complete":
                    submit_btn = self.page.locator("#mazeSubmitBtn")
                    await submit_btn.click()
                    log_event("✅ Maze SOLVED!")
                    self.stats['maze_solved'] += 1
                    return True
            except:
                pass
            
            log_event("❌ Maze failed")
            return False
            
        except Exception as e:
            log_event(f"❌ Maze error: {e}")
            return False

    async def solve_slider(self):
        """Solve slider CAPTCHA"""
        log_event("🧩 Solving Slider Puzzle...")
        
        try:
            await asyncio.sleep(2)
            
            # Get slider data
            data = await self.page.evaluate("""
                () => {
                    return {
                        targets: sliderState.targets.map(t => ({x: t.x, y: t.y})),
                        order: sliderState.sliderOrder.map(c => c.name.toLowerCase()),
                        sliders: sliderState.sliders.map(s => s.dataset.colorName)
                    };
                }
            """)
            
            targets = data["targets"]
            correct_order = data["order"]
            slider_colors = data["sliders"]
            
            log_event(f"   Order required: {correct_order}")
            
            # Move sliders in correct order
            for move_num, required_color in enumerate(correct_order, 1):
                slider_index = slider_colors.index(required_color)
                slider_id = f"slider{slider_index + 1}"
                target_x = targets[slider_index]["x"]
                
                log_event(f"   Move {move_num}/3: {required_color.upper()} to X={target_x}")
                
                # Drag slider
                container_id = f"sliderContainer{slider_index + 1}"
                slider = self.page.locator(f"#{slider_id}")
                container = self.page.locator(f"#{container_id}")
                
                slider_box = await slider.bounding_box()
                container_box = await container.bounding_box()
                
                if slider_box and container_box:
                    start_x = slider_box['x'] + slider_box['width'] / 2
                    start_y = slider_box['y'] + slider_box['height'] / 2
                    end_x = container_box['x'] + target_x + slider_box['width'] / 2
                    
                    await self.page.mouse.move(start_x, start_y)
                    await self.page.mouse.down()
                    await asyncio.sleep(0.1)
                    
                    # Smooth movement
                    steps = 15
                    for i in range(1, steps + 1):
                        x = start_x + (end_x - start_x) * (i / steps)
                        await self.page.mouse.move(x, start_y)
                        await asyncio.sleep(0.03)
                    
                    await self.page.mouse.up()
                    await asyncio.sleep(0.5)
            
            # Verify completion
            await asyncio.sleep(1)
            
            final_status = await self.page.evaluate("() => sliderState.completed")
            
            if final_status:
                log_event("✅ Slider SOLVED!")
                self.stats['slider_solved'] += 1
                return True
            
            log_event("❌ Slider failed")
            return False
            
        except Exception as e:
            log_event(f"❌ Slider error: {e}")
            return False

    async def detect_active_captcha(self):
        """Detect which CAPTCHA is currently active"""
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

    async def solve_all_captchas(self):
        """Solve all 3 CAPTCHAs in sequence"""
        log_event("="*60)
        log_event("🎯 STARTING CAPTCHA CHALLENGE")
        log_event("="*60)
        
        self.stats['attempts'] += 1
        
        try:
            # Click verify button
            verify_btn = self.page.locator("#verifyBtn")
            await verify_btn.click()
            log_event("✅ Started verification")
            await asyncio.sleep(2)
            
            captchas_solved = 0
            max_captchas = 3
            
            while captchas_solved < max_captchas:
                captcha_num = captchas_solved + 1
                
                log_event(f"\nCAPTCHA {captcha_num}/3 - Detecting type...")
                
                captcha_type = await self.detect_active_captcha()
                log_event(f"🔍 Detected: {captcha_type.upper()}")
                
                success = False
                
                if captcha_type == "maze":
                    success = await self.solve_maze()
                elif captcha_type == "slider":
                    success = await self.solve_slider()
                elif captcha_type == "candy":
                    success = await self.solve_candy_crush()
                else:
                    log_event(f"❌ Unknown CAPTCHA type")
                    success = False

                if not success:
                    log_event(f"❌ Failed at CAPTCHA {captcha_num}/3")
                    self.stats['failures'] += 1
                    return False
                
                captchas_solved += 1
                
                # Handle alerts
                try:
                    async with self.page.expect_event('dialog', timeout=2000) as dialog_info:
                        alert = await dialog_info.value
                        log_event(f"📢 Alert: {alert.message[:50]}...")
                        await alert.accept()
                        await asyncio.sleep(1)
                except:
                    pass
                
                # Check if done
                if "verified=1" in self.page.url:
                    log_event("🎉 All CAPTCHAs completed!")
                    break
                
                # Continue to next CAPTCHA
                if captchas_solved < max_captchas:
                    await asyncio.sleep(1.5)
                    try:
                        continue_btn = self.page.locator("#continueBtn")
                        await continue_btn.click(timeout=8000)
                        log_event(f"✅ CAPTCHA {captcha_num}/3 complete")
                        await asyncio.sleep(2)
                    except Exception as e:
                        log_event(f"⚠️ Continue button not found")
                        await asyncio.sleep(1)
            
            await asyncio.sleep(2)
            
            if "verified=1" in self.page.url:
                log_event("="*60)
                log_event("🎉 ALL CAPTCHAS SOLVED!")
                log_event("="*60)
                self.stats['total_captcha_success'] += 1
                return True
            else:
                log_event("❌ CAPTCHA verification incomplete")
                return False
                
        except Exception as e:
            log_event(f"❌ Critical CAPTCHA error: {e}")
            self.stats['failures'] += 1
            return False

    # ==================== EXAM SOLVING METHODS ====================
    
    async def human_type(self, element, text):
        """Simulate human typing"""
        await element.fill("")  # Clear first
        for char in text:
            await element.type(char)
            await asyncio.sleep(random.uniform(0.01, 0.05))

    async def handle_permissions(self):
        """Handle exam permission requests"""
        try:
            log_event("🔐 Handling permissions...")
            
            # Click grant permissions
            grant_btn = await self.page.wait_for_selector(
                "button:has-text('Grant Permissions')",
                timeout=10000
            )
            await grant_btn.click()
            await asyncio.sleep(1)
            
            # Wait for start button
            start_btn = await self.page.wait_for_selector("#startExamBtn", timeout=10000)
            await asyncio.sleep(2)
            await start_btn.click()
            log_event("✅ Exam started")
            
        except Exception as e:
            log_event(f"⚠️ Permission handling error: {e}")

    async def solve_exam(self):
        """Solve all exam questions using LLM"""
        log_event("="*60)
        log_event("📝 STARTING EXAM")
        log_event("="*60)
        
        try:
            await self.handle_permissions()
            await asyncio.sleep(3)
            
            # Answer each question
            for i in range(1, 4):
                log_event(f"\n📖 Question {i}/3")
                
                # Get question text
                q_selector = f"#question{i}"
                await self.page.wait_for_selector(q_selector, timeout=10000)
                
                q_element = await self.page.query_selector(f"{q_selector} h3")
                q_text = await q_element.inner_text()
                log_event(f"   Q: {q_text[:60]}...")
                
                # Generate answer using LLM
                answer = get_ai_answer(q_text)
                
                # Type answer
                text_area = await self.page.wait_for_selector(f"#answer{i}")
                await self.human_type(text_area, answer)
                
                await asyncio.sleep(random.uniform(1, 3))
                
                # Navigate
                if i < 3:
                    next_btn = await self.page.query_selector("#nextBtn")
                    await next_btn.click()
                    await asyncio.sleep(1)
                else:
                    submit_btn = await self.page.query_selector("#submitBtn")
                    await submit_btn.click()
                    log_event("✅ Exam submitted")
            
            # Check result
            await asyncio.sleep(3)
            
            try:
                status = await self.page.locator("#submissionStatus").inner_text()
                log_event(f"📊 EXAM RESULT: {status}")
                self.stats['exam_completed'] = True
                return True
            except:
                log_event("⚠️ Could not read exam result")
                return True
            
        except Exception as e:
            log_event(f"❌ Exam error: {e}")
            return False

    # ==================== MAIN EXECUTION ====================
    
    async def run(self):
        """Main execution flow"""
        try:
            await self.init()
            
            # Step 1: Solve CAPTCHAs
            captcha_success = await self.solve_all_captchas()
            
            if not captcha_success:
                log_event("❌ CAPTCHA solving failed - cannot proceed to exam")
                return False
            
            # Step 2: Navigate to exam
            log_event("\n🔄 Navigating to exam page...")
            
            try:
                # Click button to go to exam
                next_btn = await self.page.wait_for_selector(
                    "button:has-text('Next')",
                    timeout=5000
                )
                await next_btn.click()
                await asyncio.sleep(2)
            except:
                # Or navigate directly
                await self.page.goto(EXAM_URL)
                await asyncio.sleep(2)
            
            # Step 3: Solve exam
            exam_success = await self.solve_exam()
            
            # Print final stats
            elapsed = time.time() - self.stats['start_time']
            log_event("\n" + "="*60)
            log_event("📊 FINAL STATISTICS")
            log_event("="*60)
            log_event(f"CAPTCHA Attempts:     {self.stats['attempts']}")
            log_event(f"CAPTCHA Success:      {self.stats['total_captcha_success']}")
            log_event(f"  - Candy Solved:     {self.stats['candy_solved']}")
            log_event(f"  - Maze Solved:      {self.stats['maze_solved']}")
            log_event(f"  - Slider Solved:    {self.stats['slider_solved']}")
            log_event(f"Exam Completed:       {self.stats['exam_completed']}")
            log_event(f"Total Failures:       {self.stats['failures']}")
            log_event(f"Total Time:           {elapsed:.2f}s")
            log_event("="*60)
            
            # Keep browser open briefly if not headless
            if not self.headless:
                await asyncio.sleep(5)
            
            return captcha_success and exam_success
            
        finally:
            if self.browser:
                log_event("🔌 Closing browser...")
                await self.browser.close()

# ==================== MAIN ====================
async def main():
    parser = argparse.ArgumentParser(description='Unified Exam Bot - CAPTCHA + Exam Solver')
    parser.add_argument('--url', default=DEFAULT_URL, help='CAPTCHA page URL')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    args = parser.parse_args()

    print("\n" + "="*60)
    print("🤖 UNIFIED EXAM BOT v1.0")
    print("="*60)
    print("✅ CAPTCHA Solver: Qwen Vision API")
    print("✅ Exam Solver: Local Trained Model")
    print("="*60 + "\n")
    
    bot = UnifiedExamBot(args.url, headless=args.headless)
    success = await bot.run()
    
    if success:
        print("\n🏆 COMPLETE SUCCESS - All challenges solved!")
    else:
        print("\n❌ Some challenges failed - check logs")

if __name__ == "__main__":
    asyncio.run(main())