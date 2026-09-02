## 🚀 Instrucciones de Ejecución

Sigue estos pasos para instalar y ejecutar el proyecto en tu máquina local:

### 1. Clonar el repositorio

git clone [https://github.com/n1g0h/Biblioteca-django.git](https://github.com/n1g0h/Biblioteca-django.git)

cd Biblioteca-django


### 2. Crear y activar el entorno virtual. (PowerShell)

python -m venv venv
\venv\Scripts\activate

### 3. Instalar dependencias

  pip install django

### 4.Generar la base de datos local

  python manage.py migrate

### 5. Crear usuario administrador
  python manage.py createsuperuser

### 6. Iniciar el servidor
  python manage.py runserver

