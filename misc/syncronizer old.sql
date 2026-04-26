-- DROP FUNCTION "Models".synchronizer();

CREATE OR REPLACE FUNCTION "Models".synchronizer()
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    result integer := 0;
    enumType RECORD;
    enumValue RECORD;
    entity RECORD;
    function RECORD;
    attribute RECORD;
    index RECORD;
    reference RECORD;
    role RECORD;
    user RECORD;
    record RECORD;
    sql text;
    i integer;
    value text;
    str text;
    str2 text;
    str3 text;
    type text;
    checkSql text;
    oidValue int;
    attnumValue int;
    attributesStr text;
    referencedAttributesStr text;
    job RECORD;
    tablename2 text;
    condition text;
    functionname text;
    moment text;
    events text;
    event text;
    count int;
    selectedAttributes int[];
    selectedAttribute RECORD;
    "variantSelectorAttribute" record;
BEGIN
    RESET ROLE;
    
    -- TO-DO Si el esquema no existe, es que se ha podido borrar a mano, por lo que habría que resetear todos los oid's, attnum's, ...
    
    -- Cambiar nombres de roles
    FOR role IN SELECT r.rolname, r2.name 
            FROM pg_roles r, 
                 "Models"."Role" r2
            WHERE r.oid = r2.oid 
            AND   r.rolname != r2.name LOOP
        
        -- Cambiar nombre del rol
        sql := 'ALTER ROLE "' || role.rolname || '" RENAME TO "' || role."name" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Cambiar nombres de usuarios
    FOR user IN SELECT r.rolname, u.username 
            FROM pg_roles r, 
                 "Models"."User" u
            WHERE r.oid = u.oid 
            AND   r.rolname != u.username LOOP
        
        -- Cambiar nombre del usuario
        sql := 'ALTER ROLE "' || "user"."rolname" || '" RENAME TO "' || "user"."username" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Cambiar usuario de administrador a no-administrador o vicerversa
    FOR user IN SELECT r.rolname, r.rolsuper, u."isAdmin" 
            FROM pg_roles r, 
                 "Models"."User" u
            WHERE r.oid = u.oid 
            AND   r.rolsuper != u."isAdmin" LOOP
        
        -- Cambiar nombre del usuario
        IF "user"."isAdmin" THEN
            sql := 'ALTER ROLE "' || "user"."rolname" || '" WITH SUPERUSER';
        ELSE
            sql := 'ALTER ROLE "' || "user"."rolname" || '" WITH NOSUPERUSER';
        END IF;
        EXECUTE sql;
    END LOOP;
    
    -- Cambiar nombres de tablas
    FOR entity IN SELECT n.nspname, c.relname, e.name 
            FROM pg_namespace n, 
                 pg_class c, 
                 "Models"."Entity" e 
            WHERE c.relnamespace = n.oid 
            AND   c.oid = e.oid 
            AND   c.relname != e.name LOOP
        
        -- Cambiar nombre de la tabla
        sql := 'ALTER TABLE IF EXISTS "' || entity."nspname" || '"."' || entity."relname" || '" RENAME TO "' || entity."name" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Cambiar nombres de tipos enumerados
    FOR enumType IN SELECT n.nspname, t.typname, et.name 
            FROM pg_namespace n, 
                 pg_type t, 
                 "Models"."EnumType" et 
            WHERE t.typnamespace = n.oid 
            AND   t.oid = et.oid 
            AND   t.typname != et.name LOOP
        
        -- Cambiar nombre del tipo enumerado
        sql := 'ALTER TYPE "' || enumType."nspname" || '"."' || enumType."typname" || '" RENAME TO "' || enumType."name" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Cambiar tablas de esquema
    FOR entity IN SELECT n.nspname, e.schema, e.id, e.name 
            FROM pg_namespace n, 
                 pg_class c, 
                 "Models"."Entity" e 
            WHERE c.relnamespace = n.oid 
            AND   c.oid = e.oid 
            AND   e.schema != n.nspname LOOP
        
        -- Cambiar la tabla de esquema
        EXECUTE 'CREATE SCHEMA IF NOT EXISTS "' || entity."schema" || '"';
        sql := 'ALTER TABLE IF EXISTS "' || entity."nspname" || '"."' || entity."name" || '" SET SCHEMA "' || entity."schema" || '"';
        EXECUTE sql;

        -- Actualizar esquema a los índices
        sql := 'UPDATE "Models"."EntityKey" SET schema = ''' || entity."schema" || ''' WHERE container = ' || entity.id;
        EXECUTE sql;
    END LOOP;
    
    -- Cambiar tipos enumerados de esquema
    FOR enumType IN SELECT n.nspname, et.schema, et.id, et.name 
            FROM pg_namespace n, 
                 pg_type t, 
                 "Models"."EnumType" et 
            WHERE t.typnamespace = n.oid 
            AND   t.oid = et.oid 
            AND   et.schema != n.nspname LOOP
        
        -- Cambiar el tipo enumerado de esquema
        EXECUTE 'CREATE SCHEMA IF NOT EXISTS "' || enumType."schema" || '"';
        sql := 'ALTER TYPE "' || enumType."nspname" || '"."' || enumType."name" || '" SET SCHEMA "' || enumType."schema" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Cambiar nombres de atributos
    FOR attribute IN SELECT n.nspname, c.relname, a.attname, ea.name 
            FROM pg_namespace n, 
                 pg_class c, 
                 pg_attribute a, 
                 "Models"."Entity" e, 
                 "Models"."EntityAttribute" ea 
            WHERE c.relnamespace = n.oid 
            AND   a.attrelid = c.oid 
            AND   e.oid = c.oid 
            AND   ea.container = e.id 
            AND   ea.attnum = a.attnum 
            AND   a.attname != ea.name LOOP
            
        -- Cambiar nombre del atributo
        sql := 'ALTER TABLE IF EXISTS "' || attribute."nspname" || '"."' || attribute."relname" || '" RENAME "' || attribute.attname || '" TO "' || attribute."name" || '"';
        EXECUTE sql;
        BEGIN
            sql := 'ALTER TABLE IF EXISTS "' || attribute."nspname" || '"."' || attribute."relname" || '" RENAME CONSTRAINT "' || attribute.attname || '_check" TO "' || attribute."name" || '_check"';
            EXECUTE sql;
        EXCEPTION
            WHEN SQLSTATE '42704' THEN
                RAISE NOTICE 'constraint "%" does not exist, skipping', attribute.attname || '_check';
        END;
    END LOOP;
    
    -- Cambiar tipos de atributos
    -- Cambiar si es requerido un atributo
    -- Cambiar valor por defecto
    -- Estas tres me las llevo a un trigger on update de la table EntityAttribute
    -- El anterior también lo podía haber hecho así, pero bueno, lo dejo de momento como está y me sirve de referencia para otros casos
    
    -- Actualizar tipos enumerados existentes 
    -- Buscar tipos enumerados que han cambiado, por quitarles o por añadirles campos
    FOR enumValue IN 
            SELECT DISTINCT id, schema, name 
            FROM (
                SELECT *
                FROM (
                    SELECT et.id, unnest(et.values) AS value, et.schema, et.name, et.oid 
                    FROM "Models"."EnumType" et 
                    WHERE et.oid IS NOT NULL
                ) AS et
                WHERE et.value NOT IN (
                    SELECT e.enumlabel 
                    FROM pg_namespace n, 
                         pg_type t, 
                         pg_enum e 
                    WHERE e.enumtypid = t.oid 
                    AND   t.typnamespace = n.oid 
                    AND   et.oid = t.oid
                )
                UNION
                SELECT * 
                FROM (
                    SELECT et.id, e.enumlabel, et.schema, et.name, et.oid
                    FROM pg_namespace n, 
                         pg_type t, 
                         pg_enum e,
                         "Models"."EnumType" et
                    WHERE e.enumtypid = t.oid 
                    AND   t.typnamespace = n.oid 
                    AND   et.oid = t.oid
                ) AS et2 
                WHERE et2.enumlabel NOT IN (
                    SELECT unnest(et.values) 
                    FROM "Models"."EnumType" et 
                    WHERE et.oid IS NOT NULL
                    AND et.schema = et2.schema
                    AND et.name = et2.name
                    AND et.oid = et2.oid
                )
            ) AS et3 LOOP

        -- Buscar todos los campos que tienen el tipo enumerado en cuestión
        SELECT array_agg(ea.id) INTO STRICT selectedAttributes 
        FROM "Models"."EntityAttribute" ea, 
             "Models"."EnumType" et 
        WHERE ea."enumType" = et.id
        AND   et."schema" = enumValue."schema"
        AND   et."name" = enumValue."name";
        
        -- Borrar el valor por defecto y desasociar los campos del tipo enumerado
        FOR selectedAttribute IN SELECT e."schema", e."name" AS "entityName", ea."name", ea."isArray" FROM "Models"."Entity" e, "Models"."EntityAttribute" ea WHERE ea.container = e.id AND ea.id = ANY(selectedAttributes) LOOP
            sql := 'ALTER TABLE IF EXISTS "' || selectedAttribute.schema || '"."' || selectedAttribute."entityName" || '" ALTER COLUMN "' || selectedAttribute.name || '" DROP DEFAULT';
            EXECUTE sql;
            sql := 'ALTER TABLE IF EXISTS "' || selectedAttribute.schema || '"."' || selectedAttribute."entityName" || '" ALTER COLUMN "' || selectedAttribute.name || '" TYPE text' || CASE selectedAttribute."isArray" WHEN TRUE THEN '[]' ELSE '' END || ' USING "' || selectedAttribute.name || '"::text' || CASE selectedAttribute."isArray" WHEN TRUE THEN '[]' ELSE '' END;
            EXECUTE sql;
        END LOOP;  

        -- Borrar el tipo enumerado
        EXECUTE 'DROP TYPE "' || enumValue."schema" || '"."' || enumValue."name" || '"';
        
        -- Crear el tipo enumerado actualizado
        FOR enumType IN SELECT * FROM "Models"."EnumType" WHERE "schema" = enumValue."schema" AND "name" = enumValue."name" LOOP
            BEGIN
                sql := 'CREATE TYPE "' || enumType."schema" || '"."' || enumType."name" || '" AS ENUM (';
                i := 0;
                FOREACH value IN ARRAY enumType."values" LOOP
                    IF NOT i = 0 THEN
                        sql := sql || ', ';
                    END IF;
                    sql := sql || '''' || value || '''';
                    i := i + 1;
                END LOOP;
                
                sql := sql || ')';
                EXECUTE sql;
                
                -- Asignar oid
                SELECT t.oid INTO STRICT oidValue
                FROM pg_type t, 
                     pg_namespace n 
                WHERE t.typtype = 'e' 
                AND   t.typcategory = 'E'
                AND   t.typnamespace = n.oid
                AND   n.nspname = enumType."schema"
                AND   t.typname = enumType."name";
                
                sql := 'UPDATE "Models"."EnumType" SET "oid" = ' || oidValue || ' WHERE id = ' || enumType."id";
                execute sql;
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE NOTICE 'type "%" already exists, skipping', enumType."name";
            END;
        END LOOP;
        
        -- Asignar oid
        SELECT t.oid INTO STRICT oidValue
        FROM pg_type t, 
             pg_namespace n 
        WHERE t.typtype = 'e' 
        AND   t.typcategory = 'E'
        AND   t.typnamespace = n.oid
        AND   n.nspname = enumValue."schema"
        AND   t.typname = enumValue."name";
        
        sql := 'UPDATE "Models"."EnumType" SET "oid" = ' || oidValue || ' WHERE id = ' || enumValue."id";
        execute sql;
        
        -- Volver a asociar los campos al tipo enumerado y establecer el valor por defecto si lo tiene
        FOR selectedAttribute IN SELECT e."schema", e."name" AS "entityName", ea."name", ea."isArray", ea."defaultValue" FROM "Models"."Entity" e, "Models"."EntityAttribute" ea WHERE ea.container = e.id AND ea.id = ANY(selectedAttributes) LOOP
            sql := 'ALTER TABLE IF EXISTS "' || selectedAttribute.schema || '"."' || selectedAttribute."entityName" || '" ALTER COLUMN "' || selectedAttribute.name || '" TYPE "' || enumValue."schema" || '"."' || enumValue."name" || '"' || CASE selectedAttribute."isArray" WHEN TRUE THEN '[]' ELSE '' END || ' USING "' || selectedAttribute.name || '"::"' || enumValue."schema" || '"."' || enumValue.name || '"' || CASE selectedAttribute."isArray" WHEN TRUE THEN '[]' ELSE '' END;
            EXECUTE sql;
            IF selectedAttribute."defaultValue" IS NOT null THEN
                sql := 'ALTER TABLE IF EXISTS "' || selectedAttribute.schema || '"."' || selectedAttribute."entityName" || '" ALTER COLUMN "' || selectedAttribute.name || '" SET DEFAULT ''' || selectedAttribute."defaultValue" || '''';
                EXECUTE sql;
            END IF;
        END LOOP;  
    END LOOP;
    
    -- Borrar referencias que ya no estén en el modelo o (2023-08-29) que no sean deferrables (ahora por defecto se van a crear deferrables para poder asignar ids before insert y cosas así).
    FOR index IN SELECT n.nspname AS schemaname, 
                        t.relname AS tablename, 
                        c.conname AS constraintname
                 FROM pg_namespace n, 
                      pg_class t, 
                      pg_constraint c 
                 WHERE c.contype = 'f'
                 AND   n.oid = t.relnamespace 
                 AND   t.oid = c.conrelid 
                 AND   n.nspname NOT LIKE 'pg_%'
                 AND   n.nspname NOT LIKE 'information_schema'
                 AND   n.nspname NOT LIKE 'cron'
                 AND   n.nspname NOT LIKE 'iam'
                 AND   n.nspname NOT LIKE 'custom'
                 AND   n.nspname NOT LIKE '_timescaledb_%'
                 AND   n.nspname NOT LIKE 'timescaledb_%'
                 AND   n.nspname != 'Models'
                 AND ((n.nspname, t.relname, c.conname) NOT IN (
                    SELECT e.schema, e.name, r.name
                    FROM "Models"."Entity" e, 
                         "Models"."EntityReference" r 
                    WHERE r.container = e.id
                 ) OR c.condeferrable = false) LOOP
        
        -- Borrar índice
        EXECUTE 'ALTER TABLE IF EXISTS "' || index.schemaname || '"."' || index.tablename || '" DROP CONSTRAINT IF EXISTS "' || index.constraintname || '"';
    END LOOP;
    
    -- Borrar índices que ya no estén en el modelo
    FOR index IN SELECT n.nspname AS schemaname, 
                        t.relname AS tablename, 
                        i.relname AS indexname,
                        "in".indisprimary
                 FROM pg_namespace n, 
                      pg_class t, 
                      pg_class i, 
                      pg_index "in" 
                 WHERE n.oid = t.relnamespace 
                 AND   t.oid = "in".indrelid 
                 AND      i.oid = "in".indexrelid 
                 AND   n.nspname NOT LIKE 'pg_%'
                 AND   n.nspname NOT LIKE 'information_schema'
                 AND   n.nspname NOT LIKE 'cron'
                 AND   n.nspname NOT LIKE 'iam'
                 AND   n.nspname NOT LIKE 'custom'
                 AND   n.nspname NOT LIKE '_timescaledb_%'
                 AND   n.nspname NOT LIKE 'timescaledb_%'
                 AND   n.nspname != 'Models'
                 AND (n.nspname, t.relname, i.relname, "in".indisunique OR "in".indisprimary, "in".indisprimary, "in".indnullsnotdistinct, (
                            SELECT array_agg(attname::text) 
                            FROM pg_index, 
                                 pg_attribute 
                            WHERE attnum = ANY(indkey) 
                            AND   attrelid = "in".indrelid
                            AND   indexrelid = "in".indexrelid
                        )
                 ) NOT IN (
                    SELECT e.schema, e.name, k.name, k."isUnique" OR k."isPrimaryKey", k."isPrimaryKey", k."isNullsNotDistinct", (
                        SELECT array_agg(a.name) 
                        FROM "Models"."EntityAttribute" a, 
                             "Models"."EntityKeyAttribute" eka 
                        WHERE eka.container = k.id 
                        AND   eka.attribute = a.id
                    )  
                    FROM "Models"."Entity" e, 
                         "Models"."EntityKey" k 
                    WHERE k.container = e.id
                 ) LOOP
        
        -- Borrar índice
        RAISE WARNING 'dropping index "%"."%"', index.schemaname, index.indexname;
        IF (index.indisprimary) THEN
            EXECUTE 'ALTER TABLE IF EXISTS "' || index.schemaname || '"."' || index.tablename || '" DROP CONSTRAINT IF EXISTS "' || index.indexname || '"';
        ELSE
            EXECUTE 'DROP INDEX "' || index.schemaname || '"."' || index.indexname || '"';
        END IF;
    END LOOP;
    
    -- Borrar tablas que ya no estén en el modelo
    FOR entity IN SELECT c.oid, n.nspname, c.relname 
            FROM pg_class c, 
                 pg_namespace n 
            WHERE c.relnamespace = n.oid
            AND   c.relkind = 'r'
            AND   n.nspname != 'Models'
            AND   n.nspname NOT LIKE 'pg_%'
            AND   n.nspname NOT LIKE 'information_schema'
            AND   n.nspname NOT LIKE 'cron'
            AND   n.nspname NOT LIKE 'iam'
            AND   n.nspname NOT LIKE 'custom'
            AND   n.nspname NOT LIKE '_timescaledb_%'
            AND   n.nspname NOT LIKE 'timescaledb_%'
            AND   c.oid NOT IN (
                    SELECT e.oid 
                    FROM "Models"."Entity" e 
                    WHERE e.oid IS NOT NULL) LOOP
        BEGIN
            -- Borrar tabla
            EXECUTE 'DROP TABLE "' || entity."nspname" || '"."' || entity."relname" || '"';
        EXCEPTION
            WHEN dependent_objects_still_exist THEN
                RAISE NOTICE 'cannot drop table "%"."%" because other objects depend on it, skipping', entity."nspname", entity."relname";
        END;
    END LOOP;
    
    -- Borrar campos que ya no estén en el modelo
    FOR attribute IN SELECT n.nspname, c.relname, a.attname 
            FROM pg_namespace n, 
                 pg_class c, 
                 pg_attribute a 
            WHERE c.relnamespace = n.oid 
            AND   a.attrelid = c.oid 
            AND   a.atttypid != 0
            AND   n.nspname != 'Models' 
            AND   n.nspname NOT LIKE 'pg_%'
            AND   n.nspname NOT LIKE 'information_schema'
            AND   n.nspname NOT LIKE 'cron'
            AND   n.nspname NOT LIKE 'iam'
            AND   n.nspname NOT LIKE 'custom'
            AND   n.nspname NOT LIKE '_timescaledb_%'
            AND   n.nspname NOT LIKE 'timescaledb_%'
            AND   c.relkind = 'r' 
            AND   a.attnum > 0 
            AND   (c.oid, a.attnum) NOT IN (
                    SELECT e.oid, ea.attnum 
                    FROM "Models"."Entity" e, 
                         "Models"."EntityAttribute" ea 
                    WHERE ea.container = e."id" 
                    AND   e.oid IS NOT NULL 
                    AND   ea.attnum IS NOT NULL
            ) LOOP
        
        -- Borrar campo
        EXECUTE 'ALTER TABLE IF EXISTS "' || attribute.nspname || '"."' || attribute.relname || '" DROP COLUMN "' || attribute.attname || '" CASCADE';
    END LOOP;
    
    -- Borrar tipos enumerados que ya no estén en el modelo
    FOR enumType IN SELECT t.oid, n.nspname, t.typname 
            FROM pg_type t, 
                 pg_namespace n 
            WHERE t.typnamespace = n.oid 
            AND   t.typtype = 'e' 
            AND   t.typcategory = 'E'
            AND   n.nspname != 'Models' 
            AND   n.nspname NOT LIKE 'pg_%'
            AND   n.nspname NOT LIKE 'information_schema'
            AND   n.nspname NOT LIKE 'cron'
            AND   n.nspname NOT LIKE 'iam'
            AND   n.nspname NOT LIKE 'custom'
            AND   n.nspname NOT LIKE '_timescaledb_%'
            AND   n.nspname NOT LIKE 'timescaledb_%'
            AND   t.oid NOT IN (
                    SELECT et.oid 
                    FROM "Models"."EnumType" et 
                    WHERE et.oid IS NOT NULL) LOOP
        BEGIN
            -- Borrar tipo enumerado
            EXECUTE 'DROP TYPE "' || enumType."nspname" || '"."' || enumType."typname" || '"';
        EXCEPTION
            WHEN dependent_objects_still_exist THEN
                RAISE NOTICE 'cannot drop type "%"."%" because other objects depend on it, skipping', enumType."nspname", enumType."typname";
        END;
    END LOOP;
    
    -- Borrar tipos enumerados que ya no estén en el modelo
    FOR enumType IN SELECT n.nspname, t.typname 
            FROM pg_namespace n 
            LEFT JOIN pg_type t ON n.oid = t.typnamespace 
            LEFT JOIN "Models"."EnumType" e ON e."schema" = n.nspname AND e."name" = t.typname 
            WHERE t.typtype = 'e' AND n.nspname IN (SELECT "schema" FROM "Models"."EnumType") AND e.id IS NULL LOOP
        
        -- Borrar tipo enumerado
        EXECUTE 'DROP TYPE "' || enumType."nspname" || '"."' || enumType."typname" || '"';
    END LOOP;
    
    -- Crear tipos enumerados nuevos
    FOR enumType IN SELECT * FROM "Models"."EnumType" WHERE "schema" != 'Models' AND "oid" IS NULL LOOP
        
        -- Crear esquema
        EXECUTE 'CREATE SCHEMA IF NOT EXISTS "' || enumType.schema || '"';
        
        -- Crear tipos enumerados
        BEGIN
            sql := 'CREATE TYPE "' || enumType."schema" || '"."' || enumType."name" || '" AS ENUM (';
            i := 0;
            FOREACH value IN ARRAY enumType."values" LOOP
                IF NOT i = 0 THEN
                    sql := sql || ', ';
                END IF;
                sql := sql || '''' || value || '''';
                i := i + 1;
            END LOOP;
            
            sql := sql || ')';
            EXECUTE sql;
            
            -- Asignar oid
            SELECT t.oid INTO STRICT oidValue
                    FROM pg_type t, 
                         pg_namespace n 
                    WHERE t.typtype = 'e' 
                    AND   t.typcategory = 'E'
                    AND   t.typnamespace = n.oid
                    AND   n.nspname = enumType."schema"
                    AND   t.typname = enumType."name";
            
            sql := 'UPDATE "Models"."EnumType" SET "oid" = ' || oidValue || ' WHERE id = ' || enumType."id";
            execute sql;
            
        EXCEPTION
            WHEN duplicate_object THEN
                RAISE NOTICE 'type "%" already exists, skipping', enumType."name";
        END;
    END LOOP;
    
    -- Crear tablas nuevas
    FOR entity IN SELECT DISTINCT e."id", e."language", e."oid", e."schema", e."name" 
            FROM "Models"."Entity" e, 
                 "Models"."EntityAttribute" a,      -- Join con atributos para verificar que tiene al menos un atributo
                 "Models"."EntityKey" k,            -- Join con índices para verificar que tiene al menos la clave primaria
                 "Models"."EntityKeyAttribute" ka   -- Join con atributos del índice para verificar que la clave primaria tiene al menos un atributo
            WHERE e."schema" != 'Models' 
            AND   a."container" = e."id" 
            AND   k."container" = e."id" 
            AND   ka."container" = k."id" 
            AND   k."isPrimaryKey" LOOP
        
        IF entity."oid" IS NULL THEN
            
            -- Crear esquemas
            EXECUTE 'CREATE SCHEMA IF NOT EXISTS "' || entity.schema || '"';
            
            -- Crear tablas
            sql := 'CREATE TABLE IF NOT EXISTS "' || entity."schema" || '"."' || entity."name" || '" (';
            i := 0;
            FOR attribute IN SELECT * FROM "Models"."EntityAttribute" WHERE "container" = entity."id" LOOP
                IF NOT i = 0 THEN
                    sql := sql || ', ';
                END IF;
                
                IF attribute."enumType" IS NOT null THEN
                    SELECT '"' || "schema" || '"."' || "name" || '"' INTO STRICT type FROM "Models"."EnumType" WHERE "id" = attribute."enumType";
                ELSE
                    type := CASE attribute.type WHEN 'TEXT' THEN 'text'
                                                WHEN 'BOOLEAN' THEN 'boolean'
                                                WHEN 'INTEGER' THEN 'integer'
                                                WHEN 'DECIMAL' THEN 
                                                    CASE WHEN attribute.precision IS NULL THEN 'decimal'
                                                         WHEN attribute.scale IS NULL THEN 'decimal(' || attribute.precision || ')'
                                                         ELSE 'decimal(' || attribute.precision || ',' || attribute.scale || ')'
                                                    END
                                                -- WHEN 'MONEY' THEN 'money'
                                                WHEN 'DATE' THEN 'date'
                                                WHEN 'TIMESTAMP' THEN 'timestamp'
                                                -- WHEN 'CUSTOM_TYPE' THEN 'text'
                                                WHEN 'SERIAL' THEN 'serial'
                                                -- WHEN 'BYTEA' THEN 'bytea'
                                                -- WHEN 'SMALLINT' THEN 'smallint'
                                                -- WHEN 'BIGINT' THEN 'bigint'
                                                -- WHEN 'DOUBLE_PRECISION' THEN 'double precision'
                                                -- WHEN 'REAL' THEN 'real'
                                                -- WHEN 'SMALLSERIAL' THEN 'smallserial'
                                                -- WHEN 'BIGSERIAL' THEN 'bigserial'
                                                -- WHEN 'VARCHAR' THEN 
                                                --  CASE WHEN attribute.length IS NULL THEN 'varchar'
                                                --       ELSE 'varchar(' || attribute.length || ')'
                                                --  END
                                                -- WHEN 'CHAR' THEN
                                                --  CASE WHEN attribute.length IS NULL THEN 'char'
                                                --       ELSE 'char(' || attribute.length || ')'
                                                --  END
                                                WHEN 'TIME' THEN 'time'
                                                -- WHEN 'INTERVAL' THEN 'interval'
                                                -- WHEN 'TIMESTAMP_WITH_TIME_ZONE' THEN 'timestamp with time zone'
                                                -- WHEN 'TIME_WITH_TIME_ZONE' THEN 'time with time zone'
                                                WHEN 'POINT' THEN 'point'
                                                -- WHEN 'POLYGON' THEN 'polygon'
                                                WHEN 'DOCUMENT' THEN '"Models"."documentType"'
                                                WHEN 'VECTOR' THEN 'vector(' || attribute.length || ')'
                                                ELSE 'text'
                    END;
                END IF;
                IF attribute."isArray" THEN
                    type := type || '[]';
                END IF;
                
                IF attribute."isRequired" AND attribute."variants" IS NULL THEN
                    type := type || ' NOT NULL';
                END IF;
                
                checkSql := '';
                IF attribute."length" IS NOT NULL AND attribute."type" = 'TEXT' THEN
                    checkSql := ' CHECK (length("' || attribute.name || '"::text) <= ' || attribute."length";
                END IF;
                
                IF attribute."min" IS NOT NULL THEN
                    IF (checkSql = '') THEN
                        checkSql := ' CHECK (';
                    ELSE
                        checkSql := checkSql || ' AND ';
                    END IF;
                    checkSql := checkSql || '"' || attribute.name || '" >= ' || attribute."min";
                END IF;
                
                IF attribute."max" IS NOT NULL THEN
                    IF (checkSql = '') THEN
                        checkSql := ' CHECK (';
                    ELSE
                        checkSql := checkSql || ' AND ';
                    END IF;
                    checkSql := checkSql || '"' || attribute.name || '" <= ' || attribute."max";
                END IF;
                
                IF attribute."step" IS NOT NULL THEN
                    IF (checkSql = '') THEN
                        checkSql := ' CHECK (';
                    ELSE
                        checkSql := checkSql || ' AND ';
                    END IF;
                    checkSql := checkSql || '"' || attribute.name || '"::numeric % ' || attribute."step" || ' = 0';
                END IF;
                
                IF attribute."pattern" IS NOT NULL THEN
                    IF (checkSql = '') THEN
                        checkSql := ' CHECK (';
                    ELSE
                        checkSql := checkSql || ' AND ';
                    END IF;
                    IF attribute."isArray" THEN
                        checkSql := checkSql || '"Models"."similarTo"("' || attribute.name || '", ''' || attribute."pattern" || ''')';
                    ELSE
                        checkSql := checkSql || '"' || attribute.name || '" ~ ''' || attribute."pattern" || '''';
                    END IF;
                END IF;
                
                IF checkSql != '' THEN
                    checkSql := checkSql || ')';
                END IF;
                
                sql := sql || '"' || attribute.name || '" ' || type || checkSql;
                i := i + 1;
            END LOOP;
            
            sql := sql || ')';
            EXECUTE sql;
            
            -- Asignar oid
            SELECT c.oid INTO STRICT oidValue
                    FROM pg_class c, 
                         pg_namespace n 
                    WHERE c.relkind = 'r' 
                    AND   c.relnamespace = n.oid
                    AND   n.nspname = entity."schema"
                    AND   c.relname = entity."name";
            
            sql := 'UPDATE "Models"."Entity" SET "oid" = ' || oidValue || ' WHERE id = ' || entity."id";
            execute sql;
            
            entity."oid" := oidValue;
            
            -- Asignar attnum
            FOR attribute IN SELECT attnum, attname
                    FROM pg_attribute
                    WHERE attrelid = oidValue
                    AND   attnum > 0 LOOP
                    
                sql := 'UPDATE "Models"."EntityAttribute" SET "attnum" = ' || attribute.attnum 
                        || ' WHERE "container" = ' || entity."id"
                        || ' AND "name" = ''' || attribute.attname || '''';
                EXECUTE sql;    
            END LOOP;
        END IF;
        
        -- Crear atributos
        FOR attribute IN SELECT * 
                FROM "Models"."EntityAttribute" 
                WHERE "container" = entity."id" 
                AND "attnum" IS NULL LOOP
            BEGIN
                IF attribute."enumType" IS NOT null THEN
                    SELECT '"' || "schema" || '"."' || "name" || '"' INTO STRICT type FROM "Models"."EnumType" WHERE "id" = attribute."enumType";
                ELSE
                    type := CASE attribute.type WHEN 'TEXT' THEN 'text'
                                                WHEN 'BOOLEAN' THEN 'boolean'
                                                WHEN 'INTEGER' THEN 'integer'
                                                WHEN 'DECIMAL' THEN 
                                                    CASE WHEN attribute.precision IS NULL THEN 'decimal'
                                                         WHEN attribute.scale IS NULL THEN 'decimal(' || attribute.precision || ')'
                                                         ELSE 'decimal(' || attribute.precision || ',' || attribute.scale || ')'
                                                    END
                                                -- WHEN 'MONEY' THEN 'money'
                                                WHEN 'DATE' THEN 'date'
                                                WHEN 'TIMESTAMP' THEN 'timestamp'
                                                -- WHEN 'CUSTOM_TYPE' THEN 'text'
                                                WHEN 'SERIAL' THEN 'serial'
                                                -- WHEN 'BYTEA' THEN 'bytea'
                                                -- WHEN 'SMALLINT' THEN 'smallint'
                                                -- WHEN 'BIGINT' THEN 'bigint'
                                                -- WHEN 'DOUBLE_PRECISION' THEN 'double precision'
                                                -- WHEN 'REAL' THEN 'real'
                                                -- WHEN 'SMALLSERIAL' THEN 'smallserial'
                                                -- WHEN 'BIGSERIAL' THEN 'bigserial'
                                                -- WHEN 'VARCHAR' THEN 
                                                --  CASE WHEN attribute.length IS NULL THEN 'varchar'
                                                --       ELSE 'varchar(' || attribute.length || ')'
                                                --  END
                                                -- WHEN 'CHAR' THEN
                                                --  CASE WHEN attribute.length IS NULL THEN 'char'
                                                --       ELSE 'char(' || attribute.length || ')'
                                                --  END
                                                WHEN 'TIME' THEN 'time'
                                                -- WHEN 'INTERVAL' THEN 'interval'
                                                -- WHEN 'TIMESTAMP_WITH_TIME_ZONE' THEN 'timestamp with time zone'
                                                -- WHEN 'TIME_WITH_TIME_ZONE' THEN 'time with time zone'
                                                WHEN 'POINT' THEN 'point'
                                                -- WHEN 'POLYGON' THEN 'polygon'
                                                WHEN 'DOCUMENT' THEN '"Models"."documentType"'
                                                WHEN 'VECTOR' THEN 'vector(' || attribute.length || ')'
                                                ELSE 'text'
                    END;
                END IF;
                IF attribute."isArray" THEN
                    type := type || '[]';
                END IF;
                IF attribute."isRequired" AND attribute."variants" IS NULL THEN
                    type := type || ' NOT NULL';
                END IF;

                sql := 'ALTER TABLE IF EXISTS "' || entity."schema" || '"."' || entity."name" || '" ADD COLUMN "' || attribute.name || '" ' || type;
                EXECUTE sql;
                
                -- Añadir not null de variantes
                IF attribute."isRequired" AND attribute."variants" IS NOT NULL THEN 
                    sql := 'ALTER TABLE IF EXISTS "' || entity."schema" || '"."' || entity."name" || '" ADD CONSTRAINT "' || attribute."name" || '_required_check" CHECK (TRUE ';
                    
					FOR "variantSelectorAttribute" IN
	                    SELECT ea."name", ea."isArray" FROM "Models"."EntityAttribute" ea WHERE ea.container = attribute."container" AND ea."isVariantSelector" = TRUE
		            LOOP
                    	sql := sql || 'AND ("' || "variantSelectorAttribute".name || '" IS NULL OR NOT (' || CASE "variantSelectorAttribute"."isArray" WHEN true THEN ('string_to_array(array_to_string("' || "variantSelectorAttribute".name || '", '',''), '','') && ARRAY[''' || array_to_string(attribute."variants", ''',''') || ''']') ELSE ('"' || "variantSelectorAttribute".name || '" || '''' = any(ARRAY[''' || array_to_string(attribute."variants", ''',''') || '''])') END || '))';
					END LOOP;
					sql := sql || ' OR "' || attribute."name" || '" IS NOT NULL)';
                    EXECUTE sql;
                END IF;
                
                -- Asignar attnum
                SELECT attnum INTO STRICT attnumValue
                        FROM pg_attribute
                        WHERE attrelid = entity."oid"
                        AND   attname = attribute.name;
                        
                sql := 'UPDATE "Models"."EntityAttribute" SET "attnum" = ' || attnumValue 
                        || ' WHERE "container" = ' || entity."id"
                        || ' AND "name" = ''' || attribute.name || '''';
                EXECUTE sql;    
            EXCEPTION
                WHEN duplicate_column THEN
                    RAISE NOTICE 'column "%" of relation "%" already exists, skipping', attribute."name", entity."name";
            END;
        END LOOP;
        
        -- Crear índices nuevos
        FOR index IN SELECT * FROM "Models"."EntityKey" WHERE "container" = entity."id" LOOP
            BEGIN
                str := '';
                IF index."isUnique" OR index."isPrimaryKey" THEN 
                    str := ' UNIQUE';
                END IF;
                IF index."isTextSearch" THEN
                    str2 := ' USING gin(to_tsvector(''' || CASE entity."language" WHEN 'da' THEN 'danish' WHEN 'nl' THEN 'dutch' WHEN 'en_GB' THEN 'english' WHEN 'en_US' THEN 'english' WHEN 'fi' THEN 'finnish' WHEN 'fr_CA' THEN 'french' WHEN 'fr_FR' THEN 'french' WHEN 'de' THEN 'german' WHEN 'it' THEN 'italian' WHEN 'no' THEN 'norwegian' WHEN 'pt_BR' THEN 'portuguese' WHEN 'pt_PT' THEN 'portuguese' WHEN 'ro' THEN 'romanian' WHEN 'ru' THEN 'russian' WHEN 'es_419' THEN 'spanish' WHEN 'es_ES' THEN 'spanish' WHEN 'sv' THEN 'swedish' WHEN 'tr' THEN 'turkish' ELSE 'english' END || ''', ';
                    str3 := '))';
                ELSE
                    str2 := ' (';
                    str3 := ')';
                END IF;
                
                sql := 'CREATE' || str || ' INDEX IF NOT EXISTS "' || index."name" || '" ON "' || entity."schema" || '"."' || entity."name" || '"' || str2;
    
                i := 0;
                FOR attribute IN SELECT ea."name" FROM "Models"."EntityKeyAttribute" eka, "Models"."EntityAttribute" ea WHERE eka."container" = index."id" AND eka."attribute" = ea."id" LOOP
                    IF NOT i = 0 THEN
                        sql := sql || ', ';
                    END IF;
                    sql := sql || '"' || attribute.name || '"';
                    i := i + 1;
                END LOOP;
                
                sql := sql || str3;

                IF index."isNullsNotDistinct" THEN
                    sql := sql || ' NULLS NOT DISTINCT';
                END IF;
    
                IF i > 0 THEN
                    EXECUTE sql;
        
                    IF index."isPrimaryKey" THEN 
                        BEGIN
                            sql := 'ALTER TABLE IF EXISTS "' || entity."schema" || '"."' || entity."name" || '" ADD PRIMARY KEY USING INDEX "' || index."name" || '"';
                            EXECUTE sql;
                        EXCEPTION
                            WHEN object_not_in_prerequisite_state THEN
                                RAISE NOTICE 'index "%" is already associated with a constraint, skipping', index."name";
                        END;
                    END IF;
                END IF;
            EXCEPTION
                WHEN invalid_table_definition THEN
                    RAISE NOTICE 'multiple primary keys for table "%" are not allowed, skipping', entity."name";
            END;
        END LOOP;
    END LOOP;
    
    -- Crear constraints nuevas (references)
    FOR entity IN SELECT DISTINCT e."id", e."schema", e."name" FROM "Models"."Entity" e, "Models"."EntityAttribute" a WHERE e."schema" != 'Models' AND a."container" = e."id" LOOP
        -- Crear constraints nuevas
        FOR reference IN SELECT r."id", k."id" AS "referencedKeyId", r."name", r."isCascadeDelete", r."isCascadeSetNull", re."name" AS "referencedTableName", re."schema" AS "referencedTableSchema"
                FROM "Models"."EntityReference" r, 
                     "Models"."EntityKey" k,
                     "Models"."Entity" re
                WHERE k."id" = r."referencedKey" 
                AND k."container" = re."id"
                AND r."container" = entity."id" LOOP

            BEGIN
                attributesStr := '';
                i := 0;         
                FOR attribute IN SELECT ea."name"
                        FROM "Models"."EntityReferenceAttribute" era, 
                             "Models"."EntityAttribute" ea
                        WHERE era."attribute" = ea."id"
                        AND era."container" = reference."id" LOOP
                    IF NOT i = 0 THEN
                        attributesStr := attributesStr || ', ';
                    END IF;
                    attributesStr := attributesStr || '"' || attribute.name || '"';
                    i := i + 1;
                END LOOP;
                
                referencedAttributesStr := '';
                i := 0;         
                FOR attribute IN SELECT ea."name"
                        FROM "Models"."EntityKeyAttribute" eka, 
                             "Models"."EntityAttribute" ea
                        WHERE eka."attribute" = ea."id"
                        AND eka."container" = reference."referencedKeyId" LOOP
                    IF NOT i = 0 THEN
                        referencedAttributesStr := referencedAttributesStr || ', ';
                    END IF;
                    referencedAttributesStr := referencedAttributesStr || '"' || attribute.name || '"';
                    i := i + 1;
                END LOOP;
                
                IF attributesStr != '' AND referencedAttributesStr != '' THEN
                    sql := 'ALTER TABLE IF EXISTS "' || entity."schema" || '"."' || entity."name" || '" ADD CONSTRAINT "' || reference."name" || '" FOREIGN KEY (' || attributesStr || ') REFERENCES "' || reference."referencedTableSchema" || '"."' || reference."referencedTableName" || '"(' || referencedAttributesStr || ')';
                    IF reference."isCascadeDelete" THEN
                        sql := sql || ' ON DELETE CASCADE';
                    ELSIF reference."isCascadeSetNull" THEN
                        sql := sql || ' ON DELETE SET NULL';
                    END IF;
                    sql := sql || ' DEFERRABLE INITIALLY IMMEDIATE';
                    EXECUTE sql;
                END IF;
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE NOTICE 'constraint "%" for relation "%" already exists, skipping', reference."name", entity."name";
            END;
        END LOOP;
    END LOOP;
    
    -- Borrar roles (roles y usuarios) que ya no estén en el modelo
    FOR role IN SELECT rolname 
            FROM pg_roles 
            WHERE rolname NOT LIKE 'pg_%' 
            AND rolname != 'postgres' 
            AND rolname != 'anonymous'
            AND rolname NOT IN (SELECT name FROM "Models"."Role") 
            AND rolname NOT IN (SELECT username FROM "Models"."User") LOOP
        
        BEGIN
            -- Borrar rol
            EXECUTE 'DROP OWNED BY "' || role.rolname || '"';
            EXECUTE 'DROP ROLE "' || role.rolname || '"';
        EXCEPTION
            WHEN dependent_objects_still_exist THEN
                RAISE NOTICE 'role "%" cannot be dropped because some objects depend on it, skipping', role.rolname;
        END;            
    END LOOP;
    
    -- Crear roles nuevos
    FOR role IN SELECT name, id
            FROM "Models"."Role" 
            WHERE name NOT IN (SELECT rolname FROM pg_roles)
            AND oid IS NULL LOOP
        
        -- Crear rol
        EXECUTE 'CREATE ROLE "' || role.name || '"';
        
        -- Asignar oid
        SELECT r.oid INTO STRICT oidValue
                FROM pg_roles r
                WHERE r.rolname = role."name";
        
        sql := 'UPDATE "Models"."Role" SET "oid" = ' || oidValue || ' WHERE id = ' || role."id";
        execute sql;
    END LOOP;
    
    -- Crear usuarios nuevos
    FOR "user" IN SELECT "username", "password", "id", "isAdmin"
            FROM "Models"."User" 
            WHERE "username" NOT IN (SELECT "rolname" FROM "pg_roles") 
            AND oid IS NULL LOOP
        
        -- Crear usuario
        EXECUTE 'CREATE ROLE "' || "user"."username" || '" PASSWORD ''' || "user"."password" || '''' || CASE WHEN "user"."isAdmin" THEN ' SUPERUSER' ELSE ' NOSUPERUSER' END;
        
        -- Asignar oid
        SELECT r.oid INTO STRICT oidValue
                FROM pg_roles r
                WHERE r.rolname = "user"."username";
        
        sql := 'UPDATE "Models"."User" SET "oid" = ' || oidValue || ' WHERE id = ' || "user"."id";
        execute sql;
    END LOOP;
    
    -- Desasignar roles
    FOR "record" IN SELECT u.username AS "username", r.rolname AS "role"
            FROM pg_auth_members am,
                 pg_roles r,
                 "Models"."User" u
            WHERE am.member = u.oid
            AND   am.roleid = r.oid
            AND   u.username != 'modelsadmin'
            AND NOT EXISTS (
                SELECT u2.username, r2.name
                FROM "Models"."UserRole" ur,
                     "Models"."User" u2,
                     "Models"."Role" r2
                WHERE ur."user" = u2.id
                AND ur."role" = r2.id
                AND u2.username = u.username
                AND r2.name = r.rolname
            ) LOOP
        sql := 'REVOKE "' || "record"."role" || '" FROM "' || "record"."username" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Asignar roles
    FOR "record" IN SELECT u."username" AS "user", r."name" AS "role" 
            FROM "Models"."UserRole" ur,
                 "Models"."User" u,
                 "Models"."Role" r
            WHERE u.id = ur."user"
            AND   r.id = ur."role" LOOP 
        
        -- Asignar rol
        EXECUTE 'GRANT "' || "record"."role" || '" TO "' || "record"."user" || '"';
    END LOOP;
    
    -- Revocar permisos de tablas
    FOR "record" IN SELECT tp.grantee, tp.table_schema, tp.table_name, tp.privilege_type 
            FROM information_schema.table_privileges tp,
                 "Models"."Entity" e
            WHERE tp.table_schema = e."schema"
            AND   tp.table_name = e."name"
            AND   tp.grantee != 'postgres'
            AND (grantee, table_schema, table_name, privilege_type) NOT IN (
                SELECT r."name", e2."schema", e2."name", unnest(ep.types)::text 
                FROM "Models"."EntityPermission" ep, 
                     "Models"."Role" r, 
                     "Models"."Entity" e2 
                WHERE ep."role" = r."id" 
                AND   ep."entity" = e."id") LOOP
    
        sql := 'REVOKE ' || "record"."privilege_type" || ' ON "' || "record"."table_schema" || '"."' || "record"."table_name" || '" FROM "' || "record"."grantee" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Conceder permisos de tablas
    FOR "record" IN SELECT e."schema", e."name", array_remove(p."types", 'MENU') AS "types", r."name" AS "role" 
            FROM "Models"."EntityPermission" p, 
                 "Models"."Entity" e, 
                 "Models"."Role" r 
            WHERE p."role" = r."id" 
            AND   p."entity" = e."id" 
            AND   array_length(array_remove(p."types", 'MENU'), 1) >= 0 LOOP
            
        -- Conceder permiso
        EXECUTE 'GRANT USAGE ON SCHEMA "' || "record"."schema" || '" TO "' || "record"."role" || '"';
        EXECUTE 'GRANT USAGE ON ALL SEQUENCES IN SCHEMA "' || "record"."schema" || '" TO "' || "record"."role" || '"';
        sql := 'GRANT ' || array_to_string("record"."types", ',') || ' ON "' || "record"."schema" || '"."' || "record"."name" || '" TO "' || "record"."role" || '"';
        EXECUTE sql;
    END LOOP;

    -- Revocar permisos de columnas
    FOR "record" IN SELECT cp.grantee, cp.table_schema, cp.table_name, cp.column_name, cp.privilege_type 
            FROM information_schema.column_privileges cp,
                 "Models"."Entity" e,
                 "Models"."EntityAttribute" ea
        WHERE ea.container = e.id
            AND   cp.table_schema = e."schema"
            AND   cp.table_name = e."name"
            AND   cp.column_name = ea."name"
            AND   cp.grantee != 'postgres'
            AND (grantee, table_schema, table_name, column_name, privilege_type) NOT IN (
                SELECT r."name", e2."schema", e2."name", ea2.name, unnest(eap.types)::text 
                FROM "Models"."EntityAttributePermission" eap, 
                     "Models"."Role" r, 
                     "Models"."Entity" e2,
                     "Models"."EntityAttribute" ea2
                WHERE eap."role" = r."id" 
                AND   eap."attribute" = ea2."id"
                AND   ea2."container" = e2."id")
            AND (grantee, table_schema, table_name, privilege_type) NOT IN (
                SELECT r."name", e2."schema", e2."name", unnest(ep.types)::text 
                FROM "Models"."EntityPermission" ep, 
                     "Models"."Role" r, 
                     "Models"."Entity" e2 
                WHERE ep."role" = r."id" 
                AND   ep."entity" = e2."id") LOOP
    
        sql := 'REVOKE ' || "record"."privilege_type" || '("' || "record"."column_name" || '") ON "' || "record"."table_schema" || '"."' || "record"."table_name" || '" FROM "' || "record"."grantee" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Conceder permisos de columnas
    FOR "record" IN SELECT e."schema", e."name", a."name" AS "attributeName", unnest(p."types") AS "types", r."name" AS "role" 
            FROM "Models"."EntityAttributePermission" p, 
                 "Models"."EntityAttribute" a, 
                 "Models"."Entity" e, 
                 "Models"."Role" r 
            WHERE p."role" = r."id" 
            AND   p."attribute" = a."id"
            AND   a."container" = e."id" LOOP
            
        -- Conceder permiso
        EXECUTE 'GRANT USAGE ON SCHEMA "' || "record"."schema" || '" TO "' || "record"."role" || '"';
        EXECUTE 'GRANT USAGE ON ALL SEQUENCES IN SCHEMA "' || "record"."schema" || '" TO "' || "record"."role" || '"';
        sql := 'GRANT ' || "record"."types" || '("' || "record"."attributeName" || '") ON "' || "record"."schema" || '"."' || "record"."name" || '" TO "' || "record"."role" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Elimitar reglas de row level security (todas porque al crearlas postgresql le cambia el aspecto a las expresiones, les añade casting, ...) y
    --   no podemos saber con seguridad cuál ya no tiene que estar o si ha cambiado o no. Las borramos todas y las volvemos a crear.
    FOR "record" IN SELECT schemaname, 
                           tablename, 
                           policyname
            FROM pg_policies 
            WHERE schemaname != 'cron' LOOP
        
        sql := 'ALTER TABLE IF EXISTS "' || "record"."schemaname" || '"."' || "record"."tablename" || '" DISABLE ROW LEVEL SECURITY';
        EXECUTE sql;
        
        sql := 'DROP POLICY "' || "record"."policyname" || '" ON "' || "record"."schemaname" || '"."' || "record"."tablename" || '"';
        EXECUTE sql;
    END LOOP;
    
    -- Añadir reglas de row level security
    FOR "record" IN SELECT e."schema", e."name" AS tablename, rlp."name", rlp.as, rlp.for, r.name AS "role", rlp.expression, rlp."checkExpression" 
            FROM "Models"."RowLevelPermission" rlp, 
                 "Models"."Entity" e, 
                 "Models"."Role" r 
            WHERE rlp."role" = r."id" 
            AND   rlp."entity" = e."id" LOOP
            
        -- Conceder permiso
        EXECUTE 'ALTER TABLE IF EXISTS "' || "record"."schema" || '"."' || "record"."tablename" || '" ENABLE ROW LEVEL SECURITY';
        sql := 'CREATE POLICY "' || "record".name || '" ON "' || "record"."schema" || '"."' || "record"."tablename" || '" AS ' || "record"."as" || ' FOR ' || "record"."for";
        IF "record".role is not null THEN
            sql := sql || ' TO "' || "record".role || '"';
        END IF;
        IF "record".expression is not null THEN
            sql := sql || ' USING (' || "record".expression || ')';
        END IF;
        IF "record"."checkExpression" is not null THEN
            sql := sql || ' WITH CHECK (' || "record"."checkExpression" || ')';
        END IF;
        EXECUTE sql;
    END LOOP;
    
    -- Borrar funciones que ya no están
    FOR "record" IN SELECT n.nspname, p.proname 
            FROM pg_proc p, 
                 pg_namespace n 
            WHERE p.pronamespace = n.oid 
            AND   n.nspname NOT LIKE 'pg_%'
            AND   n.nspname NOT LIKE 'information_schema'
            AND   n.nspname NOT LIKE 'cron'
            AND   n.nspname NOT LIKE 'iam'
            AND   n.nspname NOT LIKE 'custom'
            AND   n.nspname != 'public' 
            AND   n.nspname NOT LIKE '_timescaledb_%'
            AND   n.nspname NOT LIKE 'timescaledb_%'
            AND   n.nspname != 'Models'
            AND   (n.nspname, p.proname) 
                    NOT IN (SELECT schema, name FROM "Models"."Function") LOOP
        
        -- Borrar función
        EXECUTE 'DROP FUNCTION IF EXISTS "' || record.nspname || '"."' || record.proname || '" CASCADE';                          
    END LOOP;
    
    -- Borrar schedules que ya no se necesitan
    FOR job IN SELECT jobid
            FROM cron.job
            WHERE jobid NOT IN (SELECT jobid FROM "Models"."Function" WHERE jobid IS NOT NULL) LOOP
        EXECUTE 'SELECT cron.unschedule(' || job.jobid || ')';
    END LOOP;
    
    -- Crear o actualizar funciones
    FOR function IN SELECT id, schema, name, language, contents, "cronExpression", jobid, "isCustomFunction", "customParameters", "customReturnType"
            FROM "Models"."Function" LOOP
        BEGIN
            -- Crear esquema
            EXECUTE 'CREATE SCHEMA IF NOT EXISTS "' || function.schema || '"';
            
            IF function.language = 'ECMAScriptNashorn' THEN
                EXECUTE 'CREATE OR REPLACE FUNCTION "' || function.schema || '"."' || function.name || '"() RETURNS trigger AS $func$DECLARE id integer;BEGIN IF (TG_OP = ''DELETE'') THEN id := old.id; ELSE id := new.id; END IF; PERFORM pg_notify(''' || function.schema || '.' || function.name || ''', TG_OP || ''.'' || id || ''.'' || current_user); IF (TG_OP = ''UPDATE'' OR TG_OP = ''INSERT'') THEN RETURN new; ELSE RETURN old; END IF; END;$func$ LANGUAGE plpgsql';
            ELSE
                IF function."cronExpression" IS NOT NULL THEN
                    EXECUTE 'CREATE OR REPLACE FUNCTION "' || function.schema || '"."' || function.name || '"() RETURNS void AS $func$' || function.contents || '$func$ LANGUAGE ' || function.language;
                ELSIF function."isCustomFunction" THEN
                    EXECUTE 'CREATE OR REPLACE FUNCTION "' || function.schema || '"."' || function.name || '"(' || CASE function."customParameters" IS NULL WHEN TRUE THEN '' ELSE function."customParameters" END ||  ')' || CASE function."customReturnType" IS NULL WHEN TRUE THEN '' ELSE ' RETURNS ' || function."customReturnType" END || ' AS $func$' || function.contents || '$func$ LANGUAGE ' || function.language;
                ELSE
                    EXECUTE 'CREATE OR REPLACE FUNCTION "' || function.schema || '"."' || function.name || '"() RETURNS trigger AS $func$' || function.contents || '$func$ LANGUAGE ' || function.language;
                END IF;
            END IF;
            
            IF function.jobid IS NOT NULL THEN
                EXECUTE 'SELECT cron.unschedule(' || function.jobid || ')';
                EXECUTE 'UPDATE "Models"."Function" SET jobid = null WHERE id = ' || function.id;
            END IF;
            
            IF function."cronExpression" IS NOT NULL THEN
                IF function.language = 'ECMAScriptNashorn' THEN
                    EXECUTE 'SELECT cron.schedule(''' || function."cronExpression" || ''', $command$SELECT pg_notify(''' || function.schema || '.' || function.name || ''', '''')$command$)' INTO STRICT job;
                    EXECUTE 'UPDATE "Models"."Function" SET jobid = ' || job || ' WHERE id = ' || function.id;
                ELSE
                    EXECUTE 'SELECT cron.schedule(''' || function."cronExpression" || ''', $command$SELECT "' || function.schema || '"."' || function.name || '"()$command$)' INTO STRICT job;
                    EXECUTE 'UPDATE "Models"."Function" SET jobid = ' || job || ' WHERE id = ' || function.id;
                END IF;
            END IF;
        EXCEPTION
            WHEN duplicate_object THEN
                RAISE NOTICE 'constraint "%" for relation "%" already exists, skipping', reference."name", entity."name";
        END;
    END LOOP;
    
    -- Re-crear triggers nuevos (se pueden haber borrado por ejemplo si se cambia el nombre a una función existente)
    FOR "record" IN SELECT et."id", et."container", et."name", et."moment", et."events", et."each", et."function", et."condition"
            FROM "Models"."EntityTrigger" et LOOP
        SELECT '"' || "schema" || '"."' || "name" || '"' INTO STRICT tablename2 FROM "Models"."Entity" WHERE "id" = "record"."container";
        SELECT '"' || "schema" || '"."' || "name" || '"' INTO STRICT functionname FROM "Models"."Function" WHERE "id" = "record"."function";
        moment := CASE "record"."moment" WHEN 'BEFORE' THEN 'BEFORE'
                                    WHEN 'AFTER' THEN 'AFTER'
                                    WHEN 'INSTEAD_OF' THEN 'INSTEAD OF'
        END;
        count := 0;
        events := '';
        FOREACH event IN ARRAY "record"."events" LOOP
            IF count > 0 THEN
                events := events || ' OR ';
            END IF;
            events := events || event;
            count := count + 1;
        END LOOP;
        IF "record"."condition" IS NOT NULL THEN
            condition := ' WHEN ' || "record"."condition";
        ELSE
            condition := '';
        END IF;
        BEGIN
            sql := 'CREATE TRIGGER "' || "record"."name" || '" ' || moment || ' ' || events || ' ON ' || tablename2 || ' FOR EACH ' || "record"."each" || condition || ' EXECUTE PROCEDURE ' || functionname || '()';
            EXECUTE sql;
        EXCEPTION
            WHEN duplicate_object THEN
                RAISE NOTICE 'trigger "%" already exists, skipping', "record"."name";
        END;
    END LOOP;
    
    -- Borrar triggers de borrado de large blobs (las funciones ya se han borrado más arriba)
    FOR entity IN SELECT "id", "schema", "name" 
            FROM "Models"."Entity" LOOP
        
        sql := 'DROP TRIGGER IF EXISTS delete_large_blob ON "' || entity."schema" || '"."' || entity."name" || '"';
        execute sql;
    END LOOP;
    
    FOR entity IN SELECT "id", "schema", "name" 
            FROM "Models"."Entity" 
            WHERE id IN (
                SELECT DISTINCT ea."container" 
                FROM "Models"."EntityAttribute" ea 
                WHERE ea.type = 'DOCUMENT'
            ) LOOP
        
        sql := 'CREATE OR REPLACE FUNCTION "' || entity."schema" || '"."' || entity."name" || '_delete_large_blob"() RETURNS trigger AS $func$ ';
        sql := sql || 'begin ';
        
        FOR attribute IN SELECT ea."name"
                FROM "Models"."EntityAttribute" ea
                WHERE ea."container" = entity.id
                AND   ea."type" = 'DOCUMENT' LOOP
            
            sql := sql || '  IF (old."' || attribute.name || '").oid is not null and (new."' || attribute.name || '").oid is null or (old."' || attribute.name || '").oid != (new."' || attribute.name || '").oid THEN ';
            sql := sql || '    RESET ROLE; ';
            sql := sql || '    BEGIN ';
            sql := sql || '      EXECUTE ''SELECT lo_unlink('' || (old."' || attribute.name || '").oid || '')''; ';
            sql := sql || '    EXCEPTION ';
            sql := sql || '      WHEN others THEN ';
            sql := sql || '        RAISE NOTICE ''cannot lo_unlink''; ';
            sql := sql || '    END; ';
            sql := sql || '  END IF; ';
        END LOOP;
        
        sql := sql || '  return new; ';
        sql := sql || 'end ';
        sql := sql || '$func$ LANGUAGE plpgsql';
        EXECUTE sql;
        
        sql := 'CREATE TRIGGER delete_large_blob AFTER UPDATE OR DELETE ON "' || entity."schema" || '"."' || entity."name" || '" FOR EACH ROW EXECUTE PROCEDURE "' || entity."schema" || '"."' || entity."name" || '_delete_large_blob"()';
        EXECUTE sql;
    END LOOP;
    
    -- Borrar triggers de generación de informes
    FOR entity IN SELECT "id", "schema", "name" 
            FROM "Models"."Entity" LOOP
        
        sql := 'DROP TRIGGER IF EXISTS generate_report ON "' || entity."schema" || '"."' || entity."name" || '"';
        execute sql;
    END LOOP;
    
    FOR entity IN SELECT "id", "schema", "name" 
            FROM "Models"."Entity" 
            WHERE id IN (
                SELECT DISTINCT "triggerEntity"
                FROM "Models"."ReportTrigger"
            ) LOOP
        sql := 'CREATE TRIGGER generate_report AFTER INSERT OR UPDATE ON "' || entity."schema" || '"."' || entity."name" || '" FOR EACH ROW EXECUTE FUNCTION "Models"."report_generate"()';
        EXECUTE sql;
    END LOOP;
    
    RETURN result;
END;
$function$
;
