-- SlotWise production records.
-- Applied when the production volume is first created.

INSERT INTO users (id, name) VALUES
    (10, 'Ada'),
    (11, 'Lin'),
    (12, 'Sam'),
    (13, 'Kai');

INSERT INTO sessions (id, title, starts_at, capacity, available_slots) VALUES
    (10, 'Sourdough Bread Basics', now(), 2, 7),
    (11, 'Winter Wreath Making', now(), 0, 0),
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
    (104, 13, 10, 'cancelled', '2025-12-01 09:00:00+00', '2026-01-01 00:00:00+00'),
    (105, 13, 11, 'active', '2026-01-01 09:00:00+00', NULL),
    (106, 10, 13, 'active', '2026-01-01 09:00:00+00', NULL),
    (107, 11, 13, 'active', '2026-01-01 09:01:00+00', NULL),
    (108, 12, 14, 'cancelled', '2026-01-01 09:00:00+00', '2026-01-01 00:00:00+00');

INSERT INTO reservation_audits
    (id, reservation_id, action, actor_user_id, created_at)
VALUES
    (200, 104, 'cancelled', 13, '2026-01-01 00:00:00+00'),
    (201, 108, 'cancelled', 12, '2026-01-01 00:00:00+00');

SELECT setval('users_id_seq', 13, true);
SELECT setval('sessions_id_seq', 14, true);
SELECT setval('reservations_id_seq', 108, true);
SELECT setval('reservation_audits_id_seq', 201, true);
