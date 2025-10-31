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
    subscription_tier ENUM('free', 'pro', 'business') DEFAULT 'free',
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_registration_date (registration_date),
    INDEX idx_subscription_tier (subscription_tier)
);

-- Ограничения анализов по подпискам (use-case 7 - частые анализы)
CREATE TABLE AnalysisLimits (
    user_id BIGINT UNSIGNED PRIMARY KEY,
    last_analysis_date DATE,
    analyses_today INT UNSIGNED DEFAULT 0,
    daily_limit INT UNSIGNED DEFAULT 10,                   -- Лимит по подписке
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Товары/проекты пользователей
CREATE TABLE Projects (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,                     -- Владелец товара
    marketplace_url VARCHAR(1000) NOT NULL,               -- Ссылка на маркетплейс
    product_name VARCHAR(500) NOT NULL,                   -- Название товара
    product_image_url VARCHAR(1000),                      -- URL изображения товара
    marketplace_type ENUM('wildberries', 'ozon', 'yandex_market') DEFAULT 'wildberries',
    current_rating DECIMAL(3,2) DEFAULT 0.00,             -- Текущий рейтинг для быстрого доступа
    last_analysis_id BIGINT UNSIGNED,                     -- Последний анализ для перфоманса
    total_analyses INT UNSIGNED DEFAULT 0,                -- Количество анализов
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,       -- Дата добавления
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,                       -- Активен для отслеживания
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (last_analysis_id) REFERENCES Analyses(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_user_active (user_id, is_active),           -- Для фильтрации активных
    INDEX idx_marketplace_url (marketplace_url(255)),     -- Префиксный индекс для длинных URL
    INDEX idx_created_at (created_at),
    INDEX idx_current_rating (current_rating),
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
    rating_trend ENUM('improved', 'declined', 'stable') DEFAULT 'stable',
    previous_analysis_id BIGINT UNSIGNED,                 -- Ссылка на предыдущий анализ для сравнения
    status ENUM('pending', 'processing', 'completed', 'failed', 'no_data') DEFAULT 'pending',
    parsing_duration INT UNSIGNED,                        -- Длительность парсинга в секундах
    error_message TEXT,                                   -- Сообщение об ошибке (если есть)
    retry_count INT UNSIGNED DEFAULT 0,                   -- Количество попыток перезапуска
    next_retry_at TIMESTAMP NULL,                         -- Время следующей попытки
    metadata JSON,                                        -- Дополнительные метаданные анализа
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (previous_analysis_id) REFERENCES Analyses(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_project_status_date (project_id, status, analysis_date DESC), -- Для последнего анализа
    INDEX idx_analysis_date (analysis_date),
    INDEX idx_period (period_start, period_end),
    INDEX idx_status (status),
    INDEX idx_rating_trend (rating_trend)
);

-- Результаты анализа (метрики и статистика)
CREATE TABLE AnalysisResults (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    analysis_id BIGINT UNSIGNED NOT NULL,                 -- Связь с сессией анализа
    aspect_name VARCHAR(100) NOT NULL,                    -- Аспект анализа (качество, доставка и т.д.)
    aspect_category ENUM('product', 'service', 'shipping', 'price', 'other') DEFAULT 'product',
    mentions_count INT UNSIGNED DEFAULT 0,                -- Сколько раз упоминался аспект
    positive_mentions INT UNSIGNED DEFAULT 0,             -- Позитивные упоминания
    negative_mentions INT UNSIGNED DEFAULT 0,             -- Негативные упоминания
    sentiment_score DECIMAL(4,3),                         -- Оценка тональности (-1 до +1)
    trend_direction ENUM('improving', 'declining', 'stable') DEFAULT 'stable',
    common_themes JSON,                                   -- Частые темы/слова по аспекту
    key_phrases JSON,                                     -- Ключевые фразы из отзывов
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE CASCADE,
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_aspect_name (aspect_name),
    INDEX idx_aspect_category (aspect_category),
    INDEX idx_sentiment_score (sentiment_score),
    UNIQUE KEY unique_analysis_aspect (analysis_id, aspect_name)
);

-- Сессии парсинга с маркетплейсов
CREATE TABLE ParsingSessions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    analysis_id BIGINT UNSIGNED,                          -- Связь с анализом
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,       -- Время начала парсинга
    finished_at TIMESTAMP NULL,                           -- Время окончания парсинга
    reviews_parsed INT UNSIGNED DEFAULT 0,                -- Сколько отзывов собрано
    pages_processed INT UNSIGNED DEFAULT 0,               -- Обработанные страницы
    parsing_status ENUM('started', 'completed', 'failed', 'no_data', 'rate_limited') DEFAULT 'started',
    error_details TEXT,                                   -- Детали ошибки парсинга
    marketplace_response_code INT,                        -- HTTP код ответа маркетплейса
    retry_count INT UNSIGNED DEFAULT 0,                   -- Количество повторных попыток
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_started_at (started_at),
    INDEX idx_parsing_status (parsing_status)
);

-- Взаимодействия с LLM (для анализа тональности)
CREATE TABLE LLMInteractions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT UNSIGNED NOT NULL,
    analysis_id BIGINT UNSIGNED,                          -- Опциональная связь с анализом
    prompt_type ENUM('sentiment_analysis', 'aspect_extraction', 'comparison_insights', 'trend_analysis') NOT NULL,
    prompt_text TEXT NOT NULL,                            -- Отправленный промпт
    llm_response JSON,                                    -- Ответ LLM в структурированном виде
    model_used VARCHAR(100) DEFAULT 'gpt-4',             -- Использованная модель
    tokens_used INT UNSIGNED,                             -- Потраченные токены
    processing_time INT UNSIGNED,                         -- Время обработки в секундах
    cost DECIMAL(10,6) DEFAULT 0.000000,                 -- Стоимость запроса
    success BOOLEAN DEFAULT TRUE,                         -- Успешен ли запрос
    error_message TEXT,                                   -- Ошибка если есть
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_id) REFERENCES Analyses(id) ON DELETE SET NULL,
    INDEX idx_project_id (project_id),
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_created_at (created_at),
    INDEX idx_prompt_type (prompt_type),
    INDEX idx_success (success)
);

-- Таблица для хранения сравнительных отчетов (use-case сравнения анализов)
CREATE TABLE ComparisonReports (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    project_id BIGINT UNSIGNED NOT NULL,
    analysis_ids JSON NOT NULL,                           -- Массив ID анализов для сравнения [1,2,3]
    analysis_count INT UNSIGNED DEFAULT 0,                -- Количество анализов в сравнении
    period_range JSON,                                    -- Диапазон периодов для быстрого доступа
    comparison_data JSON,                                 -- Структурированные данные сравнения
    key_insights JSON,                                    -- Ключевые инсайты от ИИ
    visualization_data JSON,                              -- Данные для визуализации графиков
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,                       -- Активен для отображения
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_project_id (project_id),
    INDEX idx_generated_at (generated_at),
    INDEX idx_is_active (is_active)
);

-- Системные настройки и кэш
CREATE TABLE SystemSettings (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,             -- Ключ настройки
    setting_value JSON,                                   -- Значение настройки
    description TEXT,                                     -- Описание настройки
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (setting_key)
);

-- Триггер для обновления последнего анализа в проекте
DELIMITER //
CREATE TRIGGER after_analysis_complete
    AFTER UPDATE ON Analyses
    FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        -- Обновляем последний анализ и рейтинг в проекте
        UPDATE Projects 
        SET last_analysis_id = NEW.id, 
            current_rating = NEW.average_rating,
            total_analyses = total_analyses + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.project_id;
        
        -- Обновляем счетчик анализов за день
        INSERT INTO AnalysisLimits (user_id, last_analysis_date, analyses_today, daily_limit)
        SELECT p.user_id, CURDATE(), 1, 10
        FROM Projects p 
        WHERE p.id = NEW.project_id
        ON DUPLICATE KEY UPDATE 
            analyses_today = IF(last_analysis_date = CURDATE(), analyses_today + 1, 1),
            last_analysis_date = CURDATE();
    END IF;
END//
DELIMITER ;

-- Вставка начальных настроек системы
INSERT INTO SystemSettings (setting_key, setting_value, description) VALUES
('analysis_rate_limit', '{"free": 10, "pro": 50, "business": 200}', 'Суточные лимиты анализов по подпискам'),
('parsing_timeout', '{"default": 30, "extended": 60}', 'Таймауты парсинга в секундах'),
('supported_marketplaces', '["wildberries", "ozon", "yandex_market"]', 'Поддерживаемые маркетплейсы'),
('llm_models', '["gpt-4", "gpt-3.5-turbo", "claude-3"]', 'Доступные модели ИИ');

-- Создание пользователя для приложения
CREATE USER 'review_analysis_user'@'%' IDENTIFIED BY 'secure_password_123';
GRANT SELECT, INSERT, UPDATE, DELETE ON review_analysis.* TO 'review_analysis_user'@'%';
FLUSH PRIVILEGES;
