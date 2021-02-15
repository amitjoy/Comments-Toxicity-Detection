__author__ = "Baishali Dutta"
__copyright__ = "Copyright (C) 2021 Baishali Dutta"
__license__ = "Apache License 2.0"
__version__ = "0.1"

import matplotlib.pyplot as plt
# -------------------------------------------------------------------------
#                           Import Libraries
# -------------------------------------------------------------------------
import numpy as np
from keras.layers import Input, Dense, \
    GlobalMaxPooling1D, LSTM, Bidirectional
from keras.models import Model
from sklearn.metrics import roc_auc_score

from data_preprocessing import DataPreprocess

# -------------------------------------------------------------------------
#                               Configurations
# -------------------------------------------------------------------------
EMBEDDING_DIMENSION = 100
EMBEDDING_FILE_LOC = '../glove/glove.6B.' + str(EMBEDDING_DIMENSION) + 'd.txt'
TRAINING_DATA_LOC = '../data/train.csv'
MAX_VOCAB_SIZE = 20000
MAX_SEQUENCE_LENGTH = 100
BATCH_SIZE = 128
EPOCHS = 10
VALIDATION_SPLIT = 0.2
DETECTION_CLASSES = ['toxic', 'severe_toxic', 'obscene', 'threat',
                     'insult', 'identity_hate']
MODEL_LOC = '../model/comments_toxicity.h5'


# -------------------------------------------------------------------------
#                   Build and Train the RNN Model Architecture
# -------------------------------------------------------------------------
def build_rnn_model(data, target_classes, embedding_layer):
    """
    Build and Train the RNN architecture (Bidirectional LSTM)
    :param embedding_layer: Embedding layer comprising preprocessed comments
    :param target_classes: Assigned target labels for the comments
    :return: the trained model
    """
    # create an LSTM network with a single LSTM
    input_ = Input(shape=(MAX_SEQUENCE_LENGTH,))
    x = embedding_layer(input_)
    x = Bidirectional(LSTM(15, return_sequences=True))(x)
    x = GlobalMaxPooling1D()(x)

    #  Sigmoid Classifier
    output = Dense(len(DETECTION_CLASSES), activation="sigmoid")(x)

    model = Model(input_, output)

    # Display the model
    model.summary()

    # Compile the model
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    # Train the model
    history = model.fit(data,
              target_classes,
              batch_size=BATCH_SIZE,
              epochs=EPOCHS,
              validation_split=VALIDATION_SPLIT)

    # Save the model
    model.save(MODEL_LOC)

    # Return model training history
    return model, history


# -------------------------------------------------------------------------
#                   Plotting the training history
# -------------------------------------------------------------------------
def plot_training_history(rnn_model, history, data, target_classes):
    """
    Generates plots for accuracy and loss
    :param rnn_model: the trained model
    :param data: preprocessed data
    :param target_classes: target classes for every comment
    :return: None
    """
    #  "Accuracy"
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.savefig("../plots/accuracy.jpeg")
    plt.show()

    # "Loss"
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.savefig("../plots/loss.jpeg")
    plt.show()

    # Print Average ROC_AUC_Score
    p = rnn_model.predict(data)
    aucs = []
    for j in range(6):
        auc = roc_auc_score(target_classes[:, j], p[:, j])
        aucs.append(auc)
    print(f'Average ROC_AUC Score: {np.mean(aucs)}')


# -------------------------------------------------------------------------
#                               Main Execution
# -------------------------------------------------------------------------
def execute():
    preprocessing = DataPreprocess(TRAINING_DATA_LOC)
    rnn_model, history = build_rnn_model(preprocessing.padded_data,
                                         preprocessing.target_classes,
                                         preprocessing.embedding_layer)
    plot_training_history(rnn_model,
                          history,
                          preprocessing.padded_data,
                          preprocessing.target_classes)


if __name__ == '__main__':
    execute()