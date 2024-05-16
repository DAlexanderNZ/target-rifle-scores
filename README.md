# target-rifle-scores
## Docker Deployment
1. Install Docker on the host system
2. Edit `database.ini.example` and rename it to `database.ini. Change user and password to match your custom the values in the docker compose file.
3. Edit `docker-compose.yml` and change the database variables `POSTGRES_USER` and `POSTGRES_PASSWORD` to match the custom values in `database.ini`
4. Run `docker-compose up` in the app directory to start the database and web server

## Build Docker App Image
1. `docker build -t target-rifle-scores .`
2. Run the image from Docker Desktop

## Manual Install

### Database (Linux)
1. Install postgresql for your system
2. Switch to the postgres user:`sudo -iu postgres psql`
3. Initialize the data directory: `initdb --locale $LANG -E UTF8 -D '/var/lib/postgres/data/' --data-checksums`
4. Start the postgresql service: `systemctl start postgresql`
5. Switch to the postgres user and run psql: `sudo -u postgres psql`
6. Create a user: `CREATE USER user WITH PASSWORD 'password';`
7. Create database: `CREATE DATABASE target_rifle_scores`
8. Grant permissions to the new user: `GRANT ALL PRIVILEGES ON DATABASE target_rifle_scores TO user;`
9. Grant permissions on the database schema: `\c target_rifle_scores` then `GRANT ALL ON SCHEMA public TO user;`