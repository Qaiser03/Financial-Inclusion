# Virtual Environment Setup

A virtual environment named **"Financial Inclusion"** has been created with all project dependencies installed.

## Quick Start

### Windows (Command Prompt or PowerShell)
```cmd
activate_venv.bat
```

### Windows (Git Bash) or Linux/Mac
```bash
source activate_venv.sh
```

### Manual Activation

**Windows:**
```cmd
"Financial Inclusion\Scripts\activate"
```

**Linux/Mac:**
```bash
source "Financial Inclusion/bin/activate"
```

## Verify Installation

After activation, verify everything works:

```bash
# Check Python version
python --version

# Run tests
python -m pytest tests/ -v

# Run the pipeline
python -m src.run_pipeline --config docs/PARAMETERS.yml
```

## Installed Packages

All dependencies from `requirements.txt` are installed:
- **Data Processing**: pandas, numpy, openpyxl
- **Text Analysis**: nltk, scikit-learn, unicodedata2
- **Visualization**: matplotlib, wordcloud, networkx
- **Statistics**: scipy, statsmodels
- **Configuration**: pyyaml
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, flake8

Run `pip list` to see all installed packages and versions.

## Deactivate

To exit the virtual environment:
```bash
deactivate
```

## Reinstalling Dependencies

If you need to reinstall or update dependencies:
```bash
python -m pip install -r requirements.txt --upgrade
```
