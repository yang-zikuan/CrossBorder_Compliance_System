import pandas as pd
import random
import os

# make sure data dir exists
if not os.path.exists('data'):
    os.makedirs('data')

# 1. setup compliance master table using active 10-digit HS codes
master_list = [
    # smartphones (keeping the active one from yesterday)
    {'hs_code': '8517130000', 'product_cat': 'Smartphones', 'tax_rebate': 0.13, 'reg_condition': 'A', 'insp_condition': 'L', 'min_density': 200, 'max_density': 450},
    # laptops (active code)
    {'hs_code': '8471309000', 'product_cat': 'Laptops', 'tax_rebate': 0.13, 'reg_condition': 'A', 'insp_condition': 'L', 'min_density': 150, 'max_density': 350},
    # li-ion batteries (active code, note the 6% rebate)
    {'hs_code': '8507600099', 'product_cat': 'Li-ion Batteries', 'tax_rebate': 0.06, 'reg_condition': 'A', 'insp_condition': 'M,L', 'min_density': 800, 'max_density': 1500},
    # headphones (active code)
    {'hs_code': '8518300000', 'product_cat': 'Headphones', 'tax_rebate': 0.13, 'reg_condition': 'None', 'insp_condition': 'None', 'min_density': 100, 'max_density': 250}
]

df_master = pd.DataFrame(master_list)
df_master.to_csv('data/compliance_master.csv', index=False)

# 2. generate daily operations data (invoice & packing list)
total_orders = 300
invoices = []
packing_lists = []

for i in range(total_orders):
    # generate waybill number, e.g. WB-2026-0001
    wb_no = f"WB-2026-{str(i).zfill(4)}"
    
    # randomly pick a product template
    base_item = random.choice(master_list)
    cat = base_item['product_cat']
    correct_hs = base_item['hs_code']
    
    # basic order details
    goods_desc = f"TechCorp {cat}"
    order_qty = random.randint(100, 2000)
    
    # rough market price and weight for the category
    price_map = {'Smartphones': 899, 'Laptops': 1499, 'Li-ion Batteries': 25, 'Headphones': 129}
    weight_map = {'Smartphones': 0.35, 'Laptops': 2.1, 'Li-ion Batteries': 0.15, 'Headphones': 0.3}
    
    unit_price = price_map[cat]
    total_val = unit_price * order_qty
    total_gw = weight_map[cat] * order_qty
    
    # calculate volume based on realistic density range
    current_density = random.uniform(base_item['min_density'], base_item['max_density'])
    total_vol = total_gw / current_density
    
    # default compliance fields
    decl_hs = correct_hs
    has_battery = 'Y' if cat in ['Smartphones', 'Laptops', 'Li-ion Batteries'] else 'N'
    dg_cert = 'UN38.3' if has_battery == 'Y' else 'N/A'

    # 3. inject realistic human errors (the "bugs" we want our system to catch)
    rand_chance = random.random()
    
    if rand_chance < 0.05:
        # risk type 1: value under-declaration (extremely low price to evade tax)
        total_val = total_val * 0.12 
    elif rand_chance < 0.15:
        # risk type 2: incorrect HS code & vague description
        goods_desc = "Spare Parts"
        decl_hs = "8542310000" # wrong code (e.g. CPU/IC instead of Laptop)
    elif rand_chance < 0.22:
        # risk type 3: density mismatch (maybe hiding other goods inside)
        total_vol = total_vol * 12.5 
    elif rand_chance < 0.30:
        # risk type 4: dangerous goods compliance failure (missing battery cert)
        has_battery = 'N'
        dg_cert = 'Missing'
        
    # save row data
    invoices.append({
        'waybill_id': wb_no,
        'sku': f"SKU-{random.randint(1000, 9999)}",
        'item_desc': goods_desc,
        'qty': order_qty,
        'total_usd': round(total_val, 2),
        'declared_hs': decl_hs
    })
    
    packing_lists.append({
        'waybill_id': wb_no,
        'gross_weight_kg': round(total_gw, 2),
        'volume_cbm': round(total_vol, 4),
        'contains_battery': has_battery,
        'battery_cert': dg_cert
    })

# output to files
pd.DataFrame(invoices).to_csv('data/invoice.csv', index=False)
pd.DataFrame(packing_lists).to_csv('data/packing_list.csv', index=False)

print("done. please check the /data folder.")