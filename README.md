# Recipe-Management-System
A recipe management web app built with Flask and SQL as part of a DBMS course. Features user authentication, recipe categorization, admin controls, and responsive UI. Allows users to browse, add, and manage recipes with image support and profile management.

## Features
- User authentication (login/signup)
- Browse recipes by category (Veg/Non-Veg)
- Add, edit, and delete recipes (admin)
- Manage users and categories (admin)
- User profile management
- Responsive UI with images for each recipe

## Project Structure
- `app.py` : Main Flask application
- `recipesdb.sql` : SQL file for database schema
- `static/` : Static files (CSS, images)
- `templates/` : HTML templates for the web app

## How to Run
1. Install Python and required packages (Flask, etc.)
2. Set up the database using `recipesdb.sql`
3. Run the app:
   ```
   python app.py
   ```
4. Open your browser and go to `http://localhost:5000`

