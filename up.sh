docker compose down
cd docker_tools
sh install.sh
cd ..
mkdir -p downloads
mkdir -p etc
mkdir -p log
docker compose up -d

