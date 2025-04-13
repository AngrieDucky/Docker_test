GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;

CREATE TABLE IF NOT EXISTS respondents
(

    id        bigserial primary key,
    Date      timestamp,
    respondent  integer NOT NULL,
    Sex     smallint NOT NULL,
    Age     smallint NOT NULL,
    Weight     decimal(22,19) NOT NULL
    
);