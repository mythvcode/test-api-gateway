# Скрипт для управления api-gateway
# перед использованием должна быть создана virtualenv 
# с утановленными в нее зависимостями


PROJECTDIR=/opt/test-api-gateway
ENVDIR=env # директория с virtualenv (должна быть создана в PROJECTDIR)
APPNAME=api-gateway
ACTIVATE=$PROJECTDIR/$ENVDIR/bin/activate
DAEMON=gunicorn
APP=wsgi:app
BIND=0.0.0.0:8035
PIDFILE=/var/run/$APPNAME.pid
LOGFILE=/var/log/$APPNAME/$APPNAME.log
ACCESSLOGFILE=/var/log/$APPNAME/access.log
WORKERS=3

case "$1" in
  start)
        echo "Starting" "$APPNAME"
        source $ACTIVATE
        cd $PROJECTDIR
        $DAEMON --daemon --bind=$BIND \
		--pid=$PIDFILE --workers=$WORKERS   \
	       	--log-file=$LOGFILE --access-logfile $ACCESSLOGFILE  \
		$APP
        if [ $? -eq 0 ]
	then
		echo "Done"
	else
		echo "Fail start api see " $LOGFILE
		exit 1
	fi
    ;;
  stop)
        echo  "Stopping" "$APPNAME"
        pkill -F $PIDFILE -f $DAEMON 2>$1 > /dev/null
	if [ $? -ne 0 ]
	then
		echo "Fail stop api"
	fi
    ;;
  restart)
    	$0 stop
    	$0 start
    ;;
  *)
    echo Usge "api-gateway" "{start|stop|restart}"
    exit 1
    ;;
esac

exit 0

