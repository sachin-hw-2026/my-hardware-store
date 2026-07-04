import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = "dukan_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {"stock": {}, "demands": []}
    return {"stock": {}, "demands": []}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.data, f, indent=4)

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.sidebar.title("Categories")
categories = ["General Hardware", "Plumbing", "Sanitary", "Paints", "Agriculture"]
selected_cat = st.sidebar.radio("Select Category:", categories)

st.title(f"Category: {selected_cat}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Stock Report", "Sale Entry", "Profit & Loss", "Add New Product", "Product Demand Book"])

# TAB 1: Stock Report
with tab1:
    st.subheader("Stock Report")
    # Sabse pehle latest data fetch karo
    stock_dict = st.session_state.data.get("stock", {})
    
    # Filter by category
    cat_items = {k: v for k, v in stock_dict.items() if v.get("cat") == selected_cat}
    
    if not cat_items:
        st.write(f"No products in {selected_cat}.")
    else:
        stock_list = []
        for idx, (p_id, p_info) in enumerate(cat_items.items(), 1):
            total = int(p_info.get("total", 0))
            sold = int(p_info.get("sold", 0))
            stock_list.append({
                "Sr. No.": idx,
                "Product Name": p_info.get("name", ""),
                "Wholesale Price": p_info.get("wholesale", 0),
                "Retail Price": p_info.get("retail", 0),
                "Total Quantity": total,
                "Sold Quantity": sold,
                "Remaining Quantity": total - sold
            })
        
        df = pd.DataFrame(stock_list)
        # Table display
        st.table(df.set_index("Sr. No."))

# TAB 4: Add New Product
with tab4:
    st.subheader("Add New Product")
    with st.form("add_prod", clear_on_submit=True):
        name = st.text_input("Product Name:")
        ws = st.number_input("Wholesale Price:", min_value=0.0)
        ret = st.number_input("Retail Price:", min_value=0.0)
        qty = st.number_input("Initial Stock:", min_value=0)
        
        if st.form_submit_button("Submit"):
            # Unique ID creation (Timestamp based to avoid overwrite)
            new_id = str(len(st.session_state.data["stock"]) + 1000) 
            
            # Data update
            st.session_state.data["stock"][new_id] = {
                "name": name, 
                "cat": selected_cat, 
                "wholesale": ws, 
                "retail": ret, 
                "total": qty, 
                "sold": 0
            }
            save_data()
            st.success(f"Added {name} to {selected_cat}!")
            st.rerun()

# Delete Logic (Add to Tab 1)
with tab1:
    st.write("---")
    st.subheader("Delete Product")
    cat_items = {k: v for k, v in st.session_state.data["stock"].items() if v.get("cat") == selected_cat}
    del_id = st.selectbox("Select Product to Delete:", options=list(cat_items.keys()), format_func=lambda x: f"{cat_items[x]['name']} (ID: {x})")
    if st.button("Delete This Product"):
        if del_id in st.session_state.data["stock"]:
            del st.session_state.data["stock"][del_id]
            save_data()
            st.rerun()