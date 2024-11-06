CREATE TABLE Raspberry(
   Id_Raspberry INT AUTO_INCREMENT,
   Adresse_MAC VARCHAR(17) ,
   Adresse_ip VARCHAR(16)  NOT NULL,
   Pub_Key TEXT NOT NULL,
   PRIMARY KEY(Id_Raspberry),
   UNIQUE(Adresse_ip),
   UNIQUE(Pub_Key)
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
   Port INT,
   PRIMARY KEY(Id_Service),
   UNIQUE(Libelle),
   UNIQUE(Port)
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
   PRIMARY KEY(Id_Raspberry, Id_Service),
   FOREIGN KEY(Id_Raspberry) REFERENCES Raspberry(Id_Raspberry),
   FOREIGN KEY(Id_Service) REFERENCES Service(Id_Service)
);
