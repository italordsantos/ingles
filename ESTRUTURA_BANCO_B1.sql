-- =====================================================
-- ESTRUTURA DO BANCO DE DADOS - PLATAFORMA B1 PRELIMINARY
-- =====================================================

-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS english_b1_platform;
USE english_b1_platform;

-- =====================================================
-- TABELAS PRINCIPAIS
-- =====================================================

-- Tabela de usuários
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    current_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') DEFAULT 'A2',
    target_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') DEFAULT 'B1',
    total_xp INT DEFAULT 0,
    current_streak INT DEFAULT 0,
    max_streak INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    profile_image_url VARCHAR(255) NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language_preference ENUM('pt-BR', 'en-US') DEFAULT 'pt-BR'
);

-- Tabela de níveis e progresso
CREATE TABLE user_levels (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    current_xp INT DEFAULT 0,
    xp_required INT NOT NULL,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    unlocked_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_level (user_id, level)
);

-- Tabela de categorias de gramática
CREATE TABLE grammar_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    difficulty_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    order_index INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de regras gramaticais
CREATE TABLE grammar_rules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    category_id INT NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    rule_description TEXT NOT NULL,
    b1_examples JSON NOT NULL,
    difficulty_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES grammar_categories(id) ON DELETE CASCADE
);

-- Tabela de categorias de vocabulário
CREATE TABLE vocabulary_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50) NULL,
    color VARCHAR(7) DEFAULT '#3B82F6',
    order_index INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de palavras de vocabulário
CREATE TABLE vocabulary_words (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    word VARCHAR(100) NOT NULL,
    phonetic VARCHAR(100) NULL,
    part_of_speech ENUM('noun', 'verb', 'adjective', 'adverb', 'preposition', 'conjunction', 'interjection', 'pronoun') NOT NULL,
    definition_en TEXT NOT NULL,
    definition_pt TEXT NOT NULL,
    b1_context TEXT,
    difficulty_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    category_id INT NOT NULL,
    is_phrasal_verb BOOLEAN DEFAULT FALSE,
    examples JSON NOT NULL,
    synonyms JSON NULL,
    antonyms JSON NULL,
    related_words JSON NULL,
    frequency_rating INT DEFAULT 1, -- 1-5, onde 5 é mais frequente
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES vocabulary_categories(id) ON DELETE CASCADE,
    INDEX idx_word (word),
    INDEX idx_difficulty (difficulty_level),
    INDEX idx_category (category_id)
);

-- Tabela de exercícios de gramática
CREATE TABLE grammar_exercises (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    grammar_rule_id BIGINT NOT NULL,
    exercise_type ENUM('multiple_choice', 'gap_fill', 'sentence_construction', 'error_correction', 'matching', 'ordering') NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    options JSON NULL, -- Para múltipla escolha
    explanation TEXT NOT NULL,
    difficulty_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    b1_focus BOOLEAN DEFAULT FALSE,
    time_limit INT DEFAULT 60, -- em segundos
    points_reward INT DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grammar_rule_id) REFERENCES grammar_rules(id) ON DELETE CASCADE
);

-- Tabela de exercícios de vocabulário
CREATE TABLE vocabulary_exercises (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    vocabulary_word_id BIGINT NOT NULL,
    exercise_type ENUM('flashcard', 'context', 'matching', 'gap_fill', 'multiple_choice', 'word_formation') NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    options JSON NULL,
    context_sentence TEXT NULL,
    difficulty_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    points_reward INT DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vocabulary_word_id) REFERENCES vocabulary_words(id) ON DELETE CASCADE
);

-- Tabela de questões de teste B1
CREATE TABLE b1_test_questions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    exam_part ENUM('reading', 'writing', 'listening', 'speaking') NOT NULL,
    part_number INT NOT NULL, -- 1, 2, 3, 4, 5, 6
    question_type ENUM('multiple_choice', 'gap_fill', 'matching', 'open_ended', 'picture_description') NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    options JSON NULL,
    explanation TEXT,
    difficulty_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    time_limit INT DEFAULT 120, -- em segundos
    points_reward INT DEFAULT 20,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_exam_part (exam_part, part_number)
);

-- =====================================================
-- TABELAS DE GAMIFICAÇÃO
-- =====================================================

-- Tabela de conquistas
CREATE TABLE achievements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(50) NOT NULL,
    xp_reward INT DEFAULT 0,
    badge_image_url VARCHAR(255) NULL,
    category ENUM('vocabulary', 'grammar', 'speaking', 'listening', 'streak', 'special') NOT NULL,
    requirement_type ENUM('count', 'streak', 'accuracy', 'time', 'custom') NOT NULL,
    requirement_value INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de conquistas do usuário
CREATE TABLE user_achievements (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    achievement_id INT NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress_current INT DEFAULT 0,
    progress_required INT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_achievement (user_id, achievement_id)
);

-- Tabela de sessões de estudo
CREATE TABLE study_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    session_type ENUM('vocabulary', 'grammar', 'speaking', 'listening', 'mixed') NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    duration_minutes INT DEFAULT 0,
    total_exercises INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    accuracy_percentage DECIMAL(5,2) DEFAULT 0.00,
    xp_earned INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================================================
-- TABELAS DE PROGRESSO E APRENDIZADO
-- =====================================================

-- Tabela de progresso de vocabulário do usuário
CREATE TABLE user_vocabulary_progress (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    vocabulary_word_id BIGINT NOT NULL,
    memory_strength INT DEFAULT 1, -- 1-5, onde 5 é dominado
    review_count INT DEFAULT 0,
    last_reviewed TIMESTAMP NULL,
    next_review TIMESTAMP NULL,
    is_mastered BOOLEAN DEFAULT FALSE,
    mastered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (vocabulary_word_id) REFERENCES vocabulary_words(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_word (user_id, vocabulary_word_id)
);

-- Tabela de progresso de gramática do usuário
CREATE TABLE user_grammar_progress (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    grammar_rule_id BIGINT NOT NULL,
    mastery_level INT DEFAULT 1, -- 1-5, onde 5 é dominado
    practice_count INT DEFAULT 0,
    correct_answers INT DEFAULT 0,
    accuracy_percentage DECIMAL(5,2) DEFAULT 0.00,
    last_practiced TIMESTAMP NULL,
    is_mastered BOOLEAN DEFAULT FALSE,
    mastered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (grammar_rule_id) REFERENCES grammar_rules(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_rule (user_id, grammar_rule_id)
);

-- Tabela de histórico de exercícios
CREATE TABLE exercise_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    exercise_type ENUM('vocabulary', 'grammar', 'b1_test') NOT NULL,
    exercise_id BIGINT NOT NULL,
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_taken INT DEFAULT 0, -- em segundos
    xp_earned INT DEFAULT 0,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================================================
-- TABELAS DE CONTEÚDO ADICIONAL
-- =====================================================

-- Tabela de áudios para listening
CREATE TABLE listening_audio (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    audio_url VARCHAR(255) NOT NULL,
    duration_seconds INT NOT NULL,
    difficulty_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    accent ENUM('american', 'british', 'australian', 'canadian', 'mixed') DEFAULT 'british',
    category VARCHAR(100) NULL,
    transcript TEXT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de músicas para aprendizado
CREATE TABLE learning_music (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    artist VARCHAR(200) NOT NULL,
    genre VARCHAR(100) NULL,
    audio_url VARCHAR(255) NOT NULL,
    lyrics TEXT NOT NULL,
    difficulty_level ENUM('A1', 'A2', 'B1', 'B2', 'C1', 'C2') NOT NULL,
    vocabulary_focus JSON NULL, -- Palavras-chave da música
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INSERÇÃO DE DADOS INICIAIS
-- =====================================================

-- Inserir categorias de gramática B1
INSERT INTO grammar_categories (name, description, difficulty_level, order_index) VALUES
('Adjectives and Adverbs', 'Adjetivos com -ed vs -ing, advérbios de frequência, comparativos e superlativos', 'B1', 1),
('Conditionals', 'Todos os tipos de condicionais: 0, 1st, 2nd, 3rd', 'B1', 2),
('Conjunctions', 'Palavras de conexão para causa, efeito e contraste', 'B1', 3),
('Future Tenses', 'Will, going to, future progressive, voz passiva futura', 'B1', 4),
('Gerund and Infinitive', 'Verbos seguidos de gerúndio ou infinitivo', 'B1', 5),
('Modal Verbs', 'May, might, can, could, must, have to, ought to, need', 'B1', 6),
('Past Tenses', 'Past simple, progressive, perfect, perfect progressive, used to', 'B1', 7),
('Prepositions', 'Frases preposicionais e uso correto de preposições', 'B1', 8),
('Present Tenses', 'Present simple, progressive, perfect, perfect progressive', 'B1', 9),
('Pronouns', 'Pronomes indefinidos e reflexivos', 'B1', 10),
('Questions', 'Question tags complexos e perguntas Wh-', 'B1', 11);

-- Inserir categorias de vocabulário B1
INSERT INTO vocabulary_categories (name, description, icon, color, order_index) VALUES
('Jobs and Professions', 'Vocabulário relacionado a trabalho e carreiras', '💼', '#10B981', 1),
('Family and Relationships', 'Palavras sobre família e relacionamentos', '👨‍👩‍👧‍👦', '#F59E0B', 2),
('Food and Drinks', 'Comida, bebidas e culinária', '🍕', '#EF4444', 3),
('Climate and Weather', 'Clima, tempo e condições meteorológicas', '🌤️', '#3B82F6', 4),
('Environment', 'Meio ambiente e sustentabilidade', '🌍', '#10B981', 5),
('Animals', 'Animais domésticos e selvagens', '🐾', '#8B5CF6', 6),
('Housing and Furniture', 'Casa, apartamento e móveis', '🏠', '#F59E0B', 7),
('Transportation', 'Meios de transporte e viagem', '🚗', '#EF4444', 8),
('Free Time Activities', 'Atividades de lazer e hobbies', '🎮', '#3B82F6', 9),
('Daily Routines', 'Rotinas diárias e hábitos', '⏰', '#8B5CF6', 10),
('Phrasal Verbs', 'Verbos frasais comuns do nível B1', '🔗', '#10B981', 11);

-- Inserir conquistas básicas
INSERT INTO achievements (name, description, icon, xp_reward, category, requirement_type, requirement_value) VALUES
('Vocabulary Master', 'Aprenda 100 palavras do nível B1', '📚', 100, 'vocabulary', 'count', 100),
('Grammar Champion', 'Complete 50 exercícios de gramática B1', '🎯', 150, 'grammar', 'count', 50),
('Streak Legend', 'Mantenha uma sequência de 7 dias', '🔥', 200, 'streak', 'streak', 7),
('Perfect Score', 'Alcance 100% de acerto em uma sessão', '⭐', 300, 'special', 'accuracy', 100),
('Time Master', 'Estude por 30 minutos em uma sessão', '⏱️', 100, 'special', 'time', 30),
('B1 Pioneer', 'Complete seu primeiro teste B1', '🏆', 500, 'special', 'count', 1);

-- =====================================================
-- ÍNDICES PARA OTIMIZAÇÃO
-- =====================================================

-- Índices para performance de consultas
CREATE INDEX idx_user_progress ON user_vocabulary_progress(user_id, memory_strength, next_review);
CREATE INDEX idx_grammar_progress ON user_grammar_progress(user_id, mastery_level, accuracy_percentage);
CREATE INDEX idx_exercise_history ON exercise_history(user_id, exercise_type, completed_at);
CREATE INDEX idx_study_sessions ON study_sessions(user_id, session_type, start_time);
CREATE INDEX idx_vocabulary_difficulty ON vocabulary_words(difficulty_level, category_id, is_active);
CREATE INDEX idx_grammar_difficulty ON grammar_exercises(difficulty_level, b1_focus, is_active);

-- =====================================================
-- VIEWS ÚTEIS
-- =====================================================

-- View para progresso geral do usuário
CREATE VIEW user_overall_progress AS
SELECT 
    u.id,
    u.username,
    u.current_level,
    u.total_xp,
    u.current_streak,
    COUNT(DISTINCT uvp.vocabulary_word_id) as words_learned,
    COUNT(DISTINCT ugp.grammar_rule_id) as grammar_rules_learned,
    AVG(uvp.memory_strength) as avg_vocabulary_strength,
    AVG(ugp.mastery_level) as avg_grammar_mastery
FROM users u
LEFT JOIN user_vocabulary_progress uvp ON u.id = uvp.user_id
LEFT JOIN user_grammar_progress ugp ON u.id = ugp.user_id
GROUP BY u.id;

-- View para estatísticas de exercícios
CREATE VIEW exercise_statistics AS
SELECT 
    u.username,
    COUNT(eh.id) as total_exercises,
    SUM(CASE WHEN eh.is_correct THEN 1 ELSE 0 END) as correct_answers,
    AVG(eh.time_taken) as avg_time_taken,
    SUM(eh.xp_earned) as total_xp_earned
FROM users u
JOIN exercise_history eh ON u.id = eh.user_id
GROUP BY u.id, u.username;

-- =====================================================
-- PROCEDURES ÚTEIS
-- =====================================================

-- Procedure para calcular XP do usuário
DELIMITER //
CREATE PROCEDURE CalculateUserXP(IN user_id_param BIGINT)
BEGIN
    DECLARE total_xp INT DEFAULT 0;
    
    -- XP de exercícios
    SELECT COALESCE(SUM(xp_earned), 0) INTO total_xp
    FROM exercise_history 
    WHERE user_id = user_id_param;
    
    -- XP de conquistas
    SELECT total_xp + COALESCE(SUM(xp_reward), 0) INTO total_xp
    FROM user_achievements ua
    JOIN achievements a ON ua.achievement_id = a.id
    WHERE ua.user_id = user_id_param AND ua.is_completed = TRUE;
    
    -- Atualizar XP do usuário
    UPDATE users SET total_xp = total_xp WHERE id = user_id_param;
    
    SELECT total_xp as new_total_xp;
END //
DELIMITER ;

-- Procedure para verificar se usuário pode progredir de nível
DELIMITER //
CREATE PROCEDURE CheckLevelProgression(IN user_id_param BIGINT)
BEGIN
    DECLARE current_level_val VARCHAR(2);
    DECLARE total_xp_val INT;
    DECLARE new_level VARCHAR(2);
    
    SELECT current_level, total_xp INTO current_level_val, total_xp_val
    FROM users WHERE id = user_id_param;
    
    -- Lógica de progressão de nível baseada em XP
    CASE 
        WHEN total_xp_val >= 10000 THEN SET new_level = 'B2';
        WHEN total_xp_val >= 5000 THEN SET new_level = 'B1';
        WHEN total_xp_val >= 2000 THEN SET new_level = 'A2';
        ELSE SET new_level = 'A1';
    END CASE;
    
    -- Atualizar nível se necessário
    IF new_level != current_level_val THEN
        UPDATE users SET current_level = new_level WHERE id = user_id_param;
        SELECT CONCAT('Nível atualizado para: ', new_level) as message;
    ELSE
        SELECT CONCAT('Nível atual mantido: ', current_level_val) as message;
    END IF;
END //
DELIMITER ;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger para atualizar progresso de vocabulário
DELIMITER //
CREATE TRIGGER after_vocabulary_exercise
AFTER INSERT ON exercise_history
FOR EACH ROW
BEGIN
    IF NEW.exercise_type = 'vocabulary' THEN
        INSERT INTO user_vocabulary_progress (user_id, vocabulary_word_id, review_count, last_reviewed)
        VALUES (NEW.user_id, NEW.exercise_id, 1, NOW())
        ON DUPLICATE KEY UPDATE
        review_count = review_count + 1,
        last_reviewed = NOW(),
        updated_at = NOW();
    END IF;
END //
DELIMITER ;

-- Trigger para atualizar progresso de gramática
DELIMITER //
CREATE TRIGGER after_grammar_exercise
AFTER INSERT ON exercise_history
FOR EACH ROW
BEGIN
    IF NEW.exercise_type = 'grammar' THEN
        INSERT INTO user_grammar_progress (user_id, grammar_rule_id, practice_count, correct_answers, accuracy_percentage)
        VALUES (NEW.user_id, NEW.exercise_id, 1, 
                CASE WHEN NEW.is_correct THEN 1 ELSE 0 END,
                CASE WHEN NEW.is_correct THEN 100.00 ELSE 0.00 END)
        ON DUPLICATE KEY UPDATE
        practice_count = practice_count + 1,
        correct_answers = correct_answers + CASE WHEN NEW.is_correct THEN 1 ELSE 0 END,
        accuracy_percentage = (correct_answers * 100.0) / practice_count,
        updated_at = NOW();
    END IF;
END //
DELIMITER ;

-- =====================================================
-- COMENTÁRIOS FINAIS
-- =====================================================

/*
ESTRUTURA COMPLETA DO BANCO DE DADOS PARA PLATAFORMA B1 PRELIMINARY

Este banco de dados suporta:
✅ Sistema completo de usuários e progresso
✅ Categorização de gramática e vocabulário B1
✅ Sistema de exercícios e testes
✅ Gamificação com XP e conquistas
✅ Progresso adaptativo e personalizado
✅ Histórico completo de atividades
✅ Suporte a áudio e música para learning
✅ Views e procedures para análise
✅ Triggers para atualização automática

PRÓXIMOS PASSOS:
1. Executar este script para criar o banco
2. Popular com dados dos materiais B1 analisados
3. Implementar APIs para consumir os dados
4. Desenvolver sistema de exercícios
5. Implementar algoritmo de repetição espaçada
*/
