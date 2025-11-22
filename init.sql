-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

-- Создание таблицы theme
CREATE TABLE IF NOT EXISTS theme (
    theme_id SERIAL PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL,
    parent_theme_id INTEGER REFERENCES theme(theme_id)
);

-- Создание таблицы algorythmtheories
CREATE TABLE IF NOT EXISTS algorythmtheories (
    theory_id SERIAL PRIMARY KEY,
    theme_id INTEGER UNIQUE NOT NULL REFERENCES theme(theme_id),
    description TEXT NOT NULL
);

-- Создание таблицы tasks
CREATE TABLE IF NOT EXISTS tasks (
    task_id SERIAL PRIMARY KEY,
    theme_id INTEGER NOT NULL REFERENCES theme(theme_id),
    title VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL,
    time_limit_ms INTEGER NOT NULL,
    memory_limit_mb INTEGER NOT NULL
);

-- Создание таблицы tasktestcases
CREATE TABLE IF NOT EXISTS tasktestcases (
    test_case_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(task_id),
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_example BOOLEAN NOT NULL DEFAULT FALSE
);

-- Создание таблицы submissions
CREATE TABLE IF NOT EXISTS submissions (
    submission_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL REFERENCES tasks(task_id),
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    code TEXT NOT NULL,
    is_complete BOOLEAN NOT NULL,
    status VARCHAR(50),
    run_time INTEGER,
    memory_used INTEGER,
    language VARCHAR(50)
);

-- Создание таблицы comments
CREATE TABLE IF NOT EXISTS comments (
    comment_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL
);

-- Создание таблицы taskcomments
CREATE TABLE IF NOT EXISTS taskcomments (
    task_comment_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(task_id),
    comment_id INTEGER UNIQUE NOT NULL REFERENCES comments(comment_id)
);

-- Создание таблицы theorycomments
CREATE TABLE IF NOT EXISTS theorycomments (
    theory_comment_id SERIAL PRIMARY KEY,
    theory_id INTEGER NOT NULL REFERENCES algorythmtheories(theory_id),
    comment_id INTEGER UNIQUE NOT NULL REFERENCES comments(comment_id)
);

-- Вставка тестовых данных

-- Темы
INSERT INTO theme (theme_id, title, parent_theme_id) VALUES
(1, 'Алгоритмы', NULL),
(2, 'Структуры данных', NULL),
(3, 'Сортировка', 1),
(4, 'Поиск', 1),
(5, 'Динамическое программирование', 1),
(6, 'Массивы', 2),
(7, 'Связные списки', 2)
ON CONFLICT (theme_id) DO NOTHING;

-- Теории
INSERT INTO algorythmtheories (theory_id, theme_id, description) VALUES
(1, 1, 'Алгоритм - это последовательность шагов для решения задачи. Основные характеристики алгоритмов: корректность, эффективность, конечность.'),
(2, 3, 'Алгоритмы сортировки: пузырьковая, быстрая, сортировка слиянием. Сложность от O(n²) до O(n log n).'),
(3, 5, 'Динамическое программирование - метод решения задач путем разбиения на подзадачи. Применяется когда подзадачи перекрываются.')
ON CONFLICT (theory_id) DO NOTHING;

-- Задачи
INSERT INTO tasks (task_id, theme_id, title, description, difficulty_level, time_limit_ms, memory_limit_mb) VALUES
(1, 3, 'Сумма двух чисел', 'Напишите функцию, которая принимает два числа и возвращает их сумму.', 'EASY', 2000, 128),
(2, 3, 'Сортировка массива', 'Отсортируйте массив чисел в порядке возрастания.', 'MEDIUM', 3000, 128),
(3, 5, 'Числа Фибоначчи', 'Напишите функцию, которая возвращает n-ное число Фибоначчи.', 'EASY', 2000, 128),
(4, 4, 'Бинарный поиск', 'Реализуйте алгоритм бинарного поиска в отсортированном массиве.', 'MEDIUM', 2000, 128),
(5, 5, 'Наибольшая возрастающая подпоследовательность', 'Найдите длину наибольшей возрастающей подпоследовательности в массиве.', 'HARD', 5000, 256)
ON CONFLICT (task_id) DO NOTHING;

-- Тестовые случаи
INSERT INTO tasktestcases (test_case_id, task_id, input_data, expected_output, is_example) VALUES
(1, 1, '2 3', '5', true),
(2, 1, '10 20', '30', false),
(3, 1, '-5 5', '0', false),
(4, 2, '3 1 2', '1 2 3', true),
(5, 2, '5 4 3 2 1', '1 2 3 4 5', false),
(6, 3, '5', '5', true),
(7, 3, '10', '55', false),
(8, 4, '5\n1 2 3 4 5\n3', '2', true),
(9, 4, '5\n1 2 3 4 5\n6', '-1', false),
(10, 5, '5\n10 9 2 5 3 7 101 18', '4', true)
ON CONFLICT (test_case_id) DO NOTHING;

-- Пользователь (для тестирования)
INSERT INTO users (user_id, name, login, password_hash, email, role) VALUES
(1, 'Тестовый Пользователь', 'testuser', '$2b$12$LQv3c1yqBWVHxkd0g8f7QuuKlaT7DC.ucTMgG8z1qNH38m7a3WQ1K', 'test@example.com', 'user')
ON CONFLICT (user_id) DO NOTHING;