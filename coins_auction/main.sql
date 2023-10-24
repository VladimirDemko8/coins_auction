/*
Navicat SQLite Data Transfer

Source Server         : auction_coins_db
Source Server Version : 30623
Source Host           : localhost:0

Target Server Type    : SQLite
Target Server Version : 30623
File Encoding         : 65001

Date: 2023-10-23 16:59:27
*/


-- ----------------------------
-- Table structure for "admins"
-- ----------------------------
DROP TABLE "admins";
CREATE TABLE "admins" (
"id"  INTEGER PRIMARY KEY AUTOINCREMENT,
"login"  TEXT,
"password"  TEXT,
"balance"  REAL
);

-- ----------------------------
-- Records of admins
-- ----------------------------
INSERT INTO "admins" VALUES ('1', '1', '1', '1000.0');
INSERT INTO "admins" VALUES ('2', '342', '434', '555.0');
INSERT INTO "admins" VALUES ('3', '222', '222', '222.0');
INSERT INTO "admins" VALUES ('4', '454', '567', '666.0');
INSERT INTO "admins" VALUES ('5', 'kok', '43rf', '24567.0');
INSERT INTO "admins" VALUES ('6', 'loka', '123', '1000.0');

-- ----------------------------
-- Table structure for "bids"
-- ----------------------------
DROP TABLE "bids";
CREATE TABLE "bids" (
"user_id"  INTEGER,
"lot_id"  INTEGER,
"amount"  INTEGER,
PRIMARY KEY ("user_id" ASC, "lot_id" ASC),
FOREIGN KEY ("user_id") REFERENCES "users" ("id"),
FOREIGN KEY ("lot_id") REFERENCES "lots" ("id")
);

-- ----------------------------
-- Records of bids
-- ----------------------------

-- ----------------------------
-- Table structure for "buf_complaint"
-- ----------------------------
DROP TABLE "buf_complaint";
CREATE TABLE buf_complaint (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    status TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- ----------------------------
-- Records of buf_complaint
-- ----------------------------

-- ----------------------------
-- Table structure for "buf_lots"
-- ----------------------------
DROP TABLE "buf_lots";
CREATE TABLE buf_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    start_price INTEGER,
    seller_link TEXT,
    geolocation TEXT,
    description TEXT,
    start_time TEXT,
    end_time TEXT,
    FOREIGN KEY(admin_id) REFERENCES admins(id)
);

-- ----------------------------
-- Records of buf_lots
-- ----------------------------

-- ----------------------------
-- Table structure for "documents"
-- ----------------------------
DROP TABLE "documents";
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER,
    document_type TEXT,
    document_data TEXT,
    FOREIGN KEY(lot_id) REFERENCES lots(id)
);

-- ----------------------------
-- Records of documents
-- ----------------------------

-- ----------------------------
-- Table structure for "history_trade"
-- ----------------------------
DROP TABLE "history_trade";
CREATE TABLE history_trade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER,
    buyer_id INTEGER,
    price INTEGER,
    FOREIGN KEY(lot_id) REFERENCES lots(id),
    FOREIGN KEY(buyer_id) REFERENCES users(id)
);

-- ----------------------------
-- Records of history_trade
-- ----------------------------

-- ----------------------------
-- Table structure for "images"
-- ----------------------------
DROP TABLE "images";
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER,
    image_url TEXT,
    FOREIGN KEY(lot_id) REFERENCES lots(id)
);

-- ----------------------------
-- Records of images
-- ----------------------------
INSERT INTO "images" VALUES ('2', '2', 'picture\coin.jpg');

-- ----------------------------
-- Table structure for "lots"
-- ----------------------------
DROP TABLE "lots";
CREATE TABLE lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    start_price INTEGER,
    seller_link TEXT,
    geolocation TEXT,
    description TEXT,
    start_time TEXT,
    end_time TEXT,
    FOREIGN KEY(admin_id) REFERENCES admins(id)
);

-- ----------------------------
-- Records of lots
-- ----------------------------
INSERT INTO "lots" VALUES ('2', '1', '23578', '@vovchik', 'MInsk', 'BitCoin', '2023-10-23 11-00-00', '2023-10-23 12-00-00');

-- ----------------------------
-- Table structure for "sqlite_sequence"
-- ----------------------------
DROP TABLE "sqlite_sequence";
CREATE TABLE sqlite_sequence(name,seq);

-- ----------------------------
-- Records of sqlite_sequence
-- ----------------------------
INSERT INTO "sqlite_sequence" VALUES (null, null);
INSERT INTO "sqlite_sequence" VALUES ('admins', '6');
INSERT INTO "sqlite_sequence" VALUES ('lots', '2');
INSERT INTO "sqlite_sequence" VALUES ('images', '2');
INSERT INTO "sqlite_sequence" VALUES ('buf_lots', '2');

-- ----------------------------
-- Table structure for "straiks"
-- ----------------------------
DROP TABLE "straiks";
CREATE TABLE straiks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    user_id INTEGER,
    strike_count INTEGER,
    FOREIGN KEY(admin_id) REFERENCES admins(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- ----------------------------
-- Records of straiks
-- ----------------------------

-- ----------------------------
-- Table structure for "super_admins"
-- ----------------------------
DROP TABLE "super_admins";
CREATE TABLE "super_admins" (
"id"  INTEGER PRIMARY KEY AUTOINCREMENT,
"login"  TEXT,
"password"  TEXT
);

-- ----------------------------
-- Records of super_admins
-- ----------------------------
INSERT INTO "super_admins" VALUES ('1', 'admin', 'admin');

-- ----------------------------
-- Table structure for "sup_system"
-- ----------------------------
DROP TABLE "sup_system";
CREATE TABLE sup_system (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    status TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- ----------------------------
-- Records of sup_system
-- ----------------------------

-- ----------------------------
-- Table structure for "users"
-- ----------------------------
DROP TABLE "users";
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    balance INTEGER
);

-- ----------------------------
-- Records of users
-- ----------------------------

-- ----------------------------
-- Table structure for "_bids_old_20231023"
-- ----------------------------
DROP TABLE "_bids_old_20231023";
CREATE TABLE "_bids_old_20231023" (
    user_id INTEGER,
    lot_id INTEGER,
    amount INTEGER,
    PRIMARY KEY (user_id, lot_id)
);

-- ----------------------------
-- Records of _bids_old_20231023
-- ----------------------------

-- ----------------------------
-- Table structure for "_bids_old_20231023_1"
-- ----------------------------
DROP TABLE "_bids_old_20231023_1";
CREATE TABLE "_bids_old_20231023_1" (
"user_id"  INTEGER,
"lot_id"  INTEGER,
"amount"  INTEGER,
PRIMARY KEY ("user_id" ASC, "lot_id" ASC),
FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);

-- ----------------------------
-- Records of _bids_old_20231023_1
-- ----------------------------
