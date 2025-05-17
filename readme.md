
# emr


## Table of Contents
- [Installation](#installation)
- [Swagger Documentation](#swagger-documentation)
- [Redoc Doumentation](#redoc-documentation)


## Installation
1. Clone the repository:
   ```bash
   git clone <repository url>
   cd yourproject
   ```

2. Create and activate a virtual environment:
    ```
    python3.10 -m venv venv
    source <path to virtual env>/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run migrations:
    ```
    python manage.py migrate
    ```

5. Create a superuser:
    ```
    python manage.py createsuperuser
    ```

8. To Run celery (from project root and with virtual env activated)
    ```
    python3 -m celery -A emr -l INFO
    ```

        ```

9. Run the server:
    ```
    python manage.py runserver
    ```
    Or using gunicorn,
    ```
    gunicorn -c gunicorn.conf.py emr.wsgi:application
    ```


Access the admin panel at http://localhost:8000/{{ADMIN_PANEL_URL}}/.

Here ```ADMIN_PANEL_URL``` is the url specified in the .env file



## Swagger Documentation

You can access the documentation at [swagger](http://{{API-URL}}/swagger/)

## Redoc Documentation

You can access the redoc docs i.e more advance docs of the application with each details. [redoc](http://{{API-URL}}/redoc/)
