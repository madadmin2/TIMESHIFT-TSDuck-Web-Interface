#!/bin/bash
# IPTV Timeshift Server Automated Installer

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Professional Installation...${NC}"

# 1. Update and Dependencies
sudo apt update && sudo apt install python3 python3-pip wget -y

# 2. Install TSDuck
echo -e "${BLUE}📦 Installing TSDuck Framework...${NC}"
wget https://github.com/tsduck/tsduck/releases/download/v3.34-3151/tsduck_3.34-3151.ubuntu2204_amd64.deb
sudo apt install ./tsduck_3.34-3151.ubuntu2204_amd64.deb -y
rm tsduck_3.34-3151.ubuntu2204_amd64.deb

# 3. Install Python requirements
echo -e "${BLUE}🐍 Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

# 4. Create Buffers
echo -e "${BLUE}📂 Setting up buffer directories...${NC}"
sudo mkdir -p /var/lib/tsduck/buffer
sudo chmod -R 777 /var/lib/tsduck/buffer

# 5. Create Systemd Service
echo -e "${BLUE}⚙️ Configuring background service...${NC}"
CURRENT_DIR=$(pwd)
sudo bash -c "cat > /etc/systemd/system/timeshift.service <<EOF
[Unit]
Description=IPTV Timeshift Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

# 6. Enable and Start
sudo systemctl daemon-reload
sudo systemctl enable timeshift.service
sudo systemctl start timeshift.service

echo -e "${GREEN}✅ INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}🌐 Access Web UI at http://$(hostname -I | awk '{print $1}'):80${NC}"