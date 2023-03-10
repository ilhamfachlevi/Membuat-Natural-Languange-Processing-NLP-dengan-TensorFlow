# -*- coding: utf-8 -*-
"""Muhammad Ilham Fachlevi_Dicoding_NLPTensorFlow.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WE_xYKy9EG4PHzem1qlB8_T_dGn0hUTY
"""

# install kaggle package
!pip install -q kaggle

# upload kaggle.json
from google.colab import files  
files.upload()

# create a kaggle folder
!mkdir ~/.kaggle

# copy the kaggle.json to folder created  
!cp kaggle.json ~/.kaggle/

# permisson for the json to act
!chmod 600 ~/.kaggle/kaggle.json

# to list all avalaible datasets in kaggle
!kaggle datasets list

!kaggle datasets download -d hgultekin/bbcnewsarchive

# unzip
!mkdir bbcnewsarchive
!unzip bbcnewsarchive.zip -d bbcnewsarchive
!ls bbcnewsarchive

ls

"""# Import Library"""

import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer

df = pd.read_csv('/content/bbcnewsarchive/bbc-news-data.csv', sep = '\t')

df

# delete columns (unused column)
df_new = df.drop(columns=['filename'])

df_new.info()

df_new.isna().sum()

df_new.category.value_counts()

"""# Data Cleaning"""

# import and download package
import nltk, os, re, string

from keras.layers import Input, LSTM, Bidirectional, SpatialDropout1D, Dropout, Flatten, Dense, Embedding, BatchNormalization
from keras.models import Model
from keras.callbacks import EarlyStopping
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

nltk.download('wordnet')
nltk.download('stopwords')

# lower-case all characters
df_new.title = df_new.title.apply(lambda x: x.lower())
df_new.content = df_new.content.apply(lambda x: x.lower())

# removing functuation
def cleaner(data):
    return(data.translate(str.maketrans('','', string.punctuation)))
    df_new.title = df_new.title.apply(lambda x: cleaner(x))
    df_new.content = df_new.content.apply(lambda x: lem(x))

## lematization
lemmatizer = WordNetLemmatizer()

def lem(data):
    pos_dict = {'N': wn.NOUN, 'V': wn.VERB, 'J': wn.ADJ, 'R': wn.ADV}
    return(' '.join([lemmatizer.lemmatize(w,pos_dict.get(t, wn.NOUN)) for w,t in nltk.pos_tag(data.split())]))
    df_new.title = df_new.title.apply(lambda x: lem(x))
    df_new.content = df_new.content.apply(lambda x: lem(x))

# removing number
def rem_numbers(data):
    return re.sub('[0-9]+','',data)
    df_new['title'].apply(rem_numbers)
    df_new['content'].apply(rem_numbers)

# removing stopword
st_words = stopwords.words()
def stopword(data):
    return(' '.join([w for w in data.split() if w not in st_words ]))
    df_new.title = df_new.title.apply(lambda x: stopword(x))
    df_new.content = df_new.content.apply(lambda x: lem(x))

df_new

# data category one-hot-encoding
category = pd.get_dummies(df_new.category)
df_new_cat = pd.concat([df_new, category], axis=1)
df_new_cat = df_new_cat.drop(columns='category')
df_new_cat.head(10)

# change dataframe value to numpy array
news = df_new_cat['title'].values + '' + df_new_cat['content'].values
label = df_new_cat[['business', 'entertainment', 'politics', 'sport', 'tech']].values

news

label

# Split data into training and validation
from sklearn.model_selection import train_test_split
news_latih, news_uji, label_latih, label_uji = train_test_split(news, label, test_size=0.2, shuffle=True)

# tokenizer
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
 
tokenizer = Tokenizer(num_words=5000, oov_token='x', filters='!"#$%&()*+,-./:;<=>@[\]^_`{|}~ ')
tokenizer.fit_on_texts(news_latih) 
tokenizer.fit_on_texts(news_uji)
 
sekuens_latih = tokenizer.texts_to_sequences(news_latih)
sekuens_uji = tokenizer.texts_to_sequences(news_uji)
 
padded_latih = pad_sequences(sekuens_latih) 
padded_uji = pad_sequences(sekuens_uji)

# model
import tensorflow as tf
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=64),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(5, activation='softmax')
])
model.compile(optimizer='adam', metrics=['accuracy'], loss='categorical_crossentropy',)
model.summary()

# callback
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>=0.9 and logs.get('val_accuracy')>=0.8):
      self.model.stop_training = True
      print("\nThe accuracy of the training set and the validation set has reached > 90%!")
callbacks = myCallback()

# model fit
history = model.fit(padded_latih, label_latih, epochs=50, 
                    validation_data=(padded_uji, label_uji), verbose=2, callbacks=[callbacks], validation_steps=30)
