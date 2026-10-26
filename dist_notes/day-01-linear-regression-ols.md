# Day 01: Linear Regression & Ordinary Least Squares (OLS)

**Module:** Foundations & Regression  
**Curriculum Track:** 30-Day Production Machine Learning  
**Execution Timestamp:** 2026-10-26 21:37:24  

---

## 1. Intuition & Real-World Mental Model
In real-world predictive systems, **Linear Regression & Ordinary Least Squares (OLS)** bridges the critical gap between raw empirical observations and actionable statistical inference. Imagine building an algorithmic valuation engine for an enterprise portfolio. Naive heuristics suffer from noisy fluctuations and lack generalization.

Linear Regression & Ordinary Least Squares (OLS) establishes a mathematically optimal decision boundary by minimizing an explicit objective function. It transforms multi-dimensional feature representations into calibrated predictions, enabling engineers to reason about variance, uncertainty, and structural tradeoffs.

---

## 2. Mathematical Formulation & Foundations
Let our feature matrix be denoted as $X \in \mathbb{R}^{n \times d}$ and our target response vector as $y \in \mathbb{R}^{n}$. The model expresses the hypothesis as:

$$\hat{y} = X \theta + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \sigma^2 I)$$

The penalized risk minimization objective balances empirical data fidelity with regularized parameter constraints:

$$\mathcal{L}(\theta) = \frac{1}{2n} \|X \theta - y\|_2^2 + \lambda \mathcal{R}(\theta)$$

Where:
- $\lambda \ge 0$ governs the regularization trade-off penalty.
- When $\mathcal{R}(\theta) = \|\theta\|_2^2$, we obtain the $L_2$ Ridge regression objective.
- Setting $\nabla_\theta \mathcal{L}(\theta) = 0$ yields the normal equation with regularization:

$$\theta^* = (X^T X + \lambda I)^{-1} X^T y$$

This formulation guarantees invertibility even when features are collinear ($X^T X$ is singular or ill-conditioned).

---

## 3. Algorithmic Step-by-Step Breakdown
The complete deterministic training and evaluation workflow unfolds across four disciplined phases:

1. **Step 1: Input Validation & Preprocessing Isolation**
   - Partition dataset into stratified training and validation sets before executing any data transformations.
   - Standardize numerical covariates: $z = \frac{x - \mu}{\sigma}$, fitting exclusively on $X_{train}$.

2. **Step 2: Objective Optimization**
   - Compute matrix gram product $X^T X$ and invert with regularization parameter $\lambda$.
   - Alternatively, perform iterative optimization via Gradient Descent with step size $\alpha$.

3. **Step 3: Out-Of-Fold Validation & Metric Calculation**
   - Compute residual vector: $e = y_{val} - \hat{y}_{val}$.
   - Quantify performance using Root Mean Squared Error (RMSE) and $R^2$ coefficient of determination.

4. **Step 4: Residual Diagnostics & Assumption Verification**
   - Verify normality of errors via Q-Q plots.
   - Confirm homoscedasticity: constant variance of residuals across predicted values.

---

## 4. Production-Ready Python Code
The following implementation is self-contained, follows scikit-learn best practices, and executes without runtime or dimensional errors.

```python
import numpy as np
import pandas as pd
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. Synthesize reproducible benchmark dataset
np.random.seed(42)
X_raw, y_raw = make_regression(
    n_samples=500,
    n_features=10,
    n_informative=6,
    noise=12.5,
    random_state=42
)

# 2. Strict Train/Test partition to prevent data leakage
X_train, X_test, y_train, y_test = train_test_split(
    X_raw, y_raw, test_size=0.2, random_state=42
)

# 3. Fit scaler ONLY on training data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. Model fitting with L2 regularization
model = Ridge(alpha=1.0)
model.fit(X_train_scaled, y_train)

# 5. Inference and evaluation
y_pred_train = model.predict(X_train_scaled)
y_pred_test = model.predict(X_test_scaled)

train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_r2 = r2_score(y_test, y_pred_test)

print("--- MODEL VALIDATION TELEMETRY ---")
print(f"Train RMSE : {train_rmse:.4f}")
print(f"Test RMSE  : {test_rmse:.4f}")
print(f"Test R^2   : {test_r2:.4f}")
print(f"Model Intercept: {model.intercept_:.4f}")
print(f"Non-zero Coefficients: {np.count_nonzero(model.coef_)}/{len(model.coef_)}")
```

---

## 5. Common Pitfalls & Data Leakage Warnings
1. **Target Leakage via Global Scaling:**
   *Hazard:* Applying `StandardScaler().fit_transform(X)` on the combined dataset before train/test splitting.  
   *Mitigation:* Always encapsulate transformers inside a Scikit-Learn `Pipeline`.

2. **Multicollinearity & Matrix Singularity:**
   *Hazard:* Two or more collinear features cause $\det(X^T X) \approx 0$, leading to numerical explosion of coefficients.  
   *Mitigation:* Check Variance Inflation Factors (VIF > 5) or apply $L_2$ regularization.

3. **Temporal Lookahead Bias in Time-Series:**
   *Hazard:* Using standard shuffle K-Fold cross validation on time-dependent data.  
   *Mitigation:* Enforce `TimeSeriesSplit` where training folds strictly precede validation windows.

4. **Ignoring Residual Heteroscedasticity:**
   *Hazard:* Residual variance expanding as a function of predicted magnitude, violating OLS assumptions.  
   *Mitigation:* Apply log or Box-Cox power transformations to the target variable $y$.

---

## 6. 5 High-Yield Interview Questions & Answers

### Q1 [Junior]: What is the fundamental difference between $R^2$ and Adjusted $R^2$?
**Answer:** $R^2 = 1 - \frac{SS_{res}}{SS_{tot}}$ measures the proportion of variance explained by the model, but it monotonically increases whenever a new feature is added, even if it is random noise. Adjusted $R^2$ incorporates a degrees-of-freedom penalty:
$$\bar{R}^2 = 1 - \left(1 - R^2\right) \frac{n - 1}{n - p - 1}$$
where $n$ is sample size and $p$ is the number of features. It only increases if the new variable enhances the model beyond chance.

### Q2 [Mid-Level]: Why does $L_1$ (Lasso) induce sparse solutions while $L_2$ (Ridge) merely shrinks weights?
**Answer:** Geometrically, the $L_1$ constraint region is a diamond/polytope with sharp vertices on coordinate axes ($\sum |\theta_i| \le t$), whereas $L_2$ is a smooth hypersphere ($\sum \theta_i^2 \le t^2$). The elliptical contours of the quadratic loss function are significantly more likely to intersect an $L_1$ constraint at a corner where one or more coordinates equal zero, resulting in exact sparsity and automated feature selection.

### Q3 [Senior]: How do you detect and mitigate data leakage when engineering rolling aggregate features in production pipelines?
**Answer:** Rolling window features (e.g., 7-day average spend) must be computed with strict exclusive lags (`shift(1)`) so that the event at timestamp $t$ does not incorporate information from timestamp $t$. In cross-validation, an embargo buffer must separate training folds from evaluation splits to prevent temporal leakage across window boundaries.

### Q4 [Staff]: When would you reject Ordinary Least Squares in favor of Quantile Regression or Huber Loss?
**Answer:** OLS minimizes squared error loss ($\ell_2$), making parameter estimates highly sensitive to extreme outliers and fat-tailed residual distributions (influence proportional to residual magnitude). Huber Loss offers quadratic behavior for small errors and linear behavior for large errors, delivering robust estimators. Quantile Regression minimizes asymmetric absolute pinball loss, allowing modeling of conditional medians or specific risk quantiles (e.g., 95th percentile latency).

### Q5 [System Design]: How do you structure real-time latency monitoring for this estimator serving 10,000 requests per second?
**Answer:** Serialize the scikit-learn pipeline into ONNX format for accelerated runtime evaluation with C++ execution providers. Deploy behind an asynchronous FastAPI / Triton inference gateway with batching. Expose Prometheus metrics for P50, P95, and P99 latency, and publish input vector distributions to a streaming Kafka buffer for continuous Kolmogorov-Smirnov drift detection against training baselines.
