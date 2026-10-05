 # Cross-Border Trade Compliance & Routing System

 ## Main purpose ：
   This project is mainly aimed at developing an automated verification system for the pain points in the supply chain of businesses (simulating real cross-department data interaction, malicious underreporting and tax evasion, incorrect declaration of risks, and customs declaration errors). The system integrates multiple departments' documents, performs different anomaly detection, and forwards the problematic documents to the corresponding departments, ensuring business compliance.

 ## Step1:Data Sourcing & ETL Setup
   Business implementation: Since a perfect dataset was not available, we first consulted the actual local customs database, extracted the actual customs extraction codes (10-digit HS codes), and obtained the refund rates and regulatory conditions as the actual data source.

   ain point simulation: To closely replicate the "data silos" and human errors found in real business scenarios, I wrote a script to generate daily financial invoices and logistics packing lists, and injected real dirty data such as "maliciously underreporting the value of goods, incorrect HS codes, and瞒报 of dangerous goods" into them according to certain probabilities.

## Step2:Data Integration & Pipeline
   Cleaning: Write a Pandas data fusion script to build a lightweight ETL pipeline, and perform defensive cleaning on the text fields that are prone to errors by business personnel (such as removing invisible spaces)
   Logical concatenation: By using Inner Join, invoices and packing lists are aligned at the logistics and financial levels. Subsequently, the compliance base table is mounted through Left Join. By leveraging the database connection logic, false HS Codes that were filled in randomly to evade supervision have exposed null values (NaN) due to the failed matching.

## Step3:Dual-Layer Rule Engine
   Logistics defense line: By using algorithms to calculate the density ratio of the volume and gross weight of goods, it automatically intercepts "air items" that significantly deviate from physical principles and abnormal items that may be suspected of being smuggled.

   Legal Defense Line: Precisely intercept the invalid customs codes exposed in the previous step, as well as the sensitive goods (such as lithium battery products) that have mandatory inspections but lack UN38.3 battery certification. This helps avoid the hefty fines for air transportation violations.

# Step4:Routing & OOP Refactoring
  Automatic Routing: A state machine and automatic routing module have been developed. After completing all checks, the system will automatically release risk-free and qualified files, and package different types of abnormal files separately into independent CSV reports for export (for example: abnormal density will be automatically sent to the warehouse supervisor for review, and abnormal qualifications will be automatically sent to the customs affairs specialist for follow-up). This achieves closed-loop business process collaboration across departments.

# Tech Stack：Language: 
Python 3.10+
Data processing: Pandas, NumPy
Architecture design: Object-oriented programming (OOP), State machine design (State Machine)

# How to Run
Make sure to install the required dependencies: pip install pandas numpy

Run the simulation data generator to initialize the business environment: python generate_mock_data.py

Start the main control risk management engine in one click: python main_system.py

After the operation is completed, please go to the directory data/reports/ to view the processing reports distributed to each department.