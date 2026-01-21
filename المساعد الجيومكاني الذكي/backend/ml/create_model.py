import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


try:
    data = pd.read_csv("Smart_Environmental_Dataset.csv")
except FileNotFoundError:
    print("❌ خطأ: لم يتم العثور على ملف البيانات CSV.")
    



categorical_features = ["Protected_Area", "Violation_Type", "Season"]
numerical_features = ["Area_m2", "Distance_To_Road_km", "Distance_To_Urban_km", "Year", "Fine_Amount"]
target = "Risk_Level"
X = data[categorical_features + numerical_features]
y = data["Risk_Level"]


label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)


preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", StandardScaler(), numerical_features)
    ]
)

# 5. إنشاء Pipeline
model_pipeline = Pipeline(
    steps=[
        ("preprocessing", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            random_state=42,
            class_weight="balanced"
        ))
    ]
)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, stratify=y_encoded, random_state=42)
model_pipeline.fit(X_train, y_train)


import os
if not os.path.exists('ml'): os.makedirs('ml')

joblib.dump(model_pipeline, "ml/Risk_model_pipeline.pkl")
joblib.dump(label_encoder, "ml/Risk_label_encoder.pkl")

print("✅ تم تدريب المودل وحفظه في مجلد ml/")
print("\n📈 تقرير الأداء:\n", classification_report(y_test, model_pipeline.predict(X_test), target_names=label_encoder.classes_))

# أضف هذا الجزء في نهاية create_model.py لرؤية تأثير كل ميزة
importances = model_pipeline.named_steps['classifier'].feature_importances_
feature_names = np.concatenate([
    model_pipeline.named_steps['preprocessing'].transformers_[0][1].get_feature_names_out(),
    numerical_features
])


feat_importance_dict = dict(zip(feature_names, importances))
sorted_features = sorted(feat_importance_dict.items(), key=lambda x: x[1], reverse=True)

print("\n🔍 العوامل الأكثر تأثيراً في تصنيف المودل:")
for name, val in sorted_features[:3]:
    print(f"- {name}: {val*100:.2f}%")