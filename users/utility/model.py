import os
import math
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from django.conf import settings

# ============================= #
#   Image Generator with Aug    #
# ============================= #
def generator(
    dir,
    gen=ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True
    ),
    shuffle=True,
    batch_size=32,
    target_size=(64, 64),
    class_mode='categorical'
):
    return gen.flow_from_directory(
        dir,
        batch_size=batch_size,
        shuffle=shuffle,
        color_mode='grayscale',
        class_mode=class_mode,
        target_size=target_size
    )

BS = 32
TS = (64, 64)

train_dir = os.path.join(settings.MEDIA_ROOT, 'data', 'train')
valid_dir = os.path.join(settings.MEDIA_ROOT, 'data', 'valid')

train_batch = generator(train_dir, batch_size=BS, target_size=TS)
valid_batch = generator(valid_dir, batch_size=BS, target_size=TS)

SPE = math.ceil(train_batch.samples / BS)
VS = math.ceil(valid_batch.samples / BS)

print(f"Steps per epoch: {SPE}, Validation steps: {VS}")

# ============================= #
#   Hybrid CNN + Transformer    #
# ============================= #
def hybrid_cnn_transformer_model(input_shape=(64, 64, 1), num_classes=4):
    inputs = layers.Input(shape=input_shape)

    # CNN Feature Extractor
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.Reshape((-1, 128))(x)  # flatten to sequence

    # Transformer Encoder
    attention_output = layers.MultiHeadAttention(num_heads=4, key_dim=64)(x, x)
    x = layers.Add()([attention_output, x])
    x = layers.LayerNormalization()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.GlobalAveragePooling1D()(x)

    # Final classification head
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    return Model(inputs=inputs, outputs=outputs)

model = hybrid_cnn_transformer_model(input_shape=(64, 64, 1), num_classes=4)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ============================= #
#      Add Callbacks            #
# ============================= #
callbacks = [
    tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
    tf.keras.callbacks.ModelCheckpoint(
        os.path.join(settings.MEDIA_ROOT, 'models', 'best_model.h5'),
        monitor='val_accuracy',
        save_best_only=True
    )
]

# ============================= #
#         Train Model           #
# ============================= #
model.fit(
    train_batch,
    validation_data=valid_batch,
    epochs=30,
    steps_per_epoch=SPE,
    validation_steps=VS,
    callbacks=callbacks
)

# ============================= #
#          Save Final           #
# ============================= #
model_dir = os.path.join(settings.MEDIA_ROOT, 'models')
os.makedirs(model_dir, exist_ok=True)
final_model_path = os.path.join(model_dir, 'Dp_hybrid_final.h5')
model.save(final_model_path)
print(f"Model saved to: {final_model_path}")
