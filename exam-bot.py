# Authors - Sriram and Max
import time
import random
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Transformers imports
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# --- 1. CONFIGURATION & INPUT ---
def ask_headless_mode():
    """Asks the user via terminal if they want Headless mode"""
    print("\n" + "="*40)
    print("🤖 BOT CONFIGURATION")
    print("="*40)
    while True:
        response = input("Run in HEADLESS mode (No GUI)? [y/n]: ").lower().strip()
        if response in ['y', 'yes']:
            print("✅ Selected: HEADLESS Mode (Silent)")
            return True
        elif response in ['n', 'no']:
            print("✅ Selected: GUI Mode (Visible Browser)")
            return False
        print("❌ Invalid input. Please type 'y' or 'n'.")

# Target Config
# TARGET_URL = "https://exam-portal-captcha-test.web.app/exam.html" 
TARGET_URL = "http://127.0.0.1:5500/exam.html" 
LOG_FILE = "simulation_log.txt"
HUMAN_TYPING = True

# --- 2. LOAD YOUR TRAINED MODEL ---
print("\n🔧 Loading your trained model...")
print("="*60)

MODEL_PATH = "./exam_model_final"  # Path to your trained model

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float32,  # Use float32 for CPU
    )
    model.eval()  # Set to evaluation mode
    
    print(f"✅ Model loaded successfully from: {MODEL_PATH}")
    print(f"💾 Model size: ~82MB (lightweight for Pi)")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Failed to load model from {MODEL_PATH}")
    print(f"Error: {e}")
    print("\n💡 Make sure you've trained the model first:")
    print("   python train_model.py")
    sys.exit(1)

# NOW ask for headless mode after model loads
HEADLESS_MODE = ask_headless_mode()

# --- 3. THE AI BRAIN (Your Trained Model) ---
def get_ai_answer(question_text):
    """Generate answer using YOUR trained local model"""
    print(f"🧠 Thinking about: {question_text[:50]}...")
    
    try:
        # Format as the model was trained
        prompt = f"Question: {question_text}\nAnswer:"
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
        
        # Generate answer
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=80,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.2,  # Avoid repetition
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode the full text
        full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the answer part (after "Answer:")
        if "Answer:" in full_text:
            answer = full_text.split("Answer:")[-1].strip()
        else:
            answer = full_text.strip()
        
        # Clean up
        answer = answer.split('\n')[0]  # Take first line only
        answer = answer.strip()
        
        if len(answer) < 10:  # Too short, probably failed
            answer = "This requires careful analysis of the given context and its underlying principles."
        
        print(f"✅ Answer: {answer[:60]}...")
        return answer
        
    except Exception as e:
        print(f"❌ Generation Error: {e}")
        return "Error generating answer - requires further investigation of the topic."

# --- 4. UTILITIES ---
def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def human_type(element, text):
    """Simulate human typing with random delays"""
    element.clear()
    for char in text:
        element.send_keys(char)
        if HUMAN_TYPING:
            time.sleep(random.uniform(0.01, 0.05))

# --- 5. BROWSER SETUP (Optimized for Raspberry Pi) ---
def setup_driver():
    options = Options()

    if HEADLESS_MODE:
        options.add_argument("--headless=new") 
    else:
        options.add_argument("--start-maximized")

    # Raspberry Pi optimizations
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--use-fake-device-for-media-stream")
    options.add_argument("--window-size=1280,720")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# --- 6. MAIN SIMULATION LOOP ---
def run_simulation():
    log_event("--- STARTING NEW SIMULATION ---")
    log_event("Mode: Using locally trained model (exam_model_final)")
    
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(TARGET_URL)
        log_event("Portal Loaded")

        # Handle Permissions
        grant_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Grant Permissions')]")
        ))
        grant_btn.click()
        time.sleep(1)
        
        start_btn = wait.until(EC.element_to_be_clickable((By.ID, "startExamBtn")))
        time.sleep(2) 
        start_btn.click()
        log_event("Exam Started")

        # Question Loop
        for i in range(1, 4):
            q_container = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, f"#question{i}")
            ))
            q_text = q_container.find_element(By.TAG_NAME, "h3").text
            log_event(f"Read Q{i}: {q_text[:40]}...")

            # Generate AI answer using YOUR model
            answer = get_ai_answer(q_text)
            log_event(f"Answered Q{i}: {answer[:50]}...")

            # Type answer
            text_area = driver.find_element(By.ID, f"answer{i}")
            human_type(text_area, answer)
            
            time.sleep(random.uniform(1, 3)) 
            
            # Navigate
            if i < 3:
                driver.find_element(By.ID, "nextBtn").click()
            else:
                driver.find_element(By.ID, "submitBtn").click()
                log_event("Submit Button Clicked")

        time.sleep(2)
        status = driver.find_element(By.ID, "submissionStatus").text
        log_event(f"SIMULATION ENDED. Result: {status}")

        # Keep browser open briefly if GUI mode
        if not HEADLESS_MODE:
            time.sleep(5)

    except Exception as e:
        log_event(f"CRITICAL FAIL: {e}")
        driver.save_screenshot("error_snapshot.png") 
    finally:
        driver.quit()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎓 EXAM PORTAL BOT - LOCAL MODEL VERSION")
    print("="*60)
    print("Using your custom-trained model")
    print("No APIs, tokens, or internet required!")
    print("="*60 + "\n")
    
    run_simulation()