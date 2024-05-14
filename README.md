# target-rifle-scores

## Build Docker Image
1. `docker build -t target-rifle-scores .`
2. Run the image from Docker Desktop

## Install

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