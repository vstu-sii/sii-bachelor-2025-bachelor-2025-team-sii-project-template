-- Схема базы данных для системы анализа отзывов
-- Поддерживает аутентификацию через Telegram, анализ товаров и функции сравнения

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Создание базы данных
CREATE DATABASE IF NOT EXISTS review_analysis 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE review_analysis;

-- Таблица пользователей для аутентификации через Telegram
CREATE TABLE Users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL COMMENT 'Уникальный идентификатор из Telegram',
    telegram_username VARCHAR(255) NULL COMMENT 'Имя пользователя в Telegram (с @)',
    telegram_first_name VARCHAR(255) NULL COMMENT 'Имя из Telegram',
    telegram_last_name VARCHAR(255) NULL COMMENT 'Фамилия из Telegram',
    telegram_language_code VARCHAR(10) NULL COMMENT 'Код языка пользователя из Telegram',
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Дата создания аккаунта',
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Последний успешный вход',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Статус аккаунта',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_telegram_username (telegram_username),
    INDEX idx_registration_date (registration_date),
    INDEX idx_last_login (last_login),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Хранение пользователей, аутентифицированных через Telegram';

-- Таблица проектов для товаров пользователей
CREATE TABLE Projects (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'Владелец товара',
    marketplace_url VARCHAR(1000) NOT NULL COMMENT 'URL товара на маркетплейсе',
    product_name VARCHAR(500) NOT NULL COMMENT 'Название товара с маркетплейса',
    product_image_url VARCHAR(1000) NULL COMMENT 'URL изображения товара',
    product_identifier VARCHAR(500) NULL COMMENT 'Внутренний идентификатор товара на маркетплейсе',
    marketplace_type ENUM('wildberries', 'ozon', 'yandex_market') DEFAULT 'wildberries' COMMENT 'Поддерживаемые маркетплейсы',
    initial_rating DECIMAL(3,2) NULL COMMENT 'Рейтинг при первом анализе',
    current_rating DECIMAL(3,2) NULL COMMENT 'Последний рейтинг',
    total_reviews_count INT UNSIGNED DEFAULT 0 COMMENT 'Всего отзывов за все анализы',
    last_analysis_date TIMESTAMP NULL COMMENT 'Дата последнего успешного анализа',
    is_tracking_active BOOLEAN DEFAULT TRUE COMMENT 'Отслеживать ли этот товар',
    is_public BOOLEAN DEFAULT FALSE COMMENT 'Доступен ли анализ публично',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_marketplace_type (marketplace_type),
    INDEX idx_marketplace_url (marketplace_url(255)) COMMENT 'Префиксный индекс для длинных URL',
    INDEX idx_product_identifier (product_identifier),
    INDEX idx_created_at (created_at),
    INDEX idx_last_analysis_date (last_analysis_date),
    INDEX idx_is_tracking_active (is_tracking_active),
    UNIQUE KEY unique_user_product (user_id, marketplace_url(500)) COMMENT 'Предотвращение дублирования товаров у пользователя'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Товары пользователей для отслеживания анализа';

-- Таблица сессий анализа
CREATE TABLE Analyses (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL COMMENT 'Связанный товар',
    analysis_type ENUM('initial', 'periodic', 'custom') DEFAULT 'initial' COMMENT 'Тип анализа',
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Когда был выполнен анализ',
    period_start DATE NOT NULL COMMENT 'Начало периода анализа',
    period_end DATE NOT NULL COMMENT 'Конец периода анализа',
    total_reviews_processed INT UNSIGNED DEFAULT 0 COMMENT 'Количество проанализированных отзывов',
    new_reviews_count INT UNSIGNED DEFAULT 0 COMMENT 'Новые отзывы с последнего анализа',
    average_rating DECIMAL(3,2) NULL COMMENT 'Средний рейтинг за период',
    previous_average_rating DECIMAL(3,2) NULL COMMENT 'Рейтинг из предыдущего периода для сравнения',
    rating_change DECIMAL(3,2) NULL COMMENT 'Изменение рейтинга относительно предыдущего периода',
    positive_count INT UNSIGNED DEFAULT 0 COMMENT 'Количество положительных отзывов',
    neutral_count INT UNSIGNED DEFAULT 0 COMMENT 'Количество нейтральных отзывов',
    negative_count INT UNSIGNED DEFAULT 0 COMMENT 'Количество отрицательных отзывов',
    sentiment_distribution JSON NULL COMMENT 'Структурированные данные о тональности',
    status ENUM('pending', 'parsing', 'analyzing', 'completed', 'failed', 'no_data') DEFAULT 'pending',
    parsing_duration INT UNSIGNED NULL COMMENT 'Время парсинга в секундах',
    analysis_duration INT UNSIGNED NULL COMMENT 'Время AI-анализа в секундах',
    error_message TEXT NULL COMMENT 'Детали ошибки при сбое',
    retry_count TINYINT UNSIGNED DEFAULT 0 COMMENT 'Количество попыток повтора',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_analysis_date (analysis_date),
    INDEX idx_period_range (period_start, period_end),
    INDEX idx_status (status),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_rating_change (rating_change),
    CHECK (period_start <= period_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Сессии анализа с временными данными';

-- Детальные результаты анализа
CREATE TABLE AnalysisResults (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id BIGINT UNSIGNED NOT NULL COMMENT 'Родительская сессия анализа',
    aspect_category ENUM('quality', 'delivery', 'packaging', 'price', 'functionality', 'usability', 'support', 'other') DEFAULT 'other',
    aspect_name VARCHAR(100) NOT NULL COMMENT 'Конкретное название аспекта',
    mentions_count INT UNSIGNED DEFAULT 0 COMMENT 'Общее количество упоминаний этого аспекта',
    positive_mentions INT UNSIGNED DEFAULT 0 COMMENT 'Количество положительных упоминаний',
    negative_mentions INT UNSIGNED DEFAULT 0 COMMENT 'Количество отрицательных упоминаний',
    neutral_mentions INT UNSIGNED DEFAULT 0 COMMENT 'Количество нейтральных упоминаний',
    sentiment_score DECIMAL(4,3) NULL COMMENT 'Оценка тональности от -1 до +1',
    aspect_rating DECIMAL(3,2) NULL COMMENT 'Рейтинг, специфичный для этого аспекта',
    common_themes JSON NULL COMMENT 'Частые темы и ключевые слова',
    key_phrases JSON NULL COMMENT 'Извлеченные важные фразы',
    improvement_suggestions JSON NULL COMMENT 'Предложенные улучшения из отзывов',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_aspect_category (aspect_category),
    INDEX idx_aspect_name (aspect_name),
    INDEX idx_sentiment_score (sentiment_score),
    INDEX idx_mentions_count (mentions_count),
    UNIQUE KEY unique_analysis_aspect (analysis_id, aspect_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Детальные результаты анализа по аспектам';

-- Лог сессий парсинга
CREATE TABLE ParsingSessions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    analysis_id BIGINT UNSIGNED NULL COMMENT 'Связанный анализ, если доступен',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Время начала парсинга',
    finished_at TIMESTAMP NULL COMMENT 'Время завершения парсинга',
    reviews_found INT UNSIGNED DEFAULT 0 COMMENT 'Всего отзывов найдено на странице',
    reviews_parsed INT UNSIGNED DEFAULT 0 COMMENT 'Успешно распарсено отзывов',
    pages_processed INT UNSIGNED DEFAULT 0 COMMENT 'Количество обработанных страниц',
    parsing_status ENUM('started', 'completed', 'failed', 'partial', 'blocked') DEFAULT 'started',
    error_code VARCHAR(100) NULL COMMENT 'Специфичный идентификатор ошибки',
    error_details TEXT NULL COMMENT 'Детальная информация об ошибке',
    retry_after TIMESTAMP NULL COMMENT 'Когда повторить попытку при блокировке',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_started_at (started_at),
    INDEX idx_parsing_status (parsing_status),
    INDEX idx_error_code (error_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Лог сессий парсинга с маркетплейсами';

-- Лог взаимодействий с LLM
CREATE TABLE LLMInteractions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    analysis_id BIGINT UNSIGNED NULL COMMENT 'Связанная сессия анализа',
    interaction_type ENUM('sentiment_analysis', 'aspect_extraction', 'comparison_insights', 'summary_generation') NOT NULL,
    prompt_version VARCHAR(50) DEFAULT 'v1.0' COMMENT 'Версия шаблона промпта',
    prompt_text TEXT NOT NULL COMMENT 'Полный промпт, отправленный в LLM',
    llm_response JSON NULL COMMENT 'Структурированный ответ LLM',
    model_used VARCHAR(100) DEFAULT 'gpt-4' COMMENT 'Идентификатор модели LLM',
    total_tokens INT UNSIGNED NULL COMMENT 'Всего использовано токенов',
    prompt_tokens INT UNSIGNED NULL COMMENT 'Токены в промпте',
    completion_tokens INT UNSIGNED NULL COMMENT 'Токены в ответе',
    processing_time_ms INT UNSIGNED NULL COMMENT 'Время обработки в миллисекундах',
    cost_estimate DECIMAL(10,6) NULL COMMENT 'Примерная стоимость в USD',
    success BOOLEAN DEFAULT TRUE COMMENT 'Было ли взаимодействие успешным',
    error_message TEXT NULL COMMENT 'Ошибка при сбое взаимодействия',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_interaction_type (interaction_type),
    INDEX idx_created_at (created_at),
    INDEX idx_model_used (model_used),
    INDEX idx_success (success)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Лог всех взаимодействий с LLM для аудита и улучшения';

-- Таблица отчетов сравнения
CREATE TABLE ComparisonReports (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL COMMENT 'Владелец отчета',
    project_id BIGINT UNSIGNED NOT NULL COMMENT 'Связанный товар',
    report_name VARCHAR(255) NULL COMMENT 'Пользовательское название отчета',
    analysis_ids JSON NOT NULL COMMENT 'Массив ID анализов для сравнения [id1, id2, ...]',
    comparison_period_start DATE NULL COMMENT 'Начало сравниваемого периода',
    comparison_period_end DATE NULL COMMENT 'Конец сравниваемого периода',
    comparison_data JSON NOT NULL COMMENT 'Структурированные результаты сравнения',
    key_insights TEXT NULL COMMENT 'Текстовая сводка основных инсайтов',
    visualization_data JSON NULL COMMENT 'Данные для графиков и диаграмм',
    is_shared BOOLEAN DEFAULT FALSE COMMENT 'Является ли отчет общедоступным',
    share_token VARCHAR(100) NULL COMMENT 'Токен для общего доступа',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL COMMENT 'Когда истекает срок действия общего отчета',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_project_id (project_id),
    INDEX idx_generated_at (generated_at),
    INDEX idx_share_token (share_token),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_shared (is_shared)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Сохраненные отчеты сравнения для пользователей';

-- Пользовательские сессии для аутентификации
CREATE TABLE UserSessions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE COMMENT 'JWT или токен сессии',
    telegram_auth_data JSON NULL COMMENT 'Исходные данные аутентификации Telegram',
    ip_address VARCHAR(45) NULL COMMENT 'IP-адрес пользователя',
    user_agent TEXT NULL COMMENT 'Информация о браузере/user agent',
    expires_at TIMESTAMP NOT NULL COMMENT 'Время истечения сессии',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Активна ли сессия',
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Время последнего запроса',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_token (session_token),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_active (is_active),
    INDEX idx_last_activity (last_activity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Пользовательские сессии аутентификации';

-- Очередь анализа для фоновой обработки
CREATE TABLE AnalysisQueue (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    analysis_id BIGINT UNSIGNED NULL COMMENT 'Если повторяется существующий анализ',
    queue_type ENUM('initial_analysis', 'update_analysis', 'comparison') DEFAULT 'initial_analysis',
    priority TINYINT UNSIGNED DEFAULT 5 COMMENT '1 (наивысший) до 10 (низший)',
    scheduled_for TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Когда обрабатывать',
    started_at TIMESTAMP NULL COMMENT 'Когда началась обработка',
    completed_at TIMESTAMP NULL COMMENT 'Когда завершилась обработка',
    status ENUM('pending', 'processing', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    attempts_count TINYINT UNSIGNED DEFAULT 0 COMMENT 'Количество попыток обработки',
    max_attempts TINYINT UNSIGNED DEFAULT 3 COMMENT 'Максимальное количество попыток повтора',
    error_message TEXT NULL COMMENT 'Последнее сообщение об ошибке',
    processing_node VARCHAR(100) NULL COMMENT 'Какой узел обработал это задание',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_queue_type (queue_type),
    INDEX idx_priority (priority),
    INDEX idx_scheduled_for (scheduled_for),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Очередь фоновых заданий для обработки анализа';

-- Вставка начальных данных для поддерживаемых маркетплейсов
INSERT IGNORE INTO Users (id, telegram_id, telegram_username, telegram_first_name, is_active) 
VALUES (1, 0, 'system', 'System', FALSE);

SET FOREIGN_KEY_CHECKS = 1;
