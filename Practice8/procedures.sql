DROP PROCEDURE IF EXISTS bulk_insert_contacts(text[], text[]);

CREATE OR REPLACE PROCEDURE bulk_insert_contacts(p_names TEXT[], p_phones TEXT[])
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1 .. array_upper(p_names, 1) LOOP
        -- Validation: check if phone is exactly 11 digits
        IF length(p_phones[i]) = 11 THEN
            INSERT INTO phonebook (username, phone_number)
            VALUES (p_names[i], p_phones[i])
            ON CONFLICT (username) DO UPDATE SET phone_number = p_phones[i];
        ELSE
            RAISE NOTICE 'Skipping %: % is invalid', p_names[i], p_phones[i];
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
AS $$
BEGIN
    INSERT INTO phonebook (username, phone_number)
    VALUES (p_name, p_phone)
    ON CONFLICT (username) DO UPDATE SET phone_number = p_phone;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_contact_by_val(p_val VARCHAR)
AS $$
BEGIN
    DELETE FROM phonebook WHERE username = p_val OR phone_number = p_val;
END;
$$ LANGUAGE plpgsql;