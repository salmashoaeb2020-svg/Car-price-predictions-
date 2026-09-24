import numpy as np
import pandas as pd
import streamlit as st

# إعدادات الصفحة بتصميم واسع وعصري
st.set_page_config(
    page_title="Car Price Predictor & Analysis",
    page_icon="🚗",
    layout="wide",
)

# تصميم وتنسيق CSS مخصص لتحسين شكل الـ GUI
st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        color: #1f77b4;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 18px;
        color: #555555;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
    }
    .stButton>button:hover {
        background-color: #e03e3e;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# عنوان التطبيق
st.markdown(
    '<p class="main-title">🚗 Car Price Prediction System</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">نظام ذكي لتحليل وتوقع أسعار السيارات بناءً على بيانات السوق ومواصفات السيارة</p>',
    unsafe_allow_html=True,
)
st.markdown("---")
st.markdown("👩‍💻 **Developed by:** Salma Ahmed & Habiba Essam")

# تحميل وتجهيز البيانات (الأسعار هنا افتراضية مبدئية سيتم ضربها في معامل الجنيه المصري لتناسب السوق الواقعي)
@st.cache_data
def load_and_process_data():
  data = {
      "CarName": [
          "toyota corolla",
          "toyota corona",
          "nissan stanza",
          "mazda rx7",
          "bmw 320i",
          "audi 100ls",
          "volkswagen jetta",
          "honda civic",
          "mitsubishi lancer",
          "porsche boxster",
      ],
      "fueltype": ["gas", "gas", "gas", "gas", "gas", "gas", "gas", "gas", "gas", "gas"],
      "aspiration": [
          "std",
          "std",
          "std",
          "std",
          "std",
          "std",
          "std",
          "std",
          "std",
          "turbo",
      ],
      "doornumber": [
          "four",
          "four",
          "four",
          "two",
          "two",
          "four",
          "four",
          "two",
          "four",
          "two",
      ],
      "carbody": [
          "sedan",
          "sedan",
          "sedan",
          "hatchback",
          "sedan",
          "sedan",
          "sedan",
          "hatchback",
          "sedan",
          "convertible",
      ],
      "drivewheel": ["fwd", "fwd", "fwd", "fwd", "rwd", "fwd", "fwd", "fwd", "fwd", "rwd"],
      "citympg": [21, 19, 31, 17, 21, 19, 27, 30, 31, 17],
      "highwaympg": [27, 24, 33, 23, 27, 25, 33, 34, 38, 25],
      "price": [13495, 16500, 7898, 10945, 16430, 15250, 7975, 7945, 7609, 34028],
  }
  df = pd.DataFrame(data)
  df["CarName"] = df["CarName"].str.split(" ", expand=True)[0]
  replacements = {
      "maxda": "mazda",
      "porcshce": "porsche",
      "toyouta": "toyota",
      "vokswagen": "volkswagen",
      "vw": "volkswagen",
      "Nissan": "nissan",
  }
  df["CarName"] = df["CarName"].replace(replacements)
  return df


df = load_and_process_data()

tab1, tab2 = st.tabs(["🎯 توقع الأسعار (Price Prediction)", "📊 تحليل بيانات السوق"])

with tab1:
  st.markdown("### أدخل تفاصيل ومواصفات السيارة")

  col1, col2 = st.columns(2)

  with col1:
    st.markdown("#### 🚘 المواصفات الأساسية")
    selected_brand = st.selectbox("ماركة السيارة (Car Brand)", df["CarName"].unique())
    
    fueltype = st.selectbox(
        "نوع الوقود (Fuel Type)", 
        ["Gasoline (بنزين)", "Diesel (ديزل)", "Hybrid (هجين)", "Electric (كهربائي)"]
    )
    
    transmission = st.selectbox(
        "ناقل الحركة (Transmission)", 
        ["Automatic (أوتوماتيك)", "Manual (مانيوال)"]
    )
    
    carbody = st.selectbox("هيكل السيارة (Car Body)", df["carbody"].unique())

  with col2:
    st.markdown("#### 📅 سنة الصنع والمسافة المقطوعة")
    manufacturing_year = st.number_input(
        "سنة الصنع (Manufacturing Year)",
        min_value=1980,
        max_value=2026,
        value=2015,
    )
    km_driven = st.number_input(
        "المسافة المقطوعة بالكيلومتر (KM Driven)",
        min_value=0,
        max_value=500000,
        value=80000,
        step=5000,
    )
    drivewheel = st.selectbox("نوع الجر (Drive Wheel)", df["drivewheel"].unique())
    
    citympg = st.number_input(
        "معدل استهلاك الوقود داخل المدينة (City MPG)",
        min_value=10,
        max_value=60,
        value=int(df["citympg"].mean()),
    )

  st.markdown("---")

  # زر التوقع وحساب السعر بالجنيه المصري بناءً على المعطيات وإهلاك السوق
  if st.button("احسب السعر المتوقع (Predict Price)"):
    base_avg_price = df[df["CarName"] == selected_brand]["price"].mean()
    if np.isnan(base_avg_price):
      base_avg_price = df["price"].mean()

    # حساب الإهلاك بناءً على سنة الصنع والـ KM المقطوعة
    years_old = 2026 - manufacturing_year
    age_depreciation = min(years_old * 0.03, 0.60)
    km_depreciation = min((km_driven / 20000) * 0.015, 0.20)
    total_depreciation_factor = max(1.0 - (age_depreciation + km_depreciation), 0.25)

    # تأثير نوع الوقود وناقل الحركة
    fuel_multiplier = 1.15 if "Electric" in fueltype or "Hybrid" in fueltype else (0.95 if "Diesel" in fueltype else 1.0)
    trans_multiplier = 1.08 if "Automatic" in transmission else 1.0

    # معامل تحويل تقريبي للجنيه المصري بالسوق الواقعي
    egp_conversion_rate = 55.0 

    # معادلة حساب السعر التقديري بالجنيه المصري
    estimated_price = (base_avg_price * 0.5 - (citympg * 30)) * total_depreciation_factor * fuel_multiplier * trans_multiplier * egp_conversion_rate
    estimated_price = max(estimated_price, 150000)  # حد أدنى منطقي بالجنيه المصري

    min_price = estimated_price * 0.90
    max_price = estimated_price * 1.10

    # عرض النتائج في بطاقات أنيقة
    st.success("تمت عملية التحليل والتوقع بنجاح!")

    res_col1, res_col2 = st.columns(2)
    with res_col1:
      st.metric(
          label="💰 السعر المتوقع (Estimated Price)",
          value=f"{estimated_price:,.2f} EGP",
      )
    with res_col2:
      st.metric(
          label="📊 نطاق السعر المحتمل (Price Range)",
          value=f"{min_price:,.2f} EGP — {max_price:,.2f} EGP",
      )

    chart_data = pd.DataFrame({
        "Price Range": [
            "الحد الأدنى للسعر",
            "السعر المتوقع",
            "الحد الأقصى للسعر",
        ],
        "السعر (EGP)": [min_price, estimated_price, max_price],
    })
    st.bar_chart(chart_data.set_index("Price Range"))

with tab2:
  st.markdown("### 📈 إحصائيات وتحليلات قاعدة البيانات")
  st.write("نظرة عامة على البيانات الوصفية لسيارات المنافسين:")
  st.dataframe(df.describe(), use_container_width=True)

  st.markdown("#### متوسط الأسعار حسب ماركة السيارة:")
  avg_price_by_brand = df.groupby("CarName")["price"].mean().reset_index()
  st.bar_chart(avg_price_by_brand.set_index("CarName"))
