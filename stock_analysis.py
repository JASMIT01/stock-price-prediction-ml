# ================================
# STOCK PRICE PREDICTION PROJECT
# ================================

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error



# 1️⃣ Download stock data
stock_symbol = "AAPL"   # You can change to TCS.NS, RELIANCE.NS etc.
data = yf.download(stock_symbol, start="2015-01-01", end="2025-01-01")

# 2️⃣ Use only Close price
data = data[['Close']]
data.dropna(inplace=True)

# 3️⃣ Create prediction column (future 30 days)
future_days = 30
data['Prediction'] = data['Close'].shift(-future_days)

# 4️⃣ Feature & Label
X = np.array(data.drop(['Prediction'], axis=1))[:-future_days]
y = np.array(data['Prediction'])[:-future_days]

# 5️⃣ Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 6️⃣ Train ML Model
model = LinearRegression()
model.fit(X_train, y_train)

# 7️⃣ Model Evaluation
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

print("Model Evaluation:")
print("Mean Absolute Error:", mae)
print("Root Mean Squared Error:", rmse)

# 8️⃣ Predict future prices
future_prices = model.predict(
    np.array(data.drop(['Prediction'], axis=1))[-future_days:]
)

# 9️⃣ Plot results
plt.figure(figsize=(12,6))
plt.plot(data['Close'], label="Actual Price")
plt.plot(
    range(len(data)-future_days, len(data)),
    future_prices,
    label="Predicted Price",
    color='red'
)
plt.title(f"{stock_symbol} Stock Price Prediction")
plt.xlabel("Days")
plt.ylabel("Price")
plt.legend()
plt.show(block=False)
input("Press ENTER to close the graph...")


