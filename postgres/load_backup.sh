#sudo docker-compose up db_2 -d;
sudo cat ../.backup_2_10_2021.sql | sudo docker exec -i db_2 psql -U postgres;