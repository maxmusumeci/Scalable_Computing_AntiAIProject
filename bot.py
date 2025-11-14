#!/usr/bin/env python3
"""
Smart CAPTCHA Bot Attacker - Python Version
Solves the maze CAPTCHA automatically using game state injection
Usage: python3 bot-attacker.py --url http://localhost:3000
"""

import argparse
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SmartCAPTCHABotAttacker:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.stats = {
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'start_time': time.time()
        }

    def init(self):
        print("🤖 Initializing Smart CAPTCHA Bot Attacker...")
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1280, 720)
        
        print(f"🌐 Navigating to: {self.url}")
        self.driver.get(self.url)
        
        # Wait for canvas
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "mazeCanvas"))
        )
        time.sleep(3)  # Increased wait time for initialization
        print("✅ CAPTCHA loaded")

    def get_game_state(self):
        """Extract complete game state from JavaScript"""
        script = """
        const captcha = window.captchaInstance || document.captchaInstance;
        if (!captcha) return null;
        
        return {
            player: {
                x: captcha.player.x,
                y: captcha.player.y
            },
            checkpoints: captcha.checkpoints.map(cp => ({
                x: cp.x,
                y: cp.y,
                reached: cp.reached
            })),
            goal: {
                x: captcha.goal.x,
                y: captcha.goal.y
            },
            obstacles: captcha.obstacles.map(obs => ({
                x: obs.x,
                y: obs.y,
                width: obs.width,
                height: obs.height
            })),
            dangerZones: captcha.dangerZones.map(dz => ({
                x: dz.x,
                y: dz.y,
                radius: dz.radius
            })),
            currentCheckpoint: captcha.gameState.currentCheckpoint,
            inversionLevel: captcha.gameState.invertionLevel,
            canvasWidth: captcha.canvas.width,
            canvasHeight: captcha.canvas.height
        };
        """
        return self.driver.execute_script(script)

    def expose_captcha_instance(self):
        """Make captcha instance globally accessible"""
        script = """
        // Find and expose the captcha instance
        const captchaContainer = document.querySelector('.captcha-container');
        if (captchaContainer && !window.captchaInstance) {
            // Wait a bit for initialization
            setTimeout(() => {
                console.log('Attempting to expose captcha instance...');
            }, 500);
        }
        """
        self.driver.execute_script(script)

    def calculate_path(self, current, target, obstacles, danger_zones):
        """Better pathfinding with obstacle avoidance"""
        dx = target['x'] - current['x']
        dy = target['y'] - current['y']
        
        # Normalize direction
        distance = (dx**2 + dy**2)**0.5
        if distance < 15:
            return None, None
        
        # Calculate desired direction
        move_x = 1 if dx > 5 else (-1 if dx < -5 else 0)
        move_y = 1 if dy > 5 else (-1 if dy < -5 else 0)
        
        # Check if direct path is blocked
        next_x = current['x'] + move_x * 20
        next_y = current['y'] + move_y * 20
        
        blocked = False
        
        # Check obstacles
        for obs in obstacles:
            if (next_x >= obs['x'] - 10 and next_x <= obs['x'] + obs['width'] + 10 and
                next_y >= obs['y'] - 10 and next_y <= obs['y'] + obs['height'] + 10):
                blocked = True
                break
        
        # Check danger zones
        for dz in danger_zones:
            dist = ((next_x - dz['x'])**2 + (next_y - dz['y'])**2)**0.5
            if dist < dz['radius'] + 20:
                blocked = True
                break
        
        # If blocked, try alternative route
        if blocked:
            # Try moving perpendicular to main direction
            if abs(dx) > abs(dy):
                # Moving more horizontally, try vertical detour
                move_y = 1 if current['y'] < target['y'] else -1
            else:
                # Moving more vertically, try horizontal detour  
                move_x = 1 if current['x'] < target['x'] else -1
        
        return move_x, move_y

    def apply_inversion(self, move_x, move_y, inversion_level):
        """Apply control inversion based on checkpoint progress"""
        if inversion_level == 1:  # Left/Right inverted
            move_x *= -1
        elif inversion_level == 2:  # Up/Down inverted
            move_y *= -1
        elif inversion_level == 3:  # All inverted
            move_x *= -1
            move_y *= -1
        
        return move_x, move_y

    def press_key(self, move_x, move_y):
        """Press appropriate arrow keys"""
        actions = ActionChains(self.driver)
        
        if move_x > 0:
            actions.send_keys(Keys.RIGHT)
        elif move_x < 0:
            actions.send_keys(Keys.LEFT)
        
        if move_y > 0:
            actions.send_keys(Keys.DOWN)
        elif move_y < 0:
            actions.send_keys(Keys.UP)
        
        actions.perform()

    def navigate_to_target(self, target, game_state, max_steps=500):
        """Navigate player to target position using direct game control"""
        steps = 0
        last_distance = float('inf')
        stuck_count = 0
        
        print(f"   Starting navigation to ({target['x']:.0f}, {target['y']:.0f})")
        
        while steps < max_steps:
            # Get current state
            current_state = self.get_game_state()
            if not current_state:
                print("⚠️ Could not read game state")
                return False
            
            player = current_state['player']
            
            # Check if reached target
            dx = target['x'] - player['x']
            dy = target['y'] - player['y']
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 25:
                print(f"✅ Reached target at ({target['x']:.0f}, {target['y']:.0f})")
                return True
            
            # Progress update
            if steps % 30 == 0 and steps > 0:
                print(f"   Step {steps}: Player at ({player['x']:.0f}, {player['y']:.0f}), distance = {distance:.1f}px")
            
            # Detect if stuck
            if abs(distance - last_distance) < 1:
                stuck_count += 1
                if stuck_count > 20:
                    print(f"⚠️ Stuck! Trying different angle...")
                    # Try moving perpendicular
                    for _ in range(15):
                        move_script = """
                        const captcha = window.captchaInstance;
                        captcha.keys.add('arrowup');
                        captcha.keys.add('arrowright');
                        setTimeout(() => {
                            captcha.keys.clear();
                        }, 100);
                        """
                        self.driver.execute_script(move_script)
                        time.sleep(0.1)
                    stuck_count = 0
                    continue
            else:
                stuck_count = 0
            
            last_distance = distance
            
            # Calculate movement direction
            move_x = 1 if dx > 10 else (-1 if dx < -10 else 0)
            move_y = 1 if dy > 10 else (-1 if dy < -10 else 0)
            
            # Apply inversion
            move_x, move_y = self.apply_inversion(
                move_x, 
                move_y, 
                current_state['inversionLevel']
            )
            
            # Direct control via JavaScript - holds keys for continuous movement
            self.move_player_js(move_x, move_y, duration=100)
            
            time.sleep(0.05)
            steps += 1
        
        print(f"❌ Navigation timeout after {max_steps} steps")
        print(f"   Final position: ({player['x']:.0f}, {player['y']:.0f}), distance to target: {distance:.1f}px")
        return False

    def move_player_js(self, move_x, move_y, duration=100):
        """Move player using direct JavaScript key control"""
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
        
        # Build JavaScript to hold keys
        keys_str = "', '".join(keys_to_press)
        
        script = f"""
        const captcha = window.captchaInstance;
        const keys = ['{keys_str}'];
        
        // Add all keys
        keys.forEach(key => captcha.keys.add(key));
        
        // Hold for duration then release
        setTimeout(() => {{
            keys.forEach(key => captcha.keys.delete(key));
        }}, {duration});
        """
        
        self.driver.execute_script(script)
    
    def press_key_hold(self, move_x, move_y, hold_duration=0.05):
        """Press and hold keys for better movement"""
        actions = ActionChains(self.driver)
        
        # Press multiple times for momentum
        presses = 3
        
        for _ in range(presses):
            if move_x > 0:
                actions.send_keys(Keys.RIGHT)
            elif move_x < 0:
                actions.send_keys(Keys.LEFT)
            
            if move_y > 0:
                actions.send_keys(Keys.DOWN)
            elif move_y < 0:
                actions.send_keys(Keys.UP)
        
        actions.perform()

    def solve_maze(self):
        """Solve the entire maze intelligently"""
        print("\n🎮 Starting intelligent maze solving...")
        
        self.stats['attempts'] += 1
        
        try:
            # Get initial game state
            game_state = self.get_game_state()
            
            if not game_state:
                print("❌ Could not access game state")
                self.stats['failures'] += 1
                return False
            
            print(f"📊 Game State: {len(game_state['checkpoints'])} checkpoints, {len(game_state['obstacles'])} obstacles")
            
            # Navigate to each checkpoint
            for i, checkpoint in enumerate(game_state['checkpoints']):
                print(f"\n🚩 Checkpoint {i+1}/{len(game_state['checkpoints'])}: ({checkpoint['x']:.0f}, {checkpoint['y']:.0f})")
                
                if not self.navigate_to_target(checkpoint, game_state, max_steps=400):  # Increased from 200
                    print(f"❌ Failed to reach checkpoint {i+1}")
                    self.stats['failures'] += 1
                    return False
                
                time.sleep(0.5)  # Increased wait after checkpoint
                
                # Update game state after each checkpoint
                game_state = self.get_game_state()
                print(f"🔄 Inversion level now: {game_state['inversionLevel']}")
            
            # Navigate to goal
            print(f"\n🏁 Final Goal: ({game_state['goal']['x']:.0f}, {game_state['goal']['y']:.0f})")
            
            if not self.navigate_to_target(game_state['goal'], game_state, max_steps=400):
                print("❌ Failed to reach goal")
                self.stats['failures'] += 1
                return False
            
            time.sleep(1)
            
            # Check completion
            status = self.driver.find_element(By.ID, "statusValue").text
            
            if status == "Complete":
                print("✅ MAZE SOLVED!")
                self.stats['successes'] += 1
                
                # Submit
                submit_btn = self.driver.find_element(By.ID, "submitBtn")
                submit_btn.click()
                print("🔓 CAPTCHA BYPASSED - form submitted!")
                
                time.sleep(2)
                return True
            else:
                print("❌ Maze not marked as complete")
                self.stats['failures'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.stats['failures'] += 1
            return False

    def multiple_attempts(self, count=5):
        """Run multiple solving attempts"""
        print(f"\n🔄 Starting {count} solving attempts...\n")
        
        for i in range(count):
            print(f"\n{'='*60}")
            print(f"[Attempt {i+1}/{count}]")
            print('='*60)
            
            if i > 0:
                # Refresh page
                self.driver.refresh()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "mazeCanvas"))
                )
                time.sleep(1)
            
            success = self.solve_maze()
            
            if success:
                print(f"✅ Attempt {i+1} SUCCESSFUL!")
            else:
                print(f"❌ Attempt {i+1} FAILED")
            
            if i < count - 1:
                time.sleep(3)
        
        self.print_stats()

    def print_stats(self):
        """Print attack statistics"""
        elapsed = time.time() - self.stats['start_time']
        success_rate = (self.stats['successes'] / self.stats['attempts'] * 100) if self.stats['attempts'] > 0 else 0
        
        print("\n" + "="*60)
        print("📈 BOT ATTACK STATISTICS")
        print("="*60)
        print(f"Total Attempts:  {self.stats['attempts']}")
        print(f"Successful:      {self.stats['successes']} ({success_rate:.1f}%)")
        print(f"Failed:          {self.stats['failures']}")
        print(f"Time Elapsed:    {elapsed:.2f}s")
        print(f"Avg Time/Solve:  {elapsed/max(self.stats['successes'], 1):.2f}s")
        print("="*60 + "\n")

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("🛑 Browser closed")

def main():
    parser = argparse.ArgumentParser(description='Smart CAPTCHA Bot Attacker')
    parser.add_argument('--url', default='http://127.0.0.1:5501/captcha.html', help='Target URL')
    parser.add_argument('--attempts', type=int, default=1, help='Number of attempts')
    
    args = parser.parse_args()
    
    bot = SmartCAPTCHABotAttacker(args.url)
    
    try:
        bot.init()
        bot.multiple_attempts(args.attempts)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bot.close()

if __name__ == '__main__':
    main()