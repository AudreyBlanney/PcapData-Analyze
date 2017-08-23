---
title: 开发文档说明

---
## 项目开发后端，主要使用python的flask框架作为和前段交互的中心
## 启动：run.py 
## 配置：config.py
## 功能：lib目录
## 结果：result目录
## 爆破字典：dict目录
	
### 进度条前后端交互

#### 输入域名：
	```
	index ? label domain remark userid openid 

		{'error':False|True, 'msgs':2}

	get_root_domain ? domain userid openid 

		{'error':False|True, 'msgs':25}

	get_domains ? domain userid openid  

		{'error':False|True, 'msgs':50}

	get_port ? domain lict userid openid 

		{'error':False|True, 'msgs':75}

	get_title ? domain lict userid openid  

		{'error':False|True, 'msgs':95}

	database ? domain lict userid openid  

		{'error':False|True, 'msgs':100}

	blast ?　domain userid openid

		{'error':False|True, 'msgs':ok}

	```

#### 输入ip：
	```
	index ?  ip label remark userid openid   

		{'error':False|True, 'msgs':2}

	get_port ? ip userid openid 

		{'error':False|True, 'msgs':75}

	get_title ? ip lict userid openid 

		{'error':False|True, 'msgs':95}

	database ? ip lict userid openid 

		{'error':False|True, 'msgs':100}

	blast ? domain userid openid

		{'error':False|True, 'msgs':ok}

	```

### 数据库说明

```
数据库

CREATE DATABASE db_assets;

用户信息表

CREATE TABLE tb_userinfo (
	id int(11) NOT NULL AUTO_INCREMENT,
	userid varchar(10) NOT NULL,
	qs_username varchar(40) NOT NULL COMMENT '用户名',
	qs_password varchar(255) NOT NULL COMMENT '密码',
	qs_email varchar(255) DEFAULT NULL COMMENT '邮箱',
	openid varchar(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY userid (userid) USING HASH
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

任务信息表

CREATE TABLE tb_message (
	id int(11) NOT NULL AUTO_INCREMENT,
	label varchar(100) NOT NULL,
	domainip varchar(100) NOT NULL,
	flag varchar(100) NOT NULL,
	remark varchar(100) DEFAULT NULL,
	userid varchar(100) NOT NULL,
	taskid varchar(100) NOT NULL,
	create_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	cron_time varchar(100) DEFAULT NULL,
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ip信息结果表

CREATE TABLE IF NOT EXISTS *_com (
			id INT NOT NULL AUTO_INCREMENT, 
			root_domain VARCHAR(50) DEFAULT '' COMMENT 'The root domain name',
			domain VARCHAR(50) DEFAULT '' COMMENT 'secondary domain', 
			title VARCHAR(100) DEFAULT '' NOT NULL COMMENT 'domain name corresponding to the business', 
			ip VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Have the ip', 
			port VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Open ports', 
			service VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Port corresponding to the service',
			service_info VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'fu wu xie xi',
			scan_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Scan time',
			is_confirm TINYINT(1)  NOT NULL DEFAULT '0' COMMENT 'Whether the port is open',
			domain_header VARCHAR(100) DEFAULT '' COMMENT 'domain fuzeren',
			domain_remark VARCHAR(100) DEFAULT '' COMMENT 'domains beizhu',
			root_domain_header VARCHAR(100) DEFAULT '' COMMENT 'root domains fuzeren',
			root_domain_remark VARCHAR(100) DEFAULT '' COMMENT 'root domains beizhu',
			ip_header VARCHAR(100) DEFAULT '' COMMENT 'ip fuzeren',
			ip_remark VARCHAR(100) DEFAULT '' COMMENT 'ip beizhu',
			port_remark VARCHAR(100) DEFAULT '' ,
			PRIMARY KEY ( id )
		) ENGINE=InnoDB DEFAULT CHARSET=utf8;

root_domain domain title ip port service scan_time is_confirk domain_remark social_name social_mail social_pwd social_source

弱口令结果表

CREATE TABLE IF NOT EXISTS *_com_Blast(
			id INT NOT NULL AUTO_INCREMENT, 
			ip VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Scan the ip',
			port VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'Scanned port', 
			user VARCHAR(50) DEFAULT '' NOT NULL COMMENT 'The corresponding user name', 
			pwd VARCHAR(100) DEFAULT '' NOT NULL COMMENT 'The corresponding password', 
			scan_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Scan time',
			PRIMARY KEY ( id )) ENGINE=InnoDB DEFAULT CHARSET=utf8;

社工库结果表

CREATE TABLE IF NOT EXISTS *_com_Social (
			id INT NOT NULL AUTO_INCREMENT,
			root_domain VARCHAR(100) DEFAULT '' COMMENT '',
			root_domain_email VARCHAR(100) DEFAULT '' COMMENT '***@root_domain.*** email', 
			social_name VARCHAR(100) DEFAULT '' COMMENT 'Domain name of the registrant',
			social_mail VARCHAR(100) DEFAULT '' COMMENT 'Domain name registration mailbox',
			social_pwd VARCHAR(100) DEFAULT '' COMMENT 'Domain name registrar mailbox password',
			social_source VARCHAR(100) DEFAULT '' COMMENT 'Domain Name Registrant Email Source',
			scan_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Scan time',
			PRIMARY KEY ( id )
		) ENGINE=InnoDB DEFAULT CHARSET=utf8;


```


### run.py解读

> 主要功能是调用flask框架，加入了10个路由

#### 1.`/和/index `

* 主要作用是接受前端发送的任务信息，判断是否正确，并存入数据库。

* 开始对用户信息的判断。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 如果输入域名，则过滤主域名。主要使用config.py里的getRootDomain函数。参数为域名(str)，返回为flase或者过滤后的域名(str)。判断任务是否已存在，不存在则建立任务，存在则返回错误信息。把任务信息存入json文档内，在results目录下对应任务名的目录下。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}。任务建立成功则返回正确信息，格式为json：{"error":False, "msg":2, }

* 如果输入ip，则判断ip，并获取ip列表。主要使用lib/get_ip_list.py里的get_ip_list函数，此模块不适用python3。参数为ip范围(str)，返回为ip列表(list)。判断任务是否已存在，不存在则建立任务，存在则返回错误信息。把任务信息存入json文档内，在results目录下对应任务名的目录下。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}。任务建立成功则返回正确信息，格式为json：{"error":False, "msg":2, }

#### 2.`/get_root_domain `	

* 主要是获取域名对应的兄弟域名，社工库查询和邮箱查询，返回进度，把结果存入json文件

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 获取域名对应的兄弟域名使用的是lib/get_root_domain_api.py的get_root_domain函数。参数为域名(str),返回为获取的兄弟域名(list)。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 社工库查询。使用的是lib/Social.py的Social函数。参数为域名(str),返回为社工库的邮箱弱口令(dict)。

* 泄露邮箱查询，使用lib/search_email.py的search函数。参数为域名(str),返回为获取的邮箱信息(dict)。

* 把结果写入json文件。

* 返回进度信息。

    > {"error":False, "msg":25, }

#### 3./get_domains

* 主要是获取二级域名，使用的是猪猪侠的工具加以修改。返回进度，把结果存入json文件。

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}> 	

* 打开获取到的兄弟域名文件，获取二级域名，使用的是lib/get_domain/wydomain.py里的get_domain_api函数，参数为兄弟域名列表(list)，返回为主域名对应二级域名的字典(dict)。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 把结果信息存入到json文件

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 返回进度条	

    > {"error":False, "msg":50, }

#### 4.`/get_port`

* 主要是进行端口扫描，结果存入json文档，返回进度

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}> 	

* 判断输入任务是域名或者ip，list为ip，dict为域名。打开获取到的二级域名结果文件或者ip列表文件。整理出ip列表。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* nmap扫描主机，使用的是lib/port_scan.py的Nmap函数，参数是ip列表(list),返回是端口信息(dict)。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 把结果信息存入到json文件

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

#### 5.`/get_title`

* 主要是获取页面的title，结果存入json文档，返回进度

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}> 	

* 判断输入任务是域名或者ip，list为ip，dict为域名。打开获取到的二级域名结果文件或者ip列表文件。整理出网站列表。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 获取网站title，使用的是lib/get_title_requests.py的get_titles函数。参数为子域名或者ip的列表(list)，返回为title信息(dict)。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 把结果信息存入到json文件

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

#### 6.`/database`

* 主要是写入数据到数据库

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}> 	
 
* 把域名转换为表名，把.和-转换为_，创建表

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 判断ip或域名，如果是ip，从文件导入端口和title信息，写入数据库。

	> 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 如果是域名，从文件导入兄弟域名，二级域名，端口信息，title，社工库，email，写入数据库。

	> 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

#### 7.`/database`

* 主要是进行弱口令爆破，并写入数据库

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 创建数据表，存爆破结果

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 使用线程把爆破放入后台，使用的是lib/Blast.py的Blast函数，参数为端口信息(dict)，数据库的链接(db)，表名(str),无返回。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

#### 8.`add_cron`

* 主要作用是添加定时任务

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 主要使用的是lib/Cron.py的Crons类，添加任务是add_job函数，参数为任务id(str),任务时间(date),域名(str),用户id(str),用户认证id(str),返回为true/flase。

* 写入数据库，成功和失败顺序相反。

    > 错误信息格式为json：{"taskid":True/False}

#### 9.`del_cron`

* 判断用户信息。

    > 错误信息格式为json：{"error":True, "msg":"error message", "trse":True/False}

* 主要使用的是lib/Cron.py的Crons类，添加任务是del_job函数，参数为任务id(str)，返回为true/flase.

* 删除任务后，把数据从数据库删除。

    > 错误信息格式为json：{"taskid":True/False}

### run.py备注,返回的json格式说明：
```
error 选项代表是否出错
msg 选项代表错误信息后者进度
trse 选项如果是True，则向用户显示msg信息，跳转新建任务
	 如果是False，则直接退出，提示任务失败，跳转新建任务
```


### run.py里结果json文件数据格式
```


root_domain.json

	[
		'lanou3g.com',
		'hello.com'
	]

domains.json
	{
		'lanou3g.com':{
			'oa.lanou3g.com':[
				'123.234.234.1',
				'123.534.56.5',
				'234.435.6.56'
			],
			'bbs.lanou3g.com':[
				'none'
			]
		},
		'hello.com':{
			'none':[
				'none'
			]
		}
	}

ports.json
	{
		'123.234.234.1':{
			'22':'ssh',
			'3306':'mysql',
		},
		'234.435.6.56':{
			'none':'none'
		},
		'none':{
			'none':'none'
		}
	}

titles.json
	[
		'oa.lanou3g.com':'OA'
		'bbs.lanou3g.com':'none'
	]

Socile.json
	{
		'lanou3g.com':[
			('liuhui','lanou3g@lanou.com','123456','mi_com'),
		],
		'hello.com':[
			('none','none','none','none')
		]
	}

```


## lib目录下脚本分析

### |-- __init__.py

	* 加载模块需要

### |-- Blast.py

	* 弱口令爆破模块，接口函数为Blast，加载字典为dict目录下的username和password，结果存入到*_Blast表里。
	* 主要爆破的弱口令有：ftp、telnet、mysql、mssql 、mongodb、redis、postgresql、memcached、elasticsearch、tomcat。
	* 主要参考工具F-Scrack爆破。

### |-- Cron.py

	* 计划任务模块，接口函数为Crons，通过linux系统的计划任务，来完成定时扫描。
	* 使用crontab模块。

### |-- cron_run.py

	* 计划任务执行模块，模拟系统的资产发现流程。是Cron.py的执行脚本。

### |-- get_ip_list.py

	* 获取ip列表，通过输入ip地址范围，生成一个个的ip

### |-- get_root_domain_api.py

	* 进行根域名发现，使用爱站、站长之家、alexa、links的api，输入一个厂商的一个根域名，获取所有的根域名。
	* 结构函数为get_root_domain，返回结果为list

### |-- get_title_requests.py

	* 进行业务发现，通过访问域名，获取title，判断也为类型
	* 接口函数为get_titles，输入为ip或者域名的list，返回为dict

### |-- myparser.py

	* 邮箱扫描工具的依赖。

### |-- port_scan.py

	* 端口扫描模块，主要使用nmap进行端口扫描，同事获取服务信息，
	* 接口函数为Nmap，参数为ip的list，结果为dict

### |-- search_email.py

	* 主要是获取网络上泄露的企业员工邮箱
	* 主要使用theharvester工具，
	* 接口函数为search，参数为域名list，结果为dict

### |-- Social.py

	* 主要是社工库的查询，通过email.70sec.com查询泄露的邮箱密码。
	* 接口函数1为Social，参数为域名list，获取注册者邮箱，返回结果为dict
	* 接口函数2为search_soc，参数为邮箱，返回结果为list

### |-- get_domain 目录

	* 使用猪猪侠的二级域名搜索工具，从互联网各大网站获取二级域名
	* 主要使用wydomain.py的get_domain_api函数，功能是传入主域名list，获取到dict（主域名，子域名，ip）

## results 目录

	* 主要是存放每个任务的扫描结果，以json文件保存。

## dict 目录

	* 主要是存放爆破用户名和口令

## tool 目录

	* 存放一些搭建环境软件的安装包，
	* pip目录是python的pip安装包
	* tomcat目录是tomcat的安装包
	* db.sql是初始化数据库时，建立的原始数据库。
	* ez_setup.py是安装python的pip需要的支持包
	* *.war是前台页面的war包。

## configs.py 

	* 主要存放配置，连接数据库的时候，需要修改用户名个密码

## install.sh 
	
	* 主要是搭建环境的脚本，在一台刚装好的centos7系统了，使用此脚本，快速搭建资产环境，
	* 具体用法：
		* 确定刚装好的机器，联网。
		* 执行yum update -y 对系统进行升级
		* 将assets目录存放到root的根目录
		* cd进入assets目录，把前台页面的war包存放如tool目录。
		* 执行bash ./install.sh ./tool/*.war   （*.war是指前台的war包，写具体包的名字）
		* 初始化数据库时，需要输入mysql的root用户的密码
		* 把mysql的用户密码写入配置文件。

## start.sh

	* 启动环境的脚本，会写入到开机启动项