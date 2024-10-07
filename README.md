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
7. Create database: `CREATE DATABASE target_rifle_scores;`
8. Grant permissions to the new user: `GRANT ALL PRIVILEGES ON DATABASE target_rifle_scores TO user;`
9. Grant permissions on the database schema: `\c target_rifle_scores` then `GRANT ALL ON SCHEMA public TO user;`

### Application
1. Clone Repo
2. Install Python 3 for your distro
3. Create a virtual environment on the repo directory: `python3 -m venv target-rifle-scores`
4. Activate the virtual environment: `source target-rifle-scores/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
5. Edit `database.ini.example` and rename it to `database.ini`. Change `user` and `password` to match your custom the values set in psql for the database
6. Edit `target-rifle-scores.service.example` to change `username` occurences in `[Service]` to your account username
7. Copy `configuration/target-rifle-scores.service.example` to systemd: `cp target-rifle-scores.service.example /etc/systemd/system/target-rifle-scores.service`
8. Start the application: `sudo systemctl start target-rifle-scores`
9. Check that the application started without errors: `sudo systemctl status target-rifle-scores`
10. Enable the application `sudo systemctl enable target-rifle-scores`

### Nginx Proxy
Nginx is used to proxy requests to the application. This allows for easy use of Let's Encrypt SSL certificates via [Certbot](https://certbot.eff.org/instructions?ws=nginx&os=debianbuster)
1. Install Nginx for your system
2. Edit `configuration/target-rifle-scores.nginx.example` and change the hostname to your domain and the username in `proxy_pass` to your account username
3. Copy `configuration/target-rifle-scores.nginx.example` to nginx sites-available: `cp configuration/target-rifle-scores.nginx.example /etc/nginx/sites-available/target-rifle-scores`
4. Check the site file configuration: `sudo nginx -t`
5. Enable the site: `sudo ln -s /etc/nginx/sites-available/target-rifle-scores /etc/nginx/sites-enabled/`
6. Follow [Certbot](https://certbot.eff.org/instructions?ws=nginx&os=debianbuster) instructions to install a certificate for your domain and configure nginx to use it
7. Restart nginx: `sudo systemctl restart nginx` 

### Front End
The new front end is built with Vue.js and is served by the Flask application. To build the front end go to the frontend repo and run `npm run build`. Copy the contents of the `dist` directory to the `static` directory in the Flask app. The front end will be served by the Flask app.
The Flask templates will be removed at a later date.