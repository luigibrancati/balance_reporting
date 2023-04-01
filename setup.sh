mkdir -p ~/.streamlit/
mkdir -p ~/.streamlit/data
echo "[server]
headless = true
address = '0.0.0.0'
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml