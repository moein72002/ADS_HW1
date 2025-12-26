# Assignment 3 Plan (PyTorch + Kaggle)

Based on requirements in `.cursor/rules/task_description_hw3.mdc` and aligned with `notebooks/ads_hw2_final.ipynb`.

## Datasets
- **CNN:** Flowers-102 (Kaggle: `nunenuh/pytorch-challange-flower-dataset`) at `/kaggle/input/pytorch-challange-flower-dataset`
- **RNN / Transformer:** Jena Climate (Kaggle: `mnassrib/jena-climate`) at `/kaggle/input/jena-climate`
- **MLP:** Telco Customer Churn (Kaggle: `beatafaron/telco-customer-churn-realistic-customer-feedback`, file `telco_churn_with_all_feedback.csv`); use raw CSV in-notebook.

## Framework & Environment
- **Framework:** PyTorch
- **Runtime:** Kaggle notebook with P100 GPU
- **Scope:** Systematic experiments and comparisons.

## Notebook Outline (Single Notebook)

1. **Intro & Setup**
   - State framework choice (PyTorch) and reasoning.
   - Describe datasets and tasks.
   - Set seeds, device (GPU), and utilities.

2. **MLP Section (Tabular - Telco Churn)**
   - **Tasks:**
     - Binary classification: `Churn` (Yes/No → 1/0)
     - Regression: `TotalCharges` (numeric; impute median)
   - **Preprocessing:** Median impute/Standardize (numeric), Mode impute/One-hot (categorical).
   - **Experiments (Analyze effects):**
     - **Optimization:** Optimizers (SGD vs Adam), LR scheduling, Batch size, Epochs.
     - **Architecture:** Depth (layers), Width (neurons), Activations (ReLU/LeakyReLU), Init (Xavier/He), Batch Norm.
     - **Regularization:** Dropout, L2 (Weight Decay).
   - **Metrics:** Accuracy, F1, ROC-AUC (Classif); MAE, MSE, R2 (Reg).
   - **Discussion:** Power of NNs, depth difficulty, Universal Approximation vs depth benefits.

3. **CNN Section (Images - Flowers-102)**
   - **Task:** Multi-class classification.
   - **Model A (Custom):** Conv blocks → Pooling → FC.
   - **Experiments:**
     - Kernel size, Stride, Filter counts.
     - Pooling types (Max vs Avg).
     - Depth effects.
   - **Model B (Transfer Learning):** ResNet18 or VGG19.
     - Feature extraction (frozen features) vs Fine-tuning.
   - **Data Augmentation:** Flips, rotations, crops, normalization. Analyze impact on overfitting.
   - **Metrics:** Accuracy, Loss curves.
   - **Discussion:** Parameter efficiency of CNNs vs MLPs, when MLPs might match CNNs.

4. **RNN Section (Time Series - Jena Climate)**
   - **Task:** Forecast `T (degC)` (next step or future window).
   - **Preprocessing:** Sliding windows (e.g., input 24/72h -> predict next). Normalize.
   - **Models:** Implement **Vanilla RNN**, **LSTM**, and **GRU**.
   - **Experiments:**
     - Sequence length.
     - Hidden size.
     - Stacked layers (One vs Multiple).
     - Bidirectional vs Unidirectional.
     - Dropout.
   - **Metrics:** MAE, MSE, Loss curves.
   - **Discussion:** LSTM/GRU vs Vanilla (gradients), Role of gates.

5. **Transformer Section (Time Series - Jena Climate)**
   - **Task:** Forecast `T (degC)` (same as RNN for comparison).
   - **Model:** **Transformer Encoder** (Option 2) using `nn.TransformerEncoder` or similar.
     - *Reasoning:* Allows direct performance comparison with RNN/LSTM on the same sequence task.
   - **Comparison:** Compare performance (MSE/MAE, convergence speed) vs RNN/LSTM.
   - **Discussion:** Advantages/Disadvantages, Scaling, Self-attention explanation, Positional encoding role.

6. **Research Report (Bonus)**
   - **Topic:** "Which Machine Learning Models Are Actually Used in Industry?"
   - **Content:**
     - Current industry favorites (Surveys/Reports).
     - Future predictions (5-10 years).
     - Shift in domains (Classical vs Deep Learning/LLM).
   - **Format:** Short text section in notebook (1-2 pages equivalent).

7. **Wrap-up**
   - Summary of key findings per section.
   - (Optional) Error analysis.

## Deliverables
- One clean `.ipynb` file.
- `README.md` update (optional bonus).
