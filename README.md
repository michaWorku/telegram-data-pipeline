# **Telegram Medical Business Data Pipeline**

## **Table of Contents**

- [Project Description](#project-description)
- [Business Understanding](#business-understanding)
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Business Objectives](#business-objectives)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Live Demo](#live-demo)
- [Development and Evaluation](#development-and-evaluation)
- [Contributing](#contributing)
- [License](#license)

## **Project Description**

This project develops an end-to-end data pipeline to extract, transform, and analyze data from public Telegram channels focusing on Ethiopian medical businesses. The pipeline is designed to provide actionable insights into medical product trends, pricing, visual content, and posting activities, supporting data-driven decision-making for Kara Solutions.

## **Business Understanding**

Kara Solutions, a leading data science company, aims to build a robust data platform to generate insights about Ethiopian medical businesses. This platform will leverage data scraped from public Telegram channels to answer critical business questions and enhance data analysis capabilities. The implementation of a modern ELT (Extract, Load, Transform) framework ensures data reliability, scalability, and readiness for analysis.

## **Project Overview**

The core of this project is an ELT data pipeline that processes raw Telegram data, transforms it into an analytical-ready format, enriches it with computer vision, and exposes the insights via an API.

- **Extract:** Raw data (messages and images) is scraped from public Telegram channels.
- **Load:** Unaltered raw data is stored in a data lake and then loaded into a PostgreSQL data warehouse.
- **Transform:** Data is cleaned, validated, and remodeled into a dimensional star schema using dbt.
- **Enrich:** Images are processed using YOLOv8 for object detection, and the results are integrated into the data warehouse.
- **Expose:** Final analytical data is made accessible through a FastAPI-based analytical API.
- **Orchestrate:** The entire pipeline is orchestrated using Dagster for reproducibility, observability, and scheduling.

## **Key Features**

- **Automated Data Scraping:** Extracts messages and images from specified Telegram channels.
- **Robust Data Lake:** Stores raw, immutable data for auditing and re-processing.
- **Dimensional Data Warehouse:** Implements a star schema in PostgreSQL for efficient analytical queries.
- **dbt-powered Transformations:** Ensures data quality, consistency, and modularity in data modeling.
- **AI-driven Data Enrichment:** Utilizes YOLOv8 for object detection on images, linking visual content to textual data.
- **Analytical API:** Provides structured access to key business insights via FastAPI endpoints.
- **Pipeline Orchestration:** Manages and schedules the entire data workflow using Dagster, ensuring reliability and monitoring.
- **Containerized Environment:** Uses Docker and Docker Compose for a reproducible and portable development and deployment environment.

## **Business Objectives**

The pipeline is designed to answer key business questions, including:

- Identifying the top 10 most frequently mentioned medical products or drugs across all channels.
- Analyzing price and availability variations of specific products across different channels.
- Determining which channels have the most visual content (e.g., images of pills vs. creams).
- Tracking daily and weekly trends in posting volume for health-related topics.

## **Project Structure**

The project follows a modular and organized structure to facilitate development, testing, and deployment.

```
telegram-data-pipeline/
├── .env.example              # Template for environment variables (secrets like API keys, DB credentials).
├── .gitignore                # Specifies files and directories to be ignored by Git (e.g., .env, __pycache__, data/).
├── Dockerfile                # Defines the Docker image for the Python application, including dependencies.
├── docker-compose.yml        # Orchestrates Docker containers (application, PostgreSQL database, etc.).
├── README.md                 # This file: Comprehensive project overview, setup, and usage guide.
├── requirements.txt          # Lists all Python dependencies required for the project.
├── pyproject.toml            # Modern Python packaging configuration (PEP 517/621) for project metadata and build system.
├── Makefile                  # Defines common development tasks (e.g., setup, test, lint, clean).
├── .env                      # Environment variables (e.g., API keys, database credentials) - kept out of Git.
├── src/                      # Core source code for the project's main logic.
│   ├── __init__.py           # Marks src as a Python package.
│   ├── core/                 # Core logic and foundational components of the application.
│   ├── models/               # Data models, ORM definitions, and potentially ML models.
│   ├── utils/                # Utility functions and helper classes used across the project.
│   ├── services/             # Business logic and service layer implementations.
│   ├── dbt/                  # dbt project for data transformation and modeling.
│   │   ├── models/           # SQL models defining staging and data mart tables.
│   │   │   ├── staging/      # Intermediate models for cleaning and light restructuring of raw data.
│   │   │   └── marts/        # Final analytical models (fact and dimension tables in star schema).
│   │   ├── tests/            # Custom and generic dbt tests for data quality and integrity.
│   │   └── dbt_project.yml   # dbt project configuration, defining connections and model paths.
│   ├── api/                  # FastAPI application for exposing analytical insights.
│   │   ├── main.py           # Main FastAPI application entry point, defining API routes.
│   │   ├── database.py       # Handles database connection and session management for FastAPI.
│   │   ├── models.py         # Pydantic models for defining API request/response schemas and data validation.
│   │   └── crud.py           # Contains functions for interacting with the database to retrieve analytical data.
│   └── dagster/              # Dagster definitions for pipeline orchestration.
│       ├── definitions.py    # Defines Dagster jobs, ops (individual pipeline steps), and schedules.
│       └── __init__.py       # Marks the directory as a Python package.
├── tests/                    # Test suite for the project.
│   ├── unit/                 # Unit tests for individual components and functions.
│   └── integration/          # Integration tests for combined components and system flows.
├── notebooks/                # Jupyter notebooks for experimentation, Exploratory Data Analysis (EDA), and prototyping.
├── scripts/                  # Standalone Python scripts for various pipeline stages.
│   ├── scrape_telegram.py    # Script to extract messages and images from Telegram channels.
│   ├── load_to_postgres.py   # Script to load raw data from the data lake into PostgreSQL.
│   └── enrich_data.py        # Script for running YOLOv8 object detection on images and storing results.
├── docs/                     # Project documentation (e.g., Sphinx docs, design documents).
├── data/                     # Data storage directory.
│   ├── raw/                  # Original, immutable raw data (e.g., scraped Telegram messages and images).
│   └── processed/            # Transformed, cleaned, or feature-engineered data.
├── config/                   # Configuration files for various parts of the application.
└── examples/                 # Example usage of the project components or features.

```

## **Technologies Used**

- **Orchestration:** Dagster
- **Containerization:** Docker, Docker Compose
- **Data Extraction:** Telethon (Telegram API)
- **Data Storage:** PostgreSQL (Data Warehouse), Local File System (Data Lake)
- **Data Transformation:** dbt (Data Build Tool)
- **Data Enrichment:** YOLOv8 (Object Detection)
- **API Development:** FastAPI
- **Dependency Management:** `requirements.txt`, `python-dotenv`
- **Version Control:** Git

## **Setup and Installation**

### **Prerequisites**

- Docker Desktop (or Docker Engine & Docker Compose installed)
- Git

### **Steps**

1. Clone the Repository:
    
    If you haven't already, clone the project repository:
    
    ```
    git clone https://github.com/michaWorku/telegram-data-pipeline.git
    
    ```
    cd telegram-data-pipeline
    
    ```
    
    *(If you used the `create_project_structure.py` script, you'll already be in the correct directory.)*
    
2. Configure Environment Variables:
    
    Rename the example environment file and fill in your credentials. This file will not be committed to Git.
    
    ```
    cp .env.example .env
    
    ```
    
    Open the newly created `.env` file and replace the placeholder values with your actual Telegram API credentials (obtained from [my.telegram.org](https://my.telegram.org/)) and your desired PostgreSQL database credentials:
    
    ```
    # Telegram API Credentials (from my.telegram.org)
    TELEGRAM_API_ID=YOUR_TELEGRAM_API_ID
    TELEGRAM_API_HASH=YOUR_TELEGRAM_API_HASH
    
    # PostgreSQL Database Credentials
    POSTGRES_USER=your_db_user
    POSTGRES_PASSWORD=your_db_password
    POSTGRES_DB=telegram_analytics_db
    POSTGRES_HOST=db # 'db' when running inside Docker Compose network
    POSTGRES_PORT=5432
    
    ```
    
3. Build and Run Docker Containers:
    
    This command will build the Docker images for your application and PostgreSQL database, and then start them as background services.
    
    ```
    docker-compose up --build -d
    
    ```
    
    - `-build`: Rebuilds images if changes are detected in `Dockerfile` or `docker-compose.yml`.
    - `d`: Runs containers in detached mode (in the background).
4. Access the Application Container:
    
    To execute commands within your application's environment (e.g., run scripts, dbt commands, start FastAPI), you can access its shell:
    
    ```
    docker-compose exec app bash
    
    ```
    
    Once inside the container, you will be in the `/app` directory, which is mapped to your local project root.
    

## **Usage**

After setting up the environment, you can manually run individual pipeline components for testing or use Dagster for orchestrated runs.

### **Manual Execution (for Development/Testing)**

From inside the `telegram_pipeline_app` container (`docker-compose exec app bash`):

- **Scrape Telegram Data:**
    
    ```
    python scripts/scrape_telegram.py
    
    ```
    
- **Load Raw Data to PostgreSQL:**
    
    ```
    python scripts/load_to_postgres.py
    
    ```
    
- Run dbt Transformations:
    
    Navigate to the dbt project directory and execute dbt commands:
    
    ```
    cd src/dbt # Navigate to the dbt project within src/
    dbt debug          # Verify database connection
    dbt seed           # If you have static data seed files
    dbt run            # Execute all dbt models (staging and marts)
    dbt test           # Run all defined data tests
    dbt docs generate  # Generate project documentation
    dbt docs serve     # Serve the documentation locally (accessible via host port 8000 if mapped)
    cd ../.. # Go back to /app
    
    ```
    
- **Enrich Data with YOLOv8:**
    
    ```
    python scripts/enrich_data.py
    
    ```
    
- **Start FastAPI Analytical API:**
    
    ```
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    
    ```
    
    The API will be accessible from your host machine at `http://localhost:8000` (or the port you've mapped in `docker-compose.yml`). You can explore the API documentation at `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc`.
    

### **Orchestrated Execution (Dagster)**

To run the full pipeline and monitor its execution using Dagster:

1. Launch Dagster UI:
    
    From your project root on the host machine (or inside the container, ensuring ports are mapped correctly):
    
    ```
    dagster dev -f src/dagster/definitions.py # Specify the path to Dagster definitions within src/
    
    ```
    
    Access the Dagster UI (Dagit) in your web browser at `http://localhost:3000` (or the port specified by Dagster). From here, you can view your defined jobs, launch runs, and monitor their status.
    
2. Define Schedules:
    
    Within src/dagster/definitions.py, you can define schedules to automate pipeline runs (e.g., daily, weekly).
    

## **Live Demo**

*(This section is a placeholder for a future live demo link or instructions once deployed.)*

## **Development and Evaluation**

This project emphasizes best practices in data engineering, including:

- **Reproducibility:** Achieved through Docker and `requirements.txt`.
- **Data Quality:** Ensured by dbt testing and validation.
- **Scalability:** Designed with layered data architecture and modular components.
- **Observability:** Provided by Dagster's UI and logging.
- **Security:** Adherence to secrets management best practices.

## **Contributing**

We welcome contributions to this project! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes and ensure tests pass.
4. Commit your changes (`git commit -m 'feat: Add new feature'`).
5. Push to the branch (`git push origin feature/your-feature-name`).
6. Open a Pull Request.

## **License**

This project is licensed under the [MIT License](https://www.google.com/search?q=LICENSE).