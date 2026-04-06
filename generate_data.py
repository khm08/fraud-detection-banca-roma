"""
Synthetic Data Generator for Banca Roma Digitale
Generates realistic banking transaction data with embedded fraud patterns:
- Card-present (CP) and card-not-present (CNP) fraud
- First-party fraud (friendly fraud, bust-out)
- Third-party fraud (stolen cards, account takeover)
- Synthetic identity fraud
- Money mule activity
- Phishing-related account takeover (ATO)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import hashlib
import os

np.random.seed(42)
random.seed(42)

NUM_CUSTOMERS = 2000
NUM_TRANSACTIONS = 50000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)

# ============================================================
# 1. CUSTOMERS TABLE
# ============================================================
print("Generating customers...")

italian_first = ["Marco", "Giulia", "Alessandro", "Francesca", "Lorenzo", "Sofia",
                 "Andrea", "Chiara", "Matteo", "Valentina", "Luca", "Elena",
                 "Giovanni", "Maria", "Federico", "Anna", "Davide", "Sara",
                 "Simone", "Laura", "Roberto", "Paola", "Antonio", "Martina",
                 "Giuseppe", "Alessia", "Riccardo", "Elisa", "Fabio", "Giorgia"]

italian_last = ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano",
                "Colombo", "Ricci", "Marino", "Greco", "Bruno", "Gallo",
                "Conti", "De Luca", "Mancini", "Costa", "Giordano", "Rizzo",
                "Lombardi", "Moretti", "Barbieri", "Fontana", "Santoro", "Mariani",
                "Rinaldi", "Caruso", "Ferrara", "Galli", "Martini", "Leone"]

rome_zones = ["Trastevere", "Prati", "Testaccio", "Monti", "EUR", "Parioli",
              "San Giovanni", "Flaminio", "Nomentano", "Esquilino", "Ostiense",
              "Monteverde", "Centocelle", "Tor Vergata", "Balduina"]

customers = []
for i in range(NUM_CUSTOMERS):
    cid = f"CUS{i+1:06d}"
    first = random.choice(italian_first)
    last = random.choice(italian_last)
    age = np.random.randint(18, 78)
    zone = random.choice(rome_zones)
    account_open = START_DATE - timedelta(days=np.random.randint(30, 2000))
    account_type = np.random.choice(["checking", "savings", "business"], p=[0.6, 0.25, 0.15])
    monthly_income = round(np.random.lognormal(mean=8.0, sigma=0.5), 2)
    credit_score = np.random.randint(300, 850)

    # Flag some customers as synthetic identities (1.5%)
    is_synthetic = 1 if np.random.random() < 0.015 else 0
    # Flag some as mule accounts (1%)
    is_mule = 1 if np.random.random() < 0.01 and not is_synthetic else 0

    # Synthetic identities have unusual patterns
    if is_synthetic:
        age = np.random.randint(19, 28)
        account_open = START_DATE + timedelta(days=np.random.randint(0, 180))
        credit_score = np.random.randint(620, 720)

    # Mule accounts
    if is_mule:
        account_open = START_DATE + timedelta(days=np.random.randint(0, 120))
        monthly_income = round(np.random.uniform(800, 1500), 2)

    email_domain = random.choice(["gmail.com", "yahoo.it", "libero.it", "outlook.com", "hotmail.it"])
    phone_prefix = random.choice(["+39 06", "+39 33", "+39 34", "+39 32"])
    phone = f"{phone_prefix} {np.random.randint(1000000, 9999999)}"

    customers.append({
        "customer_id": cid,
        "first_name": first,
        "last_name": last,
        "age": age,
        "city": "Roma",
        "zone": zone,
        "email": f"{first.lower()}.{last.lower()}{np.random.randint(1,999)}@{email_domain}",
        "phone": phone,
        "account_type": account_type,
        "account_open_date": account_open.strftime("%Y-%m-%d"),
        "monthly_income_eur": monthly_income,
        "credit_score": credit_score,
        "is_synthetic_identity": is_synthetic,
        "is_mule_account": is_mule,
        "kyc_verified": 0 if is_synthetic else 1,
        "id_verification_method": random.choice(["SPID", "CIE", "passport"]) if not is_synthetic else "forged_document",
    })

df_customers = pd.DataFrame(customers)

# ============================================================
# 2. DEVICES TABLE
# ============================================================
print("Generating devices...")

devices = []
for i, cust in enumerate(customers):
    num_devices = np.random.randint(1, 4)
    for d in range(num_devices):
        did = f"DEV{i*4+d+1:07d}"
        device_type = np.random.choice(["mobile_ios", "mobile_android", "desktop_windows", "desktop_mac", "tablet"], p=[0.35, 0.3, 0.2, 0.1, 0.05])
        fingerprint = hashlib.md5(f"{cust['customer_id']}_{did}_{d}".encode()).hexdigest()[:16]

        # Generate realistic IP
        if np.random.random() < 0.85:
            ip = f"93.{np.random.randint(32,50)}.{np.random.randint(0,255)}.{np.random.randint(1,254)}"  # Italian IP
        else:
            ip = f"{np.random.randint(1,223)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(1,254)}"

        devices.append({
            "device_id": did,
            "customer_id": cust["customer_id"],
            "device_type": device_type,
            "device_fingerprint": fingerprint,
            "ip_address": ip,
            "os_version": random.choice(["iOS 17", "iOS 18", "Android 14", "Android 15", "Windows 11", "macOS Sonoma"]),
            "is_jailbroken": 1 if np.random.random() < 0.02 else 0,
            "first_seen": (datetime.strptime(cust["account_open_date"], "%Y-%m-%d") + timedelta(days=np.random.randint(0, 60))).strftime("%Y-%m-%d"),
            "is_known_device": 1,
        })

df_devices = pd.DataFrame(devices)

# ============================================================
# 3. TRANSACTIONS TABLE
# ============================================================
print("Generating transactions...")

merchant_categories = {
    "grocery": (10, 150),
    "restaurant": (15, 120),
    "gas_station": (20, 100),
    "online_shopping": (5, 500),
    "electronics": (50, 2000),
    "travel": (100, 3000),
    "subscription": (5, 50),
    "atm_withdrawal": (50, 500),
    "transfer": (50, 5000),
    "utility_bill": (30, 300),
    "pharmacy": (5, 100),
    "clothing": (20, 400),
    "entertainment": (10, 200),
    "insurance": (50, 500),
    "crypto_exchange": (100, 10000),
}

merchants_rome = [
    "Conad Trastevere", "Carrefour EUR", "Esselunga Parioli", "Bar Roma Centro",
    "Ristorante Da Mario", "Pizzeria Baffetto", "Shell Via Tiburtina",
    "ENI Stazione Ostiense", "Amazon.it", "Zalando.it", "MediaWorld Roma",
    "Unieuro Porta di Roma", "Trenitalia", "Alitalia", "Netflix",
    "Spotify", "Poste Italiane ATM", "UniCredit ATM", "Enel Energia",
    "ACEA Roma", "Farmacia Trastevere", "Zara Via del Corso",
    "Cinema The Space", "Generali Assicurazioni", "Binance", "Coinbase"
]

transactions = []
fraud_labels = []

for t in range(NUM_TRANSACTIONS):
    txn_id = f"TXN{t+1:08d}"
    cust = random.choice(customers)
    cust_id = cust["customer_id"]
    cust_devices = [d for d in devices if d["customer_id"] == cust_id]

    # Timestamp
    ts = START_DATE + timedelta(
        days=np.random.randint(0, (END_DATE - START_DATE).days),
        hours=np.random.randint(0, 23),
        minutes=np.random.randint(0, 59),
        seconds=np.random.randint(0, 59)
    )

    # Channel and card presence
    channel = np.random.choice(["pos_terminal", "online", "mobile_app", "atm", "branch"], p=[0.30, 0.30, 0.20, 0.10, 0.10])
    card_present = 1 if channel in ["pos_terminal", "atm", "branch"] else 0

    # Merchant
    category = random.choice(list(merchant_categories.keys()))
    amount_range = merchant_categories[category]
    amount = round(np.random.uniform(amount_range[0], amount_range[1]), 2)
    merchant = random.choice(merchants_rome)

    # Device
    if cust_devices:
        dev = random.choice(cust_devices)
        device_id = dev["device_id"]
        device_fingerprint = dev["device_fingerprint"]
        ip = dev["ip_address"]
    else:
        device_id = "UNKNOWN"
        device_fingerprint = "UNKNOWN"
        ip = f"{np.random.randint(1,223)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(1,254)}"

    # Location
    txn_country = "IT" if np.random.random() < 0.90 else random.choice(["DE", "FR", "ES", "GB", "US", "RO", "NG", "RU", "CN", "BR"])
    txn_city = "Roma" if txn_country == "IT" else random.choice(["Berlin", "Paris", "Madrid", "London", "New York", "Bucharest", "Lagos", "Moscow", "Shanghai", "Sao Paulo"])

    # Authentication
    auth_method = np.random.choice(["pin", "3ds", "biometric", "otp", "none"], p=[0.25, 0.25, 0.20, 0.20, 0.10])
    auth_success = 1 if np.random.random() < 0.95 else 0

    # Velocity features (simplified)
    txn_count_1h = np.random.poisson(1)
    txn_count_24h = np.random.poisson(3)
    txn_amount_24h = round(amount * txn_count_24h * np.random.uniform(0.5, 2), 2)

    # Response time (ms)
    response_time_ms = np.random.randint(50, 800)

    # ---- FRAUD LOGIC ----
    is_fraud = 0
    fraud_type = "legitimate"

    r = np.random.random()

    # Card-not-present fraud (2.5%)
    if r < 0.025 and card_present == 0:
        is_fraud = 1
        fraud_type = "card_not_present_fraud"
        amount = round(np.random.uniform(200, 5000), 2)
        txn_country = random.choice(["RO", "NG", "RU", "CN", "BR"])
        txn_city = random.choice(["Bucharest", "Lagos", "Moscow", "Shanghai", "Sao Paulo"])
        ip = f"{np.random.randint(1,223)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(1,254)}"
        device_fingerprint = hashlib.md5(f"fraud_{t}".encode()).hexdigest()[:16]
        device_id = "UNKNOWN"
        auth_method = "none"
        txn_count_1h = np.random.randint(3, 10)
        txn_count_24h = np.random.randint(8, 30)

    # Card-present fraud (1%)
    elif r < 0.035 and card_present == 1:
        is_fraud = 1
        fraud_type = "card_present_fraud"
        amount = round(np.random.uniform(100, 2000), 2)
        txn_count_1h = np.random.randint(2, 6)
        auth_success = 0 if np.random.random() < 0.3 else 1

    # Account takeover / ATO (1.5%)
    elif r < 0.05:
        is_fraud = 1
        fraud_type = "account_takeover"
        amount = round(np.random.uniform(500, 10000), 2)
        category = random.choice(["transfer", "crypto_exchange", "online_shopping"])
        device_id = "UNKNOWN"
        device_fingerprint = hashlib.md5(f"ato_{t}".encode()).hexdigest()[:16]
        ip = f"{np.random.randint(1,223)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(1,254)}"
        txn_country = random.choice(["RU", "NG", "RO", "CN"])
        auth_method = "otp"
        response_time_ms = np.random.randint(10, 100)

    # First-party fraud (0.8%)
    elif r < 0.058:
        is_fraud = 1
        fraud_type = "first_party_fraud"
        amount = round(np.random.uniform(300, 3000), 2)
        category = "online_shopping"
        channel = "online"
        card_present = 0

    # Synthetic identity fraud (0.7%)
    elif r < 0.065 and cust["is_synthetic_identity"] == 1:
        is_fraud = 1
        fraud_type = "synthetic_identity"
        amount = round(np.random.uniform(1000, 8000), 2)
        category = random.choice(["electronics", "crypto_exchange", "transfer"])

    # Money mule (0.5%)
    elif r < 0.07 and cust["is_mule_account"] == 1:
        is_fraud = 1
        fraud_type = "money_mule"
        amount = round(np.random.uniform(2000, 15000), 2)
        category = "transfer"
        channel = "online"
        txn_count_24h = np.random.randint(5, 15)

    # Phishing-related (0.5%)
    elif r < 0.075:
        is_fraud = 1
        fraud_type = "phishing_ato"
        amount = round(np.random.uniform(200, 5000), 2)
        device_id = "UNKNOWN"
        ip = f"{np.random.randint(1,223)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(1,254)}"
        auth_method = "otp"
        category = "transfer"

    transactions.append({
        "transaction_id": txn_id,
        "customer_id": cust_id,
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "amount_eur": amount,
        "currency": "EUR",
        "channel": channel,
        "card_present": card_present,
        "merchant_category": category,
        "merchant_name": merchant,
        "transaction_country": txn_country,
        "transaction_city": txn_city,
        "device_id": device_id,
        "device_fingerprint": device_fingerprint,
        "ip_address": ip,
        "auth_method": auth_method,
        "auth_success": auth_success,
        "txn_count_last_1h": txn_count_1h,
        "txn_count_last_24h": txn_count_24h,
        "txn_amount_last_24h": txn_amount_24h,
        "response_time_ms": response_time_ms,
        "is_fraud": is_fraud,
        "fraud_type": fraud_type,
    })

df_transactions = pd.DataFrame(transactions)

# ============================================================
# 4. ALERTS TABLE
# ============================================================
print("Generating alerts...")

fraud_txns = df_transactions[df_transactions["is_fraud"] == 1]
alerts = []
for idx, row in fraud_txns.iterrows():
    if np.random.random() < 0.7:  # 70% of fraud triggers an alert
        alert_id = f"ALR{len(alerts)+1:06d}"
        alerts.append({
            "alert_id": alert_id,
            "transaction_id": row["transaction_id"],
            "customer_id": row["customer_id"],
            "alert_timestamp": row["timestamp"],
            "alert_type": row["fraud_type"],
            "risk_score": round(np.random.uniform(0.6, 1.0), 3),
            "rule_triggered": random.choice([
                "velocity_check", "geo_anomaly", "amount_threshold",
                "device_mismatch", "ip_blacklist", "behavioral_anomaly",
                "network_flag", "identity_mismatch"
            ]),
            "disposition": np.random.choice(["confirmed_fraud", "false_positive", "pending_review"], p=[0.6, 0.25, 0.15]),
            "analyst_notes": random.choice([
                "High-risk transaction flagged by ML model",
                "Unusual device and location combination",
                "Velocity exceeded threshold",
                "Known fraud ring network detected",
                "Customer confirmed unauthorized transaction",
                "Suspicious transfer pattern detected",
            ]),
        })

# Add some false positive alerts for legitimate transactions
legit_txns = df_transactions[df_transactions["is_fraud"] == 0].sample(n=min(500, len(df_transactions[df_transactions["is_fraud"] == 0])))
for idx, row in legit_txns.iterrows():
    if np.random.random() < 0.05:
        alert_id = f"ALR{len(alerts)+1:06d}"
        alerts.append({
            "alert_id": alert_id,
            "transaction_id": row["transaction_id"],
            "customer_id": row["customer_id"],
            "alert_timestamp": row["timestamp"],
            "alert_type": "suspicious_activity",
            "risk_score": round(np.random.uniform(0.3, 0.65), 3),
            "rule_triggered": random.choice(["velocity_check", "amount_threshold", "geo_anomaly"]),
            "disposition": "false_positive",
            "analyst_notes": "Reviewed and cleared - legitimate activity",
        })

df_alerts = pd.DataFrame(alerts)

# ============================================================
# 5. NETWORK / GRAPH DATA (for graph-based fraud detection)
# ============================================================
print("Generating network data...")

network_edges = []
# Create connections between customers sharing devices, IPs, or phone patterns
cust_list = df_customers.to_dict('records')
for i in range(len(cust_list)):
    for j in range(i+1, min(i+20, len(cust_list))):
        # Shared device fingerprint (fraud rings)
        if cust_list[i]["is_mule_account"] and cust_list[j]["is_mule_account"]:
            network_edges.append({
                "source_customer": cust_list[i]["customer_id"],
                "target_customer": cust_list[j]["customer_id"],
                "connection_type": "shared_device",
                "strength": round(np.random.uniform(0.7, 1.0), 2),
                "is_suspicious": 1,
            })
        # Random legitimate connections
        elif np.random.random() < 0.002:
            network_edges.append({
                "source_customer": cust_list[i]["customer_id"],
                "target_customer": cust_list[j]["customer_id"],
                "connection_type": random.choice(["same_employer", "family", "same_address"]),
                "strength": round(np.random.uniform(0.1, 0.5), 2),
                "is_suspicious": 0,
            })

# Add fraud ring connections
fraud_customers = df_customers[df_customers["is_synthetic_identity"] == 1]["customer_id"].tolist()
for i in range(len(fraud_customers)):
    for j in range(i+1, len(fraud_customers)):
        if np.random.random() < 0.3:
            network_edges.append({
                "source_customer": fraud_customers[i],
                "target_customer": fraud_customers[j],
                "connection_type": random.choice(["shared_device", "shared_ip", "shared_phone_pattern"]),
                "strength": round(np.random.uniform(0.6, 1.0), 2),
                "is_suspicious": 1,
            })

df_network = pd.DataFrame(network_edges) if network_edges else pd.DataFrame(columns=["source_customer", "target_customer", "connection_type", "strength", "is_suspicious"])

# ============================================================
# 6. SAVE TO EXCEL
# ============================================================
print("Saving to Excel...")

output_path = "/home/claude/fraud_project/banca_roma_digitale_data.xlsx"
with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    df_customers.to_excel(writer, sheet_name="customers", index=False)
    df_transactions.to_excel(writer, sheet_name="transactions", index=False)
    df_devices.to_excel(writer, sheet_name="devices", index=False)
    df_alerts.to_excel(writer, sheet_name="alerts", index=False)
    df_network.to_excel(writer, sheet_name="network_edges", index=False)

# Print summary stats
print(f"\n{'='*60}")
print(f"BANCA ROMA DIGITALE - Synthetic Data Summary")
print(f"{'='*60}")
print(f"Customers:    {len(df_customers):,}")
print(f"  Synthetic:  {df_customers['is_synthetic_identity'].sum()}")
print(f"  Mule:       {df_customers['is_mule_account'].sum()}")
print(f"Devices:      {len(df_devices):,}")
print(f"Transactions: {len(df_transactions):,}")
print(f"  Fraudulent: {df_transactions['is_fraud'].sum():,} ({df_transactions['is_fraud'].mean()*100:.2f}%)")
print(f"  Legitimate: {(df_transactions['is_fraud']==0).sum():,}")
print(f"\nFraud Type Breakdown:")
fraud_counts = df_transactions[df_transactions["is_fraud"]==1]["fraud_type"].value_counts()
for ft, count in fraud_counts.items():
    print(f"  {ft}: {count}")
print(f"\nAlerts:       {len(df_alerts):,}")
print(f"Network Edges:{len(df_network):,}")
print(f"\nSaved to: {output_path}")
