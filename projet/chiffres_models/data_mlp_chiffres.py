import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix
import pickle


def pad_arrays(array, longest):
    if len(array) < longest:
        filler = longest - len(array)
        filler_array = []
        for i in range(0, filler):
            zero_array = [0, 0, 0, 0, 0]
            filler_array.append(zero_array)
        return np.concatenate((array, filler_array), axis=0)
    else:
        return array


def class_array():
    driven_number = []

    for i in range(1, 3):
        for j in range(0, 12):
            driven_number.append(i)

    return driven_number


def read_data():
    movements = []
    for i in range(1, 3): #33
        #if i != 2:
        for j in range(1, 13):
            data = pd.read_csv("./../data/chiffres/" + str(i) + "_" + str(j) + ".txt", header=None)
            movement = data.values
            movements.append(movement)

    longest_array = len(max(movements, key=len))

    new_movements = []
    for i in movements:
        new_movements.append(pad_arrays(i, longest_array))

    new_new_movements = []

    for i in new_movements:
        condensed_movement = []
        for n in range(0, 5):
            counter = 1
            new_value = 0
            for j in i:
                new_value += j[n]
                counter += 1
            new_value = new_value / counter
            condensed_movement.append(new_value)
        new_new_movements.append(condensed_movement)

    return pd.DataFrame(new_new_movements)

driven_number = class_array()
data_movement = read_data()

X = data_movement
print(X)
y = driven_number

X_train, X_test, y_train, y_test = train_test_split(X, y)

print(X_train)

scaler = StandardScaler()
scaler.fit(X_train)

pickle.dump(scaler, open('mlp_scaler.pkl', 'wb'))

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

mlp = MLPClassifier(hidden_layer_sizes=(13,13,13),max_iter=500)
mlp.fit(X_train,y_train)

file = 'trained_model.sav'
pickle.dump(mlp, open(file, 'wb'))

predictions = mlp.predict(X_test)
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))
