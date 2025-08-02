CREATE DATABASE recipesDB;
USE recipesDB;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    dob DATE,
    role VARCHAR(20),
	joined_date DATE
);

CREATE TABLE Recipes(
    recipeID INT PRIMARY KEY AUTO_INCREMENT,     -- Unique ID for each recipe
    recipeName VARCHAR(100) NOT NULL,            -- Name of the food
    imageLink VARCHAR(255),                      -- URL or link to the image of the recipe
    cookingTime INT,                             -- Cooking time in minutes
    servingSize INT,                             -- Number of servings
    dateAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Steps (
    stepID INT PRIMARY KEY AUTO_INCREMENT,       -- Unique ID for each step
    recipeID INT,                                -- Foreign key linking to the Recipes table
    stepNum INT NOT NULL,                     -- The step number (order of the step)
    description TEXT NOT NULL,                    -- The actual step description
    FOREIGN KEY (recipeID) REFERENCES Recipes(recipeID)
);

CREATE TABLE Ingredients(
    ingredientID INT PRIMARY KEY AUTO_INCREMENT,  -- Unique ID for each ingredient
    ingredientName VARCHAR(100) NOT NULL          -- Name of the ingredient
);

CREATE TABLE RecipeIngredients (
    recipeID INT,                                  -- Foreign key linking to Recipes table
    ingredientID INT,                              -- Foreign key linking to Ingredients table
    quantity VARCHAR(50),                           -- Quantity of the ingredient used in the recipe
      -- Composite primary key (recipe and ingredient)
    FOREIGN KEY (recipeID) REFERENCES Recipes(recipeID),
    FOREIGN KEY (ingredientID) REFERENCES Ingredients(ingredientID)
);

CREATE TABLE UsersIngredients(
    id INT,                                   -- Foreign key linking to Users table
    ingredientID INT,                             -- Foreign key linking to Ingredients table
    PRIMARY KEY (id, ingredientID),          -- Composite primary key
    FOREIGN KEY (id) REFERENCES Users(id),
    FOREIGN KEY (ingredientID) REFERENCES Ingredients(ingredientID)
);

CREATE TABLE SearchHistory (
    searchID INT PRIMARY KEY AUTO_INCREMENT,      -- Unique ID for each search record
    id INT,                                   -- Foreign key linking to Users table
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of when the search was made
    FOREIGN KEY (id) REFERENCES Users(id)  -- Linking to the Users table
);

CREATE TABLE Search_Ingredients(
    searchID INT,                                -- Foreign key linking to Search_History table
    ingredientName VARCHAR(100),                 -- Ingredient name (e.g., "tomato")
    PRIMARY KEY (searchID, ingredientName),     -- Composite primary key
    FOREIGN KEY (searchID) REFERENCES SearchHistory(searchID) -- Linking to the Search_History table
);

CREATE TABLE Ratings (
    id INT,                                   -- Foreign key linking to Users table
    recipeID INT,                                 -- Foreign key linking to Recipes table
    rating INT CHECK (rating >= 1 AND rating <= 5), -- Rating value (1 to 5)
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of when the rating was given
    PRIMARY KEY (id, recipeID),              -- Composite primary key to ensure a user can rate a recipe only once
    FOREIGN KEY (id) REFERENCES Users(id),   -- Foreign key constraint linking to Users table
    FOREIGN KEY (recipeID) REFERENCES Recipes(recipeID) -- Foreign key constraint linking to Recipes table
);

-- Insert sample data into Recipes table
INSERT INTO Recipes (recipeName, imageLink, cookingTime, servingSize) 
VALUES 
    ('Tiramisu Cake', 'TiramisuCake.jpeg', 45, 6),
    ('Veg Biryani', 'vegBiryani.jpeg', 60, 4),
    ('Fish Fry', 'fishFry.jpeg', 20, 2),
    ('Pasta', 'pasta.jpeg', 25, 3),
    ('Butter Chicken', 'butterChicken.jpeg', 60, 4),
    ('Butter Paneer', 'butterPaneer.jpeg', 50, 4),
    ('Chicken Biryani', 'chickenBiriyani.jpeg', 90, 6),
    ('Curd Rice', 'curdRice.jpeg', 15, 2),
    ('Egg Curry', 'eggCurry.jpeg', 30, 4),
    ('Jeera Rice', 'jeeraRice.jpeg', 20, 3);

-- Insert sample steps for each recipe
INSERT INTO Steps (recipeID, stepNum, description) 
VALUES 
    -- Tiramisu Cake steps
    (1, 1, 'In a mixing bowl, whisk together eggs and sugar until fluffy.'),
    (1, 2, 'Add flour and mix gently to avoid deflating the batter.'),
    (1, 3, 'Bake the cake base at 180°C for 25 minutes.'),
    (1, 4, 'Prepare coffee mixture and soak cake layers.'),
    (1, 5, 'Layer the soaked cake with mascarpone cheese mixture.'),
    (1, 6, 'Refrigerate for at least 4 hours before serving.'),

    -- Veg Biryani steps
    (2, 1, 'Heat oil in a pan and sauté onions until golden brown.'),
    (2, 2, 'Add tomatoes, spices, and vegetables, and cook until tender.'),
    (2, 3, 'Add soaked rice to the mixture and stir well.'),
    (2, 4, 'Add water and cook rice on low heat until fully done.'),
    (2, 5, 'Garnish with fresh coriander and serve hot.'),

    -- Fish Fry steps
    (3, 1, 'Marinate fish with spices, salt, and lemon juice for 30 minutes.'),
    (3, 2, 'Heat oil in a pan and fry fish until golden brown on both sides.'),
    (3, 3, 'Serve hot with lemon wedges and salad.'),

    -- Pasta steps
    (4, 1, 'Boil pasta in salted water until al dente, then drain.'),
    (4, 2, 'Sauté garlic in butter, then add tomatoes and cook until soft.'),
    (4, 3, 'Add cheese and pasta, and toss to coat. Serve hot.'),

    -- Butter Chicken steps
    (5, 1, 'Marinate chicken with yogurt and spices for 30 minutes.'),
    (5, 2, 'Cook marinated chicken in a pan until fully cooked.'),
    (5, 3, 'Prepare a gravy with tomatoes, spices, and butter.'),
    (5, 4, 'Add chicken to the gravy and simmer for 10 minutes.'),
    (5, 5, 'Serve hot with rice or naan bread.'),

    -- Butter Paneer steps
    (6, 1, 'Marinate paneer with yogurt and spices for 30 minutes.'),
    (6, 2, 'Heat oil in a pan, sauté onions and ginger until soft.'),
    (6, 3, 'Add tomatoes and cook until the oil separates.'),
    (6, 4, 'Add marinated paneer and cook for 10 minutes.'),
    (6, 5, 'Garnish with coriander and serve with rice or naan.'),

    -- Chicken Biryani steps
    (7, 1, 'Heat oil and sauté onions until golden brown.'),
    (7, 2, 'Add marinated chicken and cook until tender.'),
    (7, 3, 'Add tomatoes, spices, and water, then bring to a boil.'),
    (7, 4, 'Add soaked rice and cook on low heat until done.'),
    (7, 5, 'Garnish with fried onions and coriander, and serve hot.'),

    -- Curd Rice steps
    (8, 1, 'Cook rice and let it cool to room temperature.'),
    (8, 2, 'In a pan, heat oil and sauté mustard seeds, curry leaves, and chilies.'),
    (8, 3, 'Add the tempering to the rice, mix well, and add curd.'),
    (8, 4, 'Garnish with coriander and serve cold or at room temperature.'),

    -- Egg Curry steps
    (9, 1, 'Boil eggs and peel them.'),
    (9, 2, 'Sauté onions, garlic, and ginger until golden brown.'),
    (9, 3, 'Add tomatoes, spices, and cook until the oil separates.'),
    (9, 4, 'Add boiled eggs to the curry and cook for 10 minutes.'),
    (9, 5, 'Serve hot with rice or bread.'),

    -- Jeera Rice steps
    (10, 1, 'Heat oil and sauté cumin seeds until fragrant.'),
    (10, 2, 'Add rice and water, and cook until the rice is tender.'),
    (10, 3, 'Garnish with coriander leaves and serve hot.');

-- Insert sample data into Ingredients table
INSERT INTO Ingredients (ingredientName) 
VALUES 
    ('Flour'), ('Sugar'), ('Eggs'), ('Butter'), ('Milk'), ('Cheese'), ('Tomatoes'), ('Rice'), ('Chicken'), ('Paneer'),
    ('Curd'), ('Cumin'), ('Onions'), ('Garlic'), ('Ginger'), ('Spices'), ('Fish'), ('Vegetables');

-- Insert sample data into RecipeIngredients table
INSERT INTO RecipeIngredients (recipeID, ingredientID, quantity)
VALUES 
    -- Tiramisu Cake
    (1, 2, '100g'),  -- 100g of Sugar
    (1, 3, '2'),     -- 2 Eggs
    (1, 4, '50g'),   -- 50g of Butter
    (1, 5, '200ml'), -- 200ml of Milk

    -- Veg Biryani
    (2, 7, '150g'),   -- 150g of Tomatoes
    (2, 8, '200g'),   -- 200g of Rice
    (2, 13, '1'),     -- 1 Onion
    (2, 15, '2 tbsp'), -- 2 tbsp of Spices

    -- Fish Fry
    (3, 17, '250g'), -- 250g of Fish
    (3, 14, '1 clove'), -- 1 clove of Garlic
    (3, 15, '1 tbsp'), -- 1 tbsp of Ginger

    -- Pasta
    (4, 6, '100g'),   -- 100g of Cheese
    (4, 7, '50g'),    -- 50g of Tomatoes
    (4, 4, '2 tbsp'), -- 2 tbsp of Butter

    -- Butter Chicken
    (5, 8, '200g'),   -- 200g of Rice
    (5, 9, '300g'),   -- 300g of Chicken
    (5, 13, '2'),     -- 2 Onions
    (5, 15, '1 tbsp'), -- 1 tbsp of Ginger

	-- butter paneer
    (6, 10, '250g'),  -- 250g of Paneer
    (6, 7, '200g'),  -- 200g of Tomatoes
    (6, 12, '1 tbsp'),-- 1 tbsp of Cumin Seeds
    (6, 16, '1 tsp'), -- 1 tsp of Red Chilli Powder

-- Chicken Biryani
    (7, 9, '300g'),  -- 300g of Chicken
    (7, 8, '200g'),  -- 200g of Rice
    (7, 7, '150g'),  -- 150g of Tomatoes
    (7, 11, '2 tbsp'),-- 2 tbsp of Yoghurt
  
   -- Curd Rice
    (8, 8, '1 cup'),  -- 1 cup of Rice
    (8, 11, '1/2 cup'),-- 1/2 cup of Curd (Yoghurt)
    (8, 16, '1 tbsp'), -- 1 tbsp of Mustard Seeds
    (8, 12, '1 tsp'),  -- 1 tsp of Cumin Seeds
    
     -- Egg Curry
    (9, 3, '6'),      -- 6 Eggs
    (9, 13, '2'),      -- 2 Onions
    (9, 7, '2'),      -- 2 Tomatoes
    
     -- Jeera Rice
    (10, 8, '200g'),  -- 200g of Rice
    (10, 12, '1 tbsp'), -- 1 tbsp of Cumin Seeds
    (10, 4, '1 tbsp'); -- 1 tbsp of Ghee
 
 
select * from users;
Select * from recipes;
select * from steps;

select * from recipeingredients;
select * from ingredients;
Select * from Ratings;
