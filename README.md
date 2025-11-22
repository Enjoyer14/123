
***

# **Auth Service** <br>

## ***auth_service/app.py*** <br>
- *create_app()*: создание и конфигурация приложения Flask
- *Migrate*: Используется для управления миграциями базы данных (добавление новых полей без потери текущих данных и крутое сохранение истории)
- *JWTManager*: Настраивает и управляет JWT токенами
- *CORS* (Cross-Origin Resource Sharing - Совместное использование ресурсов из разных источников): Обязательно для взаимодействия с реактом на другом порте. Механизм, который использует заголовки HTTP для того, чтобы разрешить веб-браузеру, запущенному на одном домене (React  на http://localhost:3000), получать доступ к ресурсам на другом домене ( Backend на http://localhost:5000).

## ***auth_service/routes.py*** <br>
- *@auth_bp.route('/register')*: endpoint для регистрации
- *register()*: Создает нового пользователя
- *@auth_bp.route('/login')*: endpoint для аутентификации
- *login()*: Проверяет данные входа и генерирует пару JWT токенов (access и refresh)
- *@jwt_required()*: Декоратор, который требует наличия действительного JWT токена в заголовке 'Authorization'
- *get_jwt_identity()*: Извлекает данные (user_id), которые мы поместили в токен

## ***auth_service/models.py*** <br>
- *User*: Модель для работы с таблицей users
- *bcrypt*: Используется для безопасного хеширования и проверки паролей
- *_set_password()*: Хеширует пароль при создании пользователя
- *check_password()*: Сравнивает введенный пароль с хешем в БД при аутентификации

***

# **Main Service** <br>

## ***main_service/routes.py*** <br>
- *get_user_id_from_request()*: Имитирует получение ID пользователя из заголовка, который должен быть добавлен Auth Service после проверки JWT.
- *submit_code()*: Главный роут. Он сохраняет запись в БД, получает ее ID (submission_id), а затем отправляет всю необходимую информацию в RabbitMQ.
- *db.session.flush()*: Необходим, чтобы получить значение submission_id до того, как мы сделаем commit.

## ***main_service/rabbitmq_producer.py*** <br>
- *pika.BlockingConnection*: Используется для синхронной отправки (подключился, отправил, отключился).
- *queue_declare(durable=True)*: Гарантирует, что очередь не пропадет при перезапуске брокера.
- *delivery_mode=pika.spec.DeliveryMode.Persistent*: Гарантирует, что сообщение сохранится на диске до его обработки, что критично для задач.

## ***main_service/models.py*** <br>
- user_id: Для Submissions и Comments мы не используем db.ForeignKey, так как таблица Users находится в Auth Service. В микросервисной архитектуре это обычная практика, чтобы избежать жестких зависимостей между БД.
- Submission: Мы добавили поля 'status', 'run_time', 'memory_used' для хранения результатов проверки.

***

# **toDo:** <br>
- Логирование
- WSGI для нормального запуска серваков
- Нормальная настройка CORS - разрешаем запросы ТОЛЬКО с Frontend домена (например, React работает на 3000 порту в разработке,  или на домене 'https://my-learning-app.com' в проде) ( CORS(app,  resources={r"/api/*": {"origins": ["http://localhost:3000", "https://my-learning-app.com"]}}, supports_credentials=True) # Маст хев для передачи куки или заголовков авторизации)
- Выбор ЯП