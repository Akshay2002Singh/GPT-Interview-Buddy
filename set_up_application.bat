@echo off
echo "Creating setup for GPT Interview Buddy"
echo.

echo "Installing virtual environment..."
echo.
pip install virtualenv

echo "Creating virtual environment..."
echo.
python -m venv env

echo "Activating virtual environment..."
echo.
call env\Scripts\activate

echo "Installing requirements..."
echo.
pip install -r Requirements.txt

echo "Deleting Files that are not required..."
echo.
rmdir /s /q "Important_Codes"
del README.md .gitignore set_up_application.bat Requirements.txt

timeout /t 15