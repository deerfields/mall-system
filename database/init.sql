-- SQL to initialize the mall database
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('red', 'yellow', 'green')) DEFAULT 'red',
    due_date DATETIME DEFAULT CURRENT_TIMESTAMP
); 