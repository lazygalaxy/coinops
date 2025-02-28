//reference files
CREATE OR REPLACE TABLE REF_MAME_2003_XML(src VARIANT);

COPY INTO REF_MAME_2003_XML
FROM @RAWFILES/reference_mame2003
FILE_FORMAT=(TYPE=XML);

SELECT * from REF_MAME_2003_XML;

CREATE OR REPLACE TABLE REF_MAME_2003_FLAT AS
SELECT
SRC:"@name"::STRING AS name,
XMLGET( SRC, 'description' ):"$"::STRING AS description,
XMLGET( SRC, 'year' ):"$"::STRING AS year,
XMLGET( SRC, 'input' ):"@players"::STRING AS players,
XMLGET( SRC, 'input' ):"@control"::STRING AS ctrltype,
XMLGET( SRC, 'input' ):"@buttons"::STRING AS buttons,
XMLGET( SRC, 'video' ):"@orientation"::STRING AS orientation,
XMLGET( SRC, 'manufacturer' ):"$"::STRING AS manufacturer
FROM REF_MAME_2003_XML;

SELECT * FROM REF_MAME_2003_FLAT;


//reference files
CREATE OR REPLACE TABLE REF_MAME_274_XML(src VARIANT);

COPY INTO REF_MAME_274_XML
FROM @RAWFILES/reference_mame274
FILE_FORMAT=(TYPE=XML);

SELECT * from REF_MAME_274_XML;

CREATE OR REPLACE TABLE REF_MAME_274_FLAT AS
SELECT
SRC:"@name"::STRING AS name,
XMLGET( SRC, 'description' ):"$"::STRING AS description,
XMLGET( SRC, 'year' ):"$"::STRING AS year,
XMLGET( SRC, 'input' ):"@players"::STRING AS players,
XMLGET( SRC, 'input' ):"@coins"::STRING AS coins,
CASE 
    WHEN XMLGET( XMLGET( SRC, 'input' ), 'control',0 ):"@type" <> XMLGET( XMLGET( SRC, 'input' ), 'control',1 ):"@type"
    THEN XMLGET( XMLGET( SRC, 'input' ), 'control',0 ):"@type" || COALESCE('+' || XMLGET( XMLGET( SRC, 'input' ), 'control',1 ):"@type", '') 
    ELSE XMLGET( XMLGET( SRC, 'input' ), 'control',0 ):"@type" 
END::STRING AS type,
COALESCE(XMLGET( XMLGET( SRC, 'input' ), 'control',0 ):"@buttons",XMLGET( XMLGET( SRC, 'input' ), 'control',1 ):"@buttons")::STRING AS buttons,
COALESCE(XMLGET( XMLGET( SRC, 'input' ), 'control',0 ):"@ways",XMLGET( XMLGET( SRC, 'input' ), 'control',1 ):"@ways")::STRING AS ways,
XMLGET( SRC, 'display' ):"@rotate"::STRING AS rotate,
XMLGET( SRC, 'manufacturer' ):"$"::STRING AS manufacturer
FROM REF_MAME_274_XML;

SELECT * FROM REF_MAME_274_FLAT;


//coinops files
--------------------------------------------------------------
CREATE OR REPLACE TABLE COINOPS_MAME_XML(src VARIANT);

COPY INTO COINOPS_MAME_XML
FROM @RAWFILES/coinops_deluxe_max_modify_MAME.xml
FILE_FORMAT=(TYPE=XML);

SELECT * from COINOPS_MAME_XML;

CREATE OR REPLACE TABLE COINOPS_MAME_FLAT AS
SELECT
SRC:"@name"::STRING AS name,
XMLGET( SRC, 'description' ):"$"::STRING AS description,
XMLGET( SRC, 'year' ):"$"::STRING AS year,
XMLGET( SRC, 'players' ):"$"::STRING AS players,
XMLGET( SRC, 'ctrltype' ):"$"::STRING AS ctrltype,
XMLGET( SRC, 'manufacturer' ):"$"::STRING AS manufacturer
FROM COINOPS_MAME_XML;

//some general select quesry only for games, exlcuding other things
SELECT * FROM COINOPS_MAME_FLAT WHERE YEAR NOT IN ('Swap','theme') ORDER by NAME;

//find duplicates in the file
SELECT name, count(name) as count from COINOPS_MAME_FLAT group by name order by count desc;
--------------------------------------------------------------

CREATE OR REPLACE TABLE COINOPS_DELUXE_MAX_ROMS(
FILE        VARCHAR2 (100)   NOT NULL,
CATEGORY        VARCHAR2 (10)   NOT NULL,
DEFAULT          VARCHAR2 (5)   NOT NULL
);

COPY INTO COINOPS_DELUXE_MAX_ROMS
FROM @RAWFILES/coinops_deluxe_max_roms.csv
FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = ',' FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 1);

SELECT * from COINOPS_DELUXE_MAX_ROMS order by file asc;

--------------------------------------------------------------

// Removed 3 duplicates, star force, Mortal Kombat 1 and 1080 Avalanche
// Added Doom, 4 player games and 2 player Centipede


//join stuff
--------------------------------------------------------------
// make sure that all actual roms match with something in the coinops mame.xml and there are no duplicates
SELECT r.*,c.*
FROM COINOPS_DELUXE_MAX_ROMS AS r LEFT OUTER JOIN COINOPS_MAME_FLAT AS c
ON r.file = c.name
WHERE c.name is null
ORDER BY NAME;

// full gamelist 974 roms in Deluxe Max
SELECT c.name,c.description,c.year,c.players,c.ctrltype,c.manufacturer,r.category,r.default
FROM COINOPS_DELUXE_MAX_ROMS AS r LEFT OUTER JOIN COINOPS_MAME_FLAT AS c
ON c.name = r.file
ORDER BY NAME;

//join extra fields from mame into coinops
SELECT c.name,c.description,c.year,c.players,c.ctrltype,m.ways,m.type,m.buttons,m.rotate
FROM COINOPS_MAME_FLAT AS c LEFT OUTER JOIN REF_MAME_274_FLAT AS m
ON c.name = m.name
WHERE c.name in (select file from COINOPS_DELUXE_MAX_ROMS)
order by c.year,c.name ASC;
--------------------------------------------------------------
