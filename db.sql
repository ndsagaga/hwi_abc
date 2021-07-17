DROP DATABASE `hwi_abc`;

CREATE DATABASE `hwi_abc`;

USE `hwi_abc`;

DROP USER 'gandalf';

CREATE USER 'gandalf' IDENTIFIED BY 'youshallpass';

GRANT ALL ON `hwi_abc`.* TO 'gandalf';

CREATE TABLE `statuses` (
	`status` VARCHAR(255) NOT NULL,
	`order` FLOAT NOT NULL,
	`description` TEXT,
	`alert_after_days` INT,
	PRIMARY KEY (`status`)
) ENGINE=InnoDB;

CREATE TABLE `roles` (
	`role` VARCHAR(255) NOT NULL,
	`level` FLOAT NOT NULL,
	`is_active` BOOLEAN NOT NULL,
	PRIMARY KEY (`role`)
) ENGINE=InnoDB;

CREATE TABLE `users` (
	`id` VARCHAR(255) NOT NULL,
	`first_name` VARCHAR(255) NOT NULL,
	`last_name` VARCHAR(255) NOT NULL,
	`gender` ENUM('M','F') NOT NULL,
	`phone_number` VARCHAR(255) NOT NULL,
	`email` VARCHAR(255) NOT NULL,
	`role` VARCHAR(255) NOT NULL,
	`password_hash` VARCHAR(255) NOT NULL,
	`is_active` BOOLEAN NOT NULL,
	PRIMARY KEY (`id`),
	FOREIGN KEY (`role`) REFERENCES roles(`role`)
) ENGINE=InnoDB;

CREATE TABLE `dogs` (
	`tag` VARCHAR(255) NOT NULL,
	`avatar` VARCHAR(255),
	`gender` ENUM('M','F') NOT NULL,
	`age` INT unsigned,
	`age_category` VARCHAR(255),
	`color` VARCHAR(255),
	`weight` INT unsigned,
	`breed` VARCHAR(255),
	`pickup_lat` FLOAT NOT NULL,
	`pickup_long` FLOAT NOT NULL,
	`pickup_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`pickup_by` VARCHAR(255) NOT NULL,
	`pickup_photo` VARCHAR(255) NOT NULL,
	`dropoff_lat` FLOAT,
	`dropoff_long` FLOAT,
	`dropoff_time` TIMESTAMP,
	`dropoff_by` VARCHAR(255),
	`dropoff_photo` VARCHAR(255),
	`is_vaccinated` BOOLEAN,
	`is_sterlized` BOOLEAN,
	`created_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`last_modified_timestamp` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	FOREIGN KEY (`pickup_by`) REFERENCES users(`id`),
	FOREIGN KEY (`dropoff_by`) REFERENCES users(`id`),
	PRIMARY KEY (`tag`)
) ENGINE=InnoDB;

CREATE TABLE `dog_status` (
	`tag` VARCHAR(255) NOT NULL,
	`status` VARCHAR(255) NOT NULL,
	`timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`by` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`tag`,`status`),
	FOREIGN KEY (`tag`) REFERENCES dogs(`tag`),
	FOREIGN KEY (`status`) REFERENCES statuses(`status`),
	FOREIGN KEY (`by`) REFERENCES users(`id`)
) ENGINE=InnoDB;

CREATE TABLE `treatment_tasks` (
	`id` INT unsigned NOT NULL AUTO_INCREMENT,
	`tag` VARCHAR(255) NOT NULL,
	`frequency` VARCHAR(255),
	`status` VARCHAR(255) NOT NULL,
	`assigned_role` VARCHAR(255) NOT NULL,
	`task` TEXT NOT NULL,
	`is_completed` BOOLEAN DEFAULT false,
	`is_active` BOOLEAN DEFAULT true,
	`last_modified_timestamp` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`last_modified_by` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`id`),
	FOREIGN KEY (`tag`) REFERENCES dogs(`tag`),
	FOREIGN KEY (`status`) REFERENCES statuses(`status`),
	FOREIGN KEY (`assigned_role`) REFERENCES roles(`role`),
	FOREIGN KEY (`last_modified_by`) REFERENCES users(`id`)
) ENGINE=InnoDB;

CREATE TABLE `treatment_task_actions` (
	`id` INT unsigned NOT NULL AUTO_INCREMENT,
	`treatment_task_id` INT unsigned NOT NULL,
	`action_performed` TEXT NOT NULL,
	`action_photo` VARCHAR(255),
	`timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`by` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`id`),
	FOREIGN KEY (`treatment_task_id`) REFERENCES treatment_tasks(`id`),
	FOREIGN KEY (`by`) REFERENCES users(`id`)
) ENGINE=InnoDB;

CREATE TABLE `user_sessions` (
	`id` VARCHAR(255) NOT NULL,
	`user_id` VARCHAR(255) NOT NULL,
	`expire_timestamp` TIMESTAMP NOT NULL,
	PRIMARY KEY (`id`),
	FOREIGN KEY (`user_id`) REFERENCES users(`id`)
) ENGINE=InnoDB;

INSERT INTO roles 
	VALUES("ADMIN", 0.0, true),
	("DOCTOR", 1.0, true), 
	("SUPERVISOR", 2.0, true), 
	("HANDLER", 3.0, true);

INSERT INTO users VALUES
	("nirup", "Nirup", "Anandaraman", "M", "+15853869161", "nirupiyer@yahoo.com", "ADMIN", "bff0c2a6cd630536804d8622ec51a5dd95a5e509bc6318f12d86561f23d949a1945d2447e718578c2ec6f7f80c3436c18eb0a8d91340d41405c85d035ddb60cc", true);

INSERT INTO statuses VALUES
	("CAPTURED", 0.0, "Captured for spaying/neutering", 1),
	("FIT_FOR_SURGERY", 1.0, "Certified fit for surgery", 2),
	("IN_SURGERY", 2.0, "Undergoing surgery", 2),
	("POST_SURGERY", 3.0, "Post-op treatments", 3),
	("FIT_FOR_RELEASE", 4.0, "Certified fit for release", 1),
	("RELEASED", 5.0, "Dog has been released", 999);