import datetime
import streamlit as st

# 1. تحديث قاموس الأسعار الأساسية (Base Prices) لتعكس قيم تقريبية واقعية لسيارة جديدة/مرجعية
CAR_MODELS = {
    "Chevrolet": {
        "Aveo": 600000,  # تم التعديل من القيم المرتفعة إلى 600,000 ج.م
        "Optra": 750000,
        "Cruze": 650000,
        "Captiva": 1500000,
    },
    "Nissan": {"Sunny": 750000, "Sentra": 950000},
    "Hyundai": {"Elantra": 1100000, "Verna": 450000, "Tucson": 1800000},
}


def predict_car_price(
    brand: str, model: str, year: int, km_driven: int, fuel_type: str
) -> float:
    base_price = CAR_MODELS.get(brand, {}).get(model, 600000)
    current_year = datetime.datetime.now().year

    # 2. حساب نسبة خصم العمر (3.5% لكل سنة قديمة، بحد أقصى 50%)
    age = max(0, current_year - year)
    age_depreciation = min(0.50, age * 0.035)

    # 3. حساب نسبة خصم الكيلومترات (1% لكل 20,000 كم)
    km_depreciation = (km_driven / 20000) * 0.01

    # إجمالي نسبة الخصم
    total_depreciation = age_depreciation + km_depreciation

    # حساب السعر المبدئي
    predicted_price = base_price * (1 - total_depreciation)

    # 4. وضع حد أدنى للسعر (Price Floor) ألا يقل عن 45% من السعر الأساسي للسيارة
    price_floor = base_price * 0.45
    final_price = max(predicted_price, price_floor)

    return final_price


# --- واجهة Streamlit ---
st.title("🚗 Car Price Predictor (Egypt)")

brand = st.selectbox("Car Brand", list(CAR_MODELS.keys()))
model = st.selectbox("Car Model", list(CAR_MODELS[brand].keys()))
year = st.number_input("Year of Manufacture", 1990, 2026, 2011)
km_driven = st.number_input("Kilometers Driven (KM)", 0, 500000, 80000)
fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "CNG"])

if st.button("Predict Price"):
    estimated_price = predict_car_price(
        brand, model, year, km_driven, fuel_type
    )

    # حساب هامش الخطأ ±5%
    min_range = estimated_price * 0.95
    max_range = estimated_price * 1.05

    st.success(
        f"🎯 Estimated Price for ({brand} {model} {year}):\n"
        f"**{estimated_price:,.2f} EGP**"
    )

    st.info(
        f"📊 Expected Range (±5% Margin):\n"
        f"**{min_range:,.2f} EGP — {max_range:,.2f} EGP**"
    )
