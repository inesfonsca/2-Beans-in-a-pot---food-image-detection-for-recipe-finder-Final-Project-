2 BEANS IN A POT

---Food Image Detection and Recipe Finder Web App---

Unlock the culinary magic with my ingredient-detecting web app and discover a world of delightful recipes at your fingertips!


Resume:
My final project is a web application that leverages the power of artificial intelligence and web scraping to detect food items in images and provide corresponding recipes. The app utilizes two APIs, Google Cloud Vision API and Clarifai API, to recognize ingredients in food images, and also performs web scraping from the 24 Kitchen website to obtain a diverse dataset of recipes.



Key Features:
Food Image Detection: The app allows users to upload images of food items, which are then processed using Google Cloud Vision API and Clarifai API to identify the ingredients present in the images.

Recipe Finder: After detecting the ingredients in the uploaded images, the app searches its dataset of recipes, obtained through web scraping from the 24 Kitchen website, to find matching recipes for the detected ingredients.

Difficulty and Category Filters: Users can further refine their recipe search by specifying the difficulty level and category (e.g., breakfast, lunch, dinner, dessert) of the desired recipes.



Technologies Used:
Flask: The web app is built using the Flask web framework, allowing for easy integration of the AI APIs and web scraping functionalities.

Google Cloud Vision API: This powerful API is utilized for image recognition, allowing the app to extract ingredient information from the uploaded food images.

Clarifai API: The Clarifai API complements the image detection capabilities of the Google Cloud Vision API, enhancing the accuracy of ingredient identification.

Web Scraping: Python's web scraping libraries are used to crawl the 24 Kitchen website, extracting a rich dataset of recipes for the app's recipe finder feature.


The web app serves as an excellent tool for food enthusiasts, helping them discover new recipes based on the ingredients they have at hand, making cooking a delightful experience. Feel free to contribute to the project and share your ideas to further enhance its capabilities.
