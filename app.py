import pandas as pd
import requests
import streamlit as st
from xml.etree import ElementTree

# إعدادات الصفحة
st.set_page_config(
    page_title="Car Price Predictor", page_icon="🚗", layout="wide"
)

CURRENT_YEAR = 2026  # ⚠️ لازم يتحدّث كل سنة (أو يتحسب تلقائي من datetime.now().year)

# 1. قاعدة بيانات الشركات والموديلات والأسعار الأساسية (أسعار الزيرو التقريبية)
CAR_MODELS = {
    "Chevrolet": {
        "Aveo": 600000,
        "Optra": 750000,
        "Cruze": 650000,
        "Captiva": 1500000,
    },
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
        "Belta": 850000,
    },
    "Hyundai": {
        "Elantra": 1300000,
        "Tucson": 1900000,
        "Accent": 900000,
        "Creta": 1400000,
        "I10": 700000,
    },
    "Kia": {
        "Cerato / K3": 1350000,
        "Sportage": 1950000,
        "Pegas": 850000,
        "Seltos": 1500000,
        "XCeed": 1600000,
    },
    "Mitsubishi": {
        "Lancer": 750000,
        "Xpander": 1300000,
        "Eclipse Cross": 1600000,
        "Attrage": 750000,
    },
    "Suzuki": {
        "Swift": 750000,
        "Ciaz": 850000,
        "Ertiga": 950000,
        "Espresso": 550000,
    },
    "Honda": {"Civic": 1700000, "City": 1200000, "CR-V": 2200000},
    "Renault": {
        "Logan": 650000,
        "Megane": 1400000,
        "Duster": 1200000,
        "Stepway": 850000,
    },
    "Peugeot": {
        "301": 850000,
        "508": 1800000,
        "2008": 1450000,
        "3008": 1950000,
        "5008": 2200000,
    },
    "Fiat": {"Tipo": 1050000, "500": 1100000, "Punto": 500000},
    "Skoda": {
        "Octavia": 1850000,
        "Kodiaq": 2600000,
        "Karoq": 2100000,
        "Scala": 1300000,
    },
    "Volkswagen": {
        "Golf": 1700000,
        "Passat": 1900000,
        "Tiguan": 2500000,
        "Jetta": 900000,
    },
    "Opel": {
        "Astra": 950000,
        "Corsa": 1250000,
        "Grandland": 1750000,
        "Mokka": 1500000,
    },
    "Seat": {
        "Ibiza": 1250000,
        "Leon": 1600000,
        "Ateca": 1850000,
        "Arona": 1350000,
    },
    "MG": {
        "MG 5": 850000,
        "MG 6": 1200000,
        "MG ZS": 1050000,
        "MG RX5": 1400000,
        "MG4": 1350000,
    },
    "Chery": {
        "Arrizo 5": 750000,
        "Tiggo 3": 880000,
        "Tiggo 7": 1100000,
        "Tiggo 8": 1450000,
    },
    "Geely": {"Emgrand": 850000, "Coolray": 1300000, "Okavango": 1650000},
    "Changan": {"Alsvin": 650000, "CS35 Plus": 1150000, "CS55 Plus": 1350000},
    "BYD": {"F3": 620000, "Song Plus": 1600000},
    "HAVAL": {"H6": 1450000, "Jolion": 1200000},
    "Ford": {"Focus": 1200000, "EcoSport": 1000000, "Kuga": 1400000},
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
    "Audi": {"A4": 2800000, "A6": 3900000, "Q3": 2500000, "Q7": 4900000},
}

# اسم مبسّط لكل موديل (من غير اللي بين قوسين) عشان البحث عن الصورة يبقى أدق
MODEL_SEARCH_OVERRIDES = {
    "Cerato / K3": "Cerato",
    "3 Series (320i)": "3 Series",
    "5 Series (520i)": "5 Series",
    "C-Class (C180/C200)": "C-Class",
    "E-Class (E200)": "E-Class",
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=800&q=80"


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24)
def get_car_image_url(brand: str, model_name: str) -> str:
    """
    بيرجع رابط صورة حقيقية للعربية عن طريق CarImagery API — خدمة مجانية بدون
    مفتاح، اتأكدنا إنها شغالة فعليًا (بعكس imagin.studio اللي كان محتاج
    اشتراك مدفوع وكان بيرجع 403). البحث بيتم بالبراند + الموديل، والنتيجة
    بتتخزّن (cache) لمدة يوم عشان ما نستهلكش حد الطلبات المجاني (100 طلب/IP).
    لو الخدمة فشلت لأي سبب، بيرجع صورة عامة بدل ما التطبيق يقع.
    """
    search_term = f"{brand} {MODEL_SEARCH_OVERRIDES.get(model_name, model_name)}"
    try:
        resp = requests.get(
            "http://www.carimagery.com/api.asmx/GetImageUrl",
            params={"searchTerm": search_term},
            timeout=6,
        )
        resp.raise_for_status()
        root = ElementTree.fromstring(resp.content)
        image_url = (root.text or "").strip()
        if image_url.startswith("http"):
            return image_url.replace("http://", "https://", 1)
    except Exception:
        pass
    return DEFAULT_IMAGE


# دالة حساب السعر
def calculate_car_price(
    brand, model_name, year, km_driven, car_condition, transmission
):
    base_price = CAR_MODELS[brand][model_name]
    years_old = max(CURRENT_YEAR - year, 0)

    # --- إهلاك العمر: انخفاض أسرع في أول سنتين، وبعدين بمعدل أبطأ ---
    # (سقف أعلى من قبل، لأن عربية عمرها 15-20 سنة فعلاً بتفقد أغلب قيمتها)
    if years_old <= 2:
        age_dep = years_old * 0.10          # 10% للسنة الأولى والتانية
    else:
        age_dep = 0.20 + (years_old - 2) * 0.035
    age_dep = min(age_dep, 0.75)

    # --- إهلاك الكيلومترات: تأثير أوضح، وسقف أعلى (كان 15% بس، دلوقتي 35%) ---
    km_dep = min((km_driven / 10000) * 0.015, 0.35)

    trans_dep = 0.05 if transmission == "Manual" else 0.0

    total_dep = age_dep + km_dep + trans_dep

    if car_condition == "Zero (Brand New)":
        est_price = base_price
        age_dep = 0.0
        km_dep = 0.0
        trans_dep = 0.0
    elif (
        car_condition == "Nearly New (كسر زيرو)"
        and years_old <= 3
        and km_driven <= 30000
    ):
        est_price = base_price * 0.92
    else:
        est_price = base_price * (1.0 - total_dep)
        # الأرضية كانت 45% وده كان بيخلي العربيات القديمة جدًا/الماشية كتير
        # مبالغ فيها في السعر. اتقلّلت لـ 15% عشان تبقى أقرب للواقع.
        est_price = max(est_price, base_price * 0.15)

    min_p = est_price * 0.95
    max_p = est_price * 1.05

    return est_price, min_p, max_p, base_price, age_dep, km_dep, trans_dep


# هيدر التطبيق
st.title("🚗 Smart Car Price Valuation System")
st.caption("👩‍💻 **Developed by:** Salma Ahmed & Habiba Essam")
st.caption(
    "⚠️ الأسعار والصور تقديرية بناءً على قواعد مبسّطة وليست بيانات سوق حية. "
    "يُنصح بتحديث `CAR_MODELS` بشكل دوري ليعكس السوق الفعلي."
)
st.markdown("---")

tab1, tab2 = st.tabs(["🔮 Predict Single Car Price", "⚖️ Compare Two Cars"])

# ==================== TAB 1 ====================
with tab1:
    col_input, col_img = st.columns([1.2, 1])

    with col_input:
        brand = st.selectbox("Car Brand", sorted(list(CAR_MODELS.keys())))
        available_models = list(CAR_MODELS[brand].keys())
        model_name = st.selectbox("Car Model / Line", available_models)
        transmission = st.selectbox("Transmission", ["Automatic", "Manual"])

    with col_img:
        img_url = get_car_image_url(brand, model_name)
        st.image(
            img_url,
            caption=f"{brand} {model_name} (صورة تقريبية)",
            use_container_width=True,
        )

    car_condition = st.radio(
        "Car Condition",
        ["Zero (Brand New)", "Nearly New (كسر زيرو)", "Used (مستعمل)"],
        horizontal=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input(
            "Manufacturing Year", min_value=2000, max_value=CURRENT_YEAR, value=2016
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
                "Kilometers Driven (KM)",
                min_value=0,
                max_value=500000,
                value=80000,
            )

    if st.button("Predict Price", key="btn_single"):
        est_p, min_p, max_p, base_p, age_dep, km_dep, trans_dep = (
            calculate_car_price(
                brand, model_name, year, km_driven, car_condition, transmission
            )
        )

        st.success(
            f"🎯 **Estimated Price for ({brand} {model_name} {year}):** {est_p:,.2f} EGP\n\n"
            f"📊 **Expected Range (±5% Margin):** {min_p:,.2f} EGP — {max_p:,.2f} EGP"
        )

        with st.expander("🔍 Price Breakdown & Factor Analysis"):
            st.write(f"• **Base Valuation (Zero Price):** {base_p:,.2f} EGP")
            st.write(
                f"• **Age Discount ({CURRENT_YEAR - year} Years Old):** -{age_dep * 100:.1f}%"
            )
            st.write(
                f"• **Mileage Discount ({km_driven:,} KM):** -{km_dep * 100:.1f}%"
            )
            if transmission == "Manual":
                st.write("• **Manual Transmission Discount:** -5.0%")

        chart_data = pd.DataFrame(
            {
                "Price Range": ["Minimum", "Estimated", "Maximum"],
                "Price (EGP)": [min_p, est_p, max_p],
            }
        )
        st.subheader("📊 Price Range Visualization")
        st.bar_chart(chart_data.set_index("Price Range"))

        st.markdown("---")
        c1, c2 = st.columns(2)

        with c1:
            st.write("##### Was this price estimate accurate?")
            fb_col1, fb_col2 = st.columns(2)
            if fb_col1.button("👍 Accurate"):
                st.toast("Thank you for your feedback!", icon="✅")
            if fb_col2.button("👎 Inaccurate"):
                st.toast("Feedback recorded for model improvement.", icon="📝")

        with c2:
            st.write("##### Download Valuation Summary")
            report_df = pd.DataFrame(
                [
                    {
                        "Brand": brand,
                        "Model": model_name,
                        "Year": year,
                        "Condition": car_condition,
                        "KM": km_driven,
                        "Transmission": transmission,
                        "Estimated Price (EGP)": est_p,
                        "Min Price": min_p,
                        "Max Price": max_p,
                    }
                ]
            )
            csv = report_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Summary Report (CSV)",
                data=csv,
                file_name=f"{brand}_{model_name}_valuation.csv",
                mime="text/csv",
            )

# ==================== TAB 2 ====================
with tab2:
    st.subheader("⚖️ Side-by-Side Car Valuation Comparison")
    col_car1, col_car2 = st.columns(2)

    with col_car1:
        st.markdown("### 🚗 Car 1")
        b1 = st.selectbox("Brand 1", sorted(list(CAR_MODELS.keys())), key="b1")
        m1 = st.selectbox("Model 1", list(CAR_MODELS[b1].keys()), key="m1")
        y1 = st.number_input("Year 1", 2000, CURRENT_YEAR, 2020, key="y1")
        cond1 = st.radio(
            "Condition 1",
            ["Used (مستعمل)", "Zero (Brand New)", "Nearly New (كسر زيرو)"],
            key="cond1",
        )
        km1 = (
            0
            if cond1 == "Zero (Brand New)"
            else st.number_input("KM 1", 0, 500000, 60000, key="km1")
        )
        trans1 = st.selectbox(
            "Transmission 1", ["Automatic", "Manual"], key="t1"
        )

    with col_car2:
        st.markdown("### 🚗 Car 2")
        b2 = st.selectbox("Brand 2", sorted(list(CAR_MODELS.keys())), key="b2")
        m2 = st.selectbox("Model 2", list(CAR_MODELS[b2].keys()), key="m2")
        y2 = st.number_input("Year 2", 2000, CURRENT_YEAR, 2018, key="y2")
        cond2 = st.radio(
            "Condition 2",
            ["Used (مستعمل)", "Zero (Brand New)", "Nearly New (كسر زيرو)"],
            key="cond2",
        )
        km2 = (
            0
            if cond2 == "Zero (Brand New)"
            else st.number_input("KM 2", 0, 500000, 100000, key="km2")
        )
        trans2 = st.selectbox(
            "Transmission 2", ["Automatic", "Manual"], key="t2"
        )

    if st.button("Compare Prices", key="btn_compare"):
        p1, _, _, _, _, _, _ = calculate_car_price(
            b1, m1, y1, km1, cond1, trans1
        )
        p2, _, _, _, _, _, _ = calculate_car_price(
            b2, m2, y2, km2, cond2, trans2
        )

        st.markdown("---")
        res1, res2 = st.columns(2)
        res1.metric(f"{b1} {m1} ({y1})", f"{p1:,.0f} EGP")
        res2.metric(f"{b2} {m2} ({y2})", f"{p2:,.0f} EGP")

        diff = abs(p1 - p2)
        cheaper = f"{b1} {m1}" if p1 < p2 else f"{b2} {m2}"
        st.info(
            f"💡 **Comparison Summary:** {cheaper} is cheaper by approximately **{diff:,.0f} EGP**."
        )
