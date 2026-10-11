-- Sanitized extract of the SlotWise production database.
--
-- Load it into the local database with ./ops/local-restore-snapshot.sh to
-- rehearse a change before running it against production.
--
-- This is an extract, not a copy. Customer names are replaced and some records
-- are held back, so production contains rows that are not here. Rehearsing
-- against this snapshot tells you that a change runs; it does not tell you that
-- you have seen every record it will touch.

CREATE TABLE users (
    id SERIAL NOT NULL,
    name VARCHAR(120) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE sessions (
    id SERIAL NOT NULL,
    title VARCHAR(200) NOT NULL,
    starts_at TIMESTAMP WITH TIME ZONE NOT NULL,
    capacity INTEGER NOT NULL,
    available_slots INTEGER NOT NULL,
    CONSTRAINT ck_sessions_capacity_nonnegative CHECK (capacity >= 0),
    CONSTRAINT ck_sessions_slots_nonnegative CHECK (available_slots >= 0),
    PRIMARY KEY (id)
);

CREATE TABLE reservations (
    id SERIAL NOT NULL,
    user_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    status VARCHAR(16) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT ck_reservation_status CHECK (status IN ('active', 'cancelled')),
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id),
    FOREIGN KEY(session_id) REFERENCES sessions (id)
);

CREATE TABLE reservation_audits (
    id SERIAL NOT NULL,
    reservation_id INTEGER NOT NULL,
    action VARCHAR(32) NOT NULL,
    actor_user_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(reservation_id) REFERENCES reservations (id),
    FOREIGN KEY(actor_user_id) REFERENCES users (id)
);

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INSERT INTO alembic_version (version_num) VALUES ('0001_initial');

INSERT INTO users (id, name) VALUES
    (10, 'Customer 10'),
    (11, 'Customer 11'),
    (12, 'Customer 12'),
    (13, 'Customer 13');

INSERT INTO sessions (id, title, starts_at, capacity, available_slots) VALUES
    (10, 'Sourdough Bread Basics', now(), 2, 7),
    (12, 'Watercolour Sketching Walk', now(), 3, 0),
    (13, 'Beginner Calligraphy', now(), 2, 5),
    (14, 'Knife Skills for Home Cooks', now(), 1, 1);

INSERT INTO reservations
    (id, user_id, session_id, status, created_at, cancelled_at)
VALUES
    (100, 10, 10, 'active', '2026-01-01 09:02:00+00', NULL),
    (101, 10, 10, 'active', '2026-01-01 09:00:00+00', NULL),
    (102, 11, 10, 'active', '2026-01-01 09:01:00+00', NULL),
    (103, 12, 10, 'active', '2026-01-01 08:59:00+00', NULL),
    (106, 10, 13, 'active', '2026-01-01 09:00:00+00', NULL),
    (107, 11, 13, 'active', '2026-01-01 09:01:00+00', NULL);

SELECT setval('users_id_seq', 13, true);
SELECT setval('sessions_id_seq', 14, true);
SELECT setval('reservations_id_seq', 107, true);
SELECT setval('reservation_audits_id_seq', 1, false);
