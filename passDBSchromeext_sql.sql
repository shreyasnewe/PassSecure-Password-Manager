select * from manage

ALTER TABLE manage
DROP COLUMN keys;

DELETE FROM manage;  

CREATE TABLE manage (
    website VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
);