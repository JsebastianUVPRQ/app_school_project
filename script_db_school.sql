-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS escuela_base_datos;
USE escuela_base_datos

CREATE TABLE `estudiantes`
(
 `id_estud`         integer NOT NULL ,
 `nombre_estud`     varchar(45) NOT NULL ,
 `fecha_nacimiento` datetime NOT NULL ,
 `id_salon`         integer NOT NULL ,

PRIMARY KEY (`id_estud`),
KEY `FK_1` (`id_salon`),
CONSTRAINT `FK_1` FOREIGN KEY `FK_1` (`id_salon`) REFERENCES `salon` (`id_salon`)
);

-- ************************************** `estudiantes_x_curso`

CREATE TABLE `estudiantes_x_curso`
(
 `id_transaccion` integer NOT NULL ,
 `id_estud`       integer NOT NULL ,
 `id_materia`     integer NOT NULL ,

PRIMARY KEY (`id_transaccion`),
KEY `FK_1` (`id_estud`),
CONSTRAINT `FK_3` FOREIGN KEY `FK_1` (`id_estud`) REFERENCES `estudiantes` (`id_estud`),
KEY `FK_2` (`id_materia`),
CONSTRAINT `FK_4` FOREIGN KEY `FK_2` (`id_materia`) REFERENCES `materias` (`id_materia`)
);

-- ************************************** `materias`

CREATE TABLE `materias`
(
 `id_materia`       integer NOT NULL ,
 `nombre_materia_1` varchar(45) NOT NULL ,
 `id_salon`         integer NOT NULL ,

PRIMARY KEY (`id_materia`),
KEY `FK_1` (`id_salon`),
CONSTRAINT `FK_2` FOREIGN KEY `FK_1` (`id_salon`) REFERENCES `salon` (`id_salon`)
);

-- #####################################################
-- ************************************** notas

CREATE TABLE `notas`
(
 `id_notas`     integer NOT NULL ,
 `calificacion` double NOT NULL ,
 `id_estud`     integer NOT NULL ,
 `id_materia`   integer NOT NULL ,

PRIMARY KEY (`id_notas`),
KEY `FK_1` (`id_estud`),
CONSTRAINT `FK_5` FOREIGN KEY `FK_1` (`id_estud`) REFERENCES `estudiantes` (`id_estud`),
KEY `FK_2` (`id_materia`),
CONSTRAINT `FK_6` FOREIGN KEY `FK_2` (`id_materia`) REFERENCES `materias` (`id_materia`)
);

-- ************************************** `salon`

CREATE TABLE `salon`
(
 `id_salon`     integer NOT NULL ,
 `nombre_salon` varchar(45) NOT NULL ,

PRIMARY KEY (`id_salon`)
);
