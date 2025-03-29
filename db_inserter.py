import mysql.connector

# 🔧 Налаштування підключення до бази
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='user',
    database='telegram_bot_db'
)
cursor = conn.cursor()

# 🔢 ID тесту
TEST_ID = 1

# 🧩 Список питань з відповідями
questions = [
    {
        "text": "Яка роль в IAM GCP має найвищі привілеї?",
        "answers": [
            ("Storage Admin", False),
            ("Viewer", False),
            ("Owner", True),
            ("Billing User", False)
        ]
    },
    {
        "text": "Що таке gcloud?",
        "answers": [
            ("Інструмент командного рядка для керування ресурсами GCP", True),
            ("Хмарне сховище Google", False),
            ("Панель керування в браузері", False),
            ("API для машинного навчання", False)
        ]
    },
    {
        "text": "Що потрібно зробити спочатку, щоб почати працювати з GCP?",
        "answers": [
            ("Створити проект у Google Cloud Console", True),
            ("Встановити Docker", False),
            ("Запустити Cloud Function", False),
            ("Створити Cloud Storage bucket", False)
        ]
    },
    {
        "text": "Яка команда ініціалізує gcloud CLI?",
        "answers": [
            ("gcloud start", False),
            ("gcloud init", True),
            ("gcloud create", False),
            ("gcloud config", False)
        ]
    },
    {
        "text": "Що таке “Billing Account” у GCP?",
        "answers": [
            ("Платіжна система Google Pay", False),
            ("API для нарахування коштів", False),
            ("Обліковий запис для оплати за ресурси GCP", True),
            ("Аккаунт адміністратора", False)
        ]
    },
    {
        "text": "Яка роль потрібна користувачу для створення об’єктів у Cloud Storage?",
        "answers": [
            ("Compute Admin", False),
            ("Storage Admin", True),
            ("Project Viewer", False),
            ("Billing Admin", False)
        ]
    },
    {
        "text": "Яка з цих команд дозволяє змінити активний проєкт у gcloud?",
        "answers": [
            ("gcloud login", False),
            ("gcloud activate", False),
            ("gcloud config set project [PROJECT_ID]", True),
            ("gcloud auth project", False)
        ]
    },
    {
        "text": "Яка команда використовується для автентифікації в gcloud CLI?",
        "answers": [
            ("gcloud auth login", True),
            ("gcloud init login", False),
            ("gcloud set credentials", False),
            ("gcloud auth user", False)
        ]
    },
    {
        "text": "Яке призначення ролі “Viewer” в IAM?",
        "answers": [
            ("Дозволяє створювати ресурси", False),
            ("Дозволяє переглядати, але не змінювати ресурси", True),
            ("Дозволяє керувати рахунками", False),
            ("Дозволяє доступ до системних логів", False)
        ]
    },
    {
        "text": "Який ресурс не вимагає billing account?",
        "answers": [
            ("Cloud Shell", True),
            ("Compute Engine", False),
            ("Cloud Run", False),
            ("BigQuery", False)
        ]
    },
    {
        "text": "Яка роль потрібна для налаштування білінгу?",
        "answers": [
            ("IAM Admin", False),
            ("Owner", False),
            ("Billing Admin", True),
            ("Viewer", False)
        ]
    },
    {
        "text": "Яка команда дозволяє переглянути список проєктів?",
        "answers": [
            ("gcloud projects list", True),
            ("gcloud get projects", False),
            ("gcloud list", False),
            ("gcloud config list", False)
        ]
    },
    {
        "text": "Що означає “principals” у контексті IAM?",
        "answers": [
            ("Паролі користувачів", False),
            ("Проекти з правами доступу", False),
            ("Користувачі, групи або сервісні акаунти, яким надаються ролі", True),
            ("Типи дозволів", False)
        ]
    },
    {
        "text": "Яка з ролей дозволяє лише перегляд білінгу?",
        "answers": [
            ("Billing Admin", False),
            ("Billing Viewer", True),
            ("Owner", False),
            ("Finance Editor", False)
        ]
    },
    {
        "text": "Що з цього є обов’язковим для створення GCP проекту?",
        "answers": [
            ("Сервісний акаунт", False),
            ("Назва проекту та billing account", True),
            ("Cloud Run функція", False),
            ("Встановлений Kubernetes кластер", False)
        ]
    }
]

# 🚀 Вставка в базу
for q in questions:
    cursor.execute("INSERT INTO questions (test_id, question_text) VALUES (%s, %s)", (TEST_ID, q["text"]))
    question_id = cursor.lastrowid  # Отримати ID щойно вставленого питання

    for answer_text, is_correct in q["answers"]:
        cursor.execute(
            "INSERT INTO answers (question_id, answer_text, is_correct) VALUES (%s, %s, %s)",
            (question_id, answer_text, is_correct)
        )

conn.commit()
cursor.close()
conn.close()

print("✅ Успішно додано всі питання та відповіді.")
