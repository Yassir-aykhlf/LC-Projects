-- SlotWise production schema.
-- Applied when the production volume is first created.

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
