chmod +x ./files/pre-rush.sh
chmod +x ./files/build_jail.sh
chmod +x ./files/process_user_auth_kc.sh
chmod +x ./files/process_user_auth.sh
chmod +x ./files/update_user_jail.sh
docker build --network host  -t overleaf_backup_image .
