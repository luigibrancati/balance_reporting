mkdir -p ~/.streamlit/echo "\
[server]\n\
headless = false\n\
address = 0.0.0.0\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml