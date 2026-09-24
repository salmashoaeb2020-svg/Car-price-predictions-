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
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e3e6f0;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# عنوان التطبيق
st.markdown('<p class="main-title">🚗 Car Price Prediction System</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">نظام ذكي لتحليل وتوقع أسعار السيارات بناءً على بيانات السوق'
    " ومواصفات السيارة</p>",
    unsafe_allow_html=True,
)
st.markdown("---")
st.markdown("👩‍💻 **Developed by:** Salma Ahmed & Habiba Essam")

# تحميل وتجهيز البيانات
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
      "enginetype": [
          "ohc",
          "ohc",
          "ohc",
          "rotary",
          "ohc",
          "ohc",
          "ohc",
          "ohc",
          "ohc",
          "ohcv",
      ],
      "cylindernumber": [
          "four",
          "four",
          "four",
          "twelve",
          "four",
          "five",
          "four",
          "four",
          "four",
          "six",
      ],
      "enginesize": [120, 120, 97, 70, 109, 136, 109, 92, 92, 198],
      "horsepower": [111, 111, 88, 101, 102, 110, 85, 76, 68, 207],
      "citympg": [21, 19, 31, 17, 21, 19, 27, 30, 31, 17],
      "highwaympg": [27, 24, 33, 23, 27, 25, 33, 34, 38, 25],
      "compressionratio": [9.0, 8.5, 9.4, 9.4, 8.8, 8.5, 9.0, 9.0, 9.0, 9.5],
      "peakrpm": [5000, 5000, 5500, 6000, 5500, 5500, 5250, 5500, 5500, 5900],
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

CAR_IMAGES = {
    "toyota": "https://images.unsplash.com/photo-1629897048514-3dd7414fe72a?auto=format&fit=crop&w=800&q=80",
    "nissan": "https://images.unsplash.com/photo-1609521263047-f8d205293f24?auto=format&fit=crop&w=800&q=80",
    "mazda": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80",
    "bmw": "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=800&q=80",
    "volkswagen": "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?auto=format&fit=crop&w=800&q=80",
    "audi": "https://images.unsplash.com/photo-1606152421802-db97b9c7a11b?auto=format&fit=crop&w=800&q=80",
    "honda": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=800&q=80",
    "mitsubishi": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80",
    "porsche": "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=800&q=80",
}

# تقسيم الشاشة إلى أقسام منظمة باستخدام Tabs أو Columns
tab1, tab2 = st.tabs(["🎯 توقع الأسعار (Price Prediction)", "📊 تحليل بيانات السوق"])

with tab1:
  st.markdown("### أدخل تفاصيل ومواصفات السيارة")

  col1, col2 = st.columns(2)

  with col1:
    st.markdown("#### 🚘 المواصفات الأساسية")
    selected_brand = st.selectbox("ماركة السيارة (Car Brand)", df["CarName"].unique())
    fueltype = st.selectbox("نوع الوقود (Fuel Type)", df["fueltype"].unique())
    aspiration = st.selectbox("نوع السحب (Aspiration)", df["aspiration"].unique())
    carbody = st.selectbox("هيكل السيارة (Car Body)", df["carbody"].unique())

    # خانات الإدخال الجديدة المطلوبة
    st.markdown("#### 📅 حالة الاستخدام والعمر")
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

  with col2:
    st.markdown("#### ⚙️ الأداء الفني والمحرك")
    drivewheel = st.selectbox("نوع الجر (Drive Wheel)", df["drivewheel"].unique())
    enginesize = st.slider(
        "حجم المحرك (Engine Size)",
        min_value=50,
        max_value=350,
        value=int(df["enginesize"].mean()),
    )
    horsepower = st.slider(
        "القدرة الحصانية (Horsepower)",
        min_value=40,
        max_value=300,
        value=int(df["horsepower"].mean()),
    )
    citympg = st.number_input(
        "معدل استهلاك الوقود داخل المدينة (City MPG)",
        min_value=10,
        max_value=60,
        value=int(df["citympg"].mean()),
    )
    highwaympg = st.number_input(
        "معدل استهلاك الوقود على الطرق السريعة (Highway MPG)",
        min_value=10,
        max_value=70,
        value=int(df["highwaympg"].mean()),
    )

  # عرض صورة الماركة بشكل جمالي
  st.markdown("---")
  img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
  with img_col2:
    img_url = CAR_IMAGES.get(
        selected_brand,
        "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80",
    )
    st.image(
        img_url,
        caption=f"معاينة ماركة السيارة: {selected_brand.capitalize()}",
        use_container_width=True,
    )

  st.markdown("---")

  # زر التنبوء وتطبيق معادلة الإهلاك مع الانحدار
  if st.button("احسب السعر المتوقع (Predict Price)"):
    base_avg_price = df[df["CarName"] == selected_brand]["price"].mean()
    if np.isnan(base_avg_price):
      base_avg_price = df["price"].mean()

    # حساب الإهلاك بناءً على سنة الصنع والـ KM المقطوعة
    years_old = 2026 - manufacturing_year
    age_depreciation = min(
        years_old * 0.03, 0.60
    )  # خصم 3% لكل سنة (بحد أقصى 60%)
    km_depreciation = min(
        (km_driven / 20000) * 0.015, 0.20
    )  # خصم 1.5% لكل 20 ألف كم (بحد أقصى 20%)
    total_depreciation_factor = max(1.0 - (age_depreciation + km_depreciation), 0.25)

    # نموذج السعر المعتمد على المحرك والأداء مع معامل الإهلاك
    estimated_price = (
        base_avg_price * 0.3
        + (enginesize * 40)
        + (horsepower * 30)
        - (citympg * 20)
    ) * total_depreciation_factor
    estimated_price = max(estimated_price, 2000)  # حد أدنى منطقي للسعر

    min_price = estimated_price * 0.90
    max_price = estimated_price * 1.10

    # عرض النتائج في بطاقات أنيقة
    st.success("تمت عملية التحليل والتوقع بنجاح!")

    res_col1, res_col2 = st.columns(2)
    with res_col1:
      st.metric(
          label="💰 السعر المتوقع (Estimated Price)",
          value=f"{estimated_price:,.2f} $",
      )
    with res_col2:
      st.metric(
          label="📊 نطاق السعر المحتمل (Price Range)",
          value=f"{min_price:,.2f} $ — {max_price:,.2f} $",
      )

    # رسم بياني تفاعلي للرينج
    chart_data = pd.DataFrame({
        "Price Range": [
            "الحد الأدنى للسعر",
            "السعر المتوقع",
            "الحد الأقصى للسعر",
        ],
        "السعر ($)": [min_price, estimated_price, max_price],
    })
    st.bar_chart(chart_data.set_index("Price Range"))

with tab2:
  st.markdown("### 📈 إحصائيات وتحليلات قاعدة البيانات")
  st.write("نظرة عامة على البيانات الوصفية لسيارات المنافسين:")
  st.dataframe(df.describe(), use_container_width=True)

  st.markdown("#### متوسط الأسعار حسب ماركة السيارة:")
  avg_price_by_brand = df.groupby("CarName")["price"].mean().reset_index()
  st.bar_chart(avg_price_by_brand.set_index("CarName"))
