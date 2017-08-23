/*
Navicat MySQL Data Transfer

Source Server         : local_mysql
Source Server Version : 50619
Source Host           : localhost:3306
Source Database       : db_assets

Target Server Type    : MYSQL
Target Server Version : 50619
File Encoding         : 65001

Date: 2017-07-07 16:14:51
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for tb_message
-- ----------------------------
DROP TABLE IF EXISTS `tb_message`;
CREATE TABLE `tb_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(100) NOT NULL COMMENT '业务标签',
  `domainip` varchar(100) NOT NULL COMMENT '域名或者ip',
  `flag` varchar(100) NOT NULL COMMENT '域名IP的标识',
  `remark` varchar(100) DEFAULT NULL COMMENT '备注',
  `userid` varchar(10) NOT NULL COMMENT '用户id',
  `taskid` varchar(100) NOT NULL COMMENT '任务id',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `scan_status` int(10) NOT NULL DEFAULT '0' COMMENT '0-未扫描；1-扫描中；2-扫描成功',
  `cron_type` tinyint(1) NOT NULL COMMENT '0-一次扫描；1-周期扫描',
  `date_time` varchar(16) DEFAULT NULL COMMENT '一次扫描',
  `week_time` varchar(10) DEFAULT NULL COMMENT '周期扫描',
  PRIMARY KEY (`id`),
  KEY `fk_userid` (`userid`),
  CONSTRAINT `fk_userid` FOREIGN KEY (`userid`) REFERENCES `tb_userinfo` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of tb_message
-- ----------------------------
