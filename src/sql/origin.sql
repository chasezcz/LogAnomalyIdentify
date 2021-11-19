/*
 Navicat Premium Data Transfer

 Source Server         : 服务器
 Source Server Type    : MySQL
 Source Server Version : 80027
 Source Host           : localhost:3306
 Source Schema         : arplogs

 Target Server Type    : MySQL
 Target Server Version : 80027
 File Encoding         : 65001

 Date: 18/11/2021 20:05:32
*/
SET
  NAMES utf8mb4;
SET
  FOREIGN_KEY_CHECKS = 0;
-- ----------------------------
  -- Table structure for origin
  -- ----------------------------
  DROP TABLE IF EXISTS `origin`;
CREATE TABLE `origin` (
    `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
    `time` double NOT NULL,
    `threadID` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `institutionID` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `userID` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '',
    `url` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
    `method` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `statusCode` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `parameterType` varchar(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `parameterName` varchar(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `parameterValue` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
    `headers` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
    `name` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `ip` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `port` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `vpnIP` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `urlEntry` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    PRIMARY KEY (`id`) USING BTREE
  ) ENGINE = InnoDB AUTO_INCREMENT = 2576902 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;
SET
  FOREIGN_KEY_CHECKS = 1;