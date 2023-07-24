#Importing the necessary libraries
from flask import Flask, render_template, request, jsonify
from google.cloud import vision
from google.oauth2 import service_account
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from googletrans import Translator
import pandas as pd
from clarifai_grpc.grpc.api.status import status_code_pb2
import re
import logging

# Specify the file path of the CSV file
csv_file_path = "final_table_api.csv"

# Read the CSV file and create a DataFrame
recipes = pd.read_csv(csv_file_path)


app = Flask(__name__)

#Google Function to detect how many objects are in my picture

def Google_API_Object_Num(image_path):
    
    # Google Cloud Vision API setup
    credentials = service_account.Credentials.from_service_account_file( r"\Users\ines_\Documents\Final Project\credenciaisfood.json")
    client = vision.ImageAnnotatorClient(credentials=credentials)


    # Load and analyze the image with Google Cloud Vision API
    image_path = image_path
    with open(image_path, "rb") as image_file:
        content = image_file.read()
  
        
    image = vision.Image(content=content)
    response = client.object_localization(image=image)
    
    #objects = number of objects in a image
    
    objects = response.localized_object_annotations
    num_objects = len(objects)    
    
    #when there is an object in the image it returns the name and the  number of objects
    if objects:
        return [obj.name for obj in objects], num_objects
    else:
        return "No objects found in the image", num_objects

##Created a function to join google api (counting the number of objects) to clarifai api who is going to identify 
#what objects are in the picture

def Clarifai_API_Food(image_path):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    # Dictionary to store the name and the value of each ingredient
    ingredients = {"Name": [], "Value": []}

    # Array to return the name of the ingredient - final output
    ingredients_Return = []

    #Calling the function 'Google_API_Object_Num' to return values and store the results.
    #the first element (index 0) to assign it to google_Return and the second element (index 1) to assign it to num_objects.
    #With the index 0 I return the detected objects and with index 1 I return the number of objects found in the image.

    google_Return = Google_API_Object_Num(image_path)[0]
    num_objects = Google_API_Object_Num(image_path)[1]

    # Clarifai API setup - my key

    metadata = (('authorization', 'Key ' + 'XXXXXXXXXXXXXX'),)
    userDataObject = resources_pb2.UserAppIDSet(user_id='clarifai', app_id='main')

    #Request to the api model for food item recognition

    with open(image_path, 'rb') as f:
        image_data = f.read()

    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,
            model_id='food-item-recognition',
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=image_data
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )

    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

    # Since we have one input, one output will exist here.
    output = post_model_outputs_response.outputs[0]

    # Adding to the dictionary all the values above 0.1
    # Check if any element contains the specified keywords

    # Num_objects = detected by the google api function, [1] is the number that the function returns [0] is the name. 
    # In this case, the number is what we want to know, how many objects are in the image
    
    # Adding to the dictionary all the values above 0.0
    # Check if any element contains the specified keywords (most common keywords can help to not detect images that doesn't contain any food)

    if any(any(keyword in return_App for keyword in ['Packaged goods', 'Vegetable', 'Fruit', 'Food', 'Banana', 'Orange', 'Grape',
                                                     'Bell pepper', 'Pear', 'Apple', 'Ingredient', 'Egg', 'Broccoli','Carrot']) for return_App in google_Return):
        for concept in output.data.concepts:
            if concept.value > 0.0:
                ingredients["Name"].append(concept.name)
                ingredients["Value"].append(concept.value)
    else: 
        ingredients["Name"].append('Ingrediente não encontrado.')

    #If num_objects is equal to 0, it sets the ingredients_Return variable to 'Por favor, insira uma nova imagem.' 
    #(Please insert a new image). This suggests that if no objects (ingredients) were detected at all, 
    #the function will return a message indicating the need for a new image.

    #If num_objects is not equal to 0, the code proceeds to translate the ingredient names from English to 
    #Portuguese using the Translator.

    if num_objects == 0:
        ingredients_Return = 'Por favor, insira uma nova imagem.'
    else:
        translator = Translator()
        while num_objects > 0:
            translation = translator.translate(ingredients["Name"][num_objects - 1], src='en', dest='pt').text
            ingredients_Return.append(translation)
            num_objects -= 1

    return ingredients_Return

##Function to search in my dataframe the ingredients detected by the function 'Clarifai_API_Food'

#searching the dataframe for recipes that contain specific ingredients, and then extracting additional 
#information related to these recipes, such as the time required for preparation, difficulty level, and category.

def search_ingredients_and_time_in_dataframe(ingredients, dataframe, column_name, target_column, difficulty, category):
    
    # Convert the ingredients to lowercase
    
    ingredients_lower = [ingredient.lower() for ingredient in ingredients]
    
    # Create a boolean mask to filter rows where the ingredients are found in the specified column
    mask_ingredients = dataframe[column_name].str.lower().str.contains('|'.join(ingredients_lower))
    
    # Create a boolean mask to filter rows based on the difficulty column and multiple difficulty levels
    mask_difficulty = True  # Default mask value
    
    if difficulty is not None:
        if isinstance(difficulty, list) and len(difficulty) > 0:
            mask_difficulty = dataframe['DIFICULDADE'].isin(difficulty)
        elif not isinstance(difficulty, list) or len(difficulty) == 0:
            mask_difficulty = True
        else:
            mask_difficulty = dataframe['DIFICULDADE'] == difficulty
    
    # Create a boolean mask to filter rows based on the category column and multiple category values
    mask_category = True  # Default mask value
    
    if category is not None:
        if isinstance(category, list) and len(category) > 0:
            mask_category = dataframe['CATEGORIAS'].isin(category)
        elif not isinstance(category, list) or len(category) == 0:
            mask_category = True
        else:
            mask_category = dataframe['CATEGORIAS'] == category
    
    # Combine the masks using logical AND to filter rows that satisfy all conditions
    mask = mask_ingredients & mask_difficulty & mask_category
    
    # Create a new DataFrame with the matching names and time from the target columns, maintaining the index numbers
    matching_df = dataframe.loc[mask, [target_column, 'TEMPO', 'YOUTUBE','URL SITE']]

    # Return the matching DataFrame and the number of recipes as a tuple
    return matching_df

#The first page of my web app where the user will upload an image and will have a result

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files.get('file')
        
        # Get the selected category values and convert them to strings
        category_values = [str(value) for value in request.form.getlist('category')]

        # Get the selected difficulty levels and convert them to strings
        difficulty_levels = [str(value) for value in request.form.getlist('difficulty')]
        
        # Save the uploaded file to a specified path
        image_path = "uploaded_image.jpg"
        file.save(image_path)
        
        #To detect the name of the ingredients
        ingredient_name =  Clarifai_API_Food(image_path)
        
        #stored in a variable the result of my functions. To get the recipes of the clarifai with my dataframe together with 
        #the categorys and time chose by the user
        result = search_ingredients_and_time_in_dataframe(
            Clarifai_API_Food(image_path), recipes, 'INGREDIENTES', 'RECEITA', difficulty_levels, category_values
        )

        #To get how many recipes is in the result
        ingredients_number = len(result)

        #Return in the 'result' page my final output, the recipes that combined with category and time and ingredient detection, and also
        # the ingredient name for the modal 

        return render_template('result.html', result=result, category_values=category_values, difficulty_levels=difficulty_levels, ingredient_name=ingredient_name,ingredients_number=ingredients_number )
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
