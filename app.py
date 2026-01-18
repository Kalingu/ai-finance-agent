import streamlit as st
import pandas as pd
import plotly.express as px
import easyocr
from PIL import Image
import numpy as np
import re
from datetime import datetime
import io

st.set_page_config(layout="wide", page_title="AI Finance Agent")
st.title("💰 AI Finance Agent - Complete Edition")
st.markdown("**📷 Upload Receipt → 🏠 Choose Category → 💾 Save to Dashboard**")

# BRAND NEW EMPTY DATABASE
if 'receipts' not in st.session_state:
    st.session_state.receipts = pd.DataFrame(columns=['date', 'category', 'subcategory', 'amount', 'notes'])

# EXPENSE CATEGORIES (Your exact list) - CLEAN TEXT ONLY
categories = {
    "Housing": ["Rent / Mortgage", "Property tax", "Home insurance", "Maintenance / Repairs"],
    "Utilities": ["Electricity", "Water", "Gas", "Internet", "Mobile phone", "TV / Streaming services"],
    "Food": ["Groceries", "Dining out", "Food delivery"],
    "Transportation": ["Fuel", "Public transport", "Vehicle loan", "Vehicle insurance", "Maintenance / Service", "Parking / Tolls"],
    "Healthcare": ["Medical bills", "Insurance premiums", "Medicines", "Doctor visits"],
    "Education": ["Tuition fees", "Online courses", "Books / Study materials"],
    "Financial": ["Credit card payments", "Loan repayments", "Bank charges", "Subscriptions"],
    "Personal & Lifestyle": ["Clothing", "Personal care", "Gym / Fitness", "Entertainment"],
    "Miscellaneous": ["Gifts", "Donations", "Emergency expenses"]
}

# **PERFECT CSV FUNCTION - FIXED**
@st.cache_data(ttl=10)
def convert_df(df):
    if df.empty:
        return "date,category,subcategory,amount,notes\n".encode('utf-8')
    
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
    df_copy['amount'] = df_copy['amount'].round(2)
    csv_buffer = io.StringIO()
    df_copy.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode('utf-8')

# LEFT COLUMN: Category Selection + Upload
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### **Choose Category**")  
    main_category = st.selectbox("Main Category", list(categories.keys()), 
                                index=None, key='main_category_key1')
    
    if main_category:
        subcategory = st.selectbox("Subcategory", categories[main_category], 
                                  index=None, key='subcategory_key1')
    else:
        subcategory = st.selectbox("Subcategory", ["Select Main Category First"], 
                                  index=0, key='subcategory_key1', disabled=True)
    
    st.markdown("---")
    st.markdown("### 📷 **Upload Receipt**")
    uploaded_file = st.file_uploader("📷 Receipt", type=['jpg', 'png', 'jpeg'])

# SPEED FIX 1: Cache OCR reader globally
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

with col2:
    if uploaded_file is not None and main_category and subcategory:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Receipt: {uploaded_file.name}", width=500)
        
        with st.spinner("🔍 Smart OCR Processing..."):
            image_rgb = image.convert('RGB')
            img_array = np.array(image_rgb)
            
            reader = load_ocr()
            
            if img_array.shape[0] > 1000 or img_array.shape[1] > 1000:
                scale_factor = 0.5
                img_array = (img_array * scale_factor).astype(np.uint8)
            
            result = reader.readtext(img_array)
            ocr_text = " ".join([text for _, text, _ in result]).lower()
            
            # IMPROVED: Prioritize TOTAL/SUBTOTAL keywords + largest amount
            total_keywords = ['total', 'subtotal', 'balance', 'amount due', 'grand total', 'final total']
            total_priority = []
            
            # First pass: Find numbers near TOTAL keywords (HIGHEST priority)
            for _, text, conf in result:
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in total_keywords):
                    numbers = re.findall(r'[\d,]+\.?\d*', text)
                    for num in numbers:
                        clean_num = num.replace(',', '').strip()
                        if len(clean_num) >= 4:
                            try:
                                value = float(clean_num)
                                if 5 < value < 5000:
                                    total_priority.append((value, clean_num, text_lower))
                            except:
                                pass
            
            # Second pass: All other numbers (backup) - **FIXED TUPLE STRUCTURE**
            if not total_priority:
                all_numbers = re.findall(r'[\d,]+\.?\d*', ocr_text)
                candidates = []
                for x in all_numbers:
                    clean_num = x.replace(',', '').strip()
                    if len(clean_num) >= 4:
                        try:
                            value = float(clean_num)
                            if 5 < value < 5000 and '.' in clean_num:
                                candidates.append((value, clean_num, "total detected"))
                        except:
                            pass
                total_priority = candidates
            
            # RENT detection (still works) - **FIXED UNPACKING**
            rent_keywords = ['rent', 'rental', 'lease', 'housing', 'apartment']
            is_rent = any(keyword in ocr_text for keyword in rent_keywords) and main_category == "Housing"
            
            if is_rent and total_priority:
                st.success("🏠 **RENT RECEIPT DETECTED**")
                sorted_candidates = sorted(total_priority, key=lambda x: x[0], reverse=True)
                rent_amount = sorted_candidates[0][1]
                # **FIXED**: Safe unpacking - handle both 2-tuple and 3-tuple
                for candidate in sorted_candidates:
                    if len(candidate) >= 2:
                        val = candidate[0]
                        if 800 <= val <= 1800:
                            rent_amount = candidate[1]
                            break
                st.session_state.detected_amount = float(rent_amount)
                st.success(f"✅ **SMART RENT TOTAL: ${rent_amount}**")
            elif total_priority:
                # Pick largest amount (most likely TOTAL) - **FIXED**: Safe context access
                best_candidate = max(total_priority, key=lambda x: x[0])
                best_amount = best_candidate[1]
                context = best_candidate[2] if len(best_candidate) > 2 else "total detected"
                st.session_state.detected_amount = float(best_amount)
                st.success(f"✅ **DETECTED TOTAL: ${best_amount}** (near '{context}')")
            else:
                st.session_state.detected_amount = 0
                st.warning("No clear total found")

# FIXED CSV-friendly metrics
@st.cache_data(ttl=60)
def get_metrics(receipts):
    if receipts.empty:
        return 0, 0, 0
    receipts_copy = receipts.copy()
    receipts_copy['date'] = pd.to_datetime(receipts_copy['date'], errors='coerce')
    total_spent = receipts_copy['amount'].sum()
    today_spent = receipts_copy[receipts_copy['date'].dt.date == datetime.now().date()]['amount'].sum()
    total_receipts = len(receipts)
    return total_spent, today_spent, total_receipts

if main_category and subcategory:
    st.markdown("### 💵 **Amount**")
    amount = st.number_input("Enter Amount (OCR auto-filled)", 
                            value=float(st.session_state.get('detected_amount', 0.0)),
                            min_value=0.0, step=0.01, format="%.2f")
    notes = st.text_area("📝 Notes", placeholder="Anything about this expense...")
    
    if st.button("💾 **SAVE EXPENSE**", type="primary"):
        if amount > 0:
            new_expense = pd.DataFrame({
                'date': [datetime.now()],
                'category': [main_category],
                'subcategory': [subcategory],
                'amount': [float(amount)],
                'notes': [notes]
            })
            st.session_state.receipts = pd.concat([st.session_state.receipts, new_expense], ignore_index=True)
            st.success(f"✅ **Saved ${amount:.2f} {subcategory}**")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Enter valid amount")
else:
    st.info("👆 **Please select Main Category and Subcategory first**")

# DASHBOARD - FIXED DATETIME + TOTAL SPEND
st.markdown("---")
st.markdown("### 📊 **LIVE DASHBOARD**")

if not st.session_state.receipts.empty:
    st.session_state.receipts['date'] = pd.to_datetime(st.session_state.receipts['date'], errors='coerce')

    col1, col2, col3, col4 = st.columns(4)
    total_spent, today_spent, total_receipts = get_metrics(st.session_state.receipts)

    with col1:
        st.metric("💰 **Total Spent**", f"${total_spent:.2f}")
    with col2:
        st.metric("📅 **Today**", f"${today_spent:.2f}")
    with col3:
        st.metric("📄 **Total Receipts**", total_receipts)
    with col4:
        st.metric("🎯 **Avg per Receipt**", f"${total_spent/total_receipts:.2f}" if total_receipts > 0 else "$0.00")

    # Charts + DELETE - ROWS START FROM 1
    col1, col2 = st.columns(2)
    
    with col1:
        @st.cache_data(ttl=300)
        def create_pie_chart(receipts):
            cat_summary = receipts.groupby('category')['amount'].sum().sort_values(ascending=False)
            fig_pie = px.pie(values=cat_summary.values, names=cat_summary.index, hole=0.4)
            return fig_pie
        
        fig_pie = create_pie_chart(st.session_state.receipts)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        recent_original = st.session_state.receipts.tail(10).sort_values('date', ascending=False)
        recent = recent_original.reset_index(drop=True).copy()
        recent['🗑️'] = False
        recent['#'] = range(1, len(recent) + 1)
        
        edited_df = st.data_editor(
            recent[['#', 'date', 'category', 'subcategory', 'amount', 'notes', '🗑️']],
            column_config={
                '🗑️': st.column_config.CheckboxColumn("Delete", default=False, width=80),
                '#': st.column_config.NumberColumn("Row", width=50, disabled=True),
                'date': st.column_config.DateColumn("Date", width=120),
                'category': st.column_config.TextColumn("Category", width=150),
                'subcategory': st.column_config.TextColumn("Subcategory", width=150),
                'amount': st.column_config.NumberColumn("Amount", format="$%.2f", width=100),
                'notes': st.column_config.TextColumn("Notes", width=200)
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("🗑️ **DELETE SELECTED**", type="secondary"):
            delete_mask = edited_df['🗑️'] == True
            
            if delete_mask.any():
                original_indices = recent_original.index.tolist()
                rows_to_delete = [original_indices[i] for i, checked in enumerate(delete_mask) if checked]
                
                st.session_state.receipts = st.session_state.receipts.drop(rows_to_delete).reset_index(drop=True)
                st.success(f"✅ **Deleted {len(rows_to_delete)} expense(s)!**")
                st.rerun()
            else:
                st.warning("⚠️ Select expenses to delete")
else:
    st.info("👆 Save your first receipt to see charts!")

# **PERFECT CSV DOWNLOAD**
csv = convert_df(st.session_state.receipts)
st.download_button(
    label="📥 Download CSV", 
    data=csv,
    file_name="expenses.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown("**✅ PERFECT CSV + Clean Categories + SMART TOTAL DETECTION**")
