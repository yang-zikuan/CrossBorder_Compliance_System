import pandas as pd

print("running compliance check...")
df = pd.read_csv('data/fused_data.csv')

# check 1: unregistered or fake HS codes
# invalid codes didn't match our master table during day 2's left join, leaving NaNs
invalid_hs = df['hs_code'].isna()
df.loc[invalid_hs, 'risk_status'] = 'HOLD_COMPLIANCE'
df.loc[invalid_hs, 'error_logs'] += 'invalid hs code; '

# check 2: dangerous goods (battery) compliance failure
# product naturally has a battery, but logistics declared 'N' or cert is missing
has_inherent_battery = df['product_cat'].isin(['Smartphones', 'Laptops', 'Li-ion Batteries'])
missing_cert = (df['contains_battery'] == 'N') | (df['battery_cert'] == 'Missing')

# use boolean indexing to find intersection (ignoring rows that already failed HS check to avoid NaN errors)
dg_violation = has_inherent_battery & missing_cert & ~invalid_hs

df.loc[dg_violation, 'risk_status'] = 'HOLD_COMPLIANCE'
df.loc[dg_violation, 'error_logs'] += 'missing DG battery cert; '

# print stats
print(f"alert: caught {invalid_hs.sum()} fake HS codes.")
print(f"alert: caught {dg_violation.sum()} battery cert violations.")

# save back to the wide table
df.to_csv('data/fused_data.csv', index=False)
print("day 4 complete. data updated.")