-- Создание базы данных
CREATE DATABASE IF NOT EXISTS review_analysis;
USE review_analysis;

-- Пользователи системы (аутентификация через Telegram)
CREATE TABLE Users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,                    -- ID из Telegram
    telegram_username VARCHAR(255),                        -- @username
    telegram_first_name VARCHAR(255),                      -- Имя в Telegram
    telegram_last_name VARCHAR(255),                       -- Фамилия в Telegram
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Дата регистрации
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        -- Последний вход
    is_active BOOLEAN DEFAULT TRUE,                       -- Активен ли аккаунт
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_registration_date (registration_date)
);

-- Товары/проекты пользователей
CREATE TABLE Projects (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,                     -- Владелец товара
    marketplace_url VARCHAR(1000) NOT NULL,               -- Ссылка на маркетплейс
    product_name VARCHAR(500) NOT NULL,                   -- Название товара
    product_image_url VARCHAR(1000),                      -- URL изображения товара
    marketplace_type ENUM('wildberries', 'ozon', 'yandex_market') DEFAULT 'wildberries',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,       -- Дата добавления
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,                       -- Активен для отслеживания
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_marketplace_url (marketplace_url(255)),     -- Префиксный индекс для длинных URL
    INDEX idx_created_at (created_at),
    UNIQUE KEY unique_user_product (user_id, marketplace_url(500)) -- Один товар у пользователя
);

-- Сессии парсинга (история анализов)
CREATE TABLE Analyses (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,                  -- Связь с товаром
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- Дата проведения анализа
    period_start DATE NOT NULL,                           -- Начало анализируемого периода
    period_end DATE NOT NULL,                             -- Конец анализируемого периода
    total_reviews INT UNSIGNED DEFAULT 0,                 -- Всего отзывов в анализе
    average_rating DECIMAL(3,2),                          -- Средний рейтинг
    positive_count INT UNSIGNED DEFAULT 0,                -- Кол-во позитивных отзывов
    neutral_count INT UNSIGNED DEFAULT 0,                 -- Кол-во нейтральных отзывов
    negative_count INT UNSIGNED DEFAULT 0,                -- Кол-во негативных отзывов
    status ENUM('pending', 'processing', 'completed', 'failed', 'no_data') DEFAULT 'pending',
    parsing_duration INT UNSIGNED,                        -- Длительность парсинга в секундах
    error_message TEXT,                                   -- Сообщение об ошибке (если есть)
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_analysis_date (analysis_date),
    INDEX idx_period (period_start, period_end),
    INDEX idx_status (status)
);

-- Результаты анализа (метрики и статистика)
CREATE TABLE AnalysisResults (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id BIGINT UNSIGNED NOT NULL,                 -- Связь с сессией анализа
    aspect_name VARCHAR(100) NOT NULL,                    -- Аспект анализа (качество, доставка и т.д.)
    mentions_count INT UNSIGNED DEFAULT 0,                -- Сколько раз упоминался аспект
    positive_mentions INT UNSIGNED DEFAULT 0,             -- Позитивные упоминания
    negative_mentions INT UNSIGNED DEFAULT 0,             -- Негативные упоминания
    sentiment_score DECIMAL(4,3),                         -- Оценка тональности (-1 до +1)
    common_themes JSON,                                   -- Частые темы/слова по аспекту
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_aspect_name (aspect_name),
    UNIQUE KEY unique_analysis_aspect (analysis_id, aspect_name)
);

-- Сессии парсинга с маркетплейсов
CREATE TABLE ParsingSessions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,       -- Время начала парсинга
    finished_at TIMESTAMP NULL,                           -- Время окончания парсинга
    reviews_parsed INT UNSIGNED DEFAULT 0,                -- Сколько отзывов собрано
    parsing_status ENUM('started', 'completed', 'failed', 'no_data') DEFAULT 'started',
    error_details TEXT,                                   -- Детали ошибки парсинга
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_started_at (started_at)
);

-- Взаимодействия с LLM (для анализа тональности)
CREATE TABLE LLMInteractions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    analysis_id BIGINT UNSIGNED,                          -- Опциональная связь с анализом
    prompt_type ENUM('sentiment_analysis', 'aspect_extraction', 'comparison_insights') NOT NULL,
    prompt_text TEXT NOT NULL,                            -- Отправленный промпт
    llm_response JSON,                                    -- Ответ LLM в структурированном виде
    model_used VARCHAR(100) DEFAULT 'gpt-4',             -- Использованная модель
    tokens_used INT UNSIGNED,                             -- Потраченные токены
    processing_time INT UNSIGNED,                         -- Время обработки в секундах
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_created_at (created_at),
    INDEX idx_prompt_type (prompt_type)
);

-- Таблица для хранения сравнительных отчетов (use-case сравнения анализов)
CREATE TABLE ComparisonReports (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    project_id BIGINT UNSIGNED NOT NULL,
    analysis_ids JSON NOT NULL,                           -- Массив ID анализов для сравнения [1,2,3]
    comparison_data JSON,                                 -- Структурированные данные сравнения
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_project_id (project_id),
    INDEX idx_generated_at (generated_at)
);
