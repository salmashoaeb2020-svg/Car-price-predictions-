import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="Car Price Predictor", page_icon="🚗", layout="centered"
)

# 1. الموديلات والأسعار الأساسية الواقعية (سعر الزيرو/كسر الزيرو التقريبي لعام 2024-2026)
CAR_MODELS = {
    "Nissan": {
        "Sunny": 800000,
        "Sentra": 1100000,
        "Qashqai": 1650000,
        "Juke": 1300000,
    },
    "Toyota": {
        "Corolla": 1600000,
        "Yaris": 1000000,
        "Fortuner": 3800000,
        "C-HR": 1750000,
    },
    "BMW": {
        "3 Series (320i)": 3500000,
        "5 Series (520i)": 4800000,
        "X1": 2900000,
        "X5": 6200000,
    },
    "Mercedes": {
        "C-Class (C180/C200)": 4200000,
        "E-Class (E200)": 5800000,
        "A-Class": 2700000,
        "GLC": 5900000,
    },
    "Hyundai": {
        "Elantra": 1300000,
        "Tucson": 1900000,
        "Accent": 900000,
        "Creta": 1400000,
    },
    "Kia": {
        "Cerato / K3": 1350000,
        "Sportage": 1950000,
        "Pegas": 850000,
        "Seltos": 1500000,
    },
    "Chevrolet": {
        "Optra": 750000,
        "Aveo": 600000,
        "Captiva": 1500000,
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
    brand = st.selectbox("Car Brand", list(CAR_MODELS.keys()))
    available_models = list(CAR_MODELS[brand].keys())
    model_name = st.selectbox("Car Model / Line", available_models)
    transmission = st.selectbox("Transmission", ["Automatic", "Manual"])

with col_img:
    st.image(
        CAR_IMAGES[brand], caption=f"{brand} Preview", use_container_width=True
    )

car_condition = st.radio(
    "Car Condition",
    ["Zero (Brand New)", "Nearly New (كسر زيرو)", "Used (مستعمل)"],
    horizontal=True,
)

col1, col2 = st.columns(2)

with col1:
    year = st.number_input(
        "Manufacturing Year", min_value=2000, max_value=2026, value=2012
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
            "Kilometers Driven (KM)", min_value=0, max_value=500000, value=200000
        )

st.markdown("---")

# حساب السعر الموزون
if st.button("Predict Price"):
    base_price = CAR_MODELS[brand][model_name]

    # 1. خصم سنوي واقعي (3.5% لكل سنة قدم عن 2026 بحد أقصى خصم 50%)
    years_old = 2026 - year
    age_depreciation = min(years_old * 0.035, 0.50)

    # 2. خصم الكيلومترات (1% لكل 20 ألف كم - بحد أقصى خصم 15%)
    km_depreciation = min((km_driven / 20000) * 0.01, 0.15)

    # 3. خصم الفتيس المانيوال (5%)
    trans_depreciation = 0.05 if transmission == "Manual" else 0.0

    # إجمالي الخصم
    total_depreciation = (
        age_depreciation + km_depreciation + trans_depreciation
    )

    if car_condition == "Zero (Brand New)":
        estimated_price = base_price
    elif car_condition == "Nearly New (كسر زيرو)":
        estimated_price = base_price * 0.92
    else:
        # حساب سعر المستعمل مع ضمان ألا يقل عن 45% من قيمة السيارة الأصلية
        estimated_price = base_price * (1.0 - total_depreciation)
        estimated_price = max(estimated_price, base_price * 0.45)

    # رينج السعر (±5%)
    min_price = estimated_price * 0.95
    max_price = estimated_price * 1.05

    # عرض النتائج
    st.success(
        f"🎯 **Estimated Price for ({brand} {model_name} {year}):** {estimated_price:,.2f} EGP\n\n"
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
