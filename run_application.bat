@echo off
echo "Running GPT Interview Buddy"
echo .

echo "Activating virtual environment..."
echo.
call env\Scripts\activate

echo "Running Application"
python gui.pyw
