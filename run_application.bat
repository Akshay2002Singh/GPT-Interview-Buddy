@echo off
echo "Running GPT Interview Buddy"
echo .

echo "Activating virtual environment..."
echo.
call env\Scripts\activate

echo "Don't close this terminal while using application"
python gui.pyw
