import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="Car Price Predictor", page_icon="🚗", layout="centered"
)

# 1. قاموس الشركات والموديلات الخاصة بكل شركة مع أسعارها الأساسية المبدئية
CAR_MODELS = {
    "Nissan": {
        "Sunny": 690000,
        "Sentra": 950000,
        "Qashqai": 1400000,
        "Juke": 1100000,
    },
    "Toyota": {
        "Corolla": 1300000,
        "Yaris": 850000,
        "Fortuner": 3200000,
        "C-HR": 1500000,
    },
    "BMW": {
        "3 Series (320i)": 2800000,
        "5 Series (520i)": 3900000,
        "X1": 2400000,
        "X5": 5200000,
    },
    "Mercedes": {
        "C-Class (C180/C200)": 3300000,
        "E-Class (E200)": 4500000,
        "A-Class": 2200000,
        "GLC": 4800000,
    },
    "Hyundai": {
        "Elantra": 1050000,
        "Tucson": 1650000,
        "Accent": 750000,
        "Creta": 1200000,
    },
    "Kia": {
        "Cerato / K3": 1100000,
        "Sportage": 1700000,
        "Pegas": 700000,
        "Seltos": 1300000,
    },
    "Chevrolet": {
        "Optra": 600000,
        "Aveo": 500000,
        "Captiva": 1350000,
    },
}

# 2. صور الماركات
CAR_IMAGES = {
    "BMW": (
        "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=800&q=80"
    ),
    "Mercedes": (
        "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=800&q=80"
    ),
    "Toyota": (
        "https://images.unsplash.com/photo-1629897048514-3dd7414fe72a?auto=format&fit=crop&w=800&q=80"
    ),
    "Hyundai": (
        "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?auto=format&fit=crop&w=800&q=80"
    ),
    "Kia": (
        "https://images.unsplash.com/photo-1606152421802-db97b9c7a11b?auto=format&fit=crop&w=800&q=80"
    ),
    "Nissan": (
        "https://images.unsplash.com/photo-1609521263047-f8d205293f24?auto=format&fit=crop&w=800&q=80"
    ),
    "Chevrolet": (
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80"
    ),
}

# عنوان التطبيق
st.title("🚗 Used Car Price Prediction System")
st.markdown("---")
st.markdown("👩‍💻 **Developed by:** Salma Ahmed & Habiba Essam")
st.markdown("---")
st.write("Select the car brand and model line to get an accurate price range.")

# مدخلات المستخدم
col_input, col_img = st.columns([1.2, 1])

with col_input:
    # 1. اختيار الشركة
    brand = st.selectbox("Car Brand", list(CAR_MODELS.keys()))

    # 2. اختيار الموديل التابع للشركة المحددة ديناميكياً
    available_models = list(CAR_MODELS[brand].keys())
    model_name = st.selectbox("Car Model / Line", available_models)

    # 3. نوع الفتيس
    transmission = st.selectbox("Transmission", ["Automatic", "Manual"])

with col_img:
    st.image(
        CAR_IMAGES[brand], caption=f"{brand} Preview", use_container_width=True
    )

# اختيار حالة السيارة
car_condition = st.radio(
    "Car Condition",
    ["Zero (Brand New)", "Nearly New (كسر زيرو)", "Used (مستعمل)"],
    horizontal=True,
)

col1, col2 = st.columns(2)

with col1:
    year = st.number_input(
        "Manufacturing Year", min_value=2000, max_value=2026, value=2022
    )
    fuel_type = st.selectbox(
        "Fuel Type", ["Petrol", "Diesel", "Hybrid", "Electric"]
    )

with col2:
    if car_condition == "Zero (Brand New)":
        km_driven = 0
        st.info("Kilometers Driven: 0 KM (Brand New)")
    else:
        km_driven = st.number_input(
            "Kilometers Driven (KM)", min_value=0, max_value=500000, value=10000
        )

st.markdown("---")

# حساب وتوقع السعر
if st.button("Predict Price"):
    # جلب السعر الأساسي الخاص بالموديل المحدد بوضوح
    base_price = CAR_MODELS[brand][model_name]

    # 1. معامل سنة الصنع
    if year >= 2025:
        year_mult = 1.18
    elif year >= 2022:
        year_mult = 1.02
    elif year >= 2018:
        year_mult = 0.80
    else:
        year_mult = 0.58

    # 2. معامل الكيلومترات
    if km_driven == 0:
        km_mult = 1.0
    elif km_driven < 50000:
        km_mult = 0.90
    elif km_driven < 100000:
        km_mult = 0.80
    else:
        km_mult = 0.68

    # 3. معامل حالة السيارة
    if car_condition == "Zero (Brand New)":
        cond_mult = 1.10
    elif car_condition == "Nearly New (كسر زيرو)":
        cond_mult = 0.98
    else:
        cond_mult = 0.85

    # 4. معامل الفتيس
    trans_mult = 0.92 if transmission == "Manual" else 1.0

    # السعر المتوقع النهائي
    estimated_price = (
        base_price * year_mult * km_mult * cond_mult * trans_mult
    )

    # رينج السعر (نسبة خطأ ±5%)
    min_price = estimated_price * 0.95
    max_price = estimated_price * 1.05

    # عرض النتائج
    st.success(
        f"🎯 **Estimated Price for ({brand} {model_name}):** {estimated_price:,.2f} EGP\n\n"
        f"📊 **Expected Price Range (±5% Error Margin):** {min_price:,.2f} EGP — {max_price:,.2f} EGP"
    )

    # رسم بياني تفاعلي
    chart_data = pd.DataFrame(
        {
            "Price Range": ["Minimum Price", "Estimated Price", "Maximum Price"],
            "Price (EGP)": [min_price, estimated_price, max_price],
        }
    )

    st.subheader("📊 Price Range Visualization")
    st.bar_chart(chart_data.set_index("Price Range"))
