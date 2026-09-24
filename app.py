import streamlit as st
import pandas as pd
import joblib
import numpy as np

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="توقع أسعار السيارات في مصر",
    page_icon="🚗",
    layout="centered"
)

# 2. تحميل الموديل المدرب مسبقاً
@st.cache_resource
def load_model():
    # تأكدي إن ملف الـ model.pkl موجود في نفس الفولدر
    return joblib.load('model.pkl')

model = load_model()

st.title("🚗 نظام توقع أسعار السيارات في السوق المصري")
st.write("أدخل تفاصيل السيارة لمعرفة السعر المحدد ورينج الأسعار المتوقع بالجنيه المصري (EGP).")

st.markdown("---")

# 3. تصميم مدخلات المستخدم (Inputs)
# ملحوظة: يمكنك تعديل الخيارات لتتناسب تماماً مع الداتا سيت الخاصة بك
col1, col2 = st.columns(2)

with col1:
    brand = st.selectbox("الشركة المصنعة (Brand)", ["Toyota", "Hyundai", "Kia", "Nissan", "Chevrolet", "Chery", "BYD"])
    # يمكنك ربط الـ lines بالشركة لو أمكن، أو وضع قائمة عامة
    car_line = st.selectbox("فئة السيارة / الموديل (Line/Model)", ["Corolla", "Elantra", "Sportage", "Sunny", "Optra", "Tiggo", "F3"])
    transmission = st.selectbox("ناقل الحركة (Transmission)", ["أوتوماتيك", "مانيول"])

with col2:
    fuel_type = st.selectbox("نوع الوقود (Fuel Type)", ["بنزين", "كهربا", "هجين (Hybrid)", "غاز"])
    year = st.slider("سنة الصنع (Year)", min_value=2010, max_value=2026, value=2020)
    km_driven = st.number_input("العداد (الكيلومترات المقطوعة)", min_value=0, max_value=500000, value=50000, step=5000)

st.markdown("---")

# 4. زر التوقع ومعالجة البيانات
if st.button("توقع السعر الآن 🔍", use_container_width=True):
    # تجهيز المدخلات بنفس شكل الداتا اللي دربتی عليها الموديل
    # (تأكدي من مطابقة طريقة الـ Encoding هنا مع اللي استخدمتيها أثناء التدريب)
    
    # كمثال افتراضي لبيانات داخلة للموديل:
    input_data = pd.DataFrame({
        'Brand': [brand],
        'Line': [car_line],
        'Transmission': [transmission],
        'Fuel_Type': [fuel_type],
        'Year': [year],
        'Km_Driven': [km_driven]
    })
    
    try:
        # التوقع بالسعر الأساسي
        predicted_price = model.predict(input_data)[0]
        
        # حساب رينج السعر (مثلاً بفرق 7% أعلى وأقل كمثال تقريبي لتباين السوق)
        margin = predicted_price * 0.07
        min_price = max(0, predicted_price - margin)
        max_price = predicted_price + margin
        
        # عرض النتائج بشكل شيك
        st.success("تم التوقع بنجاح!")
        
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric(label="🏷️ السعر المتوقع المحدّد", value=f"{int(predicted_price):,} جنيه")
        with metric_col2:
            st.metric(label="📊 رينج الأسعار المتوقع", value=f"{int(min_price):,} - {int(max_price):,} جنيه")
            
        st.info("⚠️ ملحوظة: هذا التوقع استرشادي بناءً على الأسعار الحالية في السوق المصري وقد يختلف حسب حالة السيارة الفعلية.")
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء عملية التوقع. تأكد من تطابق الـ Features: {e}")
