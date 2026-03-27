DROP FUNCTION IF EXISTS get_contacts_by_pattern(text);

CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE(contact_id INT, username VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT * FROM phonebook 
    WHERE phonebook.username ILIKE '%' || p_pattern || '%' 
       OR phonebook.phone_number LIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS get_contacts_paginated(integer, integer);

CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(contact_id INT, username VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT * FROM phonebook 
    ORDER BY contact_id 
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;