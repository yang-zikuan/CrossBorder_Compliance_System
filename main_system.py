import pandas as pd
import os

class ComplianceEngine:
    def __init__(self, data_dir='data'):
        # set up paths
        self.data_dir = data_dir
        self.reports_dir = os.path.join(data_dir, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
        self.df = None

    def load_data(self):
        # load raw csv files
        df_inv = pd.read_csv(f'{self.data_dir}/invoice.csv')
        df_pl = pd.read_csv(f'{self.data_dir}/packing_list.csv')
        df_master = pd.read_csv(f'{self.data_dir}/compliance_master.csv')
        
        # strip invisible trailing spaces just in case
        df_inv['declared_hs'] = df_inv['declared_hs'].astype(str).str.strip()
        df_master['hs_code'] = df_master['hs_code'].astype(str).str.strip()
        
        # fuse invoice and packing list (inner join)
        df_fused = pd.merge(df_inv, df_pl, on='waybill_id', how='inner')
        # attach master rules (left join to catch fake codes later)
        self.df = pd.merge(df_fused, df_master, left_on='declared_hs', right_on='hs_code', how='left')
        
        # init tracking columns
        self.df['risk_status'] = 'Pending'
        self.df['error_logs'] = ''

    def check_physical_density(self):
        # catch volumetric weight anomalies (e.g. air shipping frauds)
        self.df['actual_density'] = self.df['gross_weight_kg'] / self.df['volume_cbm']
        
        out_of_bounds = (self.df['actual_density'] < self.df['min_density']) | (self.df['actual_density'] > self.df['max_density'])
        
        self.df.loc[out_of_bounds, 'risk_status'] = 'HOLD_LOGISTICS'
        self.df.loc[out_of_bounds, 'error_logs'] += 'density anomaly; '

    def check_trade_compliance(self):
        # 1. catch unregistered hs codes (they are NaN from the left join)
        fake_hs = self.df['hs_code'].isna()
        self.df.loc[fake_hs, 'risk_status'] = 'HOLD_COMPLIANCE'
        self.df.loc[fake_hs, 'error_logs'] += 'invalid hs; '
        
        # 2. catch missing dg certs (e.g. lithium batteries without UN38.3)
        has_battery = self.df['product_cat'].isin(['Smartphones', 'Laptops', 'Li-ion Batteries'])
        missing_cert = (self.df['contains_battery'] == 'N') | (self.df['battery_cert'] == 'Missing')
        
        # ignore rows that already failed hs check to prevent cascaded NaN errors
        dg_violation = has_battery & missing_cert & ~fake_hs
        
        self.df.loc[dg_violation, 'risk_status'] = 'HOLD_COMPLIANCE'
        self.df.loc[dg_violation, 'error_logs'] += 'missing battery cert; '

    def dispatch_workflows(self):
        # auto-clear shipments that passed all checks
        self.df.loc[self.df['risk_status'] == 'Pending', 'risk_status'] = 'PASS_CLEARED'
        
        # slice dataframe and export to respective department buckets
        self.df[self.df['risk_status'] == 'HOLD_LOGISTICS'].to_csv(f'{self.reports_dir}/action_logistics.csv', index=False)
        self.df[self.df['risk_status'] == 'HOLD_COMPLIANCE'].to_csv(f'{self.reports_dir}/action_compliance.csv', index=False)
        self.df[self.df['risk_status'] == 'PASS_CLEARED'].to_csv(f'{self.reports_dir}/ready_for_customs.csv', index=False)
        
        # save the updated wide table back to db/folder
        self.df.to_csv(f'{self.data_dir}/fused_data.csv', index=False)

        # print quick daily summary
        print("\n--- system run complete ---")
        print(f"total scanned: {len(self.df)}")
        print(f"cleared: {len(self.df[self.df['risk_status'] == 'PASS_CLEARED'])}")
        print(f"logistics holds: {len(self.df[self.df['risk_status'] == 'HOLD_LOGISTICS'])}")
        print(f"compliance holds: {len(self.df[self.df['risk_status'] == 'HOLD_COMPLIANCE'])}")

    def execute(self):
        print("starting compliance engine...")
        self.load_data()
        self.check_physical_density()
        self.check_trade_compliance()
        self.dispatch_workflows()

if __name__ == "__main__":
    engine = ComplianceEngine()
    engine.execute()