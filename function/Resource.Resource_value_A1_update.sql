-- Actualiza la valoración
-- AFTER INSERT/UPDATE
DECLARE

  pre_capex_long_term DECIMAL;
  pre_capex_vacant DECIMAL;
  post_capex DECIMAL;
  post_capex_residential DECIMAL;

BEGIN

  BEGIN
    -- Intenta obtener la última valoración
    SELECT "Pre_capex_long_term", "Pre_capex_vacant", "Post_capex", "Post_capex_residential"
    INTO pre_capex_long_term, pre_capex_vacant, post_capex, post_capex_residential
    FROM "Resource"."Resource_value"
    WHERE "Resource_id" = NEW."Resource_id"
    ORDER BY "Valuation_date" DESC
    LIMIT 1;

    -- Solo si se encontró resultado, realiza el UPDATE
    UPDATE "Resource"."Resource"
    SET
      "Pre_capex_long_term" = pre_capex_long_term, 
      "Pre_capex_vacant" = pre_capex_vacant,
      "Post_capex" = post_capex, 
      "Post_capex_residential" = post_capex_residential
    WHERE id = NEW."Resource_id";

  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      -- No hacer nada si no hay resultados
      NULL;
  END;

  RETURN NEW;
END;