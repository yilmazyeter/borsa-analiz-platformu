#!/bin/bash
mkdir -p ~/.streamlit/

echo "\
[global]
developmentMode = false

[server]
headless = true
port = \$PORT
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
" > ~/.streamlit/config.toml 