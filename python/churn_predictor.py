import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

print("1. Ingesting RFM Data...")
try:
    # Try to load the actual data exported from your SQL/BigQuery engine
    # Assuming you run this from the main C:\RFM_Project directory
    df = pd.read_csv('rfm_data.csv')
    
    # Standardize column names in case SQL exported them as lowercase
    df.columns = [str(col).title() for col in df.columns]
    print(f"✅ Successfully loaded {len(df)} customer records from SQL export.")
except FileNotFoundError:
    print("⚠️ 'rfm_data.csv' not found. Auto-generating a highly realistic dataset...")
    np.random.seed(42)
    df = pd.DataFrame({
        'CustomerId': np.arange(10000, 14339),
        'Recency': np.random.exponential(scale=60, size=4339).astype(int).clip(0, 365),
        'Frequency': np.random.lognormal(mean=1.2, sigma=0.8, size=4339).astype(int) + 1,
    })
    df['Monetary'] = (df['Frequency'] * np.random.uniform(50, 350, size=4339)).round(2)

print("\n2. Feature Engineering...")
# Create a new feature: Average Order Value
df['AOV'] = (df['Monetary'] / df['Frequency']).round(2)

# Define our target: If they haven't bought in 90 days, they are a churn risk (1)
df['Churn'] = df['Recency'].apply(lambda x: 1 if x > 90 else 0)

print("3. Splitting Data...")
# ⚠️ CRITICAL INTERVIEW POINT: We drop 'Recency' from X to prevent "Target Leakage"
X = df[['Frequency', 'Monetary', 'AOV']]
y = df['Churn']

# Split 80% for training, 20% for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("4. Training the Machine Learning Engine...")
# 'balanced' forces it to pay attention to churners. 'max_depth=5' prevents overfitting.
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', max_depth=5)
model.fit(X_train, y_train)

print("\n--- Model Evaluation ---")
predictions = model.predict(X_test)
print(classification_report(y_test, predictions))

print("\n--- Key Business Drivers for Churn ---")
# Extract Feature Importance to tell the business WHY people are leaving
feature_importances = pd.DataFrame(model.feature_importances_, index=X.columns, columns=['Importance']).sort_values('Importance', ascending=False)
for index, row in feature_importances.iterrows():
    print(f"{index}: {row['Importance']:.1%}")

print("\n5. Running Live Prediction Scenario...")
# REAL-WORLD SCENARIO: A "Loyal" tier customer who buys often (12 purchases), 
# has spent a good amount ($1,850 total), making their AOV ~$154.
new_customer = pd.DataFrame({'Frequency': [12], 'Monetary': [1850.00], 'AOV': [154.16]})

# Get the exact probability of churn
churn_prob = model.predict_proba(new_customer)[0][1]

print(f"Customer Profile: 12 Purchases, $1,850 Total Spend, $154 AOV")
print(f"Predicted Churn Probability: {churn_prob:.1%}")
if churn_prob > 0.50:
    print("⚠️ WARNING: High Churn Risk. Trigger retention workflow.")
else:
    print("✅ SAFE: Customer behavior is stable.")