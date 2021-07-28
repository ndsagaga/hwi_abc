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
	`age_category` VARCHAR(255),
	`color` VARCHAR(255),
	`weight` INT unsigned,
	`additional_info` TEXT,
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
	`status` VARCHAR(255) NOT NULL,
	`assigned_role` VARCHAR(255) NOT NULL,
	`task` TEXT NOT NULL,
	`response_type` ENUM('TEXT','BINARY','COUNTER','TIMESTAMP','GEO_PHOTO') NOT NULL,
	`is_completed` BOOLEAN DEFAULT false,
	`is_required` BOOLEAN DEFAULT true,
	`last_modified_timestamp` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`last_modified_by` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`id`),
	FOREIGN KEY (`tag`) REFERENCES dogs(`tag`),
	FOREIGN KEY (`status`) REFERENCES statuses(`status`),
	FOREIGN KEY (`assigned_role`) REFERENCES roles(`role`),
	FOREIGN KEY (`last_modified_by`) REFERENCES users(`id`)
) ENGINE=InnoDB;

CREATE TABLE `treatment_task_actions` (
	`treatment_task_id` INT unsigned NOT NULL,
	`action_performed` TEXT NOT NULL,
	`action_photo` VARCHAR(255),
	`timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`by` VARCHAR(255) NOT NULL,
	PRIMARY KEY (`treatment_task_id`),
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
	("PRE_SURGERY", 1.0, "Certified fit for surgery", 2),
	("IN_SURGERY", 2.0, "Undergoing surgery", 2),
	("POST_SURGERY", 3.0, "Post-op treatments", 3),
	("RELEASED", 4.0, "Dog has been released", 999);

INSERT INTO users VALUES("nikitha", "Nikitha", "Iyer", "F","9663311681", "nikki.mitra@gmail.com", "ADMIN","22f397847ee022e224d095a1e21c0ca502de41f2d88e90dd912d8476ee669b81ee546408a3fd1200d272829bcdb93d87978761dbe5b3dbf0c4b715d7a9e4963f", 1);
INSERT INTO users VALUES
("sandeep", "Sandeep", "Handler", "M","-", "", "HANDLER","54fe80df908b8883bc7a3794ae4ce0db482bd2197ed0197cc5761a49c7d35f6ee2924e88ad2b188c0179adbb2252123f1e186691ba3d22d41f3423621738df30", 1),
("lakhinath", "Lakhinath", "Handler", "M","-", "", "HANDLER","69e613b26c3bc0e6dc4ff5a68917307ab10950ffa7ca662e11218cd51f5fefafaabbebd885ed7084cf97de1653bcc2ae19ad1cdee22b27692c7ec263333d0a7a", 1),
("biswa", "Biswa", "Handler", "M","-", "", "HANDLER","f293e74b540662f053cf6d8285302732b5dc2818dafa6797eb68109d247aae2c236d6de4ff9d47297f5980450fd75a97f6aef0e1f8d4d9f872622cb623a14c19", 1),
("bitupon", "Bitupon", "Handler", "M","-", "", "HANDLER","5196ff0cbaf6ae0c9aa9625f447579e957b114df7f2c7e7890ece215e37e8711ab597ec9572ff0801d1a60793c2bf2b6d2104a06a523eb04db1418e3c01d5199", 1);