import pandas as pd
import os

print("starting data pipeline...")

# 1. load raw data from day 1
try:
    df_inv = pd.read_csv('data/invoice.csv')
    df_pl = pd.read_csv('data/packing_list.csv')
    df_master = pd.read_csv('data/compliance_master.csv')
except FileNotFoundError:
    print("error: files not found. did you run day 1 script?")
    exit()

# 2. pragmatic text cleaning
# in real life, users often add invisible spaces by accident, e.g. "8517130000 "
df_inv['declared_hs'] = df_inv['declared_hs'].astype(str).str.strip()
df_master['hs_code'] = df_master['hs_code'].astype(str).str.strip()

# 3. fuse finance (invoice) and logistics (packing list) data
# use inner join because a valid shipment must have BOTH invoice and packing list
df_fused = pd.merge(df_inv, df_pl, on='waybill_id', how='inner')

# 4. attach customs compliance baseline
# CRITICAL: use left join here. if the declared hs code is fake/wrong, 
# it won't match anything in our master table, leaving NaNs that we can catch later.
df_fused = pd.merge(df_fused, df_master, left_on='declared_hs', right_on='hs_code', how='left')

# 5. pre-processing: setup status columns for our rule engine tomorrow
df_fused['risk_status'] = 'Pending'  # will change to Pass or Hold later
df_fused['error_logs'] = ''          # to store multiple violation reasons

# 6. quick sanity check: find how many fake HS codes we caught just by joining
invalid_hs_count = df_fused['hs_code'].isna().sum()
print(f"pipeline alert: found {invalid_hs_count} shipments with unregistered HS codes!")

# 7. save the fused wide-table
df_fused.to_csv('data/fused_data.csv', index=False)
print("day 2 complete. unified dataset saved to data/fused_data.csv")
