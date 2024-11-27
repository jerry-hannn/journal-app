CREATE DATABASE IF NOT EXISTS journalapp;


USE journalapp;


DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS images;


CREATE TABLE users
(
    uid       int not null AUTO_INCREMENT,
    username  varchar(64) not null,
    PRIMARY KEY  (userid),
    unique(username)
);


ALTER TABLE users AUTO_INCREMENT = 80001;  -- starting value


CREATE TABLE entries
(
    entryid           int not null AUTO_INCREMENT,
    uid               int not null,
    date              datetime not null, -- YYYY-MM-DD hh:mm:ss 
    notes             varchar(512) not null,
    sleep 	      int not null,  -- 1-10
    eat               int not null,
    water	      int not null,
    social	      int not null,
    overall  	      int not null,
    PRIMARY KEY (entryid),
    FOREIGN KEY (userid) REFERENCES users(userid),
    UNIQUE (date)
);




ALTER TABLE entries AUTO_INCREMENT = 1001;  -- starting value

CREATE TABLE images
(
    imageid	    int not null,
    uid		    int not null,
    date	    datetime not null,
    bucketkey	    varchar(256) not null,
    PRIMARY KEY (imageid),
    FOREIGN KEY (userid) REFERENCES users(userid),
    UNIQUE (date),
    UNIQUE (bucketkey)
)


INSERT INTO users(username)  -- pwd = abc123!!
            values('p_sarkar')



--
-- creating user accounts for database access:
--
-- ref: https://dev.mysql.com/doc/refman/8.0/en/create-user.html
--


DROP USER IF EXISTS 'journalapp-read-only';
DROP USER IF EXISTS 'journalapp-read-write';


CREATE USER 'journalapp-read-only' IDENTIFIED BY 'abc123!!';
CREATE USER 'journalapp-read-write' IDENTIFIED BY 'def456!!';


GRANT SELECT, SHOW VIEW ON journalapp.* 
      TO 'journalapp-read-only';
GRANT SELECT, SHOW VIEW, INSERT, UPDATE, DELETE, DROP, CREATE, ALTER ON journalapp.* 
      TO 'journalapp-read-write';
      
FLUSH PRIVILEGES;


--
-- done
--



