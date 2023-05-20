import sys
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split

cat_feature_names=["Equipment","Energy efficiency class", "Location"]

def pred(loss, X_test):
    loaded_model1 = CatBoostRegressor(
        cat_features=cat_feature_names,
        loss_function=loss,
    )
    # add the full path of your model
    model_path = f"./resources/python/{loss}"
    loaded_model1.load_model(model_path)

    y_pred = loaded_model1.predict(X_test)

    return y_pred


def main(file_name):
    if file_name is None:
        print("No string parameter provided.")
        sys.exit(1)
    # Load the CSV file
    data = pd.read_csv(file_name, dtype={"Location": int, "Energy efficiency class": str, "Equipment": int})
    data["Energy efficiency class"] = data["Energy efficiency class"].astype(str).dropna()
    data = pd.DataFrame([data.iloc[0]])

    y_predRMSE = pred("RMSE", data)
    y_predHuber = pred("Huber_delta=10000000", data)

    return [y_predRMSE[0], y_predHuber[0]]