# Assignment 3 Plan (PyTorch + Kaggle)

Based on requirements in `.cursor/rules/task_description_hw3.mdc` and aligned with `notebooks/ads_hw2_final.ipynb`.

## Datasets
- **Note:** Reuse existing datasets when possible; only CNN requires image data.
- **CNN:** Flowers-102 (Kaggle: `nunenuh/pytorch-challange-flower-dataset`) at `/kaggle/input/pytorch-challange-flower-dataset`.
- **RNN / Transformer:** Jena Climate (Kaggle: `mnassrib/jena-climate`) at `/kaggle/input/jena-climate`.
- **MLP:** Telco Customer Churn (Kaggle: `beatafaron/telco-customer-churn-realistic-customer-feedback`, file `telco_churn_with_all_feedback.csv`); use raw CSV in-notebook.

## Framework & Environment
- **Framework:** PyTorch (briefly explain why chosen).
- **Runtime:** Kaggle notebook with P100 GPU.
- **Scope:** Clarity-first experiments, avoid unnecessary heavy training.

## Notebook Plan (4 Separate Notebooks)

Each notebook starts with a short **Intro & Setup** section:
- State framework choice and reasoning.
- Describe the dataset and task for that part.
- Set seeds, device (GPU), and common utilities.

### Notebook 1: **Part 1 - MLP (Tabular - Telco Churn)**
- **Tasks:**
  - Binary classification: `Churn` (Yes/No -> 1/0).
  - Regression: `TotalCharges` (numeric; impute median).
- **Preprocessing:** Median impute + standardize (numeric), mode impute + one-hot (categorical).
- **Show:** Training/validation performance, loss curves, final metrics.
- **Experiments (discuss effects with short comments):**
  - **Training & Optimization:**
    - Optimizers: SGD, SGD+momentum, Adam.
    - Learning rate: too small / good / too large.
    - Learning rate scheduling.
    - Batch size effects.
    - Early stopping.
    - Number of epochs.
  - **Architecture & Representation:**
    - Depth (hidden layers).
    - Width (neurons per layer).
    - Activations: ReLU, LeakyReLU, Tanh, Sigmoid.
    - Weight initialization: Xavier, He, random.
    - Batch Normalization.
  - **Regularization & Stability:**
    - L1 / L2 weight regularization.
    - Activity regularization.
    - Dropout.
    - Gradient clipping (optional).
- **Metrics:** Accuracy, F1, ROC-AUC (classification); MAE, MSE, R2 (regression).
- **Discussion:** Why NNs are powerful, why depth is harder to train, and (optional) depth benefits beyond width.
- **Wrap-up:** Summarize findings + optional error analysis.

### Notebook 2: **Part 2 - CNN (Images - Flowers-102)**
- **Task:** Multi-class classification.
- **Model A (Custom):** Conv layers -> pooling -> fully connected.
- **Show:** Training curves and performance metrics (accuracy, loss).
- **Experiments (comment on capacity, over/underfitting, training time, performance):**
  - Kernel size (receptive field).
  - Strides.
  - Number of filters.
  - Pooling type and pooling window size (max vs avg).
  - Depth of the network.
- **Data Augmentation:** Random flips, rotations, crops, normalization and/or color jitter; analyze impact on overfitting/generalization.
- **Model B (Transfer Learning):** Choose one pretrained model (e.g., ResNet18, VGG19).
  - Feature extraction or fine-tuning.
  - Clearly state which layers are frozen (if any).
  - Compare performance to custom CNN.
- **Discussion:** Why CNNs are more parameter-efficient than MLPs; when MLPs could match and why it is unrealistic in practice.
- **Wrap-up:** Summarize findings + optional error analysis.

### Notebook 3: **Part 3 - RNN (Time Series - Jena Climate)**
- **Task:** Forecast `T (degC)` (next step or future window).
- **Preprocessing:** Sliding windows (e.g., input 24/72h -> predict next), normalize features.
- **Models (train all three):** Vanilla RNN, LSTM, GRU (use high-level `nn.*` modules).
- **Experiments:**
  - Sequence length.
  - Hidden size.
  - One vs multiple recurrent layers.
  - Bidirectional vs unidirectional.
  - Dropout between recurrent layers.
- **Discussion:** Why LSTM/GRU outperform vanilla RNNs for long sequences; role of gates and vanishing gradients.
- **Wrap-up:** Summarize findings + optional error analysis.

### Notebook 4: **Part 4 - Transformer (Time Series - Jena Climate)**
- **Approach:** Use a Transformer encoder layer from PyTorch (`nn.TransformerEncoder`) (option 2).
- **Task:** Apply to the same forecasting task; compare vs RNN/LSTM.
- **Discussion (cover all points):**
  - Advantages and disadvantages of Transformers.
  - Why they scale well with data/model size.
  - Why they need more compute.
  - What self-attention is and what it solves.
  - Why attention captures long-range dependencies better than RNNs.
  - What multi-head attention is and why it helps.
  - Role of positional encoding.
- **Research Report (Bonus, placed here to keep 4 notebooks total):**
  - **Topic:** "Which Machine Learning Models Are Actually Used in Industry?"
  - **Sources:** Use credible reports/surveys/industry blogs (include citations/links).
  - **Part 1:** Which model families are most widely used today.
  - **Part 2:** 2-3 paragraph prediction for 5-10 years.
    - Discuss classical models vs deep learning/LLMs and domain shifts.
  - **Format:** Short written report (1-3 pages equivalent).
- **Wrap-up:** Summarize findings + optional error analysis.

## Submission Notes
- Use the same GitHub repo as HW1/HW2.
- Provide GitHub link and Colab link (if used).
- Submit **four notebooks** (one per part); if a single notebook is required, merge or provide a combined version at the end.
- Optional: update `README.md` with experiment summary.
- Be ready for a short in-person review.
- Collaboration policy: individual work only.
