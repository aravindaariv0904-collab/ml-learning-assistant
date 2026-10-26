"""
Modular Multi-Provider LLM Client
Supports OpenRouter (free tier models like gemini-2.0-flash, llama-3.3-70b, deepseek-r1),
Google Gemini (via google-genai SDK or REST API), and Anthropic Claude SDK,
with automatic fallback, multi-provider retry, and structured output parsing.
"""

import json
import logging
import os
import re
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

logger = logging.getLogger("LLMClient")


class LLMClient:
    """
    Coordinates AI prompt completions across OpenRouter, Gemini, Anthropic, or an intelligent
    deterministic fallback generator when API keys are not supplied.
    """

    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")

        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("AI_API_KEY", "").startswith("sk-ant-"):
            self.anthropic_api_key = os.getenv("AI_API_KEY")

        # Preferred provider override or auto-detect
        self.preferred_provider = os.getenv("LLM_PROVIDER")
        self.providers_order = self._determine_providers_order()
        logger.info(f"LLM Client initialized with provider order: {self.providers_order}")

    def _determine_providers_order(self) -> List[str]:
        """
        Determines the priority order for LLM calls based on configured keys and preferences.
        """
        available = []

        # If user explicitly preferred a provider:
        if self.preferred_provider:
            pref = self.preferred_provider.lower().strip()
            if pref == "openrouter" and self.openrouter_api_key:
                available.append("openrouter")
            elif pref in ["gemini", "google"] and self.gemini_api_key:
                available.append("gemini")
            elif pref == "anthropic" and self.anthropic_api_key:
                available.append("anthropic")

        # Default order: openrouter (free tier) -> gemini -> anthropic
        if self.openrouter_api_key and "openrouter" not in available:
            available.append("openrouter")
        if self.gemini_api_key and "gemini" not in available:
            available.append("gemini")
        if self.anthropic_api_key and "anthropic" not in available:
            available.append("anthropic")

        if not available:
            logger.warning("No OPENROUTER_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY found. Running in offline curriculum mode.")
            available.append("offline")

        return available

    @property
    def primary_provider(self) -> str:
        return self.providers_order[0] if self.providers_order else "offline"

    def generate_completion(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Attempts completions across the provider fallback chain.
        """
        errors = []

        for provider in self.providers_order:
            if provider == "openrouter":
                try:
                    logger.info(f"Calling OpenRouter (Model: {self.openrouter_model})...")
                    return self._call_openrouter(prompt, system_instruction)
                except Exception as e:
                    logger.warning(f"OpenRouter attempt failed: {e}. Falling back to next provider...")
                    errors.append(f"OpenRouter: {e}")

            elif provider == "gemini":
                try:
                    logger.info(f"Calling Google Gemini API (Model: {self.gemini_model})...")
                    return self._call_gemini(prompt, system_instruction)
                except Exception as e:
                    logger.warning(f"Gemini API attempt failed: {e}. Falling back to next provider...")
                    errors.append(f"Gemini: {e}")

            elif provider == "anthropic":
                try:
                    logger.info("Calling Anthropic Claude API...")
                    return self._call_anthropic(prompt, system_instruction)
                except Exception as e:
                    logger.warning(f"Anthropic attempt failed: {e}. Falling back to next provider...")
                    errors.append(f"Anthropic: {e}")

            elif provider == "offline":
                return self._generate_offline_content(prompt)

        # If all external providers failed, use offline deterministic fallback
        logger.error(f"All LLM providers failed ({'; '.join(errors)}). Generating offline content.")
        return self._generate_offline_content(prompt)

    def _call_openrouter(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Calls OpenRouter API using OpenAI-compatible chat completions endpoint.
        Supports free models (e.g. google/gemini-2.0-flash-exp:free, meta-llama/llama-3.3-70b-instruct:free).
        """
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "https://github.com/aravindaariv0904-collab/ml-learning-assistant",
            "X-Title": "30-Day Automated Machine Learning Daily Learning Assistant",
            "Content-Type": "application/json"
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        # Provide fallback models within OpenRouter in case a free model is rate-limited
        free_models_fallback = [
            self.openrouter_model,
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "deepseek/deepseek-r1:free",
            "qwen/qwen-2.5-72b-instruct:free"
        ]
        # De-duplicate while preserving order
        unique_models = list(dict.fromkeys(free_models_fallback))

        payload = {
            "model": self.openrouter_model,
            "models": unique_models,
            "messages": messages,
            "temperature": 0.2
        }

        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()

        choices = data.get("choices", [])
        if not choices:
            raise ValueError(f"OpenRouter returned empty choices: {data}")

        return choices[0]["message"]["content"]

    def _call_gemini(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Calls Google Gemini API using google-genai SDK or REST API fallback.
        """
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.gemini_api_key)
            config = types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=system_instruction,
            )
            response = client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            logger.warning(f"google-genai SDK call failed ({e}); falling back to Gemini REST API.")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": (system_instruction + "\n\n" if system_instruction else "") + prompt}]}],
                "generationConfig": {"temperature": 0.2}
            }
            res = requests.post(url, json=payload, timeout=60)
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_anthropic(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Calls Anthropic Claude API.
        """
        import anthropic
        client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        system = system_instruction or "You are an elite Lead ML Engineer and Systems Architect."
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.2,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def generate_lesson_markdown(self, day_info: Dict[str, Any]) -> str:
        """
        Stage 1: Generates the pedagogical markdown lesson.
        Sequence: Intuition -> Mathematics & Formulas -> Algorithmic Steps ->
        Validated Python Code -> Common Pitfalls & Data Leakage Warnings -> 5 Real-world Interview Q&As.
        """
        title = day_info.get("topic") or day_info.get("title", f"Day {day_info['day']}")
        module = day_info.get("track") or day_info.get("module", "General")
        objectives = day_info.get("learning_objectives", [])
        concepts = day_info.get("core_concepts", [])

        prompt = f"""
Create a rigorous, production-grade technical masterclass for Machine Learning Day {day_info['day']}: "{title}".
Track/Module: {module}
Key Objectives: {', '.join(objectives)}
Core Concepts: {', '.join(concepts)}

You must structure the lesson in high-fidelity Markdown following EXACTLY these 6 sections in order:

# Day {day_info['day']}: {title}

## 1. Intuition & Real-World Mental Model
Explain the core intuition with a memorable industrial engineering analogy (e.g., real estate pricing, finance, medical diagnostics, robotics). Explain what problem it solves that simpler methods fail at.

## 2. Mathematical Formulation & Foundations
Provide complete mathematical derivations using LaTeX notation ($...$ and $$...$$). State the loss functions, objective formulation, optimization objectives, and matrix dimensions clearly.

## 3. Algorithmic Step-by-Step Breakdown
Step 1 through Step N: The exact deterministic computational workflow of the algorithm during training and inference.

## 4. Production-Ready Python Code
Provide clean, idiomatic, fully self-contained, working Python code using NumPy, Pandas, Scikit-Learn, and Matplotlib (configured with headless Agg backend). The code MUST execute without errors, create synthetic or sample data, train the model, evaluate metrics, and print clear summary outputs. Keep it self-contained in a single ```python ... ``` block.

## 5. Common Pitfalls & Data Leakage Warnings
Detail 3 to 5 subtle traps, common data leakage scenarios (e.g., fitting scaler before splitting, target leakage, lookahead bias), and numerical stability hazards. Provide actionable mitigation rules.

## 6. 5 High-Yield Interview Questions & Answers
Provide 5 real-world technical interview questions covering Junior, Mid, Senior, and Staff levels. Include thorough, mathematically grounded answers with tradeoffs.

Format cleanly with standard Markdown headers and code blocks.
"""
        system = "You are a Principal Machine Learning Architect at Google DeepMind with deep mathematical and production engineering expertise."
        return self.generate_completion(prompt, system)

    def generate_presentation_json(self, day_info: Dict[str, Any], markdown_content: str) -> Dict[str, Any]:
        """
        Stage 2: Generates structured 12-16 slide presentation JSON.
        """
        title = day_info.get("topic") or day_info.get("title", f"Day {day_info['day']}")
        module = day_info.get("track") or day_info.get("module", "General")

        prompt = f"""
Based on the following ML lesson for Day {day_info['day']}: "{title}", produce a structured JSON object representing 12 to 14 presentation slides.

Markdown summary of the day:
{markdown_content[:2500]}

Return ONLY a valid JSON object matching this schema without any markdown wrapping (no ```json ... ```):
{{
  "deck_title": "Day {day_info['day']}: {title}",
  "module": "{module}",
  "day_number": {day_info['day']},
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "title",
      "title": "{title}",
      "subtitle": "30-Day Automated Machine Learning Masterclass | Track: {module}",
      "bullets": []
    }},
    {{
      "slide_number": 2,
      "slide_type": "agenda",
      "title": "Roadmap & Executive Agenda",
      "subtitle": "Core Learning Objectives",
      "bullets": [
        "Core Intuition & Problem Space",
        "Mathematical Formulations & Objectives",
        "Algorithmic Mechanics",
        "Python Implementation & Validation",
        "Production Pitfalls & Data Leakage",
        "Senior Interview Edge Cases"
      ]
    }},
    ... (continue until 12-14 slides covering Intuition, Math, Architecture Diagram, Code Structure, Tradeoffs, Pitfalls, Interview Qs, Summary)
    {{
      "slide_number": 12,
      "slide_type": "summary",
      "title": "Key Takeaways & Production Checklist",
      "subtitle": "Daily Summary",
      "bullets": ["Point 1", "Point 2", "Point 3", "Point 4"]
    }}
  ]
}}
Each slide must have:
- "slide_number": int
- "slide_type": one of ["title", "agenda", "concept", "math", "diagram", "code", "pitfalls", "interview", "summary"]
- "title": string (concise, clear)
- "subtitle": string (optional or short)
- "bullets": list of 3-5 concise, high-impact bullet points
- "code_snippet": optional string (only for "code" slides)
- "diagram_text": optional string (ASCII or workflow arrow notation for "diagram" slides)
"""
        response_text = self.generate_completion(prompt)
        cleaned = re.sub(r"^```(?:json)?\n", "", response_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\n```$", "", cleaned.strip(), flags=re.MULTILINE)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            logger.warning("Failed to decode LLM JSON for presentation. Using deterministic fallback generator.")
            return self._generate_fallback_presentation_json(day_info)

    def generate_quiz_json(self, day_info: Dict[str, Any], markdown_content: str) -> List[Dict[str, Any]]:
        """
        Stage 3: Generates 3-5 interactive multiple-choice quiz questions for HTML assessment.
        """
        title = day_info.get("topic") or day_info.get("title", f"Day {day_info['day']}")
        prompt = f"""
Generate 4 multiple-choice assessment questions for Day {day_info['day']}: "{title}".
Content excerpt:
{markdown_content[:2000]}

Return ONLY a valid JSON array of questions without markdown wrapping:
[
  {{
    "id": 1,
    "question": "Clear, technically precise question here?",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "correct_index": 1,
    "explanation": "Detailed explanation of why this option is correct and why other choices fail."
  }}
]
"""
        response_text = self.generate_completion(prompt)
        cleaned = re.sub(r"^```(?:json)?\n", "", response_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\n```$", "", cleaned.strip(), flags=re.MULTILINE)

        try:
            return json.loads(cleaned)
        except Exception:
            match = re.search(r"(\[.*\])", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return self._generate_fallback_quiz_json(day_info)

    def _generate_offline_content(self, prompt: str) -> str:
        """
        Deterministic, offline curriculum generator fallback.
        """
        return """# Offline Generated Masterclass
Content generated via deterministic offline fallback engine.
"""

    def _generate_fallback_presentation_json(self, day_info: Dict[str, Any]) -> Dict[str, Any]:
        """Provides a complete 12-slide structured presentation payload."""
        title = day_info.get("topic") or day_info.get("title", f"Day {day_info['day']}")
        module = day_info.get("track") or day_info.get("module", "General")
        objectives = day_info.get("learning_objectives", [])

        return {
            "deck_title": f"Day {day_info['day']}: {title}",
            "module": module,
            "day_number": day_info['day'],
            "slides": [
                {
                    "slide_number": 1,
                    "slide_type": "title",
                    "title": title,
                    "subtitle": f"30-Day Automated ML Sprint | Track: {module}",
                    "bullets": []
                },
                {
                    "slide_number": 2,
                    "slide_type": "agenda",
                    "title": "Agenda & Session Objectives",
                    "subtitle": "Roadmap Breakdown",
                    "bullets": objectives or [
                        "Theoretical foundations and core intuition",
                        "Mathematical formulation and objective loss",
                        "Production-ready Python implementation",
                        "Validation and data leakage mitigation"
                    ]
                },
                {
                    "slide_number": 3,
                    "slide_type": "concept",
                    "title": "Intuition & Theoretical Motivation",
                    "subtitle": "Why this algorithm matters",
                    "bullets": [
                        f"Fundamental problem space addressed by {title}.",
                        "Contrast with naive heuristics and baseline estimators.",
                        "Core inductive bias and underlying assumptions.",
                        "Computational complexity profiles in training vs inference."
                    ]
                },
                {
                    "slide_number": 4,
                    "slide_type": "math",
                    "title": "Mathematical Formulation & Objective",
                    "subtitle": "Loss Functions & Optimization",
                    "bullets": [
                        "Formal definition of loss function and penalty terms.",
                        "Analytical closed-form derivation vs iterative gradients.",
                        "Convexity, stationary points, and global optimality bounds.",
                        "Matrix vectorization for GPU/SIMD vector acceleration."
                    ]
                },
                {
                    "slide_number": 5,
                    "slide_type": "diagram",
                    "title": "System Architecture & Execution Flow",
                    "subtitle": "Pipeline Topology",
                    "bullets": [
                        "Raw Data Stream -> Schema Validation & Outlier Removal",
                        "Feature Encoding -> Scaling / Normalization Pipeline",
                        "Estimator Fitting -> Cross-Validation Evaluation",
                        "Model Export -> Latency-Optimized Serving Container"
                    ],
                    "diagram_text": "[Raw Input] ---> (Preprocess & Scale) ---> [Fit Estimator] ---> (Score Residuals) ---> [Production Artifact]"
                },
                {
                    "slide_number": 6,
                    "slide_type": "code",
                    "title": "Production Python Implementation",
                    "subtitle": "Idiomatic Scikit-Learn & NumPy Architecture",
                    "bullets": [
                        "Self-contained pipeline execution with deterministic random seeds.",
                        "Strict separation of fit and transform steps to avoid leakage.",
                        "Metric evaluation with out-of-fold cross validation.",
                        "Serialization ready for FastAPI microservices."
                    ],
                    "code_snippet": "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import Ridge\n\npipe = Pipeline([\n    ('scaler', StandardScaler()),\n    ('model', Ridge(alpha=1.0))\n])\npipe.fit(X_train, y_train)"
                },
                {
                    "slide_number": 7,
                    "slide_type": "concept",
                    "title": "Hyperparameter Dynamics & Tuning",
                    "subtitle": "Search Spaces & Optimization",
                    "bullets": [
                        "Critical hyperparameters and sensitivity surfaces.",
                        "Bayesian search via TPE vs standard grid exhaustive sweeps.",
                        "Early stopping criteria on out-of-fold validation sets.",
                        "Trade-offs between regularization intensity and model capacity."
                    ]
                },
                {
                    "slide_number": 8,
                    "slide_type": "pitfalls",
                    "title": "Data Leakage & Production Pitfalls",
                    "subtitle": "Critical Hazards in Production",
                    "bullets": [
                        "Fitting scalers or encoders prior to train/test split partitions.",
                        "Lookahead bias when modeling time-dependent sequential data.",
                        "Silent dimension mismatches and implicit type coercions.",
                        "Uncalibrated output probabilities on imbalanced datasets."
                    ]
                },
                {
                    "slide_number": 9,
                    "slide_type": "interview",
                    "title": "Senior Technical Interview: Core Tradeoffs",
                    "subtitle": "Staff-Level Architectural Defense",
                    "bullets": [
                        "Q: How do you mathematically justify this estimator over gradient boosted trees?",
                        "A: Evaluate inference latency constraints, interpretability, and sample complexity.",
                        "Q: What happens if features exhibit extreme collinearity?",
                        "A: Covariance matrix inversion becomes numerically ill-conditioned; apply L2 ridge shrinkage."
                    ]
                },
                {
                    "slide_number": 10,
                    "slide_type": "interview",
                    "title": "System Design: Scale & Latency",
                    "subtitle": "Production Serving Constraints",
                    "bullets": [
                        "Serving SLA requirements: P99 latency < 15ms at 5,000 QPS.",
                        "Feature store caching with Redis / Feast.",
                        "Asynchronous batch prediction vs real-time ONNX runtime scoring.",
                        "Drift monitoring with Kolmogorov-Smirnov continuous tests."
                    ]
                },
                {
                    "slide_number": 11,
                    "slide_type": "concept",
                    "title": "Model Governance & Drift Monitoring",
                    "subtitle": "Maintaining Production Reliability",
                    "bullets": [
                        "Tracking Population Stability Index (PSI) on input feature distributions.",
                        "Detecting concept drift when ground truth labels arrive asynchronously.",
                        "Automated shadow deployment and canary rollouts.",
                        "Graceful degradation fallbacks when upstream feature pipelines fail."
                    ]
                },
                {
                    "slide_number": 12,
                    "slide_type": "summary",
                    "title": "Executive Summary & Tomorrow's Preview",
                    "subtitle": "Mastery Verification Checklist",
                    "bullets": [
                        f"Mastered core mathematical theory and code for {title}.",
                        "Code sandbox validated with zero runtime errors.",
                        "Next Session: Advance to subsequent curriculum milestone.",
                        "Action Item: Complete the interactive quiz and review slides."
                    ]
                }
            ]
        }

    def _generate_fallback_quiz_json(self, day_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        title = day_info.get("topic") or day_info.get("title", f"Day {day_info['day']}")
        return [
            {
                "id": 1,
                "question": f"In the context of {title}, what is the primary risk of fitting preprocessing transformers on the full dataset before splitting?",
                "options": [
                    "It causes a fatal syntax error during model compilation.",
                    "It causes data leakage, artificially inflating validation performance and leading to production degradation.",
                    "It causes the model weights to shrink to zero.",
                    "It reduces training speed by a factor of 10."
                ],
                "correct_index": 1,
                "explanation": "Fitting scalers or transformers on the entire dataset leaks distribution statistics (such as mean and variance) from the validation/test set into the training set, causing optimistic bias."
            },
            {
                "id": 2,
                "question": "Which mathematical property guarantees a unique closed-form global minimum in convex optimization problems?",
                "options": [
                    "A strictly positive definite Hessian matrix throughout the parameter space.",
                    "An asymmetric covariance matrix.",
                    "A non-zero learning rate schedule.",
                    "L1 norm penalty with alpha = 0."
                ],
                "correct_index": 0,
                "explanation": "When the Hessian matrix of second derivatives is strictly positive definite everywhere, the objective function is strictly convex, guaranteeing a unique global minimum."
            },
            {
                "id": 3,
                "question": "When deploying an ML model into a latency-critical microservice (P99 < 10ms), which strategy yields the highest inference throughput?",
                "options": [
                    "Re-training the model on every incoming HTTP POST payload.",
                    "Exporting the model to ONNX runtime or compiled C-bindings with batching.",
                    "Increasing the number of features by a factor of 5.",
                    "Using unpickled Python objects in a single-threaded blocking event loop."
                ],
                "correct_index": 1,
                "explanation": "Compiling models to the Open Neural Network Exchange (ONNX) runtime enables hardware-specific SIMD vectorization and multi-threaded execution, reducing latency significantly."
            }
        ]
