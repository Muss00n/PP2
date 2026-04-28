-- ============================================================
-- TSIS1 Procedures & Functions
-- Built on top of Practice 7 & 8 (phonebook table)
-- ============================================================

-- Keep your Practice 8 procedures (drop first to avoid conflicts)
DROP PROCEDURE IF EXISTS bulk_insert_contacts(text[], text[]);
DROP PROCEDURE IF EXISTS upsert_contact(varchar, varchar);
DROP PROCEDURE IF EXISTS delete_contact_by_val(varchar);
DROP FUNCTION  IF EXISTS get_contacts_by_pattern(text);
DROP FUNCTION  IF EXISTS get_contacts_paginated(integer, integer);

-- ── FROM PRACTICE 8 (kept & improved) ────────────────────────

-- 1. Search by pattern (name, phone) - Practice 8
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE(contact_id INT, username VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT p.contact_id, p.username, p.phone_number
    FROM phonebook p
    WHERE p.username ILIKE '%' || p_pattern || '%'
       OR p.phone_number LIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;


-- 2. Upsert single contact - Practice 8
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
AS $$
BEGIN
    INSERT INTO phonebook (username, phone_number)
    VALUES (p_name, p_phone)
    ON CONFLICT (username) DO UPDATE SET phone_number = p_phone;
END;
$$ LANGUAGE plpgsql;


-- 3. Bulk insert with loop + IF + validation - Practice 8
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(p_names TEXT[], p_phones TEXT[])
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1 .. array_upper(p_names, 1) LOOP
        IF length(p_phones[i]) = 11 THEN
            INSERT INTO phonebook (username, phone_number)
            VALUES (p_names[i], p_phones[i])
            ON CONFLICT (username) DO UPDATE SET phone_number = p_phones[i];
        ELSE
            RAISE NOTICE 'Skipping %: "%" has invalid length (need 11 digits)', p_names[i], p_phones[i];
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- 4. Paginated query - Practice 8
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(contact_id INT, username VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT p.contact_id, p.username, p.phone_number
    FROM phonebook p
    ORDER BY p.contact_id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;


-- 5. Delete by username or phone - Practice 8
CREATE OR REPLACE PROCEDURE delete_contact_by_val(p_val VARCHAR)
AS $$
BEGIN
    DELETE FROM phonebook WHERE username = p_val OR phone_number = p_val;
END;
$$ LANGUAGE plpgsql;


-- ── NEW FOR TSIS1 ─────────────────────────────────────────────

-- 6. add_phone(contact_name, phone, type)
--    Adds a new phone number to an existing contact
DROP PROCEDURE IF EXISTS add_phone(varchar, varchar, varchar);
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT contact_id INTO v_id
    FROM phonebook
    WHERE username ILIKE p_contact_name
    LIMIT 1;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type)
    ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql;


-- 7. move_to_group(contact_name, group_name)
--    Moves a contact to a group; creates group if it doesn't exist
DROP PROCEDURE IF EXISTS move_to_group(varchar, varchar);
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    SELECT id INTO v_group_id FROM groups WHERE name ILIKE p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;

    UPDATE phonebook SET group_id = v_group_id
    WHERE username ILIKE p_contact_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 8. search_contacts(query) - extended: searches email + phones table too
DROP FUNCTION IF EXISTS search_contacts(text);
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    contact_id  INT,
    username    VARCHAR,
    phone_number VARCHAR,
    email       VARCHAR,
    birthday    DATE,
    group_name  VARCHAR,
    extra_phone VARCHAR,
    phone_type  VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (pb.contact_id, ph.phone)
           pb.contact_id,
           pb.username,
           pb.phone_number,
           pb.email,
           pb.birthday,
           g.name        AS group_name,
           ph.phone      AS extra_phone,
           ph.type       AS phone_type
    FROM   phonebook pb
    LEFT JOIN groups g  ON g.id  = pb.group_id
    LEFT JOIN phones ph ON ph.contact_id = pb.contact_id
    WHERE  pb.username     ILIKE '%' || p_query || '%'
       OR  pb.phone_number LIKE  '%' || p_query || '%'
       OR  pb.email        ILIKE '%' || p_query || '%'
       OR  ph.phone        LIKE  '%' || p_query || '%'
    ORDER BY pb.contact_id, ph.phone;
END;
$$ LANGUAGE plpgsql;
