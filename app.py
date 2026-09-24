from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from joblib import load

# ----------------------------------------------------------------------------
# إعدادات عامة
# ----------------------------------------------------------------------------
# المسارات نسبةً لمكان app.py نفسه (مش مكان تشغيل الأمر)
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "hatla2ee_scraped_data.csv"
MODEL_PATH = BASE_DIR / "model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"
ENCODERS_PATH = BASE_DIR / "label_encoder.pkl"

# لو النموذج اتدرب على log(Price) خليها True عشان نرجّع السعر لأصله
TARGET_IS_LOG = False

# ترتيب الأعمدة زي ما اتدرب في الـ Notebook (بيتغير تلقائيًا لو الـ scaler حافظ الأسماء)
DEFAULT_FEATURES = [
    "Color",
    "KM",
    "Maker",
    "Model",
    "Automatic Transmission",
    "Air Conditioner",
    "Power Steering",
    "Remote Control",
    "year",
]

CURRENT_YEAR = date.today().year

st.set_page_config(
    page_title="Egyptian Used Cars Price Predictor",
    page_icon="🚗",
    layout="wide",
)

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


# ----------------------------------------------------------------------------
# دوال مساعدة
# ----------------------------------------------------------------------------
def clean_price(series: pd.Series) -> pd.Series:
    """تحويل عمود السعر لأرقام حتى لو فيه نصوص زي 'EGP' أو فواصل."""
    if pd.api.types.is_numeric_dtype(series):
        return series
    cleaned = (
        series.astype(str)
        .str.replace("EGP", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def encoder_options(encoders: dict, key: str, fallback=None) -> list:
    """اختيارات الـ selectbox من الـ encoder نفسه عشان نضمن إنها متوافقة مع التدريب."""
    if key in encoders:
        return sorted(str(c) for c in encoders[key].classes_)
    return sorted(str(x) for x in (fallback if fallback is not None else []))


# ----------------------------------------------------------------------------
# تحميل البيانات والنموذج
# ----------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    if "year" not in df.columns and "Name" in df.columns:
        df["year"] = df["Name"].astype(str).str.extract(r"\b((?:19|20)\d{2})\b")[0].astype(float)
    if "Price" in df.columns:
        df["Price"] = clean_price(df["Price"])
    return df


@st.cache_resource
def load_ml_assets():
    model = load(MODEL_PATH)
    scaler = load(SCALER_PATH)
    label_encoders = load(ENCODERS_PATH)
    return model, scaler, label_encoders


try:
    df = load_data()
    model, scaler, label_encoders = load_ml_assets()
except Exception as e:
    st.error(
        "⚠️ تنبيه: تعذر تحميل ملفات البيانات أو النماذج. تأكدي من وجود الملفات "
        f"({CSV_PATH}, {MODEL_PATH}, {SCALER_PATH}, {ENCODERS_PATH}) في مجلد المشروع.\n\n"
        f"الخطأ: {e}"
    )
    st.stop()

# اسم عمود الماركة في الـ CSV ممكن يبقى Make أو Maker
MAKE_COL = next((c for c in ("Make", "Maker") if c in df.columns), None)
MODEL_COL = "Model" if "Model" in df.columns else None

tab1, tab2 = st.tabs(["🎯 توقع الأسعار (Price Prediction)", "📊 تحليل بيانات السوق"])

# ----------------------------------------------------------------------------
# التبويب الأول: التوقع
# ----------------------------------------------------------------------------
with tab1:
    st.markdown("### أدخل تفاصيل ومواصفات السيارة")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🚘 المواصفات الأساسية")

        makers = encoder_options(
            label_encoders, "Maker", df[MAKE_COL].dropna().unique() if MAKE_COL else []
        )
        selected_maker = st.selectbox("ماركة السيارة (Car Make)", makers)

        # الموديلات المتاحة للماركة دي، بشرط تكون موجودة في الـ encoder
        valid_models = set(encoder_options(label_encoders, "Model"))
        if MAKE_COL and MODEL_COL:
            models_for_make = set(
                df.loc[df[MAKE_COL].astype(str) == selected_maker, MODEL_COL]
                .dropna()
                .astype(str)
            )
            filtered_models = sorted(models_for_make & valid_models) if valid_models else sorted(models_for_make)
        else:
            filtered_models = sorted(valid_models)

        if not filtered_models:
            st.warning("مفيش موديلات متاحة للماركة دي، هيتم عرض كل الموديلات.")
            filtered_models = sorted(valid_models)

        selected_model = st.selectbox("مُوديل السيارة (Car Model)", filtered_models)

        colors = encoder_options(
            label_encoders, "Color", df["Color"].dropna().unique() if "Color" in df.columns else []
        )
        selected_color = st.selectbox("لون السيارة (Color)", colors)

        automatic_trans = st.selectbox(
            "ناقل الحركة أوتوماتيك؟ (Automatic Transmission)",
            encoder_options(label_encoders, "Automatic Transmission", ["Yes", "No"]),
        )

    with col2:
        st.markdown("#### 📅 سنة الصنع والمسافة المقطوعة والكماليات")
        manufacturing_year = st.number_input(
            "سنة الصنع (Manufacturing Year)",
            min_value=1980,
            max_value=CURRENT_YEAR + 1,
            value=min(2021, CURRENT_YEAR),
            step=1,
        )

        km_driven = st.number_input(
            "المسافة المقطوعة بالكيلومتر (KM Driven)",
            min_value=0,
            max_value=1_000_000,
            value=80000,
            step=5000,
        )

        yes_no_ac = encoder_options(label_encoders, "Air Conditioner", ["Yes", "No"])
        yes_no_ps = encoder_options(label_encoders, "Power Steering", ["Yes", "No"])
        yes_no_rc = encoder_options(label_encoders, "Remote Control", ["Yes", "No"])

        air_conditioner = st.selectbox("تكييف الهواء (Air Conditioner)", yes_no_ac)
        power_steering = st.selectbox("باور ستيرنج (Power Steering)", yes_no_ps)
        remote_control = st.selectbox("ريموت كنترول (Remote Control)", yes_no_rc)

    st.markdown("---")

    if st.button("احسب السعر المتوقع (Predict Price)"):
        try:
            row = {
                "Color": label_encoders["Color"].transform([selected_color])[0],
                "KM": km_driven,
                "Maker": label_encoders["Maker"].transform([selected_maker])[0],
                "Model": label_encoders["Model"].transform([selected_model])[0],
                "Automatic Transmission": label_encoders["Automatic Transmission"].transform(
                    [automatic_trans]
                )[0],
                "Air Conditioner": label_encoders["Air Conditioner"].transform(
                    [air_conditioner]
                )[0],
                "Power Steering": label_encoders["Power Steering"].transform(
                    [power_steering]
                )[0],
                "Remote Control": label_encoders["Remote Control"].transform(
                    [remote_control]
                )[0],
                "year": manufacturing_year,
            }

            # نستخدم نفس ترتيب الأعمدة اللي الـ scaler اتدرب عليه لو متاح
            feature_order = list(getattr(scaler, "feature_names_in_", DEFAULT_FEATURES))
            input_data = pd.DataFrame([row])[feature_order]

            scaled_input = scaler.transform(input_data)
            predicted_price = float(model.predict(scaled_input)[0])

            if TARGET_IS_LOG:
                predicted_price = float(np.expm1(predicted_price))

            if predicted_price <= 0:
                st.warning(
                    "النموذج رجّع قيمة غير منطقية لهذه المدخلات، جرّب مواصفات مختلفة."
                )
            else:
                min_price = predicted_price * 0.90
                max_price = predicted_price * 1.10

                st.success("تمت عملية التحليل والتوقع بنجاح!")

                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric(
                        label="💰 السعر المتوقع (Estimated Price)",
                        value=f"{predicted_price:,.0f} EGP",
                    )
                with res_col2:
                    st.metric(
                        label="📊 نطاق السعر التقريبي (±10%)",
                        value=f"{min_price:,.0f} — {max_price:,.0f} EGP",
                    )
                st.caption("النطاق تقريبي (±10%) وليس فاصل ثقة إحصائي.")

        except ValueError as ex:
            st.error(f"إحدى القيم المختارة غير موجودة في بيانات التدريب: {ex}")
        except KeyError as ex:
            st.error(f"الـ encoder الخاص بالعمود {ex} غير موجود في ملف label_encoder.pkl")
        except Exception as ex:
            st.error(f"حدث خطأ أثناء عملية التوقع: {ex}")

# ----------------------------------------------------------------------------
# التبويب الثاني: تحليل البيانات
# ----------------------------------------------------------------------------
with tab2:
    st.markdown("### 📈 إحصائيات وتحليلات قاعدة البيانات الحقيقية")
    st.write("نظرة عامة على البيانات الوصفية لسيارات السوق المصري:")
    st.dataframe(df.describe())

    if MAKE_COL and "Price" in df.columns:
        st.markdown("#### متوسط الأسعار حسب ماركة السيارة:")
        top_n = st.slider("عدد الماركات المعروضة", 5, 30, 15)

        temp_df = df.dropna(subset=["Price", MAKE_COL])
        avg_price_by_brand = (
            temp_df.groupby(MAKE_COL)["Price"]
            .mean()
            .sort_values(ascending=False)
            .head(top_n)
        )
        st.bar_chart(avg_price_by_brand)
