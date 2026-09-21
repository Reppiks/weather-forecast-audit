# 🌤️ Streamlit Weather Analysis & GEM Accuracy Dashboard

A high-performance, compact Streamlit application designed to evaluate Canadian Meteorological Centre (GEM) forecast model accuracy against ground-truth observational weather data.

Built with a modern, dense layout designed for real-time forecast audit transparency and multi-metric visual inspection.

---

## ✨ Key Features

- **7-Day Historical Variance Analysis**: Dual-axis visualization comparing real-time ground observations against GEM model predictions for temperature and precipitation.
- **Audit-First Data Integrity**: Full precipitation dataset retention (including explicit `0.00 in` values) ensuring absolute transparency during hover inspections.
- **Dense Overlay Visualization**: Zero-compression `barmode="overlay"` Plotly chart layer rendering 168 hours of dual-metric time-series data without bar-splitting or distortion.
- **Pixel-Aligned UI Badges**: Custom-rendered SVG moon phase and WMO weather condition badges built with shared CSS box-models and native `st.markdown` for unified rendering heights.
- **High-Performance Async Pipeline**: Asynchronous data retrieval powered by `httpx` with `pandas` naive-datetime normalization for precise hourly `inner` join alignment.

---

## 🛠️ Tech Stack & Tooling

- **Application Framework**: [Streamlit](https://streamlit.io/)
- **Data Plotting**: [Plotly Python](https://plotly.com/python/)
- **Data Engineering**: [pandas](https://pandas.pydata.org/)
- **HTTP Client**: [httpx](https://www.python-httpx.org/)
- **Package & Environment Management**: [uv](https://github.com/astral-sh/uv)
- **Task Runner**: [Poe the Poet](https://github.com/nat-n/poethepoet)
- **Linter & Formatter**: [Ruff](https://github.com/astral-sh/ruff)

---
