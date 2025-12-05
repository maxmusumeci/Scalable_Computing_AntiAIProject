# Scalable_Computing_AntiAIProject


CS7NS1 2025 Project 2

Code Contributions:

Candycrush captcha, playwright and llm attacker (candycrush.css, candycrush.js,llm-bot.py,playwright-bot.py): Yuxin Wan

Maze captcha, playwright and exam portal attacker , exam frontend (app.js, bot-detection-integration.js, app.css, exam.html, index.html, captcha-updated.html, server.py, playwright-bot.py, exam-bot.py): Sriram Kirthivas

Puzzlepiece captcha, Playwright and LLM bot attacker, .bat script (playwright-bot.py, app.js,llm-bot.py, runme.bat, captcha-updated.html): Liwei Huang

Detection systems, exam backend and exam attacker (app.py, server.py, bot-detection.js, exam-bot.py): Max Musumeci

# Execution Instructions

## Bat File Execution

- Update the "path to your project" in the file to the path. If it is in the same path as other files like `server.py`, `app.py`, remove the `cd` line.
- Double click on the bat file.
- Execution will start.

## Manual Execution

### Setup Virtual Environment

Create a virtual environment and install all dependencies using pip:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Start Servers

Start `server.py` for frontend:

```bash
python server.py
```

Start `app.py` for backend:

```bash
python app.py
```

### Execute Attackers

Execute each of the attackers by using the following commands:

```bash
python playwright-bot.py --url http://127.0.0.1:5500/index.html
```

```bash
python llm-bot.py --url http://127.0.0.1:5500/index.html
```

```bash
python exam-bot.py
```