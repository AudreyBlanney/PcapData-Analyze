-- 导出 db_assets 的数据库结构
CREATE DATABASE IF NOT EXISTS `db_assets` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `db_assets`;

-- 导出  表 db_assets.tb_userinfo 结构
CREATE TABLE IF NOT EXISTS `tb_userinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` varchar(10) NOT NULL,
  `qs_username` varchar(40) NOT NULL COMMENT '用户名',
  `qs_password` varchar(255) NOT NULL COMMENT '密码',
  `qs_email` varchar(255) DEFAULT NULL COMMENT '邮箱',
  `openid` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userid` (`userid`) USING HASH
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- 正在导出表  db_assets.tb_userinfo 的数据：~2 rows (大约)
/*!40000 ALTER TABLE `tb_userinfo` DISABLE KEYS */;
INSERT INTO `tb_userinfo` (`id`, `userid`, `qs_username`, `qs_password`, `qs_email`, `openid`) VALUES
    (1, '00001', 'admin', 'e10adc3949ba59abbe56e057f20f883e', '', 'e10adc3949ba59ab');


-- 导出  表 db_assets.tb_message 结构
CREATE TABLE IF NOT EXISTS `tb_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(100) NOT NULL COMMENT '业务标签',
  `domainip` varchar(100) NOT NULL COMMENT '域名或者ip',
  `flag` varchar(100) NOT NULL COMMENT '域名IP的标识',
  `remark` varchar(100) DEFAULT NULL COMMENT '备注',
  `userid` varchar(10) NOT NULL COMMENT '用户id',
  `taskid` varchar(100) NOT NULL COMMENT '任务id',
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `cron_time` varchar(100) DEFAULT NULL COMMENT '计划任务时间',
  PRIMARY KEY (`id`),
  KEY `fk_userid` (`userid`),
  CONSTRAINT `fk_userid` FOREIGN KEY (`userid`) REFERENCES `tb_userinfo` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;