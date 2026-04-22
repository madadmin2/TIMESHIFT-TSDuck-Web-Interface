import os, json, subprocess, psutil, time, asyncio
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "streams.json")
RAM_DIR = "/dev/shm/tsduck_buffer"
DISK_DIR = "/var/lib/tsduck/buffer"

# Create directories and set permissions on startup
for d in [RAM_DIR, DISK_DIR]:
    os.makedirs(d, exist_ok=True)
    os.system(f"chmod -R 777 {d}")

def get_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return []
    return []

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

def run_tsp(data):
    """ Function to start tsp process with dynamic parameters """
    chan_name = data['name'].replace(' ', '_') 
    
    # Kill old processes for security:
    os.system(f"pkill -9 -f '{data['output']}'")
    os.system(f"pkill -9 -f '{chan_name}'") 
    
    use_disk = data.get('use_disk', False)
    base_path = DISK_DIR if use_disk else RAM_DIR
    
    chan_dir = os.path.join(base_path, chan_name)
    os.makedirs(chan_dir, exist_ok=True)
    os.system(f"chmod -R 777 {chan_dir}")
    
    # Optimized buffer for stability
    ram_buffer = "256" if not use_disk else "512"

    # Find interface IP addresses automatically
    in_iface_name = data.get('in_iface', '')
    out_iface_name = data.get('out_iface', '')
    in_ip, out_ip = "0.0.0.0", "0.0.0.0"
    
    for nic, addrs in psutil.net_if_addrs().items():
        if nic == in_iface_name:
            in_ip = next((a.address for a in addrs if a.family == 2), "0.0.0.0")
        if nic == out_iface_name:
            out_ip = next((a.address for a in addrs if a.family == 2), "0.0.0.0")

    cmd = [
        "chrt", "-f", "50",
        "tsp", "--realtime", 
        "--buffer-size-mb", ram_buffer,
        "-I", "ip", data['input'], "--local-address", in_ip, "--reuse-port",
        "-P", "timeshift", "--time", str(int(data['delay']) * 1000), "--directory", chan_dir,
        "-O", "ip", data['output'], "--local-address", out_ip, "--packet-burst", "4"
    ]
    
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    print(f"Started: {data['name']} ({in_ip} -> {out_ip})")

def auto_start_streams():
    lock_file = "/tmp/streams.lock"
    if os.path.exists(lock_file):
        return

    with open(lock_file, "w") as f:
        f.write("1")

    os.system("pkill -9 tsp")
    time.sleep(2)
    db = get_db()
    for channel in db:
        run_tsp(channel)

@app.post("/api/start")
async def start(request: Request):
    data = await request.json()
    run_tsp(data)
    
    db = get_db()
    db = [ch for ch in db if ch.get('name') != data['name']]
    db.append(data)
    save_db(db)
    return {"status": "ok"}

@app.get("/api/interfaces")
def interfaces():
    res = []
    for nic, addrs in psutil.net_if_addrs().items():
        if nic == 'lo' or nic.startswith('veth'): continue
        try:
            s1 = psutil.net_io_counters(pernic=True).get(nic)
            time.sleep(0.1)
            s2 = psutil.net_io_counters(pernic=True).get(nic)
            in_speed = round((s2.bytes_recv - s1.bytes_recv) * 8 / 1024 / 1024 / 0.1, 2)
            out_speed = round((s2.bytes_sent - s1.bytes_sent) * 8 / 1024 / 1024 / 0.1, 2)
            ip = next((a.address for a in addrs if a.family == 2), "0.0.0.0")
            res.append({"name": nic, "ip": ip, "in_mbps": in_speed, "out_mbps": out_speed})
        except: continue
    return res

@app.get("/api/system_stats")
def system_stats():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage(DISK_DIR).percent
    }

@app.post("/api/stop")
@app.post("/api/delete")
async def handle_stop_delete(request: Request):
    data = await request.json()
    os.system(f"pkill -9 -f '{data['output']}'")
    db = get_db()
    db = [ch for ch in db if ch.get('name') != data['name']]
    save_db(db)
    chan_name = data['name'].replace(' ', '_')
    os.system(f"rm -rf {RAM_DIR}/{chan_name}/*")
    os.system(f"rm -rf {DISK_DIR}/{chan_name}/*")
    return {"status": "ok"}

@app.get("/api/channels")
def channels():
    db = get_db()
    active_cmds = ""
    for p in psutil.process_iter(['cmdline']):
        try:
            if p.info['cmdline'] and 'tsp' in p.info['cmdline'][0]:
                active_cmds += " ".join(p.info['cmdline']) + " "
        except: continue
    for ch in db:
        ch['running'] = ch.get('output', '') in active_cmds
    return db

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

if __name__ == "__main__":
    # Cleanup old processes
    os.system("pkill -9 tsp")
    
    # Wait for network
    print("Waiting 20 seconds for network...")
    time.sleep(20)
    
    # Start channels
    auto_start_streams()
    
    # Start web server on port 80
    uvicorn.run(app, host="0.0.0.0", port=80, workers=1, reload=False)