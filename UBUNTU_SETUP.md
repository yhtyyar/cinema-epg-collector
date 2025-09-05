# Ubuntu Setup Guide for IPTV EPG Collector

This guide provides step-by-step instructions for manually deploying the IPTV EPG Collector on an Ubuntu server.

## 📋 Prerequisites

- Ubuntu 20.04 or later
- Root or sudo access
- At least 2GB RAM
- At least 10GB free disk space

## 🛠️ Installation Steps

### 1. Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
sudo apt install -y python3 python3-pip python3-venv curl git nodejs npm
```

### 3. Clone the Repository
```bash
git clone <repository-url>
cd cinema-epg-collector
```

### 4. Set Up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
```bash
cp .env.example .env
# Edit the .env file with your settings
nano .env
```

Important variables to configure:
- `TMDB_API_KEY` - Get this from https://www.themoviedb.org/settings/api
- `IPTV_HEADER_X_TOKEN` - Your IPTV provider token

### 6. Create Required Directories
```bash
mkdir -p data/posters cache logs
```

### 7. Run Data Collection Pipeline
```bash
python -m epg_collector.cli run-all
```

### 8. Start the API Server
```bash
uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://your-server-ip:8000`

### 9. Set Up Frontend (Optional)
```bash
cd frontend
npm ci
npm run build
```

Serve the built frontend files with any web server (nginx, Apache, etc.)

## 🔧 Running as a Service (Optional)

To run the application as a systemd service:

### 1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/cinema-epg.service
```

### 2. Add the following content:
```ini
[Unit]
Description=Cinema EPG Collector
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/cinema-epg-collector
ExecStart=/path/to/cinema-epg-collector/venv/bin/uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cinema-epg
sudo systemctl start cinema-epg
```

## 🔄 Updating Data

To update the movie data, run:
```bash
cd /path/to/cinema-epg-collector
source venv/bin/activate
python -m epg_collector.cli run-all
```

You can set up a cron job to automatically update data daily:
```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/cinema-epg-collector && /path/to/cinema-epg-collector/venv/bin/python -m epg_collector.cli run-all
```

## 📁 Directory Structure

After setup, your directory will contain:
- `data/` - Contains collected data and posters
- `cache/` - HTTP request cache
- `logs/` - Application logs
- `venv/` - Python virtual environment (created during setup)

## 🔒 Security Considerations

1. Change the default API port (8000) if exposing to the internet
2. Set up a reverse proxy (nginx) with SSL/TLS
3. Restrict API access with firewall rules
4. Use strong authentication for production deployments

## 🆘 Troubleshooting

### Common Issues:

1. **Permission errors**: Ensure the user running the service has read/write access to data, cache, and logs directories.

2. **Port already in use**: Change the port in the uvicorn command or stop the process using the port:
   ```bash
   sudo lsof -i :8000
   kill -9 <PID>
   ```

3. **Missing dependencies**: Ensure all required packages are installed:
   ```bash
   pip install -r requirements.txt
   ```

4. **TMDB API issues**: Verify your TMDB API key is correct and active.

### Check Logs:

Application logs are written to the `logs/` directory and to stdout when running the server.

For systemd service logs:
```bash
sudo journalctl -u cinema-epg -f
```