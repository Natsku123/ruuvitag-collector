# start services
sudo service dbus start
sudo service bluetooth start

# reset bluetooth adapter by restarting it
sudo hciconfig hci0 down
sudo hciconfig hci0 up

exec "$@"