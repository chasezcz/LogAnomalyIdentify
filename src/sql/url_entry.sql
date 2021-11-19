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

 Date: 18/11/2021 20:44:49
*/
SET
  NAMES utf8mb4;
SET
  FOREIGN_KEY_CHECKS = 0;
-- ----------------------------
  -- Table structure for urlEntry
  -- ----------------------------
  DROP TABLE IF EXISTS `urlEntry`;
CREATE TABLE `urlEntry` (
    `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
    `module` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `method` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    `urlEntry` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
    PRIMARY KEY (`id`) USING BTREE
  ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
SET
  FOREIGN_KEY_CHECKS = 1;