from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

def calculate_ckd_stage(gfr):
    """Determine CKD stage based on GFR value."""
    if gfr >= 90:
        return 1, "Stage 1", "Kidney damage with normal or high GFR", "#22c55e"
    elif gfr >= 60:
        return 2, "Stage 2", "Kidney damage with mildly decreased GFR", "#84cc16"
    elif gfr >= 45:
        return 3, "Stage 3a", "Mildly to moderately decreased kidney function", "#eab308"
    elif gfr >= 30:
        return 3, "Stage 3b", "Moderately to severely decreased kidney function", "#f97316"
    elif gfr >= 15:
        return 4, "Stage 4", "Severely decreased kidney function", "#ef4444"
    else:
        return 5, "Stage 5", "Kidney failure (End-Stage Renal Disease)", "#7f1d1d"

def analyze_parameters(data):
    alerts = []
    risk_score = 0

    blood_urea = float(data['blood_urea'])
    creatinine = float(data['creatinine'])
    hemoglobin = float(data['hemoglobin'])
    gfr = float(data['gfr'])
    systolic_bp = float(data['systolic_bp'])
    diastolic_bp = float(data['diastolic_bp'])
    sodium = float(data['sodium'])
    gender = data['gender']
    age = int(data['age'])

    # Blood Urea Analysis (normal: 7-20 mg/dL)
    if blood_urea > 40:
        alerts.append({"param": "Blood Urea", "value": f"{blood_urea} mg/dL", "status": "critical", "msg": "Severely elevated - indicates poor kidney filtration"})
        risk_score += 3
    elif blood_urea > 20:
        alerts.append({"param": "Blood Urea", "value": f"{blood_urea} mg/dL", "status": "warning", "msg": "Elevated - above normal range (7-20 mg/dL)"})
        risk_score += 1
    else:
        alerts.append({"param": "Blood Urea", "value": f"{blood_urea} mg/dL", "status": "normal", "msg": "Within normal range"})

    # Serum Creatinine Analysis
    normal_cr = (0.6, 1.1) if gender == 'female' else (0.7, 1.3)
    if creatinine > normal_cr[1] * 3:
        alerts.append({"param": "Serum Creatinine", "value": f"{creatinine} mg/dL", "status": "critical", "msg": "Critically elevated - severe kidney dysfunction"})
        risk_score += 3
    elif creatinine > normal_cr[1]:
        alerts.append({"param": "Serum Creatinine", "value": f"{creatinine} mg/dL", "status": "warning", "msg": f"Elevated - normal range is {normal_cr[0]}-{normal_cr[1]} mg/dL"})
        risk_score += 2
    else:
        alerts.append({"param": "Serum Creatinine", "value": f"{creatinine} mg/dL", "status": "normal", "msg": "Within normal range"})

    # Hemoglobin Analysis
    normal_hb = (12.0, 16.0) if gender == 'female' else (13.5, 17.5)
    if hemoglobin < normal_hb[0] - 3:
        alerts.append({"param": "Hemoglobin", "value": f"{hemoglobin} g/dL", "status": "critical", "msg": "Severely low - renal anemia likely"})
        risk_score += 2
    elif hemoglobin < normal_hb[0]:
        alerts.append({"param": "Hemoglobin", "value": f"{hemoglobin} g/dL", "status": "warning", "msg": f"Low - normal range is {normal_hb[0]}-{normal_hb[1]} g/dL"})
        risk_score += 1
    else:
        alerts.append({"param": "Hemoglobin", "value": f"{hemoglobin} g/dL", "status": "normal", "msg": "Within normal range"})

    # GFR Analysis
    if gfr < 15:
        alerts.append({"param": "GFR", "value": f"{gfr} mL/min", "status": "critical", "msg": "Kidney failure - immediate medical attention required"})
        risk_score += 5
    elif gfr < 60:
        alerts.append({"param": "GFR", "value": f"{gfr} mL/min", "status": "warning", "msg": "Reduced filtration rate - kidney function impaired"})
        risk_score += 3
    else:
        alerts.append({"param": "GFR", "value": f"{gfr} mL/min", "status": "normal", "msg": "Adequate kidney filtration"})

    # Blood Pressure Analysis
    if systolic_bp >= 180 or diastolic_bp >= 120:
        alerts.append({"param": "Blood Pressure", "value": f"{systolic_bp}/{diastolic_bp} mmHg", "status": "critical", "msg": "Hypertensive crisis - extremely dangerous"})
        risk_score += 3
    elif systolic_bp >= 140 or diastolic_bp >= 90:
        alerts.append({"param": "Blood Pressure", "value": f"{systolic_bp}/{diastolic_bp} mmHg", "status": "warning", "msg": "High BP - worsens kidney damage"})
        risk_score += 2
    else:
        alerts.append({"param": "Blood Pressure", "value": f"{systolic_bp}/{diastolic_bp} mmHg", "status": "normal", "msg": "Normal range"})

    # Sodium Analysis (normal: 135-145 mEq/L)
    if sodium < 125 or sodium > 155:
        alerts.append({"param": "Sodium", "value": f"{sodium} mEq/L", "status": "critical", "msg": "Critical electrolyte imbalance"})
        risk_score += 2
    elif sodium < 135 or sodium > 145:
        alerts.append({"param": "Sodium", "value": f"{sodium} mEq/L", "status": "warning", "msg": "Mild electrolyte imbalance - normal is 135-145 mEq/L"})
        risk_score += 1
    else:
        alerts.append({"param": "Sodium", "value": f"{sodium} mEq/L", "status": "normal", "msg": "Within normal range"})

    stage_num, stage_name, stage_desc, stage_color = calculate_ckd_stage(gfr)

    recommendations = get_recommendations(stage_num, risk_score)

    return {
        "stage_num": stage_num,
        "stage_name": stage_name,
        "stage_desc": stage_desc,
        "stage_color": stage_color,
        "risk_score": risk_score,
        "alerts": alerts,
        "recommendations": recommendations,
        "gfr": gfr
    }

def get_recommendations(stage, risk_score):
    base = [
        "Stay well hydrated unless advised otherwise by your doctor",
        "Monitor blood pressure regularly",
        "Follow a kidney-friendly diet low in sodium and phosphorus",
        "Avoid NSAIDs and nephrotoxic medications",
        "Schedule regular kidney function tests"
    ]
    if stage >= 3:
        base = [
            "Consult a nephrologist immediately",
            "Strict dietary protein restriction",
            "Tight blood pressure control (target <130/80 mmHg)",
            "Monitor potassium, phosphorus, and calcium levels",
            "Evaluate for dialysis or transplant planning (Stage 4-5)"
        ] + base[:2]
    elif stage == 2:
        base = ["Increase frequency of kidney function monitoring"] + base
    return base[:5]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    result = analyze_parameters(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
