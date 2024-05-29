CREATE DATABASE IF NOT EXISTS fonasa;
USE fonasa;

DROP TABLE IF EXISTS `Consulta`;
DROP TABLE IF EXISTS `PAnciano`;
DROP TABLE IF EXISTS `PJoven`;
DROP TABLE IF EXISTS `PNinno`;
DROP TABLE IF EXISTS `Paciente`;
DROP TABLE IF EXISTS `Hospital`;

CREATE TABLE Hospital (
	id INT AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    direccion VARCHAR(255),
    PRIMARY KEY (id)
);

CREATE TABLE Consulta (
	id INT AUTO_INCREMENT,
    cantPacientes INT DEFAULT(0),
    nombreEspecialista VARCHAR(255),
    tipoConsulta ENUM('Pediatria','Urgencia','CGI'),
    estado ENUM('en espera', 'ocupada') DEFAULT('en espera'),
    idHospital INT,
    PRIMARY KEY (id),
    FOREIGN KEY (idHospital) REFERENCES Hospital(id)
);

CREATE TABLE Paciente (
	id INT AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    edad INT NOT NULL, 
    estado ENUM('pendiente', 'sala de espera', 'atendido') DEFAULT('pendiente'),
    noHistoriaClinica INT,
    idHospital INT,
    PRIMARY KEY (id),
    FOREIGN KEY (idHospital) REFERENCES Hospital(id)
);

CREATE TABLE PAnciano (
	id INT AUTO_INCREMENT,
    tieneDieta BOOLEAN,
    idPaciente INT,
    PRIMARY KEY (id),
    FOREIGN KEY (idPaciente) REFERENCES Paciente(id)
);

CREATE TABLE PJoven (
	id INT AUTO_INCREMENT,
    fumador BOOLEAN,
    periodoFumando INT,
    idPaciente INT,
    PRIMARY KEY (id),
    FOREIGN KEY (idPaciente) REFERENCES Paciente(id)
);

CREATE TABLE PNinno (
	id INT AUTO_INCREMENT,
    relacionPesoEstatura INT,
    idPaciente INT,
    PRIMARY KEY (id),
    FOREIGN KEY (idPaciente) REFERENCES Paciente(id)
);