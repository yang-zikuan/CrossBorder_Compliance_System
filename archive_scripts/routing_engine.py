import pandas as pd
import os

print("init routing engine...")
df = pd.read_csv('data/fused_data.csv')

# 1. auto-clear healthy shipments
# anything still 'Pending' means it passed all day 3 and day 4 checks
df.loc[df['risk_status'] == 'Pending', 'risk_status'] = 'PASS_CLEARED'

# 2. route to different departments based on risk status
# create output dir for departmental reports
os.makedirs('data/reports', exist_ok=True)

# filter and export logistics holds (density issues)
df_logistics = df[df['risk_status'] == 'HOLD_LOGISTICS']
df_logistics.to_csv('data/reports/action_logistics.csv', index=False)

# filter and export compliance holds (HS code / battery issues)
df_compliance = df[df['risk_status'] == 'HOLD_COMPLIANCE']
df_compliance.to_csv('data/reports/action_compliance.csv', index=False)

# filter and export cleared shipments (ready for customs API)
df_cleared = df[df['risk_status'] == 'PASS_CLEARED']
df_cleared.to_csv('data/reports/ready_for_customs.csv', index=False)

# 3. print quick summary for management
print("\n--- Daily Dispatch Summary ---")
print(f"Total shipments processed: {len(df)}")
print(f"Cleared for customs: {len(df_cleared)}")
print(f"Routed to Logistics: {len(df_logistics)}")
print(f"Routed to Compliance: {len(df_compliance)}")
print("reports generated in data/reports/")

# save final states back to main db
df.to_csv('data/fused_data.csv', index=False)