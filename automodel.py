import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import time

# Cargar y preparar los datos
url = 'daily-min-temperatures.csv'
df = pd.read_csv(url, parse_dates=['Date'], index_col='Date')

# Crear características de tiempo
df['day'] = df.index.day
df['month'] = df.index.month
df['year'] = df.index.year

# Normalizar los datos
scaler_features = MinMaxScaler()
scaler_temp = MinMaxScaler()

X = scaler_features.fit_transform(df[['day', 'month', 'year']])
y = scaler_temp.fit_transform(df[['Temp']])

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear el modelo MLP
model = Sequential([
    Dense(64, activation='relu', input_shape=(3,)),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(1)
])

# Compilar el modelo
model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

# Variable para almacenar el número de la última fila procesada
last_row_saved = -1

while True:
    # Cargar los datos de nuevo para verificar si hay cambios
    df_new = pd.read_csv(url, parse_dates=['Date'], index_col='Date')

    # Crear características de tiempo
    df_new['day'] = df_new.index.day
    df_new['month'] = df_new.index.month
    df_new['year'] = df_new.index.year

    # Obtener el número de la última fila actual
    last_row_current = df_new.shape[0] - 1

    # Si ha habido cambios en las filas
    if last_row_current != last_row_saved:
        # Actualizar los datos normalizados
        X = scaler_features.fit_transform(df_new[['day', 'month', 'year']])
        y = scaler_temp.fit_transform(df_new[['Temp']])

        # Dividir los datos en conjuntos de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Entrenar el modelo
        history = model.fit(X_train, y_train, validation_split=0.2, epochs=100, batch_size=32, verbose=0)

        # Guardar el modelo con el número de fila en el nombre del archivo
        model_filename = f'model-{last_row_current}.h5'
        model.save(model_filename)

        # Actualizar la variable con el número de la última fila procesada
        last_row_saved = last_row_current

        print(f"Modelo guardado como {model_filename}")
    else:
        print("No hay cambios en las filas. No se realizó el entrenamiento ni se guardó el modelo.")

    # Esperar un tiempo antes de volver a verificar
    time.sleep(60)  # Esperar 60 segundos antes de la siguiente verificación
