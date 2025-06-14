# TORCS-AI-Agent
# TORCS AI Racing Driver using TensorFlow

This project implements an AI racing driver for [TORCS](http://torcs.sourceforge.net/) (The Open Racing Car Simulator) using supervised learning with TensorFlow/Keras. The system learns from human driving data and interfaces directly with TORCS to control a car in real-time.

![Training History](training_history.png)

## 🚗 Project Overview

We developed an AI agent capable of autonomous racing in TORCS. The workflow includes:

- Data collection from human driving
- Feature engineering of sensor and control data
- Neural network training using TensorFlow
- Integration of the trained model with the TORCS simulator

---

## 🧠 Model Architecture

The AI driver model combines feedforward and recurrent layers to learn both spatial and temporal aspects of driving:

- **Input:** Normalized sensor data (speed, position, angle, RPM, etc.)
- **LSTM Layer:** Learns temporal dependencies from sequential inputs
- **Dense Layers:** Processes static features and combines outputs
- **Outputs:** Acceleration, Brake, Steering, Gear

Each output uses appropriate activations:
- `accel`, `brake`: sigmoid (range [0, 1])
- `steer`: tanh (range [-1, 1])
- `gear`: raw integer prediction, post-processed

---


---

## 📊 Data Collection & Processing

We collected around **10,000 samples** from different driving scenarios:

1. Straight track driving
2. Cornering with varying angles
3. Overtaking and position changes
4. Mixed driving conditions

**Preprocessing Steps:**
- Normalized features to [-1, 1]
- Extracted useful stats from raw sensor arrays
- Applied sliding window for temporal modeling
- Converted track sensor data into mean, min, curvature values

---

## ⚙️ Running the Driver

### 1. Start TORCS with SCR server
Make sure SCR server is enabled in TORCS.

### 2. Run the Python Client

```bash
python pyclient.py --host localhost --port 3001 --id SCR --maxEpisodes 1 --stage 2

