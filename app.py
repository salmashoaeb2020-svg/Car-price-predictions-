import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="Car Price Predictor", page_icon="🚗", layout="centered"
)

# 1. صور السيارات
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

# 2. الأسعار الأساسية الموزونة لعام 2026
BASE_PRICES = {
    "BMW": 3200000,
    "Mercedes": 3500000,
    "Toyota": 1500000,
    "Hyundai": 1000000,
    "Kia": 1100000,
    "Nissan": 850000,
    "Chevrolet": 750000,
}

# عنوان التطبيق
st.title("🚗 Used Car Price Prediction System")
st.markdown("---")
st.markdown("👩‍💻 **Developed by:** Salma Ahmed & Habiba Essam")
st.markdown("---")
st.write("Enter the car specifications to get the estimated price.")

# مدخلات المستخدم
col_input, col_img = st.columns([1.2, 1])

with col_input:
    brand = st.selectbox("Car Brand", list(CAR_IMAGES.keys()))
    car_type = st.selectbox(
        "Car Type / Model", ["Sedan", "SUV", "Hatchback", "Coupe"]
    )
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
            "Kilometers Driven (KM)", min_value=0, max_value=500000, value=5000
        )

st.markdown("---")

# حساب السعر ورسم البياني
if st.button("Predict Price"):
    base_price = BASE_PRICES.get(brand, 1000000)

    # معاملات متوازنة
    type_mult = 1.12 if car_type == "SUV" else 1.0

    if year >= 2025:
        year_mult = 1.20
    elif year >= 2022:
        year_mult = 1.05
    elif year >= 2018:
        year_mult = 0.82
    else:
        year_mult = 0.60

    if km_driven == 0:
        km_mult = 1.0
    elif km_driven < 50000:
        km_mult = 0.90
    elif km_driven < 100000:
        km_mult = 0.80
    else:
        km_mult = 0.70

    if car_condition == "Zero (Brand New)":
        cond_mult = 1.10
    elif car_condition == "Nearly New (كسر زيرو)":
        cond_mult = 1.0
    else:
        cond_mult = 0.88

    # السعر المتوقع
    estimated_price = base_price * type_mult * year_mult * km_mult * cond_mult

    # رينج السعر (نسبة خطأ ±5%)
    min_price = estimated_price * 0.95
    max_price = estimated_price * 1.05

    # عرض النتائج
    st.success(
        f"🎯 **Estimated Expected Price:** {estimated_price:,.2f} EGP\n\n"
        f"📊 **Price Range (Margin of Error ±5%):** {min_price:,.2f} EGP — {max_price:,.2f} EGP"
    )

    # بيانات الرسم البياني
    chart_data = pd.DataFrame(
        {
            "Price Range": ["Minimum Price", "Estimated Price", "Maximum Price"],
            "Price (EGP)": [min_price, estimated_price, max_price],
        }
    )

    st.subheader("📊 Price Range Visualization")
    st.bar_chart(chart_data.set_index("Price Range"))
