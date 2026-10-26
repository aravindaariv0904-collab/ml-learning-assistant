# 30-Day Automated Machine Learning Daily Learning Assistant
### Autonomous Cloud Orchestrator • Zero-Cost Python Stack

An autonomous, 100% cloud-hosted learning pipeline that delivers structured, mathematically rigorous machine learning masterclasses every single day. Orchestrated automatically via GitHub Actions, verified in an isolated execution sandbox, and distributed across Google Drive, Google Calendar, Gmail, and Slack.

---

## 🏛️ System Architecture

```
                       [ 3:00 PM IST Cron / Manual Dispatch ]
                                        │
                                        ▼
                      ┌────────────────────────────────────┐
                      │    GitHub Actions Cloud Runner     │
                      └─────────────────┬──────────────────┘
                                        │
                                        ▼
                       ┌──────────────────────────────────┐
                       │         orchestrator.py          │
                       │   (Roadmap & State Management)   │
                       └────────────────┬─────────────────┘
                                        │
                ┌───────────────────────┼────────────────────────┐
                ▼                       ▼                        ▼
       [ Stage 1: Notes ]      [ Stage 2: Slides ]     [ Stage 3: HTML ]
       Intuition -> Math ->    12-16 Widescreen        Interactive Jinja2 +
       Steps -> Python Code    Presentation Deck       Tailwind CSS +
       -> Pitfalls -> Q&A      (python-pptx)           Vanilla JS Quiz
                │
                ▼
       ┌──────────────────────────────────────────────────┐
       │             Isolated Code Sandbox                │
       │   ast syntax check -> subprocess execution       │
       │   capture stdout/stderr -> set validation badge  │
       └────────────────────────┬─────────────────────────┘
                                │
        ┌───────────────────────┴────────────────────────┐
        ▼                       ▼                        ▼
  [ Google Drive ]     [ Google Calendar ]      [ Gmail & Slack ]
  Idempotent upload    Idempotent 7-9 PM IST    Rich HTML email &
  & shareable links    session + 15m reminder   Block Kit cards
                                │
                                ▼
                      ┌───────────────────┐
                      │    state.json     │
                      │ (Git commit-back) │
                      └───────────────────┘
```

---

## 📅 30-Day Curriculum Roadmap

The curriculum is tracked in `state.json` across 4 progressive engineering weeks:

### Week 1: Foundations & Regression (Days 1–7)
- **Day 01 (Foundations):** Introduction to Machine Learning
- **Day 02 (Foundations):** Python for Machine Learning (NumPy, Pandas, Vectorization)
- **Day 03 (Foundations):** Data Cleaning and Preprocessing (Imputation, Outliers, Transforms)
- **Day 04 (Regression):** Linear Regression (Closed-form OLS, Gauss-Markov Assumptions)
- **Day 05 (Regression):** Regression Evaluation Metrics (MAE, MSE, RMSE, Adjusted $R^2$)
- **Day 06 (Regression):** Polynomial Regression (Basis Expansions, Bias-Variance Tradeoff)
- **Day 07 (Regression):** Ridge, Lasso, and ElasticNet (L1/L2 Regularization, Sparsity)

### Week 2: Classification Models & Metrics (Days 8–14)
- **Day 08 (Classification):** Logistic Regression (Sigmoid, Cross-Entropy Loss, Odds Ratios)
- **Day 09 (Classification):** K-Nearest Neighbors (Distance Metrics, Curse of Dimensionality, KD-Trees)
- **Day 10 (Classification):** Naive Bayes (Bayes' Theorem, Conditional Independence, Laplace Smoothing)
- **Day 11 (Classification):** Support Vector Machines (Maximum Margin Hyperplane, Kernel Trick)
- **Day 12 (Classification):** Decision Trees (Shannon Entropy, Information Gain, Gini Impurity)
- **Day 13 (Classification):** Random Forest (Bootstrap Aggregation, Out-Of-Bag Error)
- **Day 14 (Classification):** Classification Evaluation Metrics (Confusion Matrix, ROC-AUC, PR Curves)

### Week 3: Ensembles, Validation & Clustering (Days 15–21)
- **Day 15 (Ensemble):** Ensemble Learning, Bagging, and Voting (Hard/Soft Voting, Stacking)
- **Day 16 (Ensemble):** AdaBoost and Gradient Boosting (Exponential Loss, Pseudo-Residuals)
- **Day 17 (Ensemble):** XGBoost (2nd-Order Taylor Approximation, Regularized Objectives)
- **Day 18 (Validation):** Train-Test Split and Cross-Validation (TimeSeriesSplit, Leakage Audit)
- **Day 19 (Validation):** Hyperparameter Tuning (Optuna, Bayesian Optimization, TPE)
- **Day 20 (Unsupervised):** K-Means Clustering (Lloyd's Algorithm, K-Means++, Silhouette Score)
- **Day 21 (Unsupervised):** Hierarchical Clustering, DBSCAN, and PCA (Dendrograms, Density, SVD)

### Week 4: Pipelines, Production & Capstone Projects (Days 22–30)
- **Day 22 (Pipelines):** Feature Engineering (Target Encoding, Mutual Information, Interactions)
- **Day 23 (Foundations):** Probability and Statistics Revision (Hypothesis Testing, CLT, p-values)
- **Day 24 (Pipelines):** Machine Learning Pipelines (Scikit-Learn `ColumnTransformer`, `BaseEstimator`)
- **Day 25 (Evaluation):** Model Comparison and Error Analysis (McNemar's Test, Slice Analysis)
- **Day 26 (Production):** Model Saving and Inference (Joblib, ONNX Runtime Portability)
- **Day 27 (Production):** Deploying an ML Model Using FastAPI (Asynchronous Endpoints, Pydantic)
- **Day 28 (Projects):** Regression Project (End-to-End Predictive Pricing Pipeline)
- **Day 29 (Projects):** Classification Project (End-to-End Fraud & Churn Detection System)
- **Day 30 (Projects):** Revision and Project Presentation (Mastery Review & System Design Defense)

---

## ⚡ Workspace Directory Structure

```
ml-learning-assistant/
├── .github/
│   └── workflows/
│       └── daily_ml_runner.yml    # Cron at 3:00 PM IST (9:30 UTC) with git commit-back
├── generators/
│   ├── __init__.py
│   ├── code_sandbox.py            # Subprocess AST & code execution validator
│   ├── llm_client.py              # Gemini & Anthropic Claude multi-provider client
│   └── pptx_builder.py            # 16:9 widescreen PowerPoint deck builder
├── integrations/
│   ├── __init__.py
│   ├── google_workspace.py        # Google Drive, Calendar v3, and Gmail API handlers
│   └── slack_notifier.py          # Slack Block Kit rich card dispatcher
├── templates/
│   └── lesson_template.html       # Jinja2 template with Tailwind CSS & interactive quiz
├── dist_html/                     # Rendered HTML lessons ready for GitHub Pages hosting
├── dist_pptx/                     # Generated native 16:9 .pptx slide presentations
├── dist_notes/                    # Pedagogical detailed Markdown notes (.md)
├── state.json                     # State of truth (current day, progress, delivery logs)
├── orchestrator.py                # Central pipeline engine & CLI
├── requirements.txt               # Pinned dependencies
├── .env.example                   # Environment configuration template
└── README.md                      # Documentation & architecture guide
```

---

## 🚀 Quickstart & Local Testing

### 1. Installation
Clone the repository and install requirements:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run Dry-Run (Local verification without cloud calls)
```bash
python orchestrator.py --dry-run
```
Output:
- Markdown notes written to `dist_notes/`
- Python code blocks extracted and sandboxed with execution telemetry
- 16:9 PowerPoint deck generated in `dist_pptx/`
- Interactive HTML rendered to `dist_html/` with instant-feedback quiz
- `state.json` updated with validation status

### 3. Run Specific Day
```bash
python orchestrator.py --day 5 --dry-run
```

---

## ☁️ Cloud Services & Secrets Configuration

To run autonomously on GitHub Actions, configure the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions > Repository secrets**):

| Secret Name | Description | Example / Format |
|---|---|---|
| `AI_API_KEY` | Google Gemini API Key or Anthropic Claude API Key | `AIzaSy...` or `sk-ant-...` |
| `GCP_SA_KEY` | Google Cloud Service Account JSON Key (Raw or Base64) | `{"type": "service_account", ...}` |
| `RECIPIENT_EMAIL` | Email address where daily lessons and calendar invites are sent | `student@example.com` |
| `SLACK_WEBHOOK_URL` | Incoming webhook URL for `#ml-learning` channel | `https://hooks.slack.com/services/...` |
| `GOOGLE_CALENDAR_ID` | Optional: Dedicated Calendar ID (defaults to `primary`) | `primary` |
| `GOOGLE_DRIVE_FOLDER_ID`| Optional: Target Google Drive Folder ID | `1AbCdEfGhIjKlMnOp...` |
| `GMAIL_DELEGATED_USER` | Optional: Domain-wide delegated user email for Gmail API | `admin@yourdomain.com` |

### Setting Up Google Cloud Service Account
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a Project and enable:
   - **Google Drive API**
   - **Google Calendar API**
   - **Gmail API**
3. Create a Service Account (**IAM & Admin > Service Accounts > Create**).
4. Create a JSON Key and copy the JSON string into `GCP_SA_KEY`.
5. Share your Google Drive target folder and Google Calendar with the service account email (e.g. `service-account@project.iam.gserviceaccount.com`).

---

## 🛡️ Idempotency & Fault Tolerance

1. **Duplicate Drive Upload Prevention:** Before uploading `.pptx` or `.md`, the manager queries Drive for existing files matching the day name. If found, it updates the existing file in place rather than creating duplicate files.
2. **Calendar Conflict Prevention:** Checks today's events for `[ML Sprint] Day XX` and updates existing entries instead of spawning duplicates.
3. **Execution Sandboxing:** Subprocess executes Python code blocks with strict 30-second timeouts, headless Matplotlib (`Agg` backend), and AST syntax validation.
4. **State Commit-Back:** GitHub Actions runner commits `state.json` back to the repository using git pull-rebase logic to prevent race conditions.

---

## 📜 License
MIT License. Engineered for autonomous, continuous machine learning mastery.
