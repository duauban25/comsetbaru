#!/bin/zsh

# Path project dan virtualenv
PROJECT="/Users/baktanarta/Documents/numerology"
VENV="$PROJECT/venv"
PYTHON="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
LOG_OUT="$PROJECT/run.log"
LOG_ERR="$PROJECT/error.log"

cd "$PROJECT" || exit 1

# Buat virtualenv jika belum ada
if [ ! -d "$VENV" ]; then
  echo "Creating virtualenv at $VENV" | tee -a "$LOG_OUT"
  "$PYTHON" -m venv "$VENV"
fi

VENV_PY="$VENV/bin/python"
VENV_PIP="$VENV/bin/pip"

# Upgrade pip dan install requirements
"$VENV_PY" -m pip install --upgrade pip setuptools wheel >> "$LOG_OUT" 2>> "$LOG_ERR" || true

if [ -f "requirements.txt" ]; then
  echo "Installing/updating requirements..." | tee -a "$LOG_OUT"
  "$VENV_PIP" install -r requirements.txt >> "$LOG_OUT" 2>> "$LOG_ERR"
fi

# Jalankan Streamlit di mode GUI (tanpa terminal)
"$VENV_PY" -m streamlit run app.py --server.port=8501 --server.headless=false >> "$LOG_OUT" 2>> "$LOG_ERR" &
