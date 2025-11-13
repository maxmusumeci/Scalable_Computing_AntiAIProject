# Scalable_Computing_AntiAIProject


CS7NS1 2025 Project 2


# CAPTCHA Bot - Simple Guide

## 📦 Installation

```bash
# Install Selenium
pip install selenium

# Install webdriver manager (auto-downloads ChromeDriver)
pip install webdriver-manager
```

## 🚀 How to Run

### Step 1: Start the CAPTCHA website
```bash
# Open captcha.html in browser OR
python3 -m http.server 8000

# Then visit: http://localhost:5501/captcha.html
```

### Step 2: Run the bot (in another terminal)
```bash
python3 bot.py
```

## 📝 Usage Examples

```bash
# Default - single attempt at http://localhost:8000/captcha.html
python3 bot.py

# 5 attempts
python3 bot.py --attempts 5

# Custom URL
python3 bot.py --url http://localhost:5500/captcha.html --attempts 3

# Help
python3 bot.py --help
```

## 📊 Expected Output

```
🤖 Initializing CAPTCHA Bot Attacker...
🌐 Navigating to: http://127.0.0.1:5501/captcha.html
✅ CAPTCHA loaded

🎮 Starting maze solving sequence...

🚩 Moving to checkpoint 1...
🚩 Moving to checkpoint 2...
🚩 Moving to checkpoint 3...
🏁 Moving to END point...
✅ MAZE SOLVED!
🔓 CAPTCHA bypassed - form submitted!

==================================================
📈 BOT STATISTICS
==================================================
Total Attempts: 1
Successful: 1
Failed: 0
Success Rate: 100.00%
Time Elapsed: 12.45s
==================================================
```

## ⚠️ Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'selenium'` | `pip install selenium` |
| `Connection refused` | Start website first: `python3 -m http.server 5501` |
| `element not found` | Make sure CAPTCHA is fully loaded in browser |
| `ChromeDriver version mismatch` | `pip install webdriver-manager` |

## 🎯 What the Bot Does

1. Opens your CAPTCHA website
2. Moves the player to checkpoint 1
3. Moves the player to checkpoint 2
4. Moves the player to checkpoint 3
5. Moves the player to END point
6. Clicks submit button
7. Shows success/failure statistics

## 🔧 Command Arguments

```
--url URL           Where your CAPTCHA is hosted (default: http://127.0.0.1:5501/captcha.html)
--attempts NUMBER   How many times to solve it (default: 1)
--help              Show all options
```

## 💡 Quick Setup

```bash
# 1. Install dependencies
pip install selenium webdriver-manager

# 2. Terminal 1: Run website
python3 -m http.server 5501

# 3. Terminal 2: Run bot
python3 bot.py --attempts 5
```

That's it! 🎉
