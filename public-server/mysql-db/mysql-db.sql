CREATE DATABASE IF NOT EXISTS `airlux`;
USE `airlux`;

CREATE TABLE Raspberry(
   Adresse_MAC VARCHAR(17) ,
   Adresse_ip VARCHAR(16)  NOT NULL,
   Remote_Port INT,
   PRIMARY KEY(Adresse_MAC),
   UNIQUE(Adresse_ip),
   UNIQUE(Remote_Port)
);

CREATE TABLE Device(
   Id_Device INT AUTO_INCREMENT,
   Adresse_MAC VARCHAR(17)  NOT NULL,
   PRIMARY KEY(Id_Device),
   FOREIGN KEY(Adresse_MAC) REFERENCES Raspberry(Adresse_MAC)
);

CREATE TABLE Type_Device(
   Id_Type_Device INT AUTO_INCREMENT,
   Libelle VARCHAR(50)  NOT NULL,
   PRIMARY KEY(Id_Type_Device),
   UNIQUE(Libelle)
);

CREATE TABLE Service(
   Id_Service INT AUTO_INCREMENT,
   Libelle VARCHAR(50)  NOT NULL,
   PRIMARY KEY(Id_Service),
   UNIQUE(Libelle)
);

CREATE TABLE Status(
   Id_Status INT AUTO_INCREMENT,
   Libelle VARCHAR(50) ,
   PRIMARY KEY(Id_Status)
);

CREATE TABLE Ping(
   Id_Ping INT AUTO_INCREMENT,
   TS DATETIME,
   Id_Status INT NOT NULL,
   Adresse_MAC VARCHAR(17)  NOT NULL,
   PRIMARY KEY(Id_Ping),
   FOREIGN KEY(Id_Status) REFERENCES Status(Id_Status),
   FOREIGN KEY(Adresse_MAC) REFERENCES Raspberry(Adresse_MAC)
);

CREATE TABLE Device_has_Type(
   Id_Device INT,
   Id_Type_Device INT,
   PRIMARY KEY(Id_Device, Id_Type_Device),
   FOREIGN KEY(Id_Device) REFERENCES Device(Id_Device),
   FOREIGN KEY(Id_Type_Device) REFERENCES Type_Device(Id_Type_Device)
);

CREATE TABLE Raspberry_has_Service(
   Adresse_MAC VARCHAR(17) ,
   Id_Service INT,
   URL VARCHAR(150) ,
   PRIMARY KEY(Adresse_MAC, Id_Service),
   FOREIGN KEY(Adresse_MAC) REFERENCES Raspberry(Adresse_MAC),
   FOREIGN KEY(Id_Service) REFERENCES Service(Id_Service)
);
