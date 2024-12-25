# AML/CTF Compliance Platform Code Documentation

## Project Structure
```
├── .streamlit
│   └── config.toml
├── utils
│   ├── ai_analyzer.py
│   ├── ocr_processor.py
│   ├── risk_visualization.py
│   ├── templates.py
│   ├── training_module.py
│   ├── visualization.py
│   ├── data_processor.py
│   ├── report_generator.py
│   └── transaction_monitor.py
└── main.py
```

## Main Application (main.py)
```python
${cat main.py}
```

## Utility Modules

### AI Analyzer (utils/ai_analyzer.py)
```python
${cat utils/ai_analyzer.py}
```

### Risk Visualization (utils/risk_visualization.py)
```python
${cat utils/risk_visualization.py}
```

### Visualization (utils/visualization.py)
```python
${cat utils/visualization.py}
```

### Training Module (utils/training_module.py)
```python
${cat utils/training_module.py}
```

### Templates (utils/templates.py)
```python
${cat utils/templates.py}
```

### OCR Processor (utils/ocr_processor.py)
```python
${cat utils/ocr_processor.py}
```

## Configuration Files

### Streamlit Config (.streamlit/config.toml)
```toml
${cat .streamlit/config.toml}
```

## Running the Application

1. Install dependencies:
```bash
pip install streamlit pandas plotly numpy openai pytesseract opencv-python-headless
```

2. Start the application:
```bash
streamlit run main.py
```

The application will be accessible at http://0.0.0.0:5000

## Features
1. Enhanced Customer Due Diligence (ECDD) Report Generator
2. Transaction Monitoring with AI Analysis
3. Suspicious Matter Report Generator
4. Interactive Compliance Training
5. Risk Visualization Dashboard
6. Export Customization Wizard

## Dependencies
- streamlit
- pandas
- plotly
- numpy
- openai
- pytesseract
- opencv-python-headless
