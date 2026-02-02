# PINN demonstrativa para a lei de resfriamento de Newton (TensorFlow)
# Equacao: dT/dt = -k (T - T_amb)

import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

# Reprodutibilidade
SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)

# Parametros do problema
# Valores alternativos para observar aquecimento (T0 < T_amb)
T_amb = 60
T0 = 30
k = 0.05
T_MAX = 100.0

# Para compatibilidade com MATLAB/HDL: force parametros escalares como float
T_amb_f = float(T_amb)
T0_f = float(T0)
k_f = float(k)
T_MAX_f = float(T_MAX)

# Hiperparametros
EPOCHS = 20000
N_F = 1000
LR = 1e-3
PRINT_EVERY = 200


def analytical_solution(t):
    return T_amb + (T0 - T_amb) * np.exp(-k * t)


def build_model():
    inputs = tf.keras.Input(shape=(1,))
    x = inputs
    for _ in range(3):
        x = tf.keras.layers.Dense(32, activation=tf.nn.tanh)(x)
    outputs = tf.keras.layers.Dense(1)(x)
    return tf.keras.Model(inputs, outputs)


model = build_model()
optimizer = tf.keras.optimizers.Adam(LR)


@tf.function
def train_step():
    t_f = tf.random.uniform((N_F, 1), 0.0, T_MAX, dtype=tf.float32)
    t0 = tf.zeros((1, 1), dtype=tf.float32)
    T0_target = tf.constant([[T0]], dtype=tf.float32)

    with tf.GradientTape(persistent=True) as tape:
        tape.watch(t_f)
        T_pred = model(t_f)
        dTdt = tape.gradient(T_pred, t_f)
        residual = dTdt + k * (T_pred - T_amb)

        T0_pred = model(t0)
        loss_pde = tf.reduce_mean(tf.square(residual))
        loss_ic = tf.reduce_mean(tf.square(T0_pred - T0_target))
        loss = loss_pde + loss_ic

    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return loss


for epoch in range(1, EPOCHS + 1):
    loss = train_step()
    if epoch % PRINT_EVERY == 0:
        print(f"Epoch {epoch:5d} | Loss {loss.numpy():.6e}")

# Avaliacao simples
print("\nAvaliando...")
t_eval = np.linspace(0, T_MAX, 200).reshape(-1, 1).astype(np.float32)
T_pred = model.predict(t_eval, verbose=0).reshape(-1)
T_true = analytical_solution(t_eval.reshape(-1))
rmse = np.sqrt(np.mean((T_pred - T_true) ** 2))
print(f"RMSE: {rmse:.6f}")

# Comparacao grafica
plt.figure(figsize=(8, 4))
plt.plot(t_eval, T_true, "k--", linewidth=2, label="Analytical")
plt.plot(t_eval, T_pred, "b", linewidth=2, label="PINN")
plt.xlabel("t (s)")
plt.ylabel("T (C)")
plt.title("Newton Cooling - PINN")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# Exporta pesos para reutilizacao no MATLAB
weights = model.get_weights()
W = weights[0::2]
b = weights[1::2]

# Modo fixo (HDL-friendly): salva cada camada separadamente (arrays numericos)
W1, W2, W3, W4 = W
b1, b2, b3, b4 = b

# Usa object arrays para permitir tamanhos diferentes por camada
np.savez(
    "pinn_weights.npz",
    W=np.array(W, dtype=object),
    b=np.array(b, dtype=object),
    W1=W1,
    b1=b1,
    W2=W2,
    b2=b2,
    W3=W3,
    b3=b3,
    W4=W4,
    b4=b4,
    T_amb=T_amb_f,
    T0=T0_f,
    k=k_f,
    T_MAX=T_MAX_f,
)
print("Pesos salvos em pinn_weights.npz")

try:
    from scipy.io import savemat

    savemat(
        "pinn_weights.mat",
        {
            "W": np.array(W, dtype=object),
            "b": np.array(b, dtype=object),
            "W1": W1,
            "b1": b1,
            "W2": W2,
            "b2": b2,
            "W3": W3,
            "b3": b3,
            "W4": W4,
            "b4": b4,
            "T_amb": T_amb_f,
            "T0": T0_f,
            "k": k_f,
            "t_max": T_MAX_f,
        },
    )
    print("Pesos salvos em pinn_weights.mat")
except Exception as exc:
    print("Nao foi possivel salvar .mat (scipy nao instalado).")
    print(f"Motivo: {exc}")
