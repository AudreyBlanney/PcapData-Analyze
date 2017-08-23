#! /usr/bin/bash
if [ $# != 1 ] ; then
    echo "Usage: bash $0 website.war"
    exit 0
fi
read -p '请确定使用管理员权限运行脚本(Y/n):' con
if [[ $con != 'y' && $con != '' && $con != 'yes' ]]; then
        echo 'exit ! '
        exit 0
fi

pip -V
if [[ $? != '0' ]]; then
        python /root/assets/tool/ez_setup.py 2&> /dev/null
        cd /root/assets/tool/pip
        python setup.py install 2&> /dev/null
        if [[ $? != '0' ]]; then
            echo 'pip安装出错！'
            exit 0        
        fi
else
        echo 'pip OK！'
fi
yum install java -y 2&> /dev/null
if [[ $? != '0' ]]; then
        echo 'java安装出错！'
        exit 0
else
        echo 'java OK！'
fi
cp -r /root/assets/tool/tomcat /usr/share/
if [[ $? != '0' ]]; then
        echo 'tomcat安装出错！'
        exit 0
else
        echo 'tomcat安装 OK！'
fi
chmod a+x /usr/share/tomcat/bin/*.sh
cp $1 /usr/share/tomcat/webapps/
if [[ $? != '0' ]]; then
        echo '复制网站文件war包出错！'
        exit 0
else
        echo '网站搭建 OK！'
fi
yum install nmap -y 2&> /dev/null
if [[ $? != '0' ]]; then
        echo 'nmap安装出错！'
        exit 0
else
        echo 'nmap OK！'
fi
yum install mariadb-server -y 2&> /dev/null
if [[ $? != '0' ]]; then
        echo 'mysql安装出错！'
        exit 0
else
        echo 'mysql安装 OK！'
fi
systemctl start mariadb
if [[ $? != '0' ]]; then
        echo 'mysql启动出错！'
        exit 0
else
        echo 'mysql启动 OK！'
fi
systemctl enable mariadb
if [[ $? != '0' ]]; then
        echo 'mysql设置开机自启出错！'
        exit 0
else
        echo 'mysql设置开机自启 OK！'
fi
mysql_secure_installation
if [[ $? != '0' ]]; then
        echo 'mysql初始化出错！'
        exit 0
else
        echo 'mysql初始化 OK！'
fi
mysql -uroot -p </root/assets/tool/db.sql
if [[ $? != '0' ]]; then
        echo 'mysql导入数据出错！'
        exit 0
else
        echo 'mysql导入数据 OK！'
fi
pip install requests  > /dev/null
if [[ $? != '0' ]]; then
        echo 'pip安装requests出错！'
        exit 0
else
        echo 'requests OK！'
fi
pip install python-nmap  > /dev/null
if [[ $? != '0' ]]; then
        echo 'pip安装python-nmap出错！'
        exit 0
else
        echo 'python-nmap OK！'
fi
pip install pymysql  > /dev/null
if [[ $? != '0' ]]; then
        echo 'pip安装pymysql出错！'
        exit 0
else
        echo 'pymysql OK！'
fi
pip install flask  > /dev/null
if [[ $? != '0' ]]; then
        echo 'pip安装flask出错！'
        exit 0
else
        echo 'flask OK！'
fi
pip install dnspython  > /dev/null
if [[ $? != '0' ]]; then
        echo 'pip安装dnspython出错！'
        exit 0
else
        echo 'dnspython OK！'
fi
pip install python-crontab  > /dev/null
if [[ $? != '0' ]]; then
        echo 'pip安装paramiko出错！'
        exit 0
else
        echo 'python-crontab OK！'
fi
pip install gunicorn  > /dev/null
if [[ $? != '0' ]]; then
        echo 'pip安装gunicorn出错！'
        exit 0
else
        echo 'gunicorn OK！'
fi
pip install gevent  > /dev/null
if [[ $? != '0' ]]; then
        echo 'pip安装gevent出错！'
        exit 0
else
        echo 'gevent OK！'
fi
pip install tqdm  > /dev/null
if [[ $? != '0' ]]; then
        echo 'tqdm安装gevent出错！'
        exit 0
else
        echo 'tqdm OK！'
fi
chmod a+x ./start.sh
chmod a+x /etc/rc.d/rc.local
echo '/root/assets/start.sh' >> /etc/rc.d/rc.local
systemctl stop firewalld
systemctl disable firewalld
bash /root/assets/start.sh
echo 'OK！'
