CREATE TABLE collectors (object_id INTEGER, collector_class INTEGER, count INTEGER);
INSERT INTO "collectors" VALUES(8,1000010,1);
INSERT INTO "collectors" VALUES(7,1000002,1);
INSERT INTO "collectors" VALUES(9,1000014,1);
INSERT INTO "collectors" VALUES(20,1000015,0);
INSERT INTO "collectors" VALUES(3,1000011,1);
INSERT INTO "collectors" VALUES(1,1000008,3);
INSERT INTO "collectors" VALUES(2,1000008,2);
INSERT INTO "collectors" VALUES(12,1000002,1);
INSERT INTO "collectors" VALUES(20,1000009,2);
INSERT INTO "collectors" VALUES(24,1000002,1);
INSERT INTO "collectors" VALUES(26,1000002,1);
INSERT INTO "collectors" VALUES(29,1000002,2);
INSERT INTO "collectors" VALUES(30,1000002,1);
INSERT INTO "collectors" VALUES(31,1000002,1);
INSERT INTO "collectors" VALUES(32,1000002,1);
INSERT INTO "collectors" VALUES(11,1000004,1);
INSERT INTO "collectors" VALUES(37,1000002,1);
INSERT INTO "collectors" VALUES(41,1000002,1);
INSERT INTO "collectors" VALUES(42,1000002,1);
INSERT INTO "collectors" VALUES(42,1000019,0);

CREATE TABLE animals ("building_id" INTEGER NOT NULL ,"unit_id" INTEGER NOT NULL ,"count" INTEGER NOT NULL );
INSERT INTO "animals" VALUES(18,1000003,3);

CREATE TABLE unit_production ("production_line" INTEGER NOT NULL ,"unit" INTEGER NOT NULL ,"amount" INTEGER NOT NULL );
INSERT INTO "unit_production" VALUES(15,1000001,1);
INSERT INTO "unit_production" VALUES(58,1000020,1);
INSERT INTO "unit_production" VALUES(62,1000016,1);
INSERT INTO "unit_production" VALUES(63,1000016,1);
INSERT INTO "unit_production" VALUES(64,1000016,1);
INSERT INTO "unit_production" VALUES(68,1000016,1);

CREATE TABLE start_resources (resource INT, amount INT);
INSERT INTO "start_resources" VALUES(4,30);
INSERT INTO "start_resources" VALUES(5,30);
INSERT INTO "start_resources" VALUES(6,30);
INSERT INTO "start_resources" VALUES(40,12);

CREATE TABLE player_start_res (resource int not null, amount int not null);
INSERT INTO "player_start_res" VALUES(1,30000);

CREATE TABLE deposit_resources(id int not null, resource int not null, min_amount int not null, max_amount int not null);
INSERT INTO "deposit_resources" VALUES(23,20,750,1250);
INSERT INTO "deposit_resources" VALUES(34,24,375,625);

CREATE TABLE storage_building_capacity(type INT, size INT);
INSERT INTO "storage_building_capacity" VALUES(1,30);
INSERT INTO "storage_building_capacity" VALUES(2,10);
INSERT INTO "storage_building_capacity" VALUES(4,0);

CREATE TABLE upgrade_material(level INT NOT NULL, production_line INT NOT NULL);
INSERT INTO "upgrade_material" VALUES(1,24);
INSERT INTO "upgrade_material" VALUES(2,35);

CREATE TABLE balance_values(name TEXT, value FLOAT);
INSERT INTO "balance_values" VALUES('happiness_init_value',50.0);
INSERT INTO "balance_values" VALUES('happiness_min_value',0.0);
INSERT INTO "balance_values" VALUES('happiness_max_value',100.0);
INSERT INTO "balance_values" VALUES('happiness_inhabitants_increase_requirement',70.0);
INSERT INTO "balance_values" VALUES('happiness_inhabitants_decrease_limit',30.0);
INSERT INTO "balance_values" VALUES('happiness_level_up_requirement',80.0);
INSERT INTO "balance_values" VALUES('happiness_level_down_limit',10.0);
