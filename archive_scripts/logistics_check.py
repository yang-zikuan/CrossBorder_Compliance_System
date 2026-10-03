import pandas as pd
import numpy as np

print("running logistics density check...")

# load unified data
df = pd.read_csv('data/fused_data.csv')

# handle NaN in error_logs to avoid string concat issues
df['error_logs'] = df['error_logs'].fillna('')

# calc actual density (kg/cbm)
df['actual_density'] = df['gross_weight_kg'] / df['volume_cbm']

# find density outliers based on master baseline
is_too_light = df['actual_density'] < df['min_density']
is_too_heavy = df['actual_density'] > df['max_density']
density_anomaly = is_too_light | is_too_heavy

# update status and logs for anomalies
df.loc[density_anomaly, 'risk_status'] = 'HOLD_LOGISTICS'
df.loc[density_anomaly, 'error_logs'] += 'density out of bounds; '

anomaly_count = density_anomaly.sum()
print(f"alert: intercepted {anomaly_count} shipments with density anomalies.")

# save progress
df.to_csv('data/fused_data.csv', index=False)
print("day 3 complete. data updated.")