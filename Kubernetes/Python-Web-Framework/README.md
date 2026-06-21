# Python Web Frameworks Overview

### 🏢 Heavy Enterprise / Production Standards
* **Django**
    * *Intro:* "Batteries-included" full-stack framework with built-in ORM, admin panel, and auth.
    * *Production Usage:* **Extremely High** (Instagram, Pinterest, Reddit). Use when scaling to large, database-driven applications.
* **Flask**
    * *Intro:* Minimalist, lightweight micro-framework giving full control over routing and layout.
    * *Production Usage:* **Extremely High** (Netflix, Airbnb microservices). Perfect for clean, custom web services and simple single-page apps.
* **FastAPI**
    * *Intro:* Modern, high-performance framework built on asynchronous Python (`async/await`) with automatic data validation.
    * *Production Usage:* **High & Growing** (Modern APIs, AI/ML deployments). Best choice for pure speed and interactive documentation.

### 📊 Data & Browser-Centric Options
* **Streamlit**
    * *Intro:* UI framework that turns Python data scripts into interactive frontends instantly without writing any HTML/CSS.
    * *Production Usage:* **Medium** (Standard for internal corporate tools and data science dashboards, rarely public consumer sites).
* **PyScript**
    * *Intro:* Experimental framework that executes Python code directly inside the client's browser HTML using WebAssembly.
    * *Production Usage:* **Low / Experimental**. No server backend required, but suffers from heavy initial loading times.
