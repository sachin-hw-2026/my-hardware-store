import streamlit as st
import pandas as pd
import json
import os

# --- WEB PAGE CONFIGURATION ---
st.set_page_config(page_title="Apni Hardware Store", page_icon="⚙️", layout="wide")

# --- PERMANENT STORAGE FILE ---
DATA_FILE = "dukan_data.json"

# File se data load karne ka function
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        # Agar file nahi bani hai toh ye shuruat ka default maal hai
        return {
            "stock": {
                "1": {"name": "Hammer (Hathaudi)",   "cat": "General Hardware", "wholesale": 80,   "retail": 120,  "total": 25,  "sold": 15},
                "2": {"name": "PVC Pipe 1 Inch",     "cat": "Plumbing",         "wholesale": 120,  "retail": 150,  "total": 100, "sold": 45},
                "3": {"name": "Wash Basin",          "cat": "Sanitary",         "wholesale": 800,  "retail": 1200, "total": 15,  "sold": 3},
                "4": {"name": "Asian Paint White 1L","cat": "Paints",           "wholesale": 210,  "retail": 260,  "total": 20,  "sold": 8},
                "5": {"name": "Sprayer Pump (Kheti)", "cat": "Agriculture",      "wholesale": 1200, "retail": 1500, "total": 10,  "sold": 2},
            },
            "demands": []
        }

# File me data pakka save karne ka function
def save_data_to_file():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.dukan_data, f, indent=4)

# Session state ko file se jodhna
if "dukan_data" not in st.session_state:
    st.session_state.dukan_data = load_data()

# Data nikalna loop chalane ke liye
stock = st.session_state.dukan_data["stock"]
demands = st.session_state.dukan_data["demands"]

# --- SIDEBAR NAVIGATION (Menu) ---
st.sidebar.title("⚙️ MENU OPTIONS")
menu = st.sidebar.radio("Kya dekhna hai bhai?", [
    "📋 Poora Stock Report",
    "🛍️ Maal Ki Sale Entry",
    "📊 Dukan Ka Munafa & Hisab",
    "➕ Naya Product Add Karo",
    "📝 Customer Demand Book"
])

# =====================================================================
# 1. POORA STOCK REPORT
# =====================================================================
if menu == "📋 Poora Stock Report":
    st.title("📊 Apni Dukan Ka Poora Stock")
    
    categories = ["Sabhi Categories", "General Hardware", "Plumbing", "Sanitary", "Paints", "Agriculture"]
    selected_cat = st.selectbox("Category ke hisab se chhanto:", categories)
    
    table_data = []
    for id, data in stock.items():
        baki = data["total"] - data["sold"]
        if selected_cat == "Sabhi Categories" or data["cat"] == selected_cat:
            table_data.append({
                "ID": id,
                "Saman Ka Naam": data["name"],
                "Category": data["cat"],
                "Wholesale (Rs.)": data["wholesale"],
                "Retail (Rs.)": data["retail"],
                "Total Stock": data["total"],
                "Becha (Sold)": data["sold"],
                "Baki Maal": baki
            })
            
    df = pd.DataFrame(table_data)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Is category me abhi koi maal nahi hai bhai!")

# =====================================================================
# 2. MAAL KI SALE ENTRY
# =====================================================================
elif menu == "🛍️ Maal Ki Sale Entry":
    st.title("🛒 Bikri Register (Sale Entry)")
    
    product_options = {id: f"{data['name']} ({data['cat']}) - Baki: {data['total']-data['sold']}" for id, data in stock.items()}
    selected_product_id = st.selectbox("Kaunsa saman bika?", options=list(product_options.keys()), format_func=lambda x: product_options[x])
    
    kitna_becha = st.number_input("Kitna nag (Quantity) becha?:", min_value=1, step=1)
    
    if st.button("Sale Entry Register Karo ✅"):
        prod = stock[selected_product_id]
        baki_maal = prod["total"] - prod["sold"]
        
        if kitna_becha <= baki_maal:
            st.session_state.dukan_data["stock"][selected_product_id]["sold"] += kitna_becha
            save_data_to_file()  # Pakka save ho gaya
            st.success(f"🎉 Sahi hai! {prod['name']} ki {kitna_becha} quantity bech di gayi hai aur data save ho gaya hai.")
            st.rerun()
        else:
            st.error(f"❌ Arre bhai! Stock me sirf {baki_maal} hi bache hain.")

# =====================================================================
# 3. DUKAN KA MUNAFA & HISAB
# =====================================================================
elif menu == "📊 Dukan Ka Munafa & Hisab":
    st.title("📈 Financial Report (Investment & Profit)")
    
    total_investment = 0
    total_sales = 0
    total_profit = 0
    low_stock_items = []
    max_sold = -1
    top_item = "Koi nahi"

    for id, data in stock.items():
        baki = data["total"] - data["sold"]
        total_investment += (data["wholesale"] * data["total"])
        total_sales += (data["retail"] * data["sold"])
        total_profit += ((data["retail"] - data["wholesale"]) * data["sold"])
        
        if baki <= 5:
            low_stock_items.append(f"🔴 {data['name']} (Sirf {baki} bacha hai!)")
            
        if data["sold"] > max_sold and data["sold"] > 0:
            max_sold = data["sold"]
            top_item = f"⭐ {data['name']} ({data['sold']} baar bika)"

    col1, col2, col3 = st.columns(3)
    col1.metric("Kul Lagat (Total Investment)", f"Rs. {total_investment:,}")
    col2.metric("Total Bikri (Sales Revenue)", f"Rs. {total_sales:,}")
    col3.metric("Shudh Munafa (Net Profit) 🎉", f"Rs. {total_profit:,}")
    
    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("⚠️ Maal Jo Khatam Hone Wala Hai")
        if low_stock_items:
            for item in low_stock_items:
                st.write(item)
        else:
            st.write("🟢 Sab sahi hai bhai! Maal poora baki hai.")
            
    with col_right:
        st.subheader("🔥 Sabse Zyada Bikne Wala Maal")
        st.write(top_item)

# =====================================================================
# 4. NAYA PRODUCT ADD KARO
# =====================================================================
elif menu == "➕ Naya Product Add Karo":
    st.title("➕ Dukan Me Naya Maal Jodo")
    
    with st.form("add_product_form"):
        name = st.text_input("Saman Ka Naam (e.g., T-Cock Nal 0.5 Inch)")
        cat = st.selectbox("Category chuno:", ["General Hardware", "Plumbing", "Sanitary", "Paints", "Agriculture"])
        wholesale = st.number_input("Wholesale Rate (Rs.):", min_value=0, step=1)
        retail = st.number_input("Retail Rate (Rs.):", min_value=0, step=1)
        total = st.number_input("Kitna maal लेकर आए (Quantity):", min_value=1, step=1)
        
        submit = st.form_submit_button("Naya Product Add Karo 🚀")
        
        if submit:
            if name:
                next_id = str(max([int(k) for k in stock.keys()]) + 1) if stock else "1"
                st.session_state.dukan_data["stock"][next_id] = {
                    "name": name, "cat": cat, "wholesale": wholesale, "retail": retail, "total": total, "sold": 0
                }
                save_data_to_file()  # Pakka save ho gaya
                st.success(f"✅ Sahi hai bhai! '{name}' ab dukan me permanently register ho gaya hai.")
            else:
                st.error("❌ Saman ka naam likhna zaroori hai bhai!")

# =====================================================================
# 5. CUSTOMER DEMAND BOOK
# =====================================================================
elif menu == "📝 Customer Demand Book":
    st.title("📋 Grahak Ki Demand Book")
    
    col_form, col_list = st.columns([1, 1])
    
    with col_form:
        st.subheader("✍️ Nayi Demand Note Karo")
        d_item = st.text_input("Grahak ne kya naya saman manga?")
        d_note = st.text_area("Koi khaas detail? (Size, Company, ya Kitne pieces chaiye)")
        
        if st.button("Demand Save Karo 📌"):
            if d_item:
                st.session_state.dukan_data["demands"].append({"item": d_item, "notes": d_note})
                save_data_to_file()  # Pakka save ho gaya
                st.success(f"✅ Demand permanently list me jodh di gayi hai.")
                st.rerun()
            else:
                st.error("Saman ka naam toh likho bhai!")
                
    with col_list:
        st.subheader("📋 Mangwane Wale Maal Ki List")
        if demands:
            for idx, item in enumerate(demands, 1):
                st.markdown(f"**{idx}. {item['item']}** — *Detail:* {item['notes']}")
        else:
            st.info("Abhi list khali hai bhai! Sab maal dukan me available hai.")