@echo off
cd "your path to project"

if not exist myenv (
    python -m venv myenv
)

call myenv\Scripts\activate.bat

pip install --upgrade pip
pip install flask flask-cors numpy opencv-python dashscope playwright
pip install selenium webdriver-manager
pip install transformers
pip install torch

python -m playwright install

start "Flask Server" cmd /k "call myenv\Scripts\activate.bat && python server.py"

start "Bot Runner" cmd /k "call myenv\Scripts\activate.bat && python playwright-bot.py && python llm-bot.py && echo n | python exam-bot.py"



pause

