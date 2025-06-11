-- Создаем таблицу задач (если ещё не существует)
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER CHECK(priority BETWEEN 1 AND 5),  -- 1-высокий, 5-низкий
    status TEXT CHECK(status IN ('todo', 'in_progress', 'review', 'done')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    creator_id INTEGER NOT NULL,
    assignee_id INTEGER,
    FOREIGN KEY (creator_id) REFERENCES users(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id)
);

-- Создаем индекс для ускорения поиска по статусу
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

-- Создаем индекс для ускорения поиска по ответственному
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id);