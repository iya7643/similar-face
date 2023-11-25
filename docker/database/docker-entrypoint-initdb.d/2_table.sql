-- select 'create database trading' where not exists (select from pg_database where datname='trading');
-- \c trading

CREATE TABLE faces (
    id uuid NOT NULL,
    name varchar(100),
    image bytea NOT NULL,
    image_extension varchar(5) NOT NULL,
    embedding vector NOT NULL,
    CONSTRAINT face_embedding_pkey PRIMARY KEY (id)
);
