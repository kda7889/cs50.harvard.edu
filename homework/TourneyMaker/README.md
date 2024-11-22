# TourneyMaker
#### Video Demo:  https://youtu.be/PQVH7o3lXgA
#### Description:
TourneyMaker is a comprehensive tournament management system designed to simplify the process of creating and managing tournaments for various events. This project features an intuitive user interface, supports multiple languages, and ensures a smooth experience for organizers and participants alike.

## Project Structure

### Main Files
- **`app.py`**: The core script of the project, managing routes, logic, and connections to the database.
- **`babel.cfg`**: Configuration file for localization and internationalization.
- **`messages.pot`**: Translation template file.
- **`tournament.db`**: The SQLite database storing all tournament-related data.

### Static Files
- **`static/jquery-3.6.0.min.js`**: jQuery library used for enhanced client-side functionality.

### Templates (HTML)
- **`create_match.html`**: Template for creating new matches.
- **`create_tournament.html`**: Template for setting up new tournaments.
- **`index.html`**: Homepage of the application.
- **`layout.html`**: Base layout template shared across all pages.
- **`login.html`**: User login page.
- **`participants.html`**: Manage tournament participants.
- **`recover_password.html`**: Password recovery page.
- **`register.html`**: User registration page.
- **`register_user.html`**: Template for registering a new user.
- **`tournament_bracket.html`**: Visual representation of the tournament bracket.
- **`tournament_details.html`**: Detailed view of a tournament.

### Localization
The `translations` directory contains language support files:
- `.mo` files: Compiled translations.
- `.po` files: Editable translation files.

### Utility Scripts
- **`0_DeepL_test.py`**: Script for testing automated translations.
- **`1_generate_po_files.py`**: Generates `.po` files for new languages.
- **`2_update_translations.py`**: Updates translations across languages.
- **`3_po_mo_translations.py`**: Converts `.po` files to `.mo`.

## Design Choices
- **User-friendly Interface**: Templates are designed with clarity and simplicity in mind to ensure a seamless user experience.
- **Localization**: Extensive support for multiple languages enhances global accessibility.
- **Modularity**: The codebase is divided into reusable components for ease of maintenance and scalability.

### app.py

The `app.py` file is the core of the TourneyMaker project, built using Flask. It handles routing, logic, session management, database interactions, and localization.

#### Key Features
1. **User Authentication**:
   - Provides routes for user login, registration, and logout.
   - Ensures password security with hashing using `Werkzeug`.
   - Includes a `@login_required` decorator to restrict access to authenticated users.

2. **Tournament Management**:
   - Routes to create, view, and manage tournaments.
   - Supports CRUD operations for participants and matches.

3. **Localization**:
   - Implements multi-language support with Flask-Babel.
   - Dynamically loads translations based on user preferences.

4. **Database Integration**:
   - Uses SQLite to store data related to users, tournaments, participants, and matches.

5. **Email Notifications**:
   - Enables sending emails for tasks like password recovery using `smtplib`.

6. **Logging**:
   - Employs Python’s `logging` module to track application activities and debug issues.

#### Routes Overview
- `/`: Home page displaying project information.
- `/login` and `/register`: User authentication pages.
- `/tournament/create`: Create a new tournament.
- `/tournament/<id>`: View tournament details.
- `/tournament/<id>/bracket`: Display the tournament bracket.
- `/participants`: Manage participants for a tournament.

#### Conclusion
The `app.py` file serves as the backbone of the application, integrating various components like authentication, database management, localization, and routing. It ensures a seamless user experience and robust functionality for managing tournaments.

## Installation
1. Install dependencies from `requirements.txt`. You can use `commands.sh`
2. Run the application using `python app.py`.
3. Access the application at `http://localhost:5000`.



# TourneyMaker

TourneyMaker — это система управления турнирами, разработанная для упрощения создания и управления турнирами для различных мероприятий. Проект предлагает интуитивно понятный интерфейс, поддержку нескольких языков и удобство как для организаторов, так и для участников.

## Структура проекта

### Основные файлы
- **`app.py`**: Основной скрипт проекта, управляющий маршрутами, логикой и подключением к базе данных.
- **`babel.cfg`**: Конфигурационный файл для локализации и интернационализации.
- **`messages.pot`**: Шаблон перевода.
- **`tournament.db`**: База данных SQLite, содержащая всю информацию о турнирах.

### Статические файлы
- **`static/jquery-3.6.0.min.js`**: Библиотека jQuery для расширенной функциональности на стороне клиента.

### Шаблоны (HTML)
- **`create_match.html`**: Шаблон для создания новых матчей.
- **`create_tournament.html`**: Шаблон для настройки новых турниров.
- **`index.html`**: Главная страница приложения.
- **`layout.html`**: Базовый шаблон, используемый на всех страницах.
- **`login.html`**: Страница входа в систему.
- **`participants.html`**: Управление участниками турнира.
- **`recover_password.html`**: Страница восстановления пароля.
- **`register.html`**: Страница регистрации пользователей.
- **`register_user.html`**: Шаблон для регистрации нового пользователя.
- **`tournament_bracket.html`**: Визуальное представление турнирной сетки.
- **`tournament_details.html`**: Детальный просмотр информации о турнире.

### Локализация
Директория `translations` содержит файлы поддержки языков:
- `.mo` файлы: Компилированные переводы.
- `.po` файлы: Редактируемые файлы переводов.

### Вспомогательные скрипты
- **`0_DeepL_test.py`**: Скрипт для тестирования автоматического перевода.
- **`1_generate_po_files.py`**: Генерация `.po` файлов для новых языков.
- **`2_update_translations.py`**: Обновление переводов.
- **`3_po_mo_translations.py`**: Конвертация `.po` файлов в `.mo`.

## Дизайнерские решения
- **Удобный интерфейс**: Шаблоны разработаны для обеспечения простоты и понятности.
- **Локализация**: Расширенная поддержка нескольких языков делает приложение доступным для глобальной аудитории.
- **Модульность**: Кодовая база разделена на повторно используемые компоненты для упрощения обслуживания и масштабируемости.

### app.py

Файл `app.py` является ядром проекта TourneyMaker, построенного на основе Flask. Он отвечает за маршрутизацию, логику, управление сессиями, взаимодействие с базой данных и локализацию.

#### Основные функции
1. **Аутентификация пользователей**:
   - Предоставляет маршруты для входа, регистрации и выхода из системы.
   - Обеспечивает безопасность паролей с использованием хеширования через `Werkzeug`.
   - Включает декоратор `@login_required` для ограничения доступа неавторизованным пользователям.

2. **Управление турнирами**:
   - Маршруты для создания, просмотра и управления турнирами.
   - Поддерживает операции CRUD для участников и матчей.

3. **Локализация**:
   - Реализует поддержку нескольких языков с помощью Flask-Babel.
   - Динамически загружает переводы на основе предпочтений пользователя.

4. **Интеграция с базой данных**:
   - Использует SQLite для хранения данных о пользователях, турнирах, участниках и матчах.

5. **Уведомления по электронной почте**:
   - Позволяет отправлять письма, например, для восстановления пароля, используя `smtplib`.

6. **Логирование**:
   - Использует модуль `logging` Python для отслеживания активности приложения и отладки.

#### Обзор маршрутов
- `/`: Главная страница с информацией о проекте.
- `/login` и `/register`: Страницы авторизации и регистрации пользователей.
- `/tournament/create`: Создание нового турнира.
- `/tournament/<id>`: Просмотр деталей турнира.
- `/tournament/<id>/bracket`: Отображение турнирной сетки.
- `/participants`: Управление участниками турнира.

#### Заключение
Файл `app.py` является основой приложения, интегрируя такие компоненты, как аутентификация, управление базой данных, локализация и маршрутизация. Он обеспечивает удобство использования и надежный функционал для управления турнирами.

## Установка
1. Установите зависимости из файла `requirements.txt`. Можно использовать `commands.sh`
2. Запустите приложение с помощью команды `python app.py`.
3. Откройте приложение в браузере по адресу `http://localhost:5000`.