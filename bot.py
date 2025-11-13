#!/usr/bin/env python3
"""
CAPTCHA Bot Attacker - Python Version
Solves the maze CAPTCHA automatically
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

class CAPTCHABotAttacker:
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
        print("🤖 Initializing CAPTCHA Bot Attacker...")
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1280, 720)
        
        print(f"🌐 Navigating to: {self.url}")
        self.driver.get(self.url)
        
        # Wait for canvas
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "mazeCanvas"))
        )
        print("✅ CAPTCHA loaded")

    def get_maze_data(self):
        """Extract maze information"""
        canvas = self.driver.find_element(By.ID, "mazeCanvas")
        return {
            'width': canvas.get_attribute('width'),
            'height': canvas.get_attribute('height')
        }

    def simulate_key_press(self, key, duration=0.1):
        """Simulate keyboard input"""
        actions = ActionChains(self.driver)
        actions.send_keys(key).perform()
        time.sleep(duration)

    def move_to_checkpoint(self, checkpoint_num):
        """Move player to checkpoint"""
        print(f"🚩 Moving to checkpoint {checkpoint_num}...")
        
        # Simulate arrow key presses in sequence
        for _ in range(50):
            self.simulate_key_press(Keys.RIGHT, 0.05)
            time.sleep(0.02)
        
        time.sleep(0.5)

    def solve_maze(self):
        """Solve the entire maze"""
        print("\n🎮 Starting maze solving sequence...")
        
        self.stats['attempts'] += 1
        
        try:
            # Move to checkpoint 1
            self.move_to_checkpoint(1)
            
            # Move to checkpoint 2
            self.move_to_checkpoint(2)
            
            # Move to checkpoint 3
            self.move_to_checkpoint(3)
            
            # Move to end
            print("🏁 Moving to END point...")
            for _ in range(50):
                self.simulate_key_press(Keys.RIGHT, 0.05)
                time.sleep(0.02)
            
            time.sleep(1)
            
            # Check if completed
            status = self.driver.find_element(By.ID, "statusValue").text
            
            if status == "Complete":
                print("✅ MAZE SOLVED!")
                self.stats['successes'] += 1
                
                # Submit
                submit_btn = self.driver.find_element(By.ID, "submitBtn")
                submit_btn.click()
                print("🔓 CAPTCHA bypassed - form submitted!")
                
                time.sleep(2)
                return True
            else:
                print("❌ Failed to complete maze")
                self.stats['failures'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.stats['failures'] += 1
            return False

    def multiple_attempts(self, count=5):
        """Run multiple solving attempts"""
        print(f"\n🔄 Starting {count} solving attempts...\n")
        
        for i in range(count):
            print(f"\n[Attempt {i+1}/{count}]")
            
            # Refresh page
            self.driver.refresh()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "mazeCanvas"))
            )
            
            self.solve_maze()
            
            if i < count - 1:
                time.sleep(2)
        
        self.print_stats()

    def print_stats(self):
        """Print attack statistics"""
        elapsed = time.time() - self.stats['start_time']
        success_rate = (self.stats['successes'] / self.stats['attempts'] * 100) if self.stats['attempts'] > 0 else 0
        
        print("\n" + "="*50)
        print("📈 BOT STATISTICS")
        print("="*50)
        print(f"Total Attempts: {self.stats['attempts']}")
        print(f"Successful: {self.stats['successes']}")
        print(f"Failed: {self.stats['failures']}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Time Elapsed: {elapsed:.2f}s")
        print("="*50 + "\n")

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("🛑 Browser closed")

def main():
    parser = argparse.ArgumentParser(description='CAPTCHA Bot Attacker')
    parser.add_argument('--url', default='http://localhost:8000/captcha.html', help='Target URL')
    parser.add_argument('--attempts', type=int, default=1, help='Number of attempts')
    
    args = parser.parse_args()
    
    bot = CAPTCHABotAttacker(args.url)
    
    try:
        bot.init()
        bot.multiple_attempts(args.attempts)
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        bot.close()

if __name__ == '__main__':
    main()