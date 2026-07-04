import streamlit as st
import pandas as pd
import json
import os

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

# Helper function to generate clean table for any category
def get_stock_df(category):
    stock_list = []
    i = 1
    for p_id, p_info in st.session_state.data["stock"].items():
        if p_info.get("cat") == category:
            total = int(p_info.get("total", 0))
            sold = int(p_info.get("sold", 0))
            stock_list.append({
                "Sr. No.": i,
                "Product Name": p_info.get("name", ""),
                "Wholesale Price": p_info.get("wholesale", 0),
                "Retail Price": p_info.get("retail", 0),
                "Total Quantity": total,
                "Sold Quantity": sold,
                "Remaining Quantity": total - sold
            })
            i += 1
    return pd.DataFrame(stock_list)

st.sidebar.title("Categories")
categories = ["General Hardware", "Plumbing", "Sanitary", "Paints", "Agriculture"]
selected_cat = st.sidebar.radio("Select Category:", categories)

st.title(f"Category: {selected_cat}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Stock Report", "Sale Entry", "Profit & Loss", "Add New Product", "Product Demand Book"])

# TAB 1: Stock Report
with tab1:
    st.subheader("Stock Report")
    df = get_stock_df(selected_cat)
    if df.empty:
        st.write(f"No products in {selected_cat}.")
    else:
        st.table(df.set_index("Sr. No."))
        
        st.write("---")
        st.subheader("Delete Product")
        cat_items = {k: v for k, v in st.session_state.data["stock"].items() if v.get("cat") == selected_cat}
        del_id = st.selectbox("Select Product to Delete:", options=list(cat_items.keys()), format_func=lambda x: f"{cat_items[x]['name']} (ID: {x})")
        if st.button("Delete This Product"):
            del st.session_state.data["stock"][del_id]
            save_data()
            st.rerun()

# TAB 2: Sale Entry
with tab2:
    st.subheader("Sale Entry")
    cat_prods = {k: v for k, v in st.session_state.data["stock"].items() if v.get("cat") == selected_cat}
    if not cat_prods:
        st.write("No products to sell.")
    else:
        p_id = st.selectbox("Select Product:", options=list(cat_prods.keys()), format_func=lambda x: cat_prods[x]['name'])
        qty = st.number_input("Quantity Sold:", min_value=1)
        if st.button("Confirm Sale"):
            st.session_state.data["stock"][p_id]["sold"] = int(st.session_state.data["stock"][p_id].get("sold", 0)) + qty
            save_data()
            st.success("Sale Recorded.")
            st.rerun()

# TAB 3: Profit & Loss
with tab3:
    st.subheader("Profit & Loss")
    df = get_stock_df(selected_cat)
    if not df.empty:
        df["Profit"] = (df["Retail Price"] - df["Wholesale Price"]) * df["Sold Quantity"]
        st.table(df[["Product Name", "Profit"]].set_index("Product Name"))
    else:
        st.write("No sales data.")

# TAB 4: Add New Product
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
            st.rerun()

# TAB 5: Product Demand Book
with tab5:
    st.subheader("Product Demand Book")
    d_name = st.text_input("Product Name:")
    d_qty = st.number_input("Qty:", min_value=1)
    if st.button("Add to Demand"):
        st.session_state.data["demands"].append({"Product": d_name, "Quantity": d_qty})
        save_data()
        st.rerun()
    if st.session_state.data["demands"]:
        for i, item in enumerate(st.session_state.data["demands"]):
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(item['Product'])
            c2.write(f"Qty: {item['Quantity']}")
            if c3.button("Delete", key=f"del_{i}"):
                del st.session_state.data["demands"][i]
                save_data()
                st.rerun()