import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Hardware Inventory System", layout="wide")

DATA_FILE = "dukan_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Stock Report", "Sale Entry", "Profit & Loss", "Add New Product", "Product Demand Book"
])

with tab1:
    st.subheader("Stock Report")
    # Filter: Sirf select ki gayi category ka data nikalna
    filtered_data = {k: v for k, v in st.session_state.data["stock"].items() if v["cat"] == selected_cat}
    
    if not filtered_data:
        st.write(f"No products in {selected_cat}.")
    else:
        # Table banane ka logic
        stock_list = []
        for i, (p_id, p_info) in enumerate(filtered_data.items(), 1):
            item = {"Sr. No.": i, "ID": p_id, **p_info}
            stock_list.append(item)
        
        df = pd.DataFrame(stock_list)
        # index=False karne se wo left side wali 0,1,2 numbering hat jayegi
        st.table(df.set_index("Sr. No.")) 
        
        # Delete Product section
        st.write("---")
        st.subheader("Delete Product")
        del_id = st.selectbox(
            "Select Product to Delete:", 
            options=list(filtered_data.keys()), 
            format_func=lambda x: f"{filtered_data[x]['name']} (ID: {x})"
        )
        
        if st.button("Delete This Product"):
            del st.session_state.data["stock"][del_id]
            save_data()
            st.rerun()

with tab2:
    st.subheader("Sale Entry")
    cat_prods = {k: v for k, v in st.session_state.data["stock"].items() if v["cat"] == selected_cat}
    p_id = st.selectbox("Select Product:", options=list(cat_prods.keys()), format_func=lambda x: cat_prods[x]["name"])
    qty = st.number_input("Quantity Sold:", min_value=1)
    if st.button("Confirm Sale"):
        st.session_state.data["stock"][p_id]["sold"] += qty
        save_data()
        st.success("Sale Recorded.")

with tab3:
    st.subheader("Profit & Loss")
    profit_data = [{"Name": v["name"], "Profit": (v["retail"] - v["wholesale"]) * v["sold"]} 
                   for k, v in st.session_state.data["stock"].items() if v["cat"] == selected_cat]
    st.table(pd.DataFrame(profit_data))

with tab4:
    st.subheader("Add New Product")
    with st.form("add_prod"):
        name = st.text_input("Product Name:")
        ws = st.number_input("Wholesale Price:")
        ret = st.number_input("Retail Price:")
        qty = st.number_input("Initial Stock:")
        if st.form_submit_button("Submit"):
            new_id = str(len(st.session_state.data["stock"]) + 1)
            st.session_state.data["stock"][new_id] = {"name": name, "cat": selected_cat, "wholesale": ws, "retail": ret, "total": qty, "sold": 0}
            save_data()
            st.success("Product Added.")

with tab5:
    st.subheader("Product Demand Book")
   # Entry add karne ka form
    col1, col2 = st.columns([3, 1])
    with col1:
        d_name = st.text_input("Product Name:")
    with col2:
        d_qty = st.number_input("Qty:", min_value=1)
    
    if st.button("Add to Demand"):
        st.session_state.data["demands"].append({"Product": d_name, "Quantity": d_qty})
        save_data()
        st.rerun() 
    
    # Demand list dikhana aur Delete button lagana
    st.write("---")
    if st.session_state.data["demands"]:
        for i, item in enumerate(st.session_state.data["demands"]):
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"{item['Product']}")
            c2.write(f"Qty: {item['Quantity']}")
            if c3.button("Delete", key=f"del_{i}"):
                del st.session_state.data["demands"][i]
                save_data()
                st.rerun()