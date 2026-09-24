import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score

# 1. تحميل البيانات وتنظيفها
df = pd.read_csv('hatla2ee_scraped_data.csv')

# التخلص من الصفوف التي تحتوي على قيم مفقودة في الأسعار أو الكيلومترات
df = df.dropna(subset=['Price', 'Mileage'])

# اختيار الأعمدة المناسبة للنموذج (يمكنك تعديلها حسب المتغيرات المتوفرة لديك)
# مثال: الاعتماد على الماركة، الموديل، سنة الصنع، الكيلومترات، والمدينة
features = ['Make', 'Model', 'Year', 'Mileage', 'City']
target = 'Price'

X = df[features]
y = df[target]

# تحويل المتغيرات النصية إلى ترميز عددي (One-Hot Encoding)
X = pd.get_dummies(X, drop_first=True)

# حفظ أسماء الأعمدة لضمان مطابقتها لاحقاً في واجهة الاستخدام
model_columns = X.columns.tolist()
joblib.dump(model_columns, 'model_columns.pkl')

# 2. تقسيم البيانات إلى بيانات تدريب واختبار
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. بناء وتدريب نموذج XGBoost
model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

# 4. تقييم النموذج
y_pred = model.predict(X_test)
print(f"R2 Score: {r2_score(y_test, y_pred):.4f}")

# 5. حفظ النموذج المدرب
joblib.dump(model, 'car_price_model.pkl')
print("تم تدريب وحفظ النموذج بنجاح!")
