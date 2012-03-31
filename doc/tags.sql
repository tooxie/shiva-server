PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- CREATE TABLE taggroups (
-- 	name VARCHAR(128) NOT NULL,
-- 	PRIMARY KEY (name)
-- );
INSERT INTO "taggroups" VALUES('album');
INSERT INTO "taggroups" VALUES('performer');
INSERT INTO "taggroups" VALUES('title');
INSERT INTO "taggroups" VALUES('track');
INSERT INTO "taggroups" VALUES('year');
INSERT INTO "taggroups" VALUES('genre');
INSERT INTO "taggroups" VALUES('comment');
INSERT INTO "taggroups" VALUES('date');
INSERT INTO "taggroups" VALUES('copyright');
INSERT INTO "taggroups" VALUES('encoded by');
INSERT INTO "taggroups" VALUES('url');
INSERT INTO "taggroups" VALUES('content type');
INSERT INTO "taggroups" VALUES('original artist');
INSERT INTO "taggroups" VALUES('composer');
COMMIT;

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- CREATE TABLE tags (
-- 	pk INTEGER NOT NULL,
-- 	name VARCHAR(128),
-- 	group_pk VARCHAR,
-- 	PRIMARY KEY (pk),
-- 	FOREIGN KEY(group_pk) REFERENCES taggroups (name)
-- );
INSERT INTO "tags" VALUES(1,'TIT2','title');
INSERT INTO "tags" VALUES(2,'COMM','comment');
INSERT INTO "tags" VALUES(3,'TDRC','date');
INSERT INTO "tags" VALUES(4,'TPE1','performer');
INSERT INTO "tags" VALUES(5,'TCON','content type');
INSERT INTO "tags" VALUES(6,'TRCK','track');
INSERT INTO "tags" VALUES(7,'TENC','encoded by');
INSERT INTO "tags" VALUES(8,'WXXX','url');
INSERT INTO "tags" VALUES(9,'TCOP','copyright');
INSERT INTO "tags" VALUES(10,'TOPE','original artist');
INSERT INTO "tags" VALUES(11,'TCOM','composer');
INSERT INTO "tags" VALUES(12,'TYER',NULL);
INSERT INTO "tags" VALUES(13,'TALB',NULL);
INSERT INTO "tags" VALUES(14,'TPE2',NULL);
INSERT INTO "tags" VALUES(15,'TSSE',NULL);
INSERT INTO "tags" VALUES(16,'TLEN',NULL);
INSERT INTO "tags" VALUES(17,'TPOS',NULL);
INSERT INTO "tags" VALUES(18,'APIC',NULL);
INSERT INTO "tags" VALUES(19,'PRIV',NULL);
INSERT INTO "tags" VALUES(20,'POPM',NULL);
INSERT INTO "tags" VALUES(21,'v1performer','performer');
INSERT INTO "tags" VALUES(22,'v1album',NULL);
INSERT INTO "tags" VALUES(23,'v1year',NULL);
INSERT INTO "tags" VALUES(24,'v1comment',NULL);
INSERT INTO "tags" VALUES(25,'v1genre',NULL);
INSERT INTO "tags" VALUES(26,'TLAN',NULL);
INSERT INTO "tags" VALUES(27,'TXXX',NULL);
INSERT INTO "tags" VALUES(28,'TDAT',NULL);
INSERT INTO "tags" VALUES(29,'TPUB',NULL);
INSERT INTO "tags" VALUES(30,'v1title',NULL);
INSERT INTO "tags" VALUES(31,'TCMP',NULL);
INSERT INTO "tags" VALUES(32,'USLT',NULL);
INSERT INTO "tags" VALUES(33,'MCDI',NULL);
INSERT INTO "tags" VALUES(34,'UFID',NULL);
INSERT INTO "tags" VALUES(35,'TP1','performer');
INSERT INTO "tags" VALUES(36,'TAL',NULL);
INSERT INTO "tags" VALUES(37,'TPA',NULL);
INSERT INTO "tags" VALUES(38,'TYE',NULL);
INSERT INTO "tags" VALUES(39,'TT2',NULL);
INSERT INTO "tags" VALUES(40,'TRK',NULL);
INSERT INTO "tags" VALUES(41,'PIC',NULL);
INSERT INTO "tags" VALUES(42,'TP2','performer');
INSERT INTO "tags" VALUES(43,'TT1',NULL);
INSERT INTO "tags" VALUES(44,'TCO',NULL);
INSERT INTO "tags" VALUES(45,'COM',NULL);
INSERT INTO "tags" VALUES(46,'TIT1',NULL);
INSERT INTO "tags" VALUES(47,'TEN',NULL);
INSERT INTO "tags" VALUES(48,'v1track',NULL);
INSERT INTO "tags" VALUES(49,'UFI',NULL);
INSERT INTO "tags" VALUES(50,'TMED',NULL);
INSERT INTO "tags" VALUES(51,'TOAL',NULL);
COMMIT;
