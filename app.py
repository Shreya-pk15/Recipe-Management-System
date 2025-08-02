from flask import Flask, render_template, request, redirect, flash, session, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL connection setup
def get_db_connection():
        conn = mysql.connector.connect(
            host='localhost',
            user='root',  # replace with your MySQL username
            password='shreyapk',  # replace with your MySQL password
            database='recipe_db'
        )
        return conn

# Redirect root URL to the login page
@app.route('/')
def index():
    return redirect('/login')  # Redirect to login page

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Get the database connection
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please try again later.')
            return redirect('/login')

        # Create a cursor to interact with the database
        cur = conn.cursor()

        # Check if the user exists in the database
        cur.execute("SELECT id, password, role FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        conn.close()

        if user:
            # If user exists, check if the password matches
            if user[1] == password:  # Assuming passwords are stored in plain text
                session['user_id'] = user[0]  # Store user ID in session
                session['role'] = user[2]     # Store the user role in session

                # Redirect based on the user's role
                if user[2] == 'admin':
                    return render_template('admin_dashboard.html')
                else:
                    flash('Login successful!')
                    return render_template('home.html')
            else:
                flash('Incorrect password. Please try again.')
                return render_template('login.html')
        else:
            flash('Email not found. Please sign up.')
            return render_template('signup.html')

    return render_template('login.html')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']  # Get the username from the form
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        dob = request.form['dob']
        joined_date = datetime.today()

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # Insert the user into the database, including the username
            cur.execute("INSERT INTO users (username, email, password, phone, dob, joined_date) VALUES (%s, %s, %s, %s, %s, %s)", (username, email, password, phone, dob, joined_date))
            conn.commit()  # Commit the transaction

            flash('Sign up successful! Please log in.')
            return render_template('login.html')
        except mysql.connector.Error as err:
            flash(f'Error: {err}')
            return render_template('signup.html')
        finally:
            cur.close()
            conn.close()

    return render_template('signup.html')

#Home
@app.route('/home')
def home():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)

        # Fetch all recipes for display on the home page
        cursor.execute('SELECT * FROM Recipes')
        recipes = cursor.fetchall()

        cursor.close()
        conn.close()

        # Pass 'recipes' to the template
        return render_template('home.html', recipes=recipes)

#About Us
@app.route('/about')
def about():
    return render_template('about.html')

#Recipe Details
@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)

        # Fetch recipe details
        cursor.execute('SELECT recipeID, recipeName, imageLink, cookingTime, servingSize FROM Recipes WHERE recipeID = %s', (recipe_id,))
        recipe = cursor.fetchone()

        if not recipe:
            flash('Recipe not found')
            return render_template('home.html')

        # Fetch ingredients for the specific recipe
        cursor.execute('''
        SELECT i.ingredientName, ri.quantity
        FROM Ingredients i
        JOIN RecipeIngredients ri ON i.ingredientID = ri.ingredientID
        WHERE ri.recipeID = %s
        ''', (recipe_id,))
        ingredients = cursor.fetchall()

        # Fetch steps
        cursor.execute('SELECT stepNum, description FROM Steps WHERE recipeID = %s ORDER BY stepNum', (recipe_id,))
        steps = cursor.fetchall()

        # Calculate the average rating
        cursor.execute("SELECT AVG(rating) as avg_rating FROM Ratings WHERE recipeID = %s", (recipe_id,))
        average_rating = cursor.fetchone()['avg_rating'] or 0
        average_rating = round(average_rating, 1)

        cursor.close()
        conn.close()

        # Pass recipe, ingredients, and steps to the template
        return render_template('recipes.html', recipe=recipe, ingredients=ingredients, steps=steps, average_rating=average_rating)
    else:
        flash('Error connecting to the database')
        return render_template('home.html')

#Search Recipes
@app.route('/search_recipes', methods=['GET'])
def search_recipes():
    # Get the ingredient parameter from the request
    ingredient = request.args.get('ingredient', '').strip().lower()

    if not ingredient:
        return jsonify([])  # No ingredient provided, return empty response

    # Split the ingredients by commas and remove any leading/trailing whitespace
    ingredients = [ing.strip() for ing in ingredient.split(',')]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Insert a new record into SearchHistory and get the searchID
        user_id = 1  # Replace with actual user ID from session or authentication
        cursor.execute("INSERT INTO SearchHistory (id) VALUES (%s)", (user_id,))
        search_id = cursor.lastrowid  # Get the newly inserted searchID

        # Insert each ingredient into Search_Ingredients
        for ing in ingredients:
            cursor.execute(
                "INSERT INTO Search_Ingredients (searchID, ingredientName) VALUES (%s, %s)",
                (search_id, ing)
            )

        # Build the SQL query to find recipes that contain all specified ingredients
        placeholders = ', '.join(['%s'] * len(ingredients))
        query = f"""
            SELECT r.recipeID, r.recipeName, r.imageLink
            FROM Recipes r
            JOIN RecipeIngredients ri ON r.recipeID = ri.recipeID
            JOIN Ingredients i ON ri.ingredientID = i.ingredientID
            WHERE LOWER(i.ingredientName) IN ({placeholders})
            GROUP BY r.recipeID
            HAVING COUNT(DISTINCT i.ingredientName) >= %s
        """

        # Execute the query with ingredients and the count of unique ingredients to match
        cursor.execute(query, (*ingredients, len(ingredients)))
        recipes = cursor.fetchall()

        # Commit the transaction to save search history and ingredients
        connection.commit()

    except mysql.connector.Error as err:
        print("Database error:", err)  # Log the error for debugging purposes
        connection.rollback()  # Roll back if there is any error
        return jsonify({"error": str(err)}), 500  # Provide the specific error message

    finally:
        cursor.close()
        connection.close()

    # Return the recipe results as JSON
    return jsonify(recipes)

# Route to submit a rating
@app.route('/rate_recipe/<int:recipe_id>', methods=['POST'])
def rate_recipe(recipe_id):
    if 'user_id' not in session:
        flash("You must be logged in to rate a recipe.")
        return redirect('/login')

    user_id = session['user_id']
    rating = int(request.form['rating'])

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user has already rated this recipe
    cursor.execute("SELECT * FROM Ratings WHERE id = %s AND recipeID = %s", (user_id, recipe_id))
    existing_rating = cursor.fetchone()

    if existing_rating:
        # Update the existing rating
        cursor.execute("UPDATE Ratings SET rating = %s, rated_at = %s WHERE id = %s AND recipeID = %s",
                    (rating, datetime.now(), user_id, recipe_id))
        flash("Your rating has been updated.")
    else:
        # Insert a new rating
        cursor.execute("INSERT INTO Ratings (id, recipeID, rating, rated_at) VALUES (%s, %s, %s, %s)",
                    (user_id, recipe_id, rating, datetime.now()))
        flash("Thank you for rating this recipe!")

    conn.commit()
    cursor.close()
    conn.close()

    # Redirect to recipe details
    return redirect(f'/recipe/{recipe_id}')

# Profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        role = session.get('role')

        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch user details from the database
        cursor.execute("SELECT username, dob, phone, email, joined_date, password FROM users WHERE id = %s", (user_id,))
        user_details = cursor.fetchone()

        if request.method == 'POST':
            # Handle password change
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # Verify the old password
            if user_details['password'] != old_password:
                flash('Old password is incorrect!')
                return redirect('/profile')

            # Check if the new passwords match
            if new_password != confirm_password:
                flash('New passwords and Confirm passwords do not match!')
                return redirect('/profile')

            # If old password is correct, update the password
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
            conn.commit()

            flash('Password updated successfully! Please log in again.')

            # Clear the session after password change
            session.clear()
            return redirect('/login')

        cursor.close()
        conn.close()

        # Render the profile template with user details and admin flag
        return render_template('profile.html', user=user_details, is_admin=(role == 'admin'))
    else:
        flash('You need to log in first.')
        return redirect('/login')

# Edit Profile Route
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')  # Get user_id from session
    if not user_id:
        flash('You need to log in first.')
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':
        # Get form data from the request
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']  # Ensure the format is 'yyyy-mm-dd'

        # Debugging: Print the form data to verify it's being received
        print(f"Form Data: Username: {username}, Email: {email}, Phone: {phone}, DOB: {dob}")

        try:
            with conn.cursor() as cursor:
                # SQL query to update the user's profile in the database
                cursor.execute('''UPDATE users
                                SET username = %s, email = %s, phone = %s, dob = %s
                                WHERE id = %s''',
                            (username, email, phone, dob, user_id))

                conn.commit()

                # Debugging: Print how many rows were affected
                print(f"Rows affected: {cursor.rowcount}")

                # If no rows were updated, notify the user
                if cursor.rowcount == 0:
                    flash('No profile was updated. Please check your details and try again.')
                else:
                    flash('Profile updated successfully!')

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            flash('Failed to update profile due to an error.')
            return redirect('/edit_profile')

        finally:
            conn.close()

        return redirect('/profile')  # Redirect to profile page after successful update

    # If it's a GET request, fetch the current profile data from the database
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute('SELECT username, email, phone, dob FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()

    conn.close()
    return render_template('edit_profile.html', user=user)

#Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session.get('role') == 'admin':
        # Get counts for users, recipes, and reviews
        conn = get_db_connection()
        cur = conn.cursor()

        # SQL queries to get counts
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM recipes")
        recipe_count = cur.fetchone()[0]


        conn.close()

        # Render the dashboard
        return render_template('admin_dashboard.html',
                            user_count=user_count,
                            recipe_count=recipe_count)

# Manage Users
@app.route('/manage_users')
def manage_users():
    if 'user_id' in session and session['role'] == 'admin':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all users, excluding the admin
        cursor.execute("SELECT id, username, email, role FROM users")
        users = cursor.fetchall()

        # Exclude the admin user from the list
        users = [user for user in users if user['role'] != 'admin']

        cursor.close()
        conn.close()

        return render_template('manage_users.html', users=users)
    return redirect('/login')

# Route to edit user details
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Handle form submission for updating the user details
    if request.method == 'POST' and 'updateUser' in request.form:
        new_username = request.form['username']
        new_email = request.form['email']
        new_phone = request.form['phone']
        new_dob = request.form['dob']

        # Update user information in the database
        update_query = """
            UPDATE Users
            SET username = %s, email = %s, phone = %s, dob = %s
            WHERE id = %s
        """
        cursor.execute(update_query, (new_username, new_email, new_phone, new_dob, user_id))
        conn.commit()
        flash("User details updated successfully!")

        cursor.close()
        conn.close()

        return redirect('/manage_users')

    # Fetch existing user details for display
    cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash("User not found!")
        cursor.close()
        conn.close()
        return redirect('/manage_users')

    cursor.close()
    conn.close()

    return render_template('edit_user.html', user=user)

# Route to delete user
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if there are any related data before deleting the user
        cursor.execute("SELECT COUNT(*) FROM RelatedTable WHERE user_id = %s", (user_id,))
        related_count = cursor.fetchone()[0]

        if related_count > 0:
            flash("Error: Cannot delete this user due to related data.")
            return redirect('/manage_users')

        # Proceed with deleting the user
        cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
        conn.commit()
        flash("User deleted successfully!")

    except mysql.connector.IntegrityError as e:
        flash(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect('/manage_users')

# Route to manage recipes (and display recipe details when clicked)
@app.route('/manage_recipes', methods=['GET', 'POST'])
def manage_recipes():
    if 'user_id' in session and session['role'] == 'admin':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all recipes
        cursor.execute("SELECT recipeID, recipeName, imageLink, cookingTime, servingSize FROM Recipes")
        recipes = cursor.fetchall()

        # Recipe count
        recipe_count = len(recipes)

        # Handle edit request
        if request.method == 'POST' and 'editRecipeID' in request.form:
            edit_recipe_id = request.form['editRecipeID']
            cursor.execute("SELECT * FROM Recipes WHERE recipeID = %s", (edit_recipe_id,))
            recipe = cursor.fetchone()

            return render_template('edit_recipe.html', recipe=recipe)

        # Handle delete request
        if request.method == 'POST' and 'deleteRecipeID' in request.form:
            delete_recipe_id = request.form['deleteRecipeID']
            cursor.execute("DELETE FROM Recipes WHERE recipeID = %s", (delete_recipe_id,))
            conn.commit()

            # Optionally delete related data like ingredients, steps, etc.
            cursor.execute("DELETE FROM RecipeIngredients WHERE recipeID = %s", (delete_recipe_id,))
            cursor.execute("DELETE FROM Steps WHERE recipeID = %s", (delete_recipe_id,))
            conn.commit()

            # Redirect back to manage recipes after deletion
            return redirect('/manage_recipes')

        # If a recipe is selected, display its details
        if request.method == 'POST' and 'recipeID' in request.form:
            selected_recipe_id = request.form['recipeID']

            # Log search history for the user
            user_id = session['user_id']
            cursor.execute("INSERT INTO SearchHistory (id) VALUES (%s)", (user_id,))
            conn.commit()
            search_id = cursor.lastrowid  # Get the last inserted searchID

            # Fetch ingredients for the selected recipe
            cursor.execute("""
                SELECT ri.quantity, i.ingredientName
                FROM RecipeIngredients ri
                JOIN Ingredients i ON ri.ingredientID = i.ingredientID
                WHERE ri.recipeID = %s
            """, (selected_recipe_id,))
            ingredients = cursor.fetchall()

            # Fetch steps for the selected recipe
            cursor.execute("""
                SELECT stepNum, description
                FROM Steps
                WHERE recipeID = %s
                ORDER BY stepNum
            """, (selected_recipe_id,))
            steps = cursor.fetchall()

            # Log the ingredients searched
            for ingredient in ingredients:
                cursor.execute("""
                    INSERT INTO Search_Ingredients (searchID, ingredientName)
                    VALUES (%s, %s)
                """, (search_id, ingredient['ingredientName']))
            conn.commit()

            # Fetch the selected recipe details
            cursor.execute("""
                SELECT recipeName, imageLink, cookingTime, servingSize
                FROM Recipes WHERE recipeID = %s
            """, (selected_recipe_id,))
            recipe = cursor.fetchone()

            cursor.close()
            conn.close()

            return render_template('manage_recipes.html', recipe=recipe, ingredients=ingredients, steps=steps, recipes=recipes, recipe_count=recipe_count)

        cursor.close()
        conn.close()

        return render_template('manage_recipes.html', recipes=recipes, recipe_count=recipe_count)
    return redirect('/login')

# Route to edit a recipe
@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get updated recipe details
        recipe_name = request.form['recipeName']
        image_link = request.form['imageLink']
        cooking_time = request.form['cookingTime']
        serving_size = request.form['servingSize']

        # Update the recipe details
        cursor.execute("""
            UPDATE Recipes
            SET recipeName = %s, imageLink = %s, cookingTime = %s, servingSize = %s
            WHERE recipeID = %s
        """, (recipe_name, image_link, cooking_time, serving_size, recipe_id))

        # Update ingredients (remove existing ingredients first)
        cursor.execute("DELETE FROM RecipeIngredients WHERE recipeID = %s", (recipe_id,))

        # Add new ingredients (both edited and new)
        ingredient_names = request.form.getlist('ingredientName_new[]') + request.form.getlist('ingredientName_{{ ingredient.ingredientID }}')
        ingredient_quantities = request.form.getlist('quantity_new[]') + request.form.getlist('quantity_{{ ingredient.ingredientID }}')

        for i in range(len(ingredient_names)):
            ingredient_name = ingredient_names[i]
            quantity = ingredient_quantities[i]
            cursor.execute("""
                INSERT INTO RecipeIngredients (recipeID, ingredientID, quantity)
                VALUES (%s, (SELECT ingredientID FROM Ingredients WHERE ingredientName = %s), %s)
            """, (recipe_id, ingredient_name, quantity))

        # Update steps (remove existing steps first)
        cursor.execute("DELETE FROM Steps WHERE recipeID = %s", (recipe_id,))

        # Add new steps (both edited and new)
        for i in range(len(request.form.getlist('stepDescription_new[]'))):
            step_description = request.form.getlist('stepDescription_new[]')[i]
            cursor.execute("""
                INSERT INTO Steps (recipeID, stepNum, description)
                VALUES (%s, %s, %s)
            """, (recipe_id, i+1, step_description))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(f'/view_recipe/{recipe_id}')  # Redirect to the recipe view page

    # Retrieve recipe data
    cursor.execute("SELECT * FROM Recipes WHERE recipeID = %s", (recipe_id,))
    recipe = cursor.fetchone()

    # Retrieve ingredients for the recipe
    cursor.execute("""
        SELECT ri.ingredientID, i.ingredientName, ri.quantity
        FROM RecipeIngredients ri
        JOIN Ingredients i ON ri.ingredientID = i.ingredientID
        WHERE ri.recipeID = %s
    """, (recipe_id,))
    ingredients = cursor.fetchall()

    # Retrieve steps for the recipe
    cursor.execute("SELECT * FROM Steps WHERE recipeID = %s ORDER BY stepNum", (recipe_id,))
    steps = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('edit_recipe.html', recipe=recipe, ingredients=ingredients, steps=steps)

# View Recipe
@app.route('/view_recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Retrieve the main recipe information
    cursor.execute("SELECT * FROM Recipes WHERE recipeID = %s", (recipe_id,))
    recipe = cursor.fetchone()

    # Retrieve the ingredients for the recipe
    cursor.execute("""
        SELECT ri.ingredientID, i.ingredientName, ri.quantity
        FROM RecipeIngredients ri
        JOIN Ingredients i ON ri.ingredientID = i.ingredientID
        WHERE ri.recipeID = %s
    """, (recipe_id,))
    ingredients = cursor.fetchall()

    # Retrieve the steps for the recipe
    cursor.execute("SELECT * FROM Steps WHERE recipeID = %s ORDER BY stepNum", (recipe_id,))
    steps = cursor.fetchall()

    cursor.close()

    return render_template('recipes.html', recipe=recipe, ingredients=ingredients, steps=steps)

# Delete Ingredient
@app.route('/delete_ingredient/<int:recipe_id>/<int:ingredient_id>', methods=['POST'])
def delete_ingredient(recipe_id, ingredient_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete ingredient from RecipeIngredients
    cursor.execute("DELETE FROM RecipeIngredients WHERE recipeID = %s AND ingredientID = %s", (recipe_id, ingredient_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(f'/edit_recipe/{recipe_id}')

# Delete Steps
@app.route('/delete_step/<int:recipe_id>/<int:step_id>', methods=['POST'])
def delete_step(recipe_id, step_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete step from Steps
    cursor.execute("DELETE FROM Steps WHERE recipeID = %s AND stepID = %s", (recipe_id, step_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(f'/edit_recipe/{recipe_id}')

# Delete Recipes
@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # First, delete associated ingredients from RecipeIngredients table
        cursor.execute("""
            DELETE FROM RecipeIngredients WHERE recipeID = %s
        """, (recipe_id,))

        # Then, delete associated steps from the Steps table
        cursor.execute("""
            DELETE FROM Steps WHERE recipeID = %s
        """, (recipe_id,))

        # Finally, delete the recipe from the Recipes table
        cursor.execute("""
            DELETE FROM Recipes WHERE recipeID = %s
        """, (recipe_id,))

        # Commit the transaction
        conn.commit()
        flash('Recipe deleted successfully!', 'success')
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        # Close the connection
        cursor.close()
        conn.close()

    # Redirect back to the manage recipes page
    return redirect('/manage_recipes')

# Add Recipes
@app.route('/add_recipe')
def add_recipe():
    return render_template('add_recipe.html')

# Save Recipe
@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    # Capture recipe details
    recipe_name = request.form['recipeName']
    image_link = request.form['imageLink']
    cooking_time = request.form['cookingTime']
    serving_size = request.form['servingSize']

    # Capture ingredients and steps from the form
    ingredients = request.form.getlist('ingredients[]')
    quantities = request.form.getlist('quantities[]')
    steps = request.form.getlist('steps[]')

    # Check if all required fields are filled
    if not recipe_name or not cooking_time or not serving_size or not ingredients or not steps:
        flash('Please fill all required fields!', 'danger')
        return redirect('/add_recipe')

    # Establish a connection to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert the new recipe into the Recipes table
        cursor.execute("""
            INSERT INTO Recipes (recipeName, imageLink, cookingTime, servingSize)
            VALUES (%s, %s, %s, %s)
        """, (recipe_name, image_link, cooking_time, serving_size))

        # Get the recipe ID of the newly inserted recipe
        recipe_id = cursor.lastrowid

        # Insert ingredients into RecipeIngredients table
        for ingredient, quantity in zip(ingredients, quantities):
            cursor.execute("""
                INSERT INTO Ingredients (ingredientName) VALUES (%s)
            """, (ingredient,))
            ingredient_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO RecipeIngredients (recipeID, ingredientID, quantity)
                VALUES (%s, %s, %s)
            """, (recipe_id, ingredient_id, quantity))

        # Insert steps into the Steps table
        for step_num, step_description in enumerate(steps, start=1):
            cursor.execute("""
                INSERT INTO Steps (recipeID, stepNum, description)
                VALUES (%s, %s, %s)
            """, (recipe_id, step_num, step_description))

        # Commit the transaction
        conn.commit()
        flash('Recipe added successfully!', 'success')
    except Exception as e:
        # Handle any errors
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        # Close the connection
        cursor.close()
        conn.close()

    # Redirect to manage recipes page after saving the recipe
    return redirect('/manage_recipes')

# User Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    session.clear()  # Clear the session data
    flash('You have been logged out.')  # Flash message for logout
    return redirect('/login')  # Redirect to the login page

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)