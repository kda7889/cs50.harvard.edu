
# English: This script installs all required dependencies for the project.
# Русский: Этот скрипт устанавливает все необходимые зависимости для проекта.

# Step 1: Create a virtual environment
# English: Ensure you have a clean Python environment.
# Русский: Убедитесь, что у вас есть чистое окружение Python.
python3 -m venv venv

# Step 2: Activate the virtual environment
# English: Activate the environment to isolate project dependencies.
# Русский: Активируйте окружение для изоляции зависимостей проекта.
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate   # For Windows

# Step 3: Install dependencies
# English: Install required Python libraries.
# Русский: Установите необходимые библиотеки Python.
pip install -r requirements.txt

# Step 4: Run the application
# English: Start the application.
# Русский: Запустите приложение.
python app.py
