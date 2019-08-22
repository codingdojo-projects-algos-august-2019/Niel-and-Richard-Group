-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema jokes
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `jokes` ;

-- -----------------------------------------------------
-- Schema jokes
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `jokes` DEFAULT CHARACTER SET utf8 ;
USE `jokes` ;

-- -----------------------------------------------------
-- Table `jokes`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `jokes`.`users` ;

CREATE TABLE IF NOT EXISTS `jokes`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `alias` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT NOW(),
  `updated_at` DATETIME NOT NULL DEFAULT NOW() ON UPDATE NOW(),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `jokes`.`jokes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `jokes`.`jokes` ;

CREATE TABLE IF NOT EXISTS `jokes`.`jokes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `joke` VARCHAR(255) NOT NULL,
  `punchline` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT NOW(),
  `updated_at` DATETIME NOT NULL DEFAULT NOW() ON UPDATE NOW(),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `fk_jokes_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_jokes_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `jokes`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `jokes`.`likes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `jokes`.`likes` ;

CREATE TABLE IF NOT EXISTS `jokes`.`likes` (
  `user_id` INT(11) NOT NULL,
  `joke_id` INT(11) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT NOW(),
  `updated_at` DATETIME NOT NULL DEFAULT NOW() ON UPDATE NOW(),
  INDEX `fk_users_has_jokes_jokes1_idx` (`joke_id` ASC) VISIBLE,
  INDEX `fk_users_has_jokes_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_jokes_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `jokes`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_jokes_jokes1`
    FOREIGN KEY (`joke_id`)
    REFERENCES `jokes`.`jokes` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
