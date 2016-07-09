DROP TABLE IF EXISTS users CASCADE;

CREATE OR REPLACE FUNCTION updated_row() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = date_trunc('second', now());
    RETURN NEW; 
END;
$$ language 'plpgsql';

CREATE TABLE users (
    id              serial          NOT NULL    PRIMARY KEY,
    email           varchar(64)     NOT NULL,
    account         varchar(32)     NOT NULL,
    password        varchar(32)     NOT NULL,
    token           varchar(64)     NOT NULL,
    created_at      timestamp       DEFAULT date_trunc('second', now()),
    updated_at      timestamp       DEFAULT date_trunc('second', now())
);
CREATE TRIGGER users_updated_row BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE updated_row();
CREATE UNIQUE INDEX on users (email);
CREATE UNIQUE INDEX on users (account);
CREATE UNIQUE INDEX on users (token);
INSERT INTO users (email, account, password, token) VALUES ('admin', 'admin', '0145bd5070d84c19c71402aca60940f8', 'TOKEN@21232f297a@6244de18fb52aa3e0f95265d35380181');

