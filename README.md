📡 Professional IPTV Timeshift Server

A powerful, high-performance multicast UDP timeshift solution for IPTV streams. Built with FastAPI, Vue.js, and TSDuck.

🚀 Quick Start (Automated Installation)
Run the following commands to install the server and all its dependencies:
**************************************************************
git clone https://github.com/madadmin2/TIMESHIFT-TSDuck-Web-Interface.git
cd TIMESHIFT-TSDuck-Web-Interface
chmod +x install.sh
sudo ./install.sh
**************************************************************

🔐 Default Login Credentials

After installation, access the Web UI at: http://your-server-ip:80

Username: admin (or leave empty if first time)

Password: admin (or leave empty if first time)

⚠️ Security Tip: The current version uses client-side authentication for ease of use in private networks. You can change credentials by modifying the doLogin method in index.html.

🛠 Features

RAM & Disk Buffering: Use /dev/shm for speed or disk storage for long delays.

TSDuck Integration: Professional-grade stream manipulation using tsp.

Interface Monitoring: Real-time bandwidth tracking for all network interfaces.

Auto-Recovery: Streams automatically restart after a system reboot or crash.

📁 Project Structure

main.py - FastAPI backend and stream management logic.

index.html - Modern Vue.js dashboard.

install.sh - Full system automation script.

requirements.txt - Python dependencies.

⚖️ License

This project is licensed under the MIT License.

☕ Support

Created by Iliya P. © 2026.

If this project helped you, consider supporting the work:

Revolut: revolut.me/YOUR_USER

PayPal: paypal.me/YOUR_USER
