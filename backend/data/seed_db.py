"""
seed_db.py — Creates and populates data/crm.db with 13 synthetic datasets
Run: python data/seed_db.py (from backend/)
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")
JSON_PATH = os.path.join(os.path.dirname(__file__), "crm_knowledge.json")

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── TABLE 1: customers ────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY, name TEXT, segment TEXT, industry TEXT,
        ltv REAL, churn_risk TEXT, deals_count INTEGER, since_year INTEGER, status TEXT
    )""")
    customers = [
        (1,"Apex Retail Corp","Enterprise","Retail",320000,"Low",8,2021,"Active"),
        (2,"BlueSky Logistics","Enterprise","Logistics",275000,"Medium",6,2020,"Active"),
        (3,"CoreTech Solutions","SMB","Technology",95000,"Low",4,2022,"Active"),
        (4,"DeltaWave Finance","Enterprise","Finance",410000,"Low",10,2019,"Active"),
        (5,"EcoGrow Industries","SMB","Agriculture",48000,"High",2,2023,"At-Risk"),
        (6,"FusionMed Hospital","Enterprise","Healthcare",380000,"Low",9,2020,"Active"),
        (7,"GreenPath Energy","SMB","Energy",72000,"Medium",3,2022,"Active"),
        (8,"HorizonBank","Enterprise","Finance",520000,"Low",12,2018,"Active"),
        (9,"InnovateTech Startup","Startup","Technology",18000,"High",1,2024,"At-Risk"),
        (10,"JetStream Airways","Enterprise","Aviation",290000,"Medium",7,2021,"Active"),
        (11,"KloudBase SaaS","Startup","Technology",22000,"High",1,2024,"At-Risk"),
        (12,"LunarFarm Organics","SMB","Agriculture",35000,"High",2,2023,"At-Risk"),
        (13,"MetroCity Council","Enterprise","Government",195000,"Low",5,2020,"Active"),
        (14,"NovaMed Pharma","Enterprise","Healthcare",445000,"Low",11,2019,"Active"),
        (15,"OmniChain Supply","SMB","Logistics",68000,"Medium",3,2022,"Active"),
        (16,"PeakForm Fitness","Startup","Wellness",14000,"High",1,2024,"At-Risk"),
        (17,"QuantumBuild","SMB","Construction",82000,"Low",4,2022,"Active"),
        (18,"RapidShip Couriers","SMB","Logistics",59000,"Medium",3,2023,"Active"),
        (19,"SolarNest Energy","SMB","Energy",91000,"Low",4,2021,"Active"),
        (20,"TerraFlex Properties","Enterprise","Real Estate",310000,"Medium",8,2020,"Active"),
        (21,"UrbanDine Group","SMB","F&B",44000,"High",2,2023,"At-Risk"),
        (22,"VeroVault Security","Enterprise","Cybersecurity",260000,"Low",6,2021,"Active"),
        (23,"WaveRider Marine","SMB","Maritime",53000,"Medium",3,2022,"Active"),
        (24,"XenithAI Labs","Startup","Technology",28000,"High",1,2024,"At-Risk"),
        (25,"YellowBrick Retail","SMB","Retail",66000,"Low",3,2022,"Active"),
        (26,"ZenithCare Clinics","SMB","Healthcare",77000,"Medium",4,2023,"Active"),
        (27,"AtlasGlobal Trade","Enterprise","Trade",340000,"Low",9,2019,"Active"),
        (28,"BrightMind EdTech","Startup","Education",19000,"High",1,2024,"At-Risk"),
        (29,"ClearPath Insurance","Enterprise","Insurance",285000,"Low",7,2020,"Active"),
        (30,"DawnRise Manufacturing","Enterprise","Manufacturing",460000,"Medium",10,2018,"Active"),
    ]
    cur.executemany("INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?,?,?,?,?)", customers)

    # ── TABLE 2: deals ────────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY, customer_id INTEGER, customer_name TEXT,
        title TEXT, stage TEXT, value REAL, probability INTEGER, owner TEXT, close_date TEXT, department TEXT
    )""")
    deals = [
        (1,1,"Apex Retail Corp","Annual Expansion License","Closed-Won",85000,100,"Priya Nair","2023-01-15","Sales"),
        (2,2,"BlueSky Logistics","Supply Chain Platform Upgrade","Negotiation",62000,75,"Rahul Singh","2023-08-30","Sales"),
        (3,3,"CoreTech Solutions","DevOps Consulting Package","Proposal",28000,50,"Ananya Kumar","2023-09-15","Sales"),
        (4,4,"DeltaWave Finance","Risk Analytics Suite","Closed-Won",110000,100,"Kiran Mehta","2023-02-28","Sales"),
        (5,5,"EcoGrow Industries","IoT Sensor Network","Qualified",18000,30,"Priya Nair","2023-10-01","Sales"),
        (6,6,"FusionMed Hospital","Patient Data Platform","Closed-Won",120000,100,"Rahul Singh","2023-03-10","Sales"),
        (7,7,"GreenPath Energy","Carbon Credit Tracking","Proposal",22000,45,"Ananya Kumar","2023-09-20","Sales"),
        (8,8,"HorizonBank","Fraud Detection Engine Tier2","Negotiation",95000,80,"Kiran Mehta","2023-08-15","Sales"),
        (9,9,"InnovateTech Startup","Startup CRM Bundle","Prospect",8000,20,"Priya Nair","2023-11-01","Sales"),
        (10,10,"JetStream Airways","Fleet Management Dashboard","Proposal",74000,55,"Rahul Singh","2023-09-30","Sales"),
        (11,11,"KloudBase SaaS","API Integration Starter","Prospect",6000,15,"Ananya Kumar","2023-11-15","Sales"),
        (12,12,"LunarFarm Organics","Crop Analytics Lite","Qualified",12000,25,"Kiran Mehta","2023-10-10","Sales"),
        (13,13,"MetroCity Council","Smart City Dashboard","Closed-Won",55000,100,"Priya Nair","2023-04-05","Sales"),
        (14,14,"NovaMed Pharma","Clinical Trial Management","Closed-Won",135000,100,"Rahul Singh","2023-01-30","Sales"),
        (15,15,"OmniChain Supply","Inventory Optimizer","Proposal",19000,40,"Ananya Kumar","2023-09-25","Sales"),
        (16,16,"PeakForm Fitness","Member Analytics App","Prospect",5000,10,"Kiran Mehta","2023-12-01","Sales"),
        (17,17,"QuantumBuild","Project Cost Tracker","Negotiation",31000,70,"Priya Nair","2023-08-20","Sales"),
        (18,18,"RapidShip Couriers","Route Optimization Module","Qualified",17000,35,"Rahul Singh","2023-10-05","Sales"),
        (19,19,"SolarNest Energy","Grid Analytics Platform","Closed-Won",42000,100,"Ananya Kumar","2023-05-12","Sales"),
        (20,20,"TerraFlex Properties","Portfolio Risk Engine","Negotiation",88000,78,"Kiran Mehta","2023-08-28","Sales"),
        (21,21,"UrbanDine Group","POS Integration Suite","Qualified",11000,20,"Priya Nair","2023-10-15","Sales"),
        (22,22,"VeroVault Security","Zero-Trust Security Audit","Closed-Won",72000,100,"Rahul Singh","2023-03-22","Sales"),
        (23,23,"WaveRider Marine","Fleet GPS Tracker","Proposal",16000,45,"Ananya Kumar","2023-09-18","Sales"),
        (24,24,"XenithAI Labs","MLOps Pipeline","Prospect",9000,15,"Kiran Mehta","2023-11-20","Sales"),
        (25,25,"YellowBrick Retail","Retail Analytics Bundle","Proposal",21000,50,"Priya Nair","2023-09-10","Sales"),
        (26,26,"ZenithCare Clinics","Clinical Workflow Tool","Closed-Won",28000,100,"Rahul Singh","2024-12-05","Sales"),
        (27,27,"AtlasGlobal Trade","Trade Compliance Suite","Closed-Won",102000,100,"Ananya Kumar","2024-02-14","Sales"),
        (28,28,"BrightMind EdTech","Learning Management System","Prospect",7000,10,"Kiran Mehta","2024-12-10","Sales"),
        (29,29,"ClearPath Insurance","Claims Automation Engine","Closed-Won",78000,100,"Priya Nair","2024-04-18","Sales"),
        (30,30,"DawnRise Manufacturing","Smart Factory Integration","Negotiation",118000,82,"Rahul Singh","2024-08-10","Sales"),
        (31,1,"Apex Retail Corp","2025 Renewal Add-On","Proposal",32000,60,"Ananya Kumar","2024-10-20","Sales"),
        (32,4,"DeltaWave Finance","Compliance Module Upgrade","Closed-Won",45000,100,"Kiran Mehta","2024-12-12","Sales"),
        (33,8,"HorizonBank","AML Analytics Add-On","Proposal",38000,55,"Priya Nair","2024-10-12","Sales"),
        (34,14,"NovaMed Pharma","Lab Data Integration","Closed-Won",55000,100,"Rahul Singh","2024-12-18","Sales"),
        (35,27,"AtlasGlobal Trade","2025 Enterprise Renewal","Proposal",98000,65,"Ananya Kumar","2024-10-08","Sales"),
        (36,6,"FusionMed Hospital","Telehealth Module","Qualified",29000,40,"Kiran Mehta","2024-10-25","Sales"),
        (37,2,"BlueSky Logistics","Warehouse Automation Phase 2","Prospect",43000,25,"Priya Nair","2024-11-30","Sales"),
        (38,30,"DawnRise Manufacturing","Predictive Maintenance","Closed-Won",67000,100,"Rahul Singh","2024-12-25","Sales"),
        (39,20,"TerraFlex Properties","Market Intelligence Tool","Qualified",34000,35,"Ananya Kumar","2024-11-10","Sales"),
        (40,10,"JetStream Airways","Fuel Cost Optimizer","Closed-Won",95000,100,"Kiran Mehta","2024-12-29","Sales"),
    ]
    cur.executemany("INSERT OR REPLACE INTO deals VALUES (?,?,?,?,?,?,?,?,?,?)", deals)

    # ── TABLE 3: financials ───────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS financials (
        id INTEGER PRIMARY KEY, month TEXT, revenue REAL,
        cost_of_goods REAL, operating_cost REAL, profit REAL, budget REAL, headcount INTEGER
    )""")
    financials = [
        (1,"2023-01",750000,420000,380000,-50000,800000,48),
        (2,"2023-02",710000,390000,375000,-55000,800000,48),
        (3,"2023-03",890000,440000,380000,70000,850000,49),
        (4,"2023-04",1120000,510000,390000,220000,900000,51),
        (5,"2023-05",1250000,550000,400000,300000,920000,51),
        (6,"2023-06",1320000,580000,410000,330000,960000,52),
        (7,"2023-07",850000,460000,420000,-30000,1000000,53),
        (8,"2023-08",820000,450000,420000,-50000,1020000,54),
        (9,"2023-09",980000,490000,425000,65000,1050000,55),
        (10,"2023-10",1280000,590000,430000,260000,1080000,56),
        (11,"2023-11",1350000,610000,430000,310000,1120000,57),
        (12,"2023-12",1650000,720000,460000,470000,1200000,58),
        (13,"2024-01",950000,520000,480000,-50000,1150000,58),
        (14,"2024-02",920000,510000,480000,-70000,1180000,59),
        (15,"2024-03",1180000,580000,490000,110000,1260000,60),
        (16,"2024-04",1420000,680000,510000,230000,1280000,61),
        (17,"2024-05",1510000,720000,520000,270000,1300000,62),
        (18,"2024-06",1680000,780000,530000,370000,1350000,63),
    ]
    cur.executemany("INSERT OR REPLACE INTO financials VALUES (?,?,?,?,?,?,?,?)", financials)

    # ── TABLE 4: team ─────────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS team (
        id INTEGER PRIMARY KEY, name TEXT, department TEXT, role TEXT,
        salary REAL, performance REAL, tenure_years REAL, status TEXT
    )""")
    team = [
        (1,"Priya Nair","Sales","Senior Sales Executive",72000,4.5,3.5,"Active"),
        (2,"Rahul Singh","Sales","Sales Executive",62000,4.2,2.8,"Active"),
        (3,"Ananya Kumar","Sales","Sales Executive",62000,4.0,2.1,"Active"),
        (4,"Kiran Mehta","Sales","Account Manager",68000,4.3,4.0,"Active"),
        (5,"Deepa Krishnan","Sales","Sales Trainee",38000,3.2,0.5,"Active"),
        (6,"Arjun Nambiar","Finance","CFO",145000,4.8,7.0,"Active"),
        (7,"Meera Pillai","Finance","Financial Analyst",75000,4.4,3.2,"Active"),
        (8,"Suresh Babu","Finance","Accounts Manager",65000,4.1,5.0,"Active"),
        (9,"Divya Menon","Operations","Operations Manager",88000,4.6,6.0,"Active"),
        (10,"Ravi Chandran","Operations","Logistics Coordinator",55000,3.8,2.5,"Active"),
        (11,"Lakshmi Iyer","Operations","Process Analyst",58000,4.0,1.8,"On-Leave"),
        (12,"Arun Pillai","HR","HR Manager",78000,4.3,4.5,"Active"),
        (13,"Sowmya Nair","HR","HR Executive",52000,3.9,2.0,"Active"),
        (14,"Vinod Kumar","Technology","CTO",150000,4.9,5.5,"Active"),
        (15,"Nisha Raj","Technology","Senior Developer",95000,4.7,3.0,"Active"),
    ]
    cur.executemany("INSERT OR REPLACE INTO team VALUES (?,?,?,?,?,?,?,?)", team)

    # ── TABLE 5: decisions ────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY, date TEXT, category TEXT, decision TEXT,
        outcome TEXT, financial_impact REAL, confidence_at_time INTEGER, lesson TEXT
    )""")
    decisions = [
        (1,"2023-01-10","Expansion","Expanded to Chennai branch","Failed",-180000,62,"Logistics and local market not analyzed. Closed after 5 months."),
        (2,"2023-02-15","Hiring","Hired 10 sales reps in Q1 2023","Success",320000,78,"Demand aligned with capacity. Revenue grew 18% within 2 quarters."),
        (3,"2023-03-01","Marketing","Cut prices by 10% to fight new competitor","Mixed",-25000,55,"Volume grew 25% but gross margins dropped 12%. Profit flat."),
        (4,"2023-04-20","Operations","Invested in warehouse automation software","Success",210000,82,"Operational cost down 15%; picking errors near zero."),
        (5,"2023-05-05","Operations","Outsourced logistics to 3rd-party provider","Failed",-140000,48,"SLA breaches led to 40% increase in customer complaints."),
        (6,"2023-06-12","Product","Launched premium product line","Success",275000,71,"Brand differentiation. High margins offset lower volume."),
        (7,"2023-07-18","Marketing","Increased social media spend by 50%","Mixed",15000,60,"Awareness up but conversion rate was low. High CAC."),
        (8,"2023-08-22","Expansion","Expanded to Bangalore (new city, 2023)","Failed",-220000,57,"Underestimated competition. Did not localize. Exited in 6 months."),
        (9,"2023-09-30","Marketing","Implemented customer referral program","Success",190000,75,"LTV increased 22%. High-quality inbound leads."),
        (10,"2023-10-14","Hiring","Hired full-time CTO","Success",450000,88,"Tech debt cleared. Product velocity up 30%."),
        (11,"2023-11-05","Operations","Moved to remote-first work policy","Mixed",-8000,64,"Employee satisfaction up; collaboration slightly reduced."),
        (12,"2023-12-20","Finance","Secured bulk inventory purchase at 20% discount","Failed",-95000,52,"No warehouse space. External storage costs ate the discount."),
        (13,"2024-01-08","Hiring","Promoted Priya Nair to Senior Sales Exec","Success",95000,85,"Win rate on enterprise deals improved 15%."),
        (14,"2024-02-10","Product","Launched API integration product tier","Success",310000,80,"3 enterprise clients upsold immediately. ARR grew 22%."),
        (15,"2024-03-01","Finance","Renegotiated vendor contract for 3 years","Success",130000,79,"Fixed cost base. Saved 8% on COGS per year."),
        (16,"2024-03-15","Expansion","Opened Hyderabad co-working office","Mixed",20000,65,"Cost lower than expected, but team collaboration uneven."),
        (17,"2024-04-01","Hiring","Hired 2 operations coordinators","Success",60000,74,"Reduced delivery delay complaints by 35%."),
        (18,"2024-04-20","Marketing","Ran TV ad campaign for product launch","Failed",-80000,45,"Wrong channel for target audience. Low ROI."),
        (19,"2024-05-10","Product","Integrated AI-based churn prediction module","Success",180000,83,"Retained 5 at-risk enterprise clients. Saved $180k ARR."),
        (20,"2024-05-25","Finance","Invested in 2-year office lease extension","Success",50000,76,"Locked in current rate. Market rates rose 18% after signing."),
        (21,"2024-06-05","Operations","Adopted real-time inventory tracking system","Success",155000,81,"Stock-outs dropped 60%. On-time delivery improved to 94%."),
        (22,"2024-06-20","Hiring","Attempt to hire 5 senior developers","Failed",-40000,55,"Only 2 hired; 3 offers rejected due to below-market salary."),
        (23,"2024-07-01","Marketing","Launched B2B LinkedIn outreach campaign","Success",125000,72,"Pipeline grew by 18 qualified deals in 45 days."),
        (24,"2024-07-15","Product","Delayed mobile app launch by 2 months","Mixed",-30000,61,"Quality improved but competitor launched first. Market share dip."),
        (25,"2024-08-01","Expansion","Started Southeast Asia expansion feasibility","Mixed",10000,58,"Research phase only. No commit yet. Market looks promising."),
    ]
    cur.executemany("INSERT OR REPLACE INTO decisions VALUES (?,?,?,?,?,?,?,?)", decisions)

    # ── TABLE 6: products ─────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY, name TEXT, category TEXT, sku TEXT,
        unit_price REAL, unit_cost REAL, margin_pct REAL,
        units_sold_ytd INTEGER, revenue_ytd REAL, inventory_qty INTEGER,
        reorder_point INTEGER, status TEXT
    )""")
    products = [
        (1,"Analytics Pro","SaaS","FRI-PRO-001",299,45,84.9,142,42458,0,0,"Active"),
        (2,"Analytics Enterprise","SaaS","FRI-ENT-001",999,150,85.0,38,37962,0,0,"Active"),
        (3,"Analytics Starter","SaaS","FRI-STR-001",99,18,81.8,285,28215,0,0,"Active"),
        (4,"Decision API Access","SaaS","FRI-API-001",199,35,82.4,67,13333,0,0,"Active"),
        (5,"Data Connector Premium","SaaS","FRI-CON-001",149,28,81.2,89,13261,0,0,"Active"),
        (6,"Custom Integration Service","Service","FRI-SVC-001",5000,2000,60.0,18,90000,0,0,"Active"),
        (7,"Onboarding & Training","Service","FRI-TRN-001",2500,800,68.0,42,105000,0,0,"Active"),
        (8,"Annual Business Review","Service","FRI-ABR-001",1500,400,73.3,28,42000,0,0,"Active"),
        (9,"Data Migration Service","Service","FRI-MIG-001",8000,3500,56.3,8,64000,0,0,"Active"),
        (10,"Strategic Advisory","Service","FRI-ADV-001",3500,1200,65.7,12,42000,0,0,"Active"),
        (11,"Edge Gateway Device","Hardware","FRI-HW-001",1500,850,43.3,34,51000,45,20,"Active"),
        (12,"Analytics Dashboard Hub","Hardware","FRI-HW-002",3200,1800,43.8,18,57600,22,10,"Active"),
        (13,"Data Collection Pod","Hardware","FRI-HW-003",800,420,47.5,56,44800,78,30,"Active"),
        (14,"Support Plan Silver","Support","FRI-SUP-001",250,80,68.0,89,22250,0,0,"Active"),
        (15,"Support Plan Gold","Support","FRI-SUP-002",500,150,70.0,62,31000,0,0,"Active"),
        (16,"Support Plan Platinum","Support","FRI-SUP-003",1200,380,68.3,28,33600,0,0,"Active"),
        (17,"Advanced Analytics Module","Add-on","FRI-ADD-001",149,30,79.9,78,11622,0,0,"Active"),
        (18,"Compliance Reporting Add-on","Add-on","FRI-ADD-002",99,20,79.8,45,4455,0,0,"Active"),
        (19,"White-Label License","License","FRI-LIC-001",2000,500,75.0,4,8000,0,0,"Limited"),
        (20,"Legacy System Bridge","Service","FRI-LGB-001",6000,2800,53.3,3,18000,0,0,"Limited"),
    ]
    cur.executemany("INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", products)

    # ── TABLE 7: inventory ────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY, product_name TEXT, sku TEXT,
        qty_on_hand INTEGER, reorder_point INTEGER, days_of_supply INTEGER,
        last_restocked TEXT, warehouse_location TEXT, status TEXT
    )""")
    inventory = [
        (1,"Edge Gateway Device","FRI-HW-001",45,20,18,"2024-05-20","Warehouse A","OK"),
        (2,"Analytics Dashboard Hub","FRI-HW-002",22,10,25,"2024-04-15","Warehouse A","OK"),
        (3,"Data Collection Pod","FRI-HW-003",78,30,21,"2024-06-01","Warehouse B","OK"),
        (4,"Power Adapter Kit","ACC-PWR-001",142,50,28,"2024-05-10","Warehouse A","OK"),
        (5,"Ethernet Module","ACC-ETH-001",89,40,22,"2024-05-25","Warehouse A","OK"),
        (6,"Mounting Bracket Set","ACC-MNT-001",205,80,25,"2024-04-20","Warehouse B","OK"),
        (7,"Replacement Battery Pack","ACC-BAT-001",38,30,12,"2024-06-10","Warehouse B","Low"),
        (8,"USB-C Hub 4-Port","ACC-USB-001",15,25,6,"2024-03-15","Warehouse A","Critical"),
        (9,"Network Switch 8-Port","ACC-NET-001",28,20,14,"2024-05-05","Warehouse A","Low"),
        (10,"Rugged Carrying Case","ACC-CAS-001",62,25,24,"2024-04-30","Warehouse B","OK"),
        (11,"Demo Unit - Pro Bundle","DEMO-001",8,5,60,"2024-06-15","Demo Room","OK"),
        (12,"Sensor Array Module","ACC-SEN-001",12,15,8,"2024-02-28","Warehouse B","Critical"),
        (13,"Cloud Activation Cards","SW-CAR-001",350,100,70,"2024-06-20","Warehouse A","OK"),
        (14,"Training Kit Materials","SVC-TRN-001",45,20,45,"2024-05-01","Office","OK"),
        (15,"Hardware Warranty Cards","DOC-WRN-001",180,50,60,"2024-04-01","Office","OK"),
    ]
    cur.executemany("INSERT OR REPLACE INTO inventory VALUES (?,?,?,?,?,?,?,?,?)", inventory)

    # ── TABLE 8: campaigns ────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY, name TEXT, channel TEXT,
        start_date TEXT, end_date TEXT, budget REAL, spend REAL,
        leads_generated INTEGER, mql_count INTEGER, sql_count INTEGER,
        conversions INTEGER, revenue_attributed REAL, roi_pct REAL, status TEXT
    )""")
    campaigns = [
        (1,"Q1 LinkedIn B2B Campaign","LinkedIn","2023-01-05","2023-03-31",15000,14200,342,89,28,11,87500,516.2,"Completed"),
        (2,"Google Search - Analytics Intent","Google Ads","2023-01-15","2023-06-30",25000,23800,512,128,45,19,156000,555.5,"Completed"),
        (3,"Email Nurture - Enterprise Prospects","Email","2023-02-01","2023-12-31",8000,7200,890,198,62,28,105000,1358.3,"Completed"),
        (4,"SaaStr Conference 2023","Events","2023-04-15","2023-04-17",35000,34500,89,42,18,8,185000,436.2,"Completed"),
        (5,"Content Marketing - SEO Blog","Content","2023-01-01","2023-12-31",42000,38500,2840,420,95,38,312000,710.4,"Completed"),
        (6,"Q2 Retargeting Campaign","Google Ads","2023-04-01","2023-06-30",12000,11200,245,62,22,9,72000,542.9,"Completed"),
        (7,"Webinar Series - Decision Intelligence","Webinar","2023-05-01","2023-11-30",18000,16500,1240,285,82,32,224000,1257.6,"Completed"),
        (8,"Product Hunt Launch","Product Hunt","2023-07-10","2023-07-10",5000,4800,1580,320,88,42,168000,3400.0,"Completed"),
        (9,"Q3 LinkedIn Enterprise Push","LinkedIn","2023-07-01","2023-09-30",20000,18900,428,98,35,15,132500,601.1,"Completed"),
        (10,"Email Win-Back Campaign","Email","2023-08-01","2023-10-31",6000,5400,320,65,18,7,42000,677.8,"Completed"),
        (11,"Q4 Year-End Push","Email","2023-10-01","2023-12-31",22000,20500,580,145,52,24,198000,866.0,"Completed"),
        (12,"2024 Brand Awareness - YouTube","YouTube","2024-01-01","2024-06-30",30000,22000,892,178,52,22,148000,572.7,"Completed"),
        (13,"Q1 2024 LinkedIn ABM","LinkedIn","2024-01-15","2024-03-31",18000,16800,285,72,28,12,98000,483.3,"Completed"),
        (14,"Google Performance Max Q2 2024","Google Ads","2024-04-01","2024-06-30",28000,25200,648,158,55,23,189000,650.0,"Completed"),
        (15,"Analyst Relations & PR Q2 2024","PR/Media","2024-03-01","2024-06-30",45000,42000,0,0,0,0,0,-100.0,"Completed"),
    ]
    cur.executemany("INSERT OR REPLACE INTO campaigns VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", campaigns)

    # ── TABLE 9: support_tickets ──────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY, customer_name TEXT, category TEXT,
        priority TEXT, status TEXT, opened_date TEXT, resolved_date TEXT,
        resolution_days INTEGER, csat_score REAL, agent TEXT
    )""")
    support_tickets = [
        (1,"HorizonBank","Integration","Critical","Closed","2023-01-05","2023-01-06",1,5.0,"Vinod Kumar"),
        (2,"DeltaWave Finance","Bug","High","Closed","2023-01-08","2023-01-10",2,4.5,"Nisha Raj"),
        (3,"Apex Retail Corp","Feature Request","Medium","Closed","2023-01-12","2023-01-20",8,4.0,"Priya Nair"),
        (4,"NovaMed Pharma","Integration","Critical","Closed","2023-01-15","2023-01-16",1,5.0,"Vinod Kumar"),
        (5,"EcoGrow Industries","Billing","High","Closed","2023-01-18","2023-01-22",4,3.5,"Meera Pillai"),
        (6,"FusionMed Hospital","Bug","High","Closed","2023-01-20","2023-01-23",3,4.5,"Nisha Raj"),
        (7,"InnovateTech Startup","Training","Low","Closed","2023-01-25","2023-02-01",7,4.0,"Ananya Kumar"),
        (8,"BlueSky Logistics","Integration","High","Closed","2023-01-28","2023-01-31",3,4.0,"Vinod Kumar"),
        (9,"KloudBase SaaS","Bug","Medium","Closed","2023-02-02","2023-02-06",4,3.5,"Nisha Raj"),
        (10,"DawnRise Manufacturing","Feature Request","Medium","Closed","2023-02-05","2023-02-15",10,4.0,"Rahul Singh"),
        (11,"AtlasGlobal Trade","Integration","High","Closed","2023-02-08","2023-02-10",2,5.0,"Vinod Kumar"),
        (12,"HorizonBank","Security","Critical","Closed","2023-02-12","2023-02-13",1,5.0,"Vinod Kumar"),
        (13,"LunarFarm Organics","Billing","High","Closed","2023-02-15","2023-02-20",5,3.0,"Meera Pillai"),
        (14,"CoreTech Solutions","Training","Low","Closed","2023-02-18","2023-02-28",10,4.5,"Ananya Kumar"),
        (15,"VeroVault Security","Integration","Critical","Closed","2023-02-20","2023-02-21",1,5.0,"Vinod Kumar"),
        (16,"TerraFlex Properties","Feature Request","Medium","Closed","2023-03-01","2023-03-12",11,3.5,"Kiran Mehta"),
        (17,"JetStream Airways","Bug","High","Closed","2023-03-05","2023-03-08",3,4.0,"Nisha Raj"),
        (18,"ClearPath Insurance","Integration","High","Closed","2023-03-10","2023-03-13",3,4.5,"Vinod Kumar"),
        (19,"MetroCity Council","Training","Medium","Closed","2023-03-14","2023-03-21",7,4.0,"Ananya Kumar"),
        (20,"XenithAI Labs","Bug","Medium","Closed","2023-03-18","2023-03-22",4,3.5,"Nisha Raj"),
        (21,"NovaMed Pharma","Feature Request","High","Closed","2023-03-22","2023-04-01",10,4.0,"Rahul Singh"),
        (22,"OmniChain Supply","Integration","Medium","Closed","2023-04-01","2023-04-05",4,4.0,"Vinod Kumar"),
        (23,"UrbanDine Group","Billing","High","Closed","2023-04-05","2023-04-10",5,3.0,"Meera Pillai"),
        (24,"SolarNest Energy","Bug","Low","Closed","2023-04-08","2023-04-14",6,4.5,"Nisha Raj"),
        (25,"Apex Retail Corp","Integration","High","Closed","2023-04-12","2023-04-14",2,5.0,"Vinod Kumar"),
        (26,"DeltaWave Finance","Security","Critical","Closed","2024-04-15","2024-04-16",1,5.0,"Vinod Kumar"),
        (27,"WaveRider Marine","Feature Request","Low","Closed","2024-04-18","2024-04-30",12,4.0,"Kiran Mehta"),
        (28,"GreenPath Energy","Training","Low","Closed","2024-04-22","2024-05-01",9,4.5,"Ananya Kumar"),
        (29,"HorizonBank","Performance","High","Closed","2024-04-25","2024-04-28",3,4.5,"Nisha Raj"),
        (30,"BrightMind EdTech","Billing","Medium","Closed","2024-05-02","2024-05-08",6,3.5,"Meera Pillai"),
        (31,"FusionMed Hospital","Integration","Critical","Closed","2024-05-05","2024-05-06",1,5.0,"Vinod Kumar"),
        (32,"RapidShip Couriers","Bug","Medium","Closed","2024-05-08","2024-05-12",4,4.0,"Nisha Raj"),
        (33,"ZenithCare Clinics","Training","Low","Closed","2024-05-10","2024-05-20",10,4.0,"Ananya Kumar"),
        (34,"AtlasGlobal Trade","Feature Request","Medium","Closed","2024-05-14","2024-05-25",11,3.5,"Rahul Singh"),
        (35,"PeakForm Fitness","Billing","High","Closed","2024-05-18","2024-05-22",4,3.0,"Meera Pillai"),
        (36,"QuantumBuild","Bug","Medium","Closed","2024-05-20","2024-05-25",5,4.5,"Nisha Raj"),
        (37,"DawnRise Manufacturing","Integration","High","Closed","2024-05-25","2024-05-28",3,4.5,"Vinod Kumar"),
        (38,"YellowBrick Retail","Performance","Medium","Closed","2024-07-15","2024-07-20",5,4.0,"Nisha Raj"),
        (39,"ClearPath Insurance","Bug","High","Closed","2024-08-05","2024-08-08",3,4.5,"Nisha Raj"),
        (40,"HorizonBank","Security","Critical","Closed","2024-09-12","2024-09-13",1,5.0,"Vinod Kumar"),
        (41,"NovaMed Pharma","Integration","High","Closed","2024-10-10","2024-10-12",2,4.5,"Vinod Kumar"),
        (42,"BlueSky Logistics","Bug","High","Closed","2024-11-15","2024-11-18",3,4.0,"Nisha Raj"),
        (43,"InnovateTech Startup","Billing","Medium","Closed","2024-11-20","2024-11-22",2,3.5,"Meera Pillai"),
        (44,"EcoGrow Industries","Feature Request","Low","Closed","2024-12-01","2024-12-05",4,4.0,"Ananya Kumar"),
        (45,"TerraFlex Properties","Integration","High","Closed","2024-12-08","2024-12-10",2,4.5,"Vinod Kumar"),
        (46,"KloudBase SaaS","Bug","Medium","Closed","2024-12-15","2024-12-18",3,4.0,"Nisha Raj"),
        (47,"LunarFarm Organics","Billing","High","Closed","2024-12-20","2024-12-23",3,3.0,"Meera Pillai"),
        (48,"JetStream Airways","Performance","High","Closed","2024-12-25","2024-12-26",1,4.5,"Vinod Kumar"),
        (49,"Apex Retail Corp","Feature Request","Medium","Closed","2024-12-28","2024-12-30",2,4.0,"Kiran Mehta"),
        (50,"DeltaWave Finance","Security","Critical","Closed","2024-12-31","2024-12-31",0,5.0,"Vinod Kumar"),
    ]
    cur.executemany("INSERT OR REPLACE INTO support_tickets VALUES (?,?,?,?,?,?,?,?,?,?)", support_tickets)

    # ── TABLE 10: suppliers ───────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY, name TEXT, category TEXT,
        reliability_score REAL, lead_time_days INTEGER, active_contracts INTEGER,
        annual_spend REAL, last_issue_date TEXT, risk_level TEXT
    )""")
    suppliers = [
        (1,"Amazon Web Services","Cloud Infrastructure",98.0,0,3,180000,None,"Low"),
        (2,"Microsoft Azure","Cloud Infrastructure",96.5,0,2,95000,None,"Low"),
        (3,"Lenovo India","Hardware",82.0,14,2,68000,"2024-02-15","Medium"),
        (4,"Ingram Micro","Hardware Distribution",78.0,21,1,42000,"2023-11-20","Medium"),
        (5,"Salesforce","CRM Software",95.0,0,1,28000,None,"Low"),
        (6,"HubSpot","Marketing Software",92.0,0,1,18000,None,"Low"),
        (7,"Workday","HR Software",88.0,0,1,22000,None,"Low"),
        (8,"DHL Express","Logistics / Shipping",71.0,3,1,12000,"2024-03-10","High"),
        (9,"Tata Communications","Networking",85.0,5,2,35000,"2023-09-05","Low"),
        (10,"WeWork India","Office Space",90.0,0,1,96000,None,"Low"),
    ]
    cur.executemany("INSERT OR REPLACE INTO suppliers VALUES (?,?,?,?,?,?,?,?,?)", suppliers)

    # ── TABLE 11: expenses ────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY, month TEXT, salaries REAL, cloud_infrastructure REAL,
        marketing_spend REAL, office_rent REAL, software_tools REAL,
        operations REAL, r_and_d REAL, travel REAL, other REAL, total REAL
    )""")
    expenses = [
        (1,"2023-01",92000,28000,14200,8000,12000,18500,22000,3500,6800,205000),
        (2,"2023-02",92000,26500,7200,8000,12000,18200,22000,2800,5300,194000),
        (3,"2023-03",95000,29000,38500,8000,12500,19000,23000,4200,8800,238000),
        (4,"2023-04",98000,31000,11200,8000,13000,19500,24000,3800,9500,218000),
        (5,"2023-05",98000,32000,16500,8000,13500,20000,24000,4100,8400,224500),
        (6,"2023-06",102000,33500,18900,8200,14000,20500,25000,4500,7400,233000),
        (7,"2023-07",105000,35000,14200,8200,14500,21000,26000,5000,8100,237000),
        (8,"2023-08",105000,36000,5400,8200,14500,21500,26500,4200,7700,229000),
        (9,"2023-09",108000,37500,20500,8500,15000,22000,27000,4800,7700,251000),
        (10,"2023-10",110000,38500,16800,8500,15000,22500,27500,5200,8000,252000),
        (11,"2023-11",112000,40000,20500,8500,15500,23000,28000,5500,8500,261500),
        (12,"2023-12",118000,42000,25200,9000,16500,25000,30000,7500,9800,283000),
        (13,"2024-01",115000,40000,16800,9000,16000,23500,29000,5000,9700,264000),
        (14,"2024-02",118000,41500,7200,9000,16500,24000,29500,4800,9500,260000),
        (15,"2024-03",122000,43500,42000,9500,17000,25000,30000,6200,10300,305500),
        (16,"2024-04",125000,45000,25200,9500,17500,25500,31000,6500,10800,296000),
        (17,"2024-05",128000,46500,16500,9500,18000,26000,32000,5800,11200,293500),
        (18,"2024-06",132000,48000,25200,10000,18500,27000,33000,6800,11500,312000),
        (19,"2024-07",135000,49000,18000,10000,18500,28000,33000,7000,12000,320500),
        (20,"2024-08",135000,47000,12500,10000,18500,27500,33000,6500,11500,311500),
        (21,"2024-09",138000,51000,22500,10500,19000,28500,34000,7200,11800,332500),
        (22,"2024-10",142000,53500,28000,10500,19500,29000,35000,8000,12000,347500),
        (23,"2024-11",145000,55000,32000,10500,19500,29500,35500,8500,12500,358000),
        (24,"2024-12",152000,62000,45000,11000,21000,31000,37000,10500,14500,384000),
    ]
    cur.executemany("INSERT OR REPLACE INTO expenses VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", expenses)

    # ── TABLE 12: kpis ────────────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS kpis (
        id INTEGER PRIMARY KEY, period TEXT, mrr REAL, arr REAL,
        churn_rate_pct REAL, nps_score INTEGER, customer_acquisition_cost REAL,
        avg_deal_size REAL, pipeline_velocity_days REAL, win_rate_pct REAL
    )""")
    kpis = [
        (1,"Q1 2023",750000,9000000,3.2,42,3200,4500,68,24.0),
        (2,"Q2 2023",980000,11760000,2.2,48,2600,4800,64,28.5),
        (3,"Q3 2023",830000,9960000,4.5,39,3500,4200,72,21.0),
        (4,"Q4 2023",1180000,14160000,1.8,52,2200,5600,57,32.5),
        (5,"Q1 2024",950000,11400000,3.8,44,3000,4900,65,23.8),
        (6,"Q2 2024",1280000,15360000,2.1,50,2150,6100,55,30.2),
        (7,"Q3 2024",1080000,12960000,4.2,41,3300,5100,68,22.4),
        (8,"Q4 2024",1520000,18240000,1.6,55,2000,6500,52,34.8),
    ]
    cur.executemany("INSERT OR REPLACE INTO kpis VALUES (?,?,?,?,?,?,?,?,?,?)", kpis)

    # ── TABLE 13: contracts ───────────────────────────────────────────────────
    cur.execute("""CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY, customer_name TEXT, arr REAL,
        start_date TEXT, renewal_date TEXT, health_score INTEGER,
        status TEXT, products TEXT, expansion_potential TEXT
    )""")
    contracts = [
        (1,"Apex Retail Corp",384000,"2023-01-15","2024-12-31",92,"Active","Analytics Enterprise + Support Gold","Medium"),
        (2,"BlueSky Logistics",330000,"2022-06-01","2024-08-31",62,"At Risk","Analytics Enterprise + API","Low"),
        (3,"CoreTech Solutions",114000,"2023-03-01","2025-02-28",85,"Active","Analytics Pro + Support Silver","High"),
        (4,"DeltaWave Finance",492000,"2022-01-20","2024-11-30",95,"Active","Analytics Enterprise + Compliance Add-on","High"),
        (5,"EcoGrow Industries",57600,"2023-08-01","2024-07-31",38,"At Risk","Analytics Starter + Data Pod","Low"),
        (6,"FusionMed Hospital",456000,"2022-04-10","2025-03-31",88,"Active","Analytics Enterprise + Support Platinum","High"),
        (7,"GreenPath Energy",86400,"2023-01-15","2024-12-31",72,"Active","Analytics Pro + Advanced Module","Medium"),
        (8,"HorizonBank",624000,"2021-11-01","2024-10-31",91,"Active","Analytics Enterprise x2 + Support Platinum","High"),
        (9,"InnovateTech Startup",21600,"2024-02-01","2025-01-31",45,"At Risk","Analytics Starter","Low"),
        (10,"JetStream Airways",348000,"2022-09-15","2024-09-14",70,"At Risk","Analytics Enterprise + Gateway Devices","Low"),
        (11,"NovaMed Pharma",534000,"2021-06-01","2025-05-31",94,"Active","Analytics Enterprise + Integration + Support Platinum","High"),
        (12,"SolarNest Energy",108000,"2023-05-12","2025-04-30",82,"Active","Analytics Pro + Advanced Module","Medium"),
        (13,"AtlasGlobal Trade",408000,"2022-02-14","2024-11-30",89,"Active","Analytics Enterprise + Compliance Add-on","High"),
        (14,"ClearPath Insurance",342000,"2022-08-18","2025-07-31",87,"Active","Analytics Enterprise + Support Gold","Medium"),
        (15,"DawnRise Manufacturing",552000,"2021-10-01","2024-09-30",76,"At Risk","Analytics Enterprise + Gateway Devices + Support Platinum","Medium"),
    ]
    cur.executemany("INSERT OR REPLACE INTO contracts VALUES (?,?,?,?,?,?,?,?,?)", contracts)

    conn.commit()
    conn.close()
    print(f"[OK] Database created at: {DB_PATH}")


def export_knowledge_json():
    """Export narrative sentences from all 13 tables to crm_knowledge.json."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    entries = []

    # ── Customers ──────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM customers").fetchall():
        entries.append({"type":"customer","id":row["id"],"text":(
            f"Customer '{row['name']}' is a {row['segment']} client in {row['industry']}. "
            f"Lifetime value ${row['ltv']:,.0f}, {row['deals_count']} deals completed, "
            f"churn risk: {row['churn_risk'].upper()}, status: {row['status']}, since {row['since_year']}."
        )})

    # ── Deals ──────────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM deals").fetchall():
        entries.append({"type":"deal","id":row["id"],"text":(
            f"Deal '{row['title']}' with {row['customer_name']} is in stage '{row['stage']}'. "
            f"Value ${row['value']:,.0f}, win probability {row['probability']}%, "
            f"expected close {row['close_date']}, owned by {row['owner']}."
        )})

    # ── Financials ─────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM financials").fetchall():
        margin = round(row['profit']/row['revenue']*100, 1) if row['revenue'] else 0
        entries.append({"type":"financial","id":row["id"],"text":(
            f"In {row['month']}: Revenue ${row['revenue']:,.0f}, profit ${row['profit']:,.0f} ({margin}% margin), "
            f"COGS ${row['cost_of_goods']:,.0f}, operating costs ${row['operating_cost']:,.0f}, "
            f"budget ${row['budget']:,.0f}, headcount {row['headcount']}."
        )})

    # ── Team ───────────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM team").fetchall():
        entries.append({"type":"team","id":row["id"],"text":(
            f"{row['name']} is {row['role']} in {row['department']}. "
            f"Salary ${row['salary']:,.0f}/yr, performance {row['performance']}/5, "
            f"tenure {row['tenure_years']}yrs, status {row['status']}."
        )})

    # ── Decisions ──────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM decisions").fetchall():
        sign = "+" if row['financial_impact'] >= 0 else "-"
        amt = abs(row['financial_impact'])
        entries.append({"type":"decision","id":row["id"],"text":(
            f"Decision on {row['date']} ({row['category']}): '{row['decision']}'. "
            f"Outcome: {row['outcome']}. Financial impact: {sign}${amt:,.0f}. "
            f"Confidence then: {row['confidence_at_time']}%. Lesson: {row['lesson']}"
        )})

    # ── Products ───────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM products").fetchall():
        entries.append({"type":"product","id":row["id"],"text":(
            f"Product '{row['name']}' ({row['category']}, SKU {row['sku']}): "
            f"priced at ${row['unit_price']}/unit, cost ${row['unit_cost']}, margin {row['margin_pct']}%. "
            f"Sold {row['units_sold_ytd']} units YTD generating ${row['revenue_ytd']:,.0f} revenue. "
            f"Status: {row['status']}."
        )})

    # ── Inventory ──────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM inventory").fetchall():
        entries.append({"type":"inventory","id":row["id"],"text":(
            f"Inventory item '{row['product_name']}' (SKU {row['sku']}): "
            f"{row['qty_on_hand']} units on hand in {row['warehouse_location']}. "
            f"Reorder point {row['reorder_point']}, {row['days_of_supply']} days of supply. "
            f"Last restocked {row['last_restocked']}. Status: {row['status']}."
        )})

    # ── Campaigns ──────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM campaigns").fetchall():
        entries.append({"type":"campaign","id":row["id"],"text":(
            f"Marketing campaign '{row['name']}' via {row['channel']} ({row['start_date']} to {row['end_date']}): "
            f"Budget ${row['budget']:,.0f}, spent ${row['spend']:,.0f}. "
            f"Generated {row['leads_generated']} leads, {row['mql_count']} MQLs, {row['conversions']} conversions. "
            f"Revenue attributed: ${row['revenue_attributed']:,.0f}, ROI: {row['roi_pct']}%."
        )})

    # ── Support Tickets ────────────────────────────────────────────────────────
    closed = cur.execute(
        "SELECT COUNT(*) as c, AVG(resolution_days) as avg_days, AVG(csat_score) as avg_csat "
        "FROM support_tickets WHERE status='Closed' AND resolution_days IS NOT NULL"
    ).fetchone()
    open_count = cur.execute("SELECT COUNT(*) as c FROM support_tickets WHERE status IN ('Open','In Progress')").fetchone()
    critical = cur.execute("SELECT COUNT(*) as c FROM support_tickets WHERE priority='Critical'").fetchone()
    entries.append({"type":"support_summary","id":1,"text":(
        f"Support ticket summary: {closed['c']} resolved tickets, avg resolution time {round(closed['avg_days'],1)} days, "
        f"avg CSAT score {round(closed['avg_csat'],1)}/5. "
        f"{open_count['c']} tickets currently open/in-progress. {critical['c']} critical priority tickets raised."
    )})
    for row in cur.execute("SELECT * FROM support_tickets WHERE priority IN ('Critical','High') ORDER BY opened_date DESC LIMIT 10").fetchall():
        entries.append({"type":"support_ticket","id":row["id"],"text":(
            f"Support ticket from {row['customer_name']}: {row['category']} issue, priority {row['priority']}, "
            f"status {row['status']}. Opened {row['opened_date']}, "
            f"resolved in {row['resolution_days']} days, CSAT {row['csat_score']}/5."
            if row['resolution_days'] else
            f"Support ticket from {row['customer_name']}: {row['category']} issue, priority {row['priority']}, "
            f"status {row['status']}. Opened {row['opened_date']}. Awaiting resolution."
        )})

    # ── Suppliers ──────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM suppliers").fetchall():
        issue_str = f"Last issue: {row['last_issue_date']}." if row['last_issue_date'] else "No recent issues."
        entries.append({"type":"supplier","id":row["id"],"text":(
            f"Supplier '{row['name']}' ({row['category']}): reliability score {row['reliability_score']}/100, "
            f"lead time {row['lead_time_days']} days, {row['active_contracts']} active contracts, "
            f"annual spend ${row['annual_spend']:,.0f}. Risk: {row['risk_level']}. {issue_str}"
        )})

    # ── Expenses ───────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM expenses ORDER BY month").fetchall():
        entries.append({"type":"expense","id":row["id"],"text":(
            f"In {row['month']}, total expenses were ${row['total']:,.0f}: "
            f"Salaries ${row['salaries']:,.0f}, Cloud ${row['cloud_infrastructure']:,.0f}, "
            f"Marketing ${row['marketing_spend']:,.0f}, Office ${row['office_rent']:,.0f}, "
            f"Software ${row['software_tools']:,.0f}, Ops ${row['operations']:,.0f}, "
            f"R&D ${row['r_and_d']:,.0f}, Travel ${row['travel']:,.0f}."
        )})

    # ── KPIs ───────────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM kpis").fetchall():
        entries.append({"type":"kpi","id":row["id"],"text":(
            f"KPIs for {row['period']}: MRR ${row['mrr']:,.0f}, ARR ${row['arr']:,.0f}, "
            f"churn rate {row['churn_rate_pct']}%, NPS {row['nps_score']}, "
            f"CAC ${row['customer_acquisition_cost']:,.0f}, avg deal size ${row['avg_deal_size']:,.0f}, "
            f"pipeline velocity {row['pipeline_velocity_days']} days, win rate {row['win_rate_pct']}%."
        )})

    # ── Contracts ──────────────────────────────────────────────────────────────
    for row in cur.execute("SELECT * FROM contracts").fetchall():
        entries.append({"type":"contract","id":row["id"],"text":(
            f"Contract with {row['customer_name']}: ARR ${row['arr']:,.0f}, "
            f"health score {row['health_score']}/100, renews {row['renewal_date']}. "
            f"Status: {row['status']}. Products: {row['products']}. "
            f"Expansion potential: {row['expansion_potential']}."
        )})

    # ── Aggregate Knowledge Summaries ──────────────────────────────────────────
    # Top products by revenue
    top_prods = cur.execute("SELECT name, category, revenue_ytd, margin_pct FROM products ORDER BY revenue_ytd DESC LIMIT 5").fetchall()
    entries.append({"type":"insight","id":1001,"text":(
        "Top revenue-generating products YTD: " +
        ", ".join([f"{r['name']} (${r['revenue_ytd']:,.0f}, {r['margin_pct']}% margin)" for r in top_prods]) + "."
    )})
    # Campaign ROI leaders
    top_camp = cur.execute("SELECT name, channel, roi_pct, conversions FROM campaigns WHERE roi_pct > 0 ORDER BY roi_pct DESC LIMIT 3").fetchall()
    entries.append({"type":"insight","id":1002,"text":(
        "Highest ROI marketing campaigns: " +
        ", ".join([f"{r['name']} via {r['channel']} ({r['roi_pct']}% ROI, {r['conversions']} conversions)" for r in top_camp]) + "."
    )})
    # Contract renewal risk
    at_risk_contracts = cur.execute("SELECT customer_name, arr, renewal_date, health_score FROM contracts WHERE status='At Risk' ORDER BY arr DESC").fetchall()
    entries.append({"type":"insight","id":1003,"text":(
        "Contracts at risk of not renewing: " +
        ", ".join([f"{r['customer_name']} (ARR ${r['arr']:,.0f}, health {r['health_score']}/100, renews {r['renewal_date']})" for r in at_risk_contracts]) +
        ". Total at-risk ARR: $" + f"{sum(r['arr'] for r in at_risk_contracts):,.0f}."
    )})
    # KPI trend
    kpi_trend = cur.execute("SELECT period, arr, churn_rate_pct, nps_score FROM kpis ORDER BY id").fetchall()
    entries.append({"type":"insight","id":1004,"text":(
        "Business KPI trend: ARR grew from ${:,.0f} in {} to ${:,.0f} in {}. "
        "Churn improved from {}% to {}%. NPS improved from {} to {}.".format(
            kpi_trend[0]['arr'], kpi_trend[0]['period'],
            kpi_trend[-1]['arr'], kpi_trend[-1]['period'],
            kpi_trend[0]['churn_rate_pct'], kpi_trend[-1]['churn_rate_pct'],
            kpi_trend[0]['nps_score'], kpi_trend[-1]['nps_score']
        )
    )})
    # Expense trend
    exp_rows = cur.execute("SELECT month, total, salaries, cloud_infrastructure FROM expenses ORDER BY month DESC LIMIT 3").fetchall()
    entries.append({"type":"insight","id":1005,"text":(
        "Recent monthly expense trend: " +
        ", ".join([f"{r['month']}: ${r['total']:,.0f} total (salaries ${r['salaries']:,.0f}, cloud ${r['cloud_infrastructure']:,.0f})" for r in exp_rows]) + "."
    )})
    # Supplier risk
    risky = cur.execute("SELECT name, reliability_score, last_issue_date FROM suppliers WHERE risk_level='High'").fetchall()
    entries.append({"type":"insight","id":1006,"text":(
        "High-risk suppliers: " + (
            ", ".join([f"{r['name']} (reliability {r['reliability_score']}/100, last issue {r['last_issue_date']})" for r in risky])
            if risky else "None flagged."
        )
    )})
    # Inventory alerts
    critical_inv = cur.execute("SELECT product_name, qty_on_hand, reorder_point, days_of_supply FROM inventory WHERE status IN ('Critical','Low') ORDER BY days_of_supply").fetchall()
    entries.append({"type":"insight","id":1007,"text":(
        "Inventory alerts: " +
        ", ".join([f"{r['product_name']} has {r['qty_on_hand']} units ({r['days_of_supply']} days supply, reorder at {r['reorder_point']})" for r in critical_inv]) +
        ". Immediate reorder required for critical items."
        if critical_inv else "All inventory levels are healthy."
    )})

    conn.close()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print(f"[OK] Knowledge JSON exported: {JSON_PATH} ({len(entries)} entries)")


if __name__ == "__main__":
    create_db()
    export_knowledge_json()
    print("\n[DONE] 13-table CRM Knowledge Base ready. Restart the backend.")
