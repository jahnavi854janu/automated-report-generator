import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create sample sales data
np.random.seed(42)

# Generate dates
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=x) for x in range(100)]

# Generate sample data
data = {
    'Date': dates,
    'Product': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'], 100),
    'Sales': np.random.randint(10, 100, 100),
    'Revenue': np.random.uniform(1000, 50000, 100).round(2),
    'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
    'Customer_Rating': np.random.uniform(3.5, 5.0, 100).round(1)
}

df = pd.DataFrame(data)

# Add some missing values intentionally
df.loc[5:7, 'Customer_Rating'] = np.nan
df.loc[15:17, 'Revenue'] = np.nan

# Save to CSV
df.to_csv('sample_sales_data.csv', index=False)
print("✅ Sample data created: sample_sales_data.csv")
print(f"   - {len(df)} rows")
print(f"   - {len(df.columns)} columns")
print(f"\n📊 Preview:")
print(df.head())