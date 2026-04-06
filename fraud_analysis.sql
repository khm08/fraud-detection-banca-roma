-- ============================================================
-- BANCA ROMA DIGITALE - Fraud Detection SQL Analysis
-- Author: Kareem Makki
-- ============================================================

-- ============================================================
-- TABLE CREATION (SQLite schema)
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    city TEXT,
    zone TEXT,
    email TEXT,
    phone TEXT,
    account_type TEXT,
    account_open_date DATE,
    monthly_income_eur REAL,
    credit_score INTEGER,
    is_synthetic_identity INTEGER,
    is_mule_account INTEGER,
    kyc_verified INTEGER,
    id_verification_method TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT,
    timestamp DATETIME,
    amount_eur REAL,
    currency TEXT,
    channel TEXT,
    card_present INTEGER,
    merchant_category TEXT,
    merchant_name TEXT,
    transaction_country TEXT,
    transaction_city TEXT,
    device_id TEXT,
    device_fingerprint TEXT,
    ip_address TEXT,
    auth_method TEXT,
    auth_success INTEGER,
    txn_count_last_1h INTEGER,
    txn_count_last_24h INTEGER,
    txn_amount_last_24h REAL,
    response_time_ms INTEGER,
    is_fraud INTEGER,
    fraud_type TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    customer_id TEXT,
    device_type TEXT,
    device_fingerprint TEXT,
    ip_address TEXT,
    os_version TEXT,
    is_jailbroken INTEGER,
    first_seen DATE,
    is_known_device INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    transaction_id TEXT,
    customer_id TEXT,
    alert_timestamp DATETIME,
    alert_type TEXT,
    risk_score REAL,
    rule_triggered TEXT,
    disposition TEXT,
    analyst_notes TEXT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

CREATE TABLE IF NOT EXISTS network_edges (
    source_customer TEXT,
    target_customer TEXT,
    connection_type TEXT,
    strength REAL,
    is_suspicious INTEGER
);

-- ============================================================
-- 1. FRAUD OVERVIEW DASHBOARD QUERIES
-- ============================================================

-- Overall fraud rate by channel
SELECT
    channel,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_txns,
    ROUND(AVG(is_fraud) * 100, 2) AS fraud_rate_pct,
    ROUND(AVG(CASE WHEN is_fraud = 1 THEN amount_eur END), 2) AS avg_fraud_amount
FROM transactions
GROUP BY channel
ORDER BY fraud_rate_pct DESC;

-- Fraud by type breakdown
SELECT
    fraud_type,
    COUNT(*) AS count,
    ROUND(AVG(amount_eur), 2) AS avg_amount,
    ROUND(SUM(amount_eur), 2) AS total_exposure,
    ROUND(MIN(amount_eur), 2) AS min_amount,
    ROUND(MAX(amount_eur), 2) AS max_amount
FROM transactions
WHERE is_fraud = 1
GROUP BY fraud_type
ORDER BY total_exposure DESC;

-- Monthly fraud trend
SELECT
    strftime('%Y-%m', timestamp) AS month,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_count,
    ROUND(AVG(is_fraud) * 100, 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount_eur ELSE 0 END), 2) AS fraud_losses
FROM transactions
GROUP BY strftime('%Y-%m', timestamp)
ORDER BY month;

-- ============================================================
-- 2. CARD-PRESENT vs CARD-NOT-PRESENT ANALYSIS
-- ============================================================

-- CP vs CNP fraud comparison
SELECT
    CASE WHEN card_present = 1 THEN 'Card Present' ELSE 'Card Not Present' END AS txn_type,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_count,
    ROUND(AVG(is_fraud) * 100, 2) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount_eur ELSE 0 END), 2) AS total_fraud_amount
FROM transactions
GROUP BY card_present;

-- CNP fraud by merchant category
SELECT
    merchant_category,
    COUNT(*) AS total_cnp_txns,
    SUM(is_fraud) AS cnp_fraud,
    ROUND(AVG(is_fraud) * 100, 2) AS cnp_fraud_rate
FROM transactions
WHERE card_present = 0
GROUP BY merchant_category
ORDER BY cnp_fraud_rate DESC
LIMIT 10;

-- ============================================================
-- 3. ACCOUNT TAKEOVER (ATO) DETECTION
-- ============================================================

-- Identify ATO patterns: unknown devices + high amounts + foreign IPs
SELECT
    t.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(*) AS ato_txn_count,
    ROUND(SUM(t.amount_eur), 2) AS total_ato_amount,
    GROUP_CONCAT(DISTINCT t.transaction_country) AS countries_used,
    GROUP_CONCAT(DISTINCT t.device_id) AS devices_used
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.fraud_type = 'account_takeover'
GROUP BY t.customer_id
ORDER BY total_ato_amount DESC
LIMIT 20;

-- Device anomaly detection for ATO
SELECT
    t.customer_id,
    t.device_id,
    t.device_fingerprint,
    t.ip_address,
    t.transaction_country,
    t.amount_eur,
    t.auth_method,
    t.timestamp
FROM transactions t
WHERE t.device_id = 'UNKNOWN'
  AND t.amount_eur > 1000
  AND t.transaction_country != 'IT'
ORDER BY t.amount_eur DESC
LIMIT 50;

-- ============================================================
-- 4. SYNTHETIC IDENTITY DETECTION
-- ============================================================

-- Synthetic identity customers and their activity
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS name,
    c.age,
    c.credit_score,
    c.account_open_date,
    c.kyc_verified,
    c.id_verification_method,
    COUNT(t.transaction_id) AS txn_count,
    ROUND(SUM(t.amount_eur), 2) AS total_amount,
    SUM(t.is_fraud) AS fraud_count
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
WHERE c.is_synthetic_identity = 1
GROUP BY c.customer_id
ORDER BY total_amount DESC;

-- ============================================================
-- 5. MONEY MULE DETECTION
-- ============================================================

-- Mule account activity patterns
SELECT
    c.customer_id,
    c.account_open_date,
    c.monthly_income_eur,
    COUNT(t.transaction_id) AS txn_count,
    SUM(CASE WHEN t.merchant_category = 'transfer' THEN 1 ELSE 0 END) AS transfer_count,
    ROUND(SUM(CASE WHEN t.merchant_category = 'transfer' THEN t.amount_eur ELSE 0 END), 2) AS total_transfers,
    ROUND(AVG(t.txn_count_last_24h), 1) AS avg_daily_velocity
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
WHERE c.is_mule_account = 1
GROUP BY c.customer_id
ORDER BY total_transfers DESC;

-- Accounts with high transfer-to-income ratio (mule indicator)
SELECT
    c.customer_id,
    c.monthly_income_eur,
    ROUND(SUM(CASE WHEN t.merchant_category = 'transfer' THEN t.amount_eur ELSE 0 END), 2) AS total_transfers,
    ROUND(SUM(CASE WHEN t.merchant_category = 'transfer' THEN t.amount_eur ELSE 0 END) / NULLIF(c.monthly_income_eur, 0), 2) AS transfer_income_ratio,
    COUNT(DISTINCT strftime('%Y-%m', t.timestamp)) AS active_months
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id
HAVING transfer_income_ratio > 5
ORDER BY transfer_income_ratio DESC
LIMIT 20;

-- ============================================================
-- 6. NETWORK / GRAPH ANALYSIS
-- ============================================================

-- Suspicious network clusters
SELECT
    source_customer,
    target_customer,
    connection_type,
    strength,
    is_suspicious
FROM network_edges
WHERE is_suspicious = 1
ORDER BY strength DESC;

-- Customers with highest network connections (potential fraud rings)
SELECT
    customer_id,
    COUNT(*) AS connection_count,
    SUM(is_suspicious) AS suspicious_connections,
    ROUND(AVG(strength), 2) AS avg_strength
FROM (
    SELECT source_customer AS customer_id, is_suspicious, strength FROM network_edges
    UNION ALL
    SELECT target_customer AS customer_id, is_suspicious, strength FROM network_edges
)
GROUP BY customer_id
HAVING suspicious_connections > 0
ORDER BY suspicious_connections DESC
LIMIT 20;

-- ============================================================
-- 7. RULE PERFORMANCE ANALYSIS
-- ============================================================

-- Alert rule effectiveness
SELECT
    rule_triggered,
    COUNT(*) AS total_alerts,
    SUM(CASE WHEN disposition = 'confirmed_fraud' THEN 1 ELSE 0 END) AS true_positives,
    SUM(CASE WHEN disposition = 'false_positive' THEN 1 ELSE 0 END) AS false_positives,
    ROUND(AVG(CASE WHEN disposition = 'confirmed_fraud' THEN 1.0 ELSE 0.0 END) * 100, 2) AS precision_pct,
    ROUND(AVG(risk_score), 3) AS avg_risk_score
FROM alerts
GROUP BY rule_triggered
ORDER BY precision_pct DESC;

-- ============================================================
-- 8. DEVICE FINGERPRINTING ANALYSIS
-- ============================================================

-- Devices associated with multiple customers (suspicious)
SELECT
    d.device_fingerprint,
    COUNT(DISTINCT d.customer_id) AS customer_count,
    GROUP_CONCAT(DISTINCT d.customer_id) AS customers,
    d.device_type,
    d.is_jailbroken
FROM devices d
GROUP BY d.device_fingerprint
HAVING customer_count > 1
ORDER BY customer_count DESC;

-- Jailbroken devices and fraud correlation
SELECT
    d.is_jailbroken,
    COUNT(DISTINCT t.transaction_id) AS txn_count,
    SUM(t.is_fraud) AS fraud_count,
    ROUND(AVG(t.is_fraud) * 100, 2) AS fraud_rate_pct
FROM transactions t
JOIN devices d ON t.device_id = d.device_id
GROUP BY d.is_jailbroken;

-- ============================================================
-- 9. GEO-ANOMALY DETECTION
-- ============================================================

-- Customers transacting from multiple countries in short windows
SELECT
    customer_id,
    COUNT(DISTINCT transaction_country) AS country_count,
    GROUP_CONCAT(DISTINCT transaction_country) AS countries,
    SUM(is_fraud) AS fraud_txns,
    ROUND(SUM(amount_eur), 2) AS total_amount
FROM transactions
WHERE date(timestamp) >= date('2025-01-01')
GROUP BY customer_id
HAVING country_count >= 3
ORDER BY fraud_txns DESC
LIMIT 20;

-- ============================================================
-- 10. REAL-TIME SCORING FEATURE EXTRACTION
-- ============================================================

-- Feature extraction query for real-time ML scoring
SELECT
    t.transaction_id,
    t.amount_eur,
    t.card_present,
    t.txn_count_last_1h,
    t.txn_count_last_24h,
    t.txn_amount_last_24h,
    t.response_time_ms,
    CASE WHEN t.device_id = 'UNKNOWN' THEN 1 ELSE 0 END AS unknown_device,
    CASE WHEN t.transaction_country != 'IT' THEN 1 ELSE 0 END AS foreign_txn,
    CASE WHEN t.auth_method = 'none' THEN 1 ELSE 0 END AS no_auth,
    c.credit_score,
    c.is_synthetic_identity,
    c.is_mule_account,
    julianday(t.timestamp) - julianday(c.account_open_date) AS account_age_days,
    t.is_fraud
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
ORDER BY t.timestamp;
