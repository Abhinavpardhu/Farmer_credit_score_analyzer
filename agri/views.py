from django.shortcuts import render
import os
import sys

# Create your views here.

def index(request):
   
    return render(request, "index.html")

def predict(request):
    if request.method == "POST":
        import joblib
        import pandas as pd
        
        # Extract form data from POST request
        age = request.POST.get('age')
        land_area = request.POST.get('land_area')
        soil_type = request.POST.get('soil_type')
        sunlight_hours = request.POST.get('sunlight_hours')
        water_freq = request.POST.get('water_freq')
        fertilizer_type = request.POST.get('fertilizer_type')
        temperature = request.POST.get('temperature')
        humidity = request.POST.get('humidity')
        past_loan_status = request.POST.get('past_loan_status')
        income = request.POST.get('income')
        loan_amount_requested = request.POST.get('loan_amount_requested')
        
        # Debug: Print received data
        print(f"DEBUG: Received data - Age: {age}, Land: {land_area}, Soil: {soil_type}")
        
        # Convert numeric values to appropriate types
        try:
            age = float(age) if age else None
            land_area = float(land_area) if land_area else None
            sunlight_hours = float(sunlight_hours) if sunlight_hours else None
            temperature = float(temperature) if temperature else None
            humidity = float(humidity) if humidity else None
            income = float(income) if income else None
            loan_amount_requested = float(loan_amount_requested) if loan_amount_requested else None
        except ValueError as ve:
            print(f"DEBUG: ValueError during conversion - {str(ve)}")
            return render(request, "pre.html", {"error": "Invalid input values. Please enter valid numbers."})
        
        try:
            # Create a DataFrame with the input data
            input_data = pd.DataFrame({
                'Age': [age],
                'Land_Area': [land_area],
                'Soil_Type': [soil_type],
                'Sunlight_Hours': [sunlight_hours],
                'Water_Freq': [water_freq],
                'Fertilizer_Type': [fertilizer_type],
                'Temperature': [temperature],
                'Humidity': [humidity],
                'Past_Loan_Status': [past_loan_status],
                'Income': [income],
                'Loan_Amount_Requested': [loan_amount_requested]
            })
            
            print(f"DEBUG: Created DataFrame with shape {input_data.shape}")
            print(f"DEBUG: DataFrame columns: {list(input_data.columns)}")

            # One-hot encode categorical columns (same as training)
            # Note: Water_Freq was NOT part of training data, so drop it
            input_data = input_data.drop('Water_Freq', axis=1)
            print(f"DEBUG: After dropping Water_Freq: {list(input_data.columns)}")
            
            input_data = pd.get_dummies(input_data, columns=['Soil_Type', 'Fertilizer_Type', 'Past_Loan_Status'])
            print(f"DEBUG: After one-hot encoding: {list(input_data.columns)}")

            # Load the model
            model_path = os.path.join(os.path.dirname(__file__), 'loan_model.joblib')
            print(f"DEBUG: Model path: {model_path}")
            print(f"DEBUG: Model exists: {os.path.exists(model_path)}")
            
            if not os.path.exists(model_path):
                return render(request, "pre.html", {"error": "Model file not found. Please contact support."})
            
            model = joblib.load(model_path)
            print(f"DEBUG: Model loaded successfully")

            # Try predicting; if columns mismatch, attempt to align with model's expected features
            try:
                prediction = model.predict(input_data)[0]
                print(f"DEBUG: Prediction successful: {prediction}")
            except Exception as pred_err:
                print(f"DEBUG: Prediction error: {str(pred_err)}")
                # If model exposes feature names, reindex to match (fill missing with 0)
                if hasattr(model, 'feature_names_in_'):
                    expected = list(model.feature_names_in_)
                    print(f"DEBUG: Model expected features: {expected}")
                    print(f"DEBUG: Input features: {list(input_data.columns)}")
                    input_data = input_data.reindex(columns=expected, fill_value=0)
                    prediction = model.predict(input_data)[0]
                    print(f"DEBUG: Prediction after reindexing: {prediction}")
                else:
                    # As a last resort, try to reindex using columns saved alongside the model
                    cols_path = os.path.join(os.path.dirname(__file__), 'model_columns.json')
                    if os.path.exists(cols_path):
                        import json
                        with open(cols_path, 'r') as f:
                            expected = json.load(f)
                        print(f"DEBUG: Expected columns from JSON: {expected}")
                        input_data = input_data.reindex(columns=expected, fill_value=0)
                        prediction = model.predict(input_data)[0]
                        print(f"DEBUG: Prediction after JSON reindex: {prediction}")
                    else:
                        print(f"DEBUG: No model_columns.json found")
                        raise pred_err

            result = "Approved" if int(prediction) == 1 else "Rejected"
            
            print(f"DEBUG: Final result: {result}, Raw prediction: {prediction}")

            return render(request, "pre.html", {"result": result, "prediction": prediction, "raw_prediction": float(prediction)})

        except Exception as e:
            print(f"DEBUG: Exception caught - {str(e)}")
            import traceback
            traceback.print_exc()
            return render(request, "pre.html", {"error": f"Prediction error: {str(e)}"})
   
    return render(request, "pre.html")