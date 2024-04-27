from django.shortcuts import render
# # from django.http import JsonResponse
# # from .models import ChatMessage
# # from django.contrib.auth.decorators import login_required


# # # @login_required
# # def chatbot_view(request):
# #     if request.method == 'POST':
# #         message = request.POST.get('message')
# #         if message:
# #             # Save the user message to the database
# #             ChatMessage.objects.create(sender='User', message=message)
# #             # Basic reply from the chatbot
# #             response_message = "Hello! I'm a chatbot. You said: " + message
# #             # Save the chatbot response to the database
# #             ChatMessage.objects.create(sender='Chatbot', message=response_message)
# #             return JsonResponse({'message': response_message})
# #     return render(request,'chatbot/chatbot.html')


# # views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import re
# import numpy as np
# import pickle as pk
# from keras.models import load_model
# from sklearn.feature_extraction.text import CountVectorizer
# from nltk.stem.porter import PorterStemmer  # Add this import

# # Load models and other necessary data
# loadedIntentClassifier = load_model('models/saved_state/intent_model.h5')
# loaded_intent_CV = pk.load(open('models/saved_state/IntentCountVectorizer.sav', 'rb'))
# loadedEntityCV = pk.load(open('models/saved_state/EntityCountVectorizer.sav', 'rb'))
# loadedEntityClassifier = pk.load(open('models/saved_state/entity_model.sav', 'rb'))


# # Function to get entities
# def getEntities(query):
#     query = loadedEntityCV.transform(query).toarray()
#     response_tags = loadedEntityClassifier.predict(query)
#     entity_list=[]
#     for tag in response_tags:
#         if tag in entity_label_map.values():
#             entity_list.append(list(entity_label_map.keys())[list(entity_label_map.values()).index(tag)])
#     return entity_list

# # Function to predict intent
# def predict_intent(user_query):
#     query = re.sub('[^a-zA-Z]', ' ', user_query)
#     query = query.split(' ')
#     ps = PorterStemmer()
#     tokenized_query = [ps.stem(word.lower()) for word in query]
#     processed_text = ' '.join(tokenized_query)
#     processed_text = loaded_intent_CV.transform([processed_text]).toarray()
#     predicted_Intent = loadedIntentClassifier.predict(processed_text)
#     result = np.argmax(predicted_Intent, axis=1)
#     for key, value in intent_label_map.items():
#         if value==result[0]:
#             return key

# # Chatbot view
# @csrf_exempt
# def chatbot_view(request):
#     if request.method == 'POST':
#         message = request.POST.get('message')
#         if message:
#             # Predict intent from user message
#             intent = predict_intent(message)
            
#             # Process intent and generate response
#             if intent == 'greeting':
#                 response_message = "Hello! How can I assist you today?"
#             elif intent == 'farewell':
#                 response_message = "Goodbye! Have a great day!"
#             else:
#                 response_message = "I'm sorry, I didn't understand that."

#             return JsonResponse({'message': response_message})
#     return render(request,'chatbot/chatbot.html')





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re
from nltk.stem.porter import PorterStemmer
import numpy as np
from keras.models import load_model
import pickle as pk
import random
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_extraction.text import CountVectorizer
import keras
from keras.models import Sequential
from keras.layers import Dense


def trainIntentModel():
    # Load the dataset and prepare it to the train the model

    # Importing dataset and splitting into words and labels
    dataset = pd.read_csv('models/saved_state/intent.csv', names=["Query", "Intent"])
    X = dataset["Query"]
    y = dataset["Intent"]

    unique_intent_list = list(set(y))

    print("Intent Dataset successfully loaded!")
    
    # Clean and prepare the intents corpus
    queryCorpus = []
    ps = PorterStemmer()

    for query in X:
        query = re.sub('[^a-zA-Z]', ' ', query)

        # Tokenize sentence
        query = query.split(' ')

        # Lemmatizing
        tokenized_query = [ps.stem(word.lower()) for word in query]

        # Recreate the sentence from tokens
        tokenized_query = ' '.join(tokenized_query)

        # Add to corpus
        queryCorpus.append(tokenized_query)
        
    print(queryCorpus)
    print("Corpus created")
    
    countVectorizer= CountVectorizer(max_features=800)
    corpus = countVectorizer.fit_transform(queryCorpus).toarray()
    print(corpus.shape)
    print("Bag of words created!")
    
    # Save the CountVectorizer
    pk.dump(countVectorizer, open("models/saved_state/IntentCountVectorizer.sav", 'wb'))
    print("Intent CountVectorizer saved!")
    
    # Encode the intent classes
    labelencoder_intent = LabelEncoder()
    y = labelencoder_intent.fit_transform(y)
    y = keras.utils.to_categorical(y)
    print("Encoded the intent classes!")
    print(y)
    
    # Return a dictionary, mapping labels to their integer values
    res = {}
    for cl in labelencoder_intent.classes_:
        res.update({cl:labelencoder_intent.transform([cl])[0]})

    intent_label_map = res
    print(intent_label_map)
    print("Intent Label mapping obtained!")
    
    # Initialising the Aritifcial Neural Network
    classifier = Sequential()

    # Adding the input layer and the first hidden layer
    classifier.add(Dense(units = 96, kernel_initializer = 'uniform', activation = 'relu', input_dim = 133))

    # Adding the second hidden layer
    classifier.add(Dense(units = 96, kernel_initializer = 'uniform', activation = 'relu'))

    # Adding the output layer
    classifier.add(Dense(units = 32, kernel_initializer = 'uniform', activation = 'softmax'))

    # Compiling the ANN
    classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    
    # Fitting the ANN to the Training set
    classifier.fit(corpus, y, batch_size = 10, epochs = 500)
    
    return classifier, intent_label_map




intent_model, intent_label_map = trainIntentModel()

def trainEntityModel():
    # Importing dataset and splitting into words and labels
    dataset = pd.read_csv('models/saved_state/data-tags.csv', names=["word", "label"])
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, 1].values
#     X = X.reshape(630,)
    print(X)
    print("Entity Dataset successfully loaded!")

    entityCorpus=[]
    ps = PorterStemmer()

    # Stem words in X
    for word in X.astype(str):
        word = [ps.stem(word[0])]
        entityCorpus.append(word)
    
    print(entityCorpus)
    X = entityCorpus
    from numpy import array
    X = array(X)
    X = X.reshape(len(X),)
    
    # Create a bag of words model for words
    from sklearn.feature_extraction.text import CountVectorizer
    cv = CountVectorizer(max_features=1500)
#     X = cv.fit_transform(X.astype('U')).toarray()
    X = cv.fit_transform(X).toarray()
    print("Entity Bag of words created!")
    
    # Save CountVectorizer state
    pk.dump(cv, open('models/saved_state/CountVectorizer.sav', 'wb'))
    print("Entity CountVectorizer state saved!")
    
    # Encoding categorical data of labels
    labelencoder_y = LabelEncoder()
    y = labelencoder_y.fit_transform(y.astype(str))
    print("Encoded the entity classes!")
    
    # Return a dict mapping labels to their integer values
    res = {}
    for cl in labelencoder_y.classes_:
        res.update({cl:labelencoder_y.transform([cl])[0]})
    entity_label_map = res
    print("Entity Label mapping obtained!")
    
    # Fit classifier to dataset
    classifier = GaussianNB()
    classifier.fit(X, y)
    print("Entity Model trained successfully!")
    
    # Save the entity classifier model
    pk.dump(classifier, open('models/saved_state/entity_model.sav', 'wb'))
    print("Trained entity model saved!")
    
    return entity_label_map

# Load the models and other resources
loadedIntentClassifier = load_model('models/saved_state/intent_model.h5')
loaded_intent_CV = pk.load(open('models/saved_state/IntentCountVectorizer.sav', 'rb'))    
entity_label_map = trainEntityModel()
loadedEntityCV = pk.load(open('models/saved_state/CountVectorizer.sav', 'rb'))
loadedEntityClassifier = pk.load(open('models/saved_state/entity_model.sav', 'rb'))

# Load intents file
with open('models/saved_state/intents.json') as json_data:
    intents = json.load(json_data)

# Define the view
def chatbot_view(request):
    if request.method == 'POST':
        # Load JSON data from the POST request
        data = json.loads(request.body)
        user_query = data.get('query')
        
        # Process user query and predict intent
        query = re.sub('[^a-zA-Z]', ' ', user_query)
        query = query.split(' ')
        ps = PorterStemmer()
        tokenized_query = [ps.stem(word.lower()) for word in query]
        processed_text = ' '.join(tokenized_query)
        processed_text = loaded_intent_CV.transform([processed_text]).toarray()
        predicted_Intent = loadedIntentClassifier.predict(processed_text)
        result = np.argmax(predicted_Intent, axis=1)
        
        for key, value in intent_label_map.items():
            if value == result[0]:
                user_intent = key
                break
        
        for intent in intents['intents']:
            if intent['tag'] == user_intent:
                response = random.choice(intent['responses'])
        
        # Predict entities
        query = loadedEntityCV.transform([user_query]).toarray()
        response_tags = loadedEntityClassifier.predict(query)
        entity_list = []
        for tag in response_tags:
            if tag in entity_label_map.values():
                entity_list.append(list(entity_label_map.keys())[list(entity_label_map.values()).index(tag)])
        
        # Return the chatbot response as JSON
        return JsonResponse({
            'response': response,
            'entities': entity_list
        })
    
    # If the request is GET, render the HTML template
    elif request.method == 'GET':
        return render(request, 'chatbot/chatbot.html')
    
    else:
        # If the request is not POST or GET, return a method not allowed response
        return JsonResponse({'error': 'Method not allowed'}, status=405)
