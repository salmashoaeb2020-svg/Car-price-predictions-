import streamlit as st
import pandas as pd
import joblib

# إعدادات صفحة التطبيق
st.set_page_config(page_title="توقع أسعار السيارات المستعملة", page_icon="🚗", layout="centered")

st.title("🚗 تطبيق التنبؤ بأسعار السيارات المستعملة في مصر")
st.write("أدخل مواصفات السيارة لمعرفة السعر المتوقع بناءً على نموذج الذكاء الاصطناعي.")

# تحميل النموذج والأعمدة المحفوظة مسبقاً
@st.cache_resource
def load_artifacts():
    model = joblib.load('car_price_model.pkl')
    model_columns = joblib.load('model_columns.pkl')
    return model, model_columns

model, model_columns = load_artifacts()

# مدخلات المستخدم في واجهة Streamlit
st.sidebar.header("مواصفات السيارة المطلوبة")

mileage = st.sidebar.number_input("عدد الكيلومترات (Mileage)", min_value=0, max_value=500000, value=50000, step=5000)
year = st.sidebar.number_input("سنة الصنع (Year)", min_value=1990, max_value=2026, value=2020, step=1)
city = st.sidebar.selectbox("المدينة (City)", ["Cairo", "Giza", "Alexandria", "Mansoura", "Tanta"])
make = st.sidebar.text_input("ماركة السيارة (Make)", "Toyota")
car_model = st.sidebar.text_input("موديل السيارة (Model)", "Corolla")

# زر التنبؤ
if st.button("توقع السعر الآن"):
    # إنشاء إطار بيانات للمدخلات الجديدة
    input_data = pd.DataFrame({
        'Mileage': [mileage],
        'Year': [year],
        'City': [city],
        'Make': [make],
        'Model': [car_model]
    })
    
    # ترميز المدخلات
    input_data = pd.get_dummies(input_data)
    
    # مطابقة الأعمدة تماماً لما تم التدريب عليه
    input_data = input_data.reindex(columns=model_columns, fill_value=0)
    
    # التنبؤ بالسعر
    predicted_price = model.predict(input_data)[0]
    
    # عرض النتيجة
    st.success(f"### السعر المتوقع للسيارة هو: حوالي **{predicted_price:,.0f} جنيه**")
