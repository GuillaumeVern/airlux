CREATE TABLE Raspberry(
   Id_Raspberry INT AUTO_INCREMENT,
   Adresse_MAC VARCHAR(17)  NOT NULL,
   Adresse_ip VARCHAR(16)  NOT NULL,
   Prefixe VARCHAR(50)  NOT NULL,
   PRIMARY KEY(Id_Raspberry),
   UNIQUE(Adresse_MAC),
   UNIQUE(Prefixe)
);

CREATE TABLE Device(
   Id_Device INT AUTO_INCREMENT,
   Id_Raspberry INT NOT NULL,
   PRIMARY KEY(Id_Device),
   FOREIGN KEY(Id_Raspberry) REFERENCES Raspberry(Id_Raspberry)
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
   Prefixe VARCHAR(50)  NOT NULL,
   Local_Port INT NOT NULL,
   PRIMARY KEY(Id_Service),
   UNIQUE(Libelle),
   UNIQUE(Prefixe),
   UNIQUE(Local_Port)
);

CREATE TABLE Device_has_Type(
   Id_Device INT,
   Id_Type_Device INT,
   PRIMARY KEY(Id_Device, Id_Type_Device),
   FOREIGN KEY(Id_Device) REFERENCES Device(Id_Device),
   FOREIGN KEY(Id_Type_Device) REFERENCES Type_Device(Id_Type_Device)
);

CREATE TABLE Raspberry_has_Service(
   Id_Raspberry INT,
   Id_Service INT,
   Remote_Port INT NOT NULL,
   PRIMARY KEY(Id_Raspberry, Id_Service),
   UNIQUE(Remote_Port),
   FOREIGN KEY(Id_Raspberry) REFERENCES Raspberry(Id_Raspberry),
   FOREIGN KEY(Id_Service) REFERENCES Service(Id_Service)
);


INSERT INTO Service(Libelle, Prefixe, Local_Port) VALUES('SSH', 'ssh', 22);
INSERT INTO Service(Libelle, Prefixe, Local_Port) VALUES('Home Assistant', 'home', 8123);
INSERT INTO Service(Libelle, Prefixe, Local_Port) VALUES('Mosquitto', 'mqtt', 1883);
INSERT INTO Service(Libelle, Prefixe, Local_Port) VALUES('Redis', 'redis', 6379);

