# Kitsain-Backend-Autumn2024

## Setup Instructions
Check that you have Python installed before 
moving on to the next step!

Clone the repository:

    git clone <repository-url>
    
    cd Kitsain-Backend-Autumn2024


NOTE: Installing dependencies takes few minutes!

Install dependecies:

**Windows**:

      .\setup.bat

**Mac/Linux**:

      ./setup.sh

      chmod +x setup.sh


## Run the program
Run the program:

    cd Kitsain-Backend-Autumn2024

    python app.py

Close the program:

    Crtl + C

Open the application in your browser:

    http://127.0.0.1:5000


## The application shortly
This is an application to help users to find discounted food items and prevent 
food waste.

First user must log into their own account. If user has forgotten their password, 
it can be changed by clicking the link "Forgot password?" which will then go to a 
page where user enters an email and a password can be changed from the link that 
is send to user's email.

Once user has logged into their account, they can start adding stores, products 
and their prices, discounts etc. On the mainpage user can see latest updates, search 
product with or without filters or add products. On the main page user can also 
see the stores that are near.

On the products page user can view all products, search them with or without 
filters, add, modify and delete products. When user adds a new product, they can 
choose to use information from Open Food Fact. This then fills the product 
details with Open Food Fact information.

On the stores page, user can see different stores, search them with or without 
filters, add more stores, delete them and modify shopkeepers.

On the profile page user can see their profile, edit it, view added products, see 
their aurapoints and how their aurapoints have changed during the time user has 
used the application. The total amount points are shown in a graph for user to 
get a visualization on how the points have changed. From the profile page user can 
also change their password if they want to.