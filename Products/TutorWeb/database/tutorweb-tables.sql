/* This file contains database table definitions for the tutor-web
   run script: mysql -u root < tutorweb-tables.sql
 */

create database if not exists tutorweb;
use tutorweb;
create table if not exists question_information (
    question_id integer unsigned not null auto_increment primary key,
    question_location varchar(64) not null,
    num_asked_for integer unsigned not null,
    num_correct integer unsigned not null,
    correct_id integer unsigned not null,
    question_unique_id varchar(64) UNIQUE not null,
    index correct_answer(correct_id),
    index question_url(question_location)
    --TODO: Wot, no index on question_unique_id?
) engine=InnoDB;
create table if not exists question_modification (
    modification_id integer unsigned not null auto_increment primary key,
    question_id integer unsigned not null,
    modification_time datetime not null,
    foreign key(question_id)
        references question_information(question_id)
            on update restrict
            on delete restrict
    
) engine=InnoDB;
create table if not exists student_information (
       student_id integer unsigned not null auto_increment primary key,
       student_username varchar(64) not null,
       student_randomnumber varchar(64) UNIQUE not null,
       student_firstname varchar(64) not null,
       student_family varchar(64) not null,
       student_email varchar(64) not null,
       index student_user(student_username)
) engine=InnoDB;
create table if not exists school_information (
       school_id integer unsigned not null auto_increment primary key,
       school_name varchar(64) not null,
       index schoolname(school_name)
) engine=InnoDB;
create table if not exists class_information (
       class_id integer unsigned not null auto_increment primary key,
       school_id integer unsigned not null,
       class_name varchar(64) not null,
       email varchar(64) not null,
       foreign key(school_id)
        references school_information(school_id)
            on update restrict
            on delete restrict
) engine=InnoDB;
create table if not exists classregistration_information (
       classregistration_id integer unsigned not null auto_increment primary key,
       student_id integer unsigned not null,
       class_id integer unsigned not null,
       registration_date_start datetime not null,
       registration_date_end datetime not null,
       foreign key(student_id)
        references student_information(student_id)
            on update restrict
            on delete restrict,
       foreign key(class_id)
        references class_information(class_id)
            on update restrict
            on delete restrict
) engine=InnoDB;
create table if not exists quiz_information (
       quiz_id integer unsigned not null auto_increment primary key,
       student_id integer unsigned not null,
       question_id integer unsigned not null,
       quiz_location varchar(64) not null,
       quiz_time datetime not null,
       student_answer integer not null,
       answer_time datetime not null,
       foreign key(student_id)
        references student_information(student_id)
            on update restrict
            on delete restrict,
       foreign key(question_id)
        references question_information(question_id)
            on update restrict
            on delete restrict
) engine=InnoDB;

CREATE TABLE IF NOT EXISTS allocation_information (
       allocation_id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
       student_id INTEGER UNSIGNED NOT NULL,
       quiz_location VARCHAR(64) NOT NULL, -- Strictly speaking the lecture location
       question_id INTEGER UNSIGNED NOT NULL,
       allocation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       answered_flag BOOLEAN NOT NULL DEFAULT false, -- Question answered, so out of the pool
       FOREIGN KEY(student_id)
        REFERENCES student_information(student_id)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT,
       FOREIGN KEY(question_id)
        REFERENCES question_information(question_id)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT
) engine=InnoDB DEFAULT CHARSET=utf8;
