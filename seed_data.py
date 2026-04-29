"""
SSOD — seed_data.py
Populates the database with realistic logs and alerts for testing
Author: SYLVAH™ | 2026
Run: python seed_data.py (with venv active, from backend folder)
"""

import requests
import random
import time
from datetime import datetime

BASE = "http://localhost:5000/api"

# ── Login as admin to get token ──
print("🔐 Logging in as admin...")
res = requests.post(f"{BASE}/auth/login", json={"username":"admin","password":"admin123"})
if res.status_code != 200:
    print("❌ Login failed:", res.json())
    exit(1)
token = res.json()["token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print("✅ Logged in successfully\n")

# ── Seed Alerts ──
alerts = [
    {"title":"Multiple failed SSH login attempts from 192.168.1.200","severity":"critical","category":"Security","source":"ids-engine","description":"5 failed attempts in 60 seconds — possible brute force attack"},
    {"title":"Unauthorized API access attempt blocked","severity":"high","category":"Authentication","source":"api-gateway","description":"JWT token from revoked session used to access /api/users/"},
    {"title":"CPU usage exceeded 85% for 5 consecutive minutes","severity":"high","category":"Performance","source":"perf-agent","description":"Node app-server-01 experiencing sustained high load"},
    {"title":"Database connection pool at 90% capacity","severity":"medium","category":"Database","source":"db-primary","description":"Active connections: 18/20 — consider increasing pool size"},
    {"title":"SSL certificate expires in 7 days","severity":"medium","category":"System","source":"ssl-monitor","description":"Certificate for api.ssod.local expires on 2026-05-02"},
    {"title":"Unusual outbound traffic detected on port 8443","severity":"high","category":"Network","source":"firewall-01","description":"2.3GB sent to unknown external IP in last hour"},
    {"title":"Log rotation completed successfully","severity":"low","category":"System","source":"sys-scheduler","description":"Archived 847MB of logs to /var/logs/archive/2026-04/"},
    {"title":"New user account created from unrecognized device","severity":"medium","category":"Authentication","source":"auth-service","description":"Account viewer_05 registered from IP 10.0.0.99 — first seen device"},
    {"title":"Disk usage on /var reached 78%","severity":"medium","category":"System","source":"sys-monitor","description":"Disk /var at 78% — threshold is 80%. Cleanup recommended"},
    {"title":"Privilege escalation attempt detected and blocked","severity":"critical","category":"Security","source":"ids-engine","description":"Process tried to gain root via sudo exploit — blocked by policy"},
    {"title":"API response time degraded — avg 1.2s","severity":"low","category":"Performance","source":"perf-agent","description":"Endpoint /api/logs/ averaging 1.2s response (threshold: 0.5s)"},
    {"title":"Scheduled backup completed successfully","severity":"low","category":"System","source":"backup-agent","description":"Full DB backup to s3://ssod-backups/2026-04-25/ — 2.1GB"},
]

print(f"📢 Seeding {len(alerts)} alerts...")
for a in alerts:
    r = requests.post(f"{BASE}/alerts/add", json=a, headers=headers)
    status = "✅" if r.status_code == 201 else "❌"
    print(f"  {status} [{a['severity'].upper()}] {a['title'][:60]}")
    time.sleep(0.1)

# ── Resolve some alerts ──
print("\n✅ Resolving some alerts...")
res2 = requests.get(f"{BASE}/alerts", headers=headers)
all_alerts = res2.json()
# Resolve low and some medium ones
to_resolve = [a for a in all_alerts if a['severity'] in ['low'] ][:4]
for a in to_resolve:
    r = requests.put(f"{BASE}/alerts/resolve/{a['id']}", headers=headers)
    if r.status_code == 200:
        print(f"  ✅ Resolved: {a['title'][:60]}")

# ── Seed Logs ──
logs = [
    {"source":"Auth","log_type":"security","action":"Admin login from 192.168.1.45","details":"MFA verified — device fingerprint matched"},
    {"source":"Auth","log_type":"security","action":"Failed login attempt — user viewer_03","details":"4 consecutive failures — account locked for 15 minutes"},
    {"source":"System","log_type":"info","action":"Health check completed — all nodes nominal","details":"8 nodes checked · Score: 160/200 · avg response: 12ms"},
    {"source":"API","log_type":"warning","action":"Rate limit threshold reached on /api/metrics/live","details":"85% of rate limit consumed — auto-throttling enabled"},
    {"source":"Admin","log_type":"security","action":"Security policy updated by admin","details":"Password complexity rules strengthened — min 8 chars + special char"},
    {"source":"System","log_type":"info","action":"Database backup initiated","details":"Backup target: s3://ssod-backups/2026-04-25/ · Estimated size: 2.1GB"},
    {"source":"Auth","log_type":"info","action":"New user registered — noor","details":"Role: viewer · Email: noor@ssod.io · Device: Chrome/Windows"},
    {"source":"Security","log_type":"error","action":"IDS rule triggered — port scan detected","details":"Source IP: 203.0.113.42 · Scanned 847 ports in 30 seconds · Blocked"},
    {"source":"System","log_type":"info","action":"Log rotation executed by scheduler","details":"Rotated 847MB · Compressed to 124MB · Archived successfully"},
    {"source":"Admin","log_type":"info","action":"User role updated — operator_01 → admin","details":"Changed by: admin · Previous role: operator · New role: admin"},
    {"source":"API","log_type":"info","action":"Metrics endpoint polled — live data served","details":"Response: 200 OK · CPU: 43.5% · RAM: 90.4% · DISK: 65.7%"},
    {"source":"Security","log_type":"security","action":"Intrusion attempt blocked by firewall","details":"Rule #447 triggered · Source: 198.51.100.23 · Protocol: TCP/8443"},
    {"source":"Auth","log_type":"warning","action":"Token refresh failed — session expired","details":"User: viewer_02 · Token age: 9h · User redirected to login"},
    {"source":"System","log_type":"error","action":"SSL certificate renewal daemon failed","details":"Error: ACME challenge failed for api.ssod.local · Manual renewal required"},
    {"source":"Admin","log_type":"info","action":"Dashboard configuration saved","details":"Widget layout updated by admin · Affected role: operator"},
]

print(f"\n📋 Seeding {len(logs)} logs...")
for l in logs:
    r = requests.post(f"{BASE}/logs/add", json=l, headers=headers)
    status = "✅" if r.status_code == 201 else "❌"
    print(f"  {status} [{l['log_type'].upper()}] {l['action'][:60]}")
    time.sleep(0.1)

print(f"\n🎉 Seeding complete!")
print(f"   Alerts created: {len(alerts)}")
print(f"   Logs created:   {len(logs)}")
print(f"\nRefresh your browser to see the data.")