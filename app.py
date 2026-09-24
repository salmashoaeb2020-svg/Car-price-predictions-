from joblib import load
import numpy as np
import pandas as pd
import streamlit as st

# إعدادات الصفحة بتصميم واسع وعصري
st.set_page_config(
    page_title="Egyptian Used Cars Price Predictor",
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
    '<p class="main-title">🚗 Egyptian Used Cars Price Prediction System</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">نظام ذكي لتوقع أسعار السيارات المستعملة في مصر بناءً على داتا سيت هتلابي ونموذج XGBoost</p>',
    unsafe_allow_html=True,
)
st.markdown("---")
st.markdown("👩‍💻 **Developed by:** Salma Ahmed & Habiba Essam")


# تحميل البيانات والنموذج والأدوات المحفوظة
@st.cache_data
def load_data():
  # تأكدي من وضع ملف الـ csv في نفس مجلد المشروع
  df = pd.read_csv("hatla2ee_scraped_data.csv")
  return df


@st.cache_resource
def load_ml_assets():
  model = load("model.pkl")
  scaler = load("scaler.pkl")
  label_encoders = load("label_encoder.pkl")
  return model, scaler, label_encoders


try:
  df = load_data()
  model, scaler, label_encoders = load_ml_assets()
  data_loaded = True
except Exception as e:
  data_loaded = False
  st.error(
      f"⚠️ تنبيه: تعذر تحميل ملفات البيانات أو النماذج. تأكدي من وجود ملفات (hatla2ee_scraped_data.csv, model.pkl, scaler.pkl, label_encoder.pkl) في مجلد المشروع. الخطأ: {e}"
  )

if data_loaded:
  # تنظيف أولي خفيف لتوافق الخيارات مع الكود السابق
  # استخراج سنة الصنع من عمود Name إذا لم تكن موجودة، أو التعامل مع الأعمدة المتاحة
  if "year" not in df.columns and "Name" in df.columns:
    df["year"] = df["Name"].str.extract(r"(\d{4})").astype(float)

  tab1, tab2 = st.tabs(["🎯 توقع الأسعار (Price Prediction)", "📊 تحليل بيانات السوق"])

  with tab1:
    st.markdown("### أدخل تفاصيل ومواصفات السيارة")

    col1, col2 = st.columns(2)

    with col1:
      st.markdown("#### 🚘 المواصفات الأساسية")

      # اختيار الماركة (Maker)
      available_makers = (
          label_encoders["Maker"].classes_
          if "Maker" in label_encoders
          else df["Make"].unique()
      )
      selected_maker = st.selectbox("ماركة السيارة (Car Make)", available_makers)

      # تصفية الموديلات بناءً على الماركة المختارة لتجربة مستخدم أفضل
      filtered_models = (
          df[df["Make"] == selected_maker]["Model"].unique()
          if "Make" in df.columns
          else df["Model"].unique()
      )
      if len(filtered_models) == 0:
        filtered_models = (
            label_encoders["Model"].classes_
            if "Model" in label_encoders
            else []
        )

      selected_model = st.selectbox("مُوديل السيارة (Car Model)", filtered_models)

      available_colors = (
          label_encoders["Color"].classes_
          if "Color" in label_encoders
          else df["Color"].unique()
      )
      selected_color = st.selectbox("لون السيارة (Color)", available_colors)

      # خيارات ناقل الحركة والكماليات
      automatic_trans = st.selectbox(
          "ناقل الحركة أوتوماتيك؟ (Automatic Transmission)", ["Yes", "No"]
      )

    with col2:
      st.markdown("#### 📅 سنة الصنع والمسافة المقطوعة والكماليات")
      manufacturing_year = st.number_input(
          "سنة الصنع (Manufacturing Year)",
          min_value=1980,
          max_value=2026,
          value=2021,
      )

      km_driven = st.number_input(
          "المسافة المقطوعة بالكيلومتر (KM Driven)",
          min_value=0,
          max_value=500000,
          value=80000,
          step=5000,
      )

      air_conditioner = st.selectbox(
          "تكييف الهواء (Air Conditioner)", ["Yes", "No"]
      )
      power_steering = st.selectbox("باور ستيرنج (Power Steering)", ["Yes", "No"])
      remote_control = st.selectbox("ريموت كنترول (Remote Control)", ["Yes", "No"])

    st.markdown("---")

    # زر التوقع باستخدام النموذج الحقيقي
    if st.button("احسب السعر المتوقع (Predict Price)"):
      try:
        # تشفير المدخلات باستخدام الـ Label Encoders المحفوظة
        encoded_maker = label_encoders["Maker"].transform([selected_maker])[0]
        encoded_model = label_encoders["Model"].transform([selected_model])[0]
        encoded_color = label_encoders["Color"].transform([selected_color])[0]
        encoded_trans = label_encoders["Automatic Transmission"].transform(
            [automatic_trans]
        )[0]
        encoded_ac = label_encoders["Air Conditioner"].transform(
            [air_conditioner]
        )[0]
        encoded_ps = label_encoders["Power Steering"].transform(
            [power_steering]
        )[0]
        encoded_rc = label_encoders["Remote Control"].transform(
            [remote_control]
        )[0]

        # ترتيب Features بنفس ترتيب التدريب في الـ Notebook:
        # ['Color', 'KM', 'Maker', 'Model', 'Automatic Transmission', 'Air Conditioner', 'Power Steering', 'Remote Control', 'year']
        input_data = pd.DataFrame(
            [[
                encoded_color,
                km_driven,
                encoded_maker,
                encoded_model,
                encoded_trans,
                encoded_ac,
                encoded_ps,
                encoded_rc,
                manufacturing_year,
            ]],
            columns=[
                "Color",
                "KM",
                "Maker",
                "Model",
                "Automatic Transmission",
                "Air Conditioner",
                "Power Steering",
                "Remote Control",
                "year",
            ],
        )

        # عمل Scaler للمدخلات إذا تم استخدامه أثناء التدريب
        scaled_input = scaler.transform(input_data)

        # التوقع بالنموذج
        predicted_price = model.predict(scaled_input)[0]
        predicted_price = max(
            predicted_price, 50000
        )  # حد أدنى منطقي بالجنيه المصري

        min_price = predicted_price * 0.90
        max_price = predicted_price * 1.10

        st.success("تمت عملية التحليل والتوقع بنجاح!")

        res_col1, res_col2 = st.columns(2)
        with res_col1:
          st.metric(
              label="💰 السعر المتوقع (Estimated Price)",
              value=f"{predicted_price:,.2f} EGP",
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
            "السعر (جنيه مصري)": [min_price, predicted_price, max_price],
        })
        st.bar_chart(chart_data.set_index("Price Range"))

      except Exception as ex:
        st.error(
            f"حدث خطأ أثناء عملية التوقع (تأكد من توافق اختيار الموديل مع الماركة في الداتا): {ex}"
        )

  with tab2:
    st.markdown("### 📈 إحصائيات وتحليلات قاعدة البيانات الحقيقية")
    st.write("نظرة عامة على البيانات الوصفية لسيارات السوق المصري:")
    st.dataframe(df.describe(), use_container_width=True)

    if "Make" in df.columns and "Price" in df.columns:
      st.markdown("#### متوسط الأسعار حسب ماركة السيارة:")
      # تنظيف الأسعار مؤقتاً للعرض لو كانت تحتوي على نصوص
      temp_df = df.dropna(subset=["Price"]).copy()
      if temp_df["Price"].dtype == object:
        temp_df["Price"] = (
            temp_df["Price"]
            .astype(str)
            .str.replace("EGP", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )
      avg_price_by_brand = (
          temp_df.groupby("Make")["Price"].mean().reset_index()
      )
      st.bar_chart(avg_price_by_brand.set_index("Make"))
