---
title: Email Triage Agent Environment
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
tags:
  - openenv
  - rl
  - agents
  - email-triage
---

# Email Triage System (OpenEnv RL Challenge Submission)

## Environment Overview and Motivation

Email triage is a classic real-world operational bottleneck. Knowledge workers and customer support agents frequently spend large chunks of their day reading, categorizing, prioritizing, and drafting responses to incoming emails. 

This repository implements the **Email Triage System**, an OpenEnv-compliant reinforcement learning environment that simulates this exact real-world scenario. The goal is to provide a grounded, practical domain where agents must make sequential decisions (priority assignment -> action determination -> response drafting) that mimic genuine human workflows. It avoids toy problems by enforcing constraints typical of an automated pipeline.

## Definitions of Action and Observation Spaces

### Observation Space
The state is emitted at every timestep and is composed of the exact attributes available to an assistant triaging an inbox.
- **`task_id` (str)**: Identifier of the current difficulty track.
- **`current_email` (EmailModel)**: The email object containing `id`, `sender`, `subject`, `body`, and `timestamp`.
- **`emails_remaining` (int)**: Number of emails left in the episode queue.
- **`history_so_far` (int)**: The count of emails processed in the current episode.

### Action Space
The agent responds by emitting an `Action` object with the following fields:
- **`predicted_priority` (str)**: The urgency level of the email (`low`, `normal`, `high`).
- **`predicted_action` (Optional[str])**: The routing or handling action (`ignore`, `auto-reply`, `escalate`).
- **`drafted_response` (Optional[str])**: A drafted reply string of at least 10 characters, if the action is `auto-reply`.

## Task Descriptions and Difficulty Levels

This environment features three tasks, each assessed by deterministic agent graders:

1. **`email-triage-easy` (Difficulty: Easy)**
   - *Objective*: Assign the correct priority (`low`, `normal`, `high`) to an incoming email based on its sender, subject, and content.
   - *Scoring*: 1.0 points per email if the exact underlying truth priority is matched, else 0.0.

2. **`email-triage-medium` (Difficulty: Medium)**
   - *Objective*: Determine both the priority and the immediate action needed for the email.
   - *Scoring*: 0.5 points for correct priority + 0.5 points for correct action.

3. **`email-triage-hard` (Difficulty: Hard)**
   - *Objective*: End-to-end processing. Determine priority, the necessary action, and if the action is `auto-reply`, provide a valid non-empty drafted response.
   - *Scoring*: Provides fractional rewards. ~0.33 for priority, ~0.33 for action, and ~0.34 for drafting a meaningful response when appropriate.

## Setup and Usage Instructions

1. **Local Setup:**
   Ensure you have Python 3.10+ installed.
   ```bash
   pip install -r requirements.txt
   pip install openai pydantic pydantic-settings
   ```

2. **OpenEnv Validation:**
   The environment definitions are defined in `openenv.yaml`. If you have the OpenEnv CLI installed, run:
   ```bash
   openenv validate
   ```

3. **Running the Baseline Inference:**
   You must set `HF_TOKEN` explicitly. `API_BASE_URL` and `MODEL_NAME` can default or be overridden.
   ```bash
   # Windows PowerShell
   $env:HF_TOKEN="your_huggingface_token"
   $env:MODEL_NAME="gpt-4o-mini"
   python inference.py

   # Linux/Mac
   export HF_TOKEN="your_huggingface_token"
   export MODEL_NAME="gpt-4o-mini"
   python inference.py
   ```

4. **Containerized Execution (Hugging Face Space):**
   ```bash
   docker build -t email-env .
   docker run -e HF_TOKEN="your_huggingface_token" email-env
   ```

## Baseline Performance Scores

Testing the environment with `gpt-4o-mini` over the simulated dataset yields baseline reproducible behaviors:
- **Easy Task (`email-triage-easy`)**: Model focuses effectively on priority keys (e.g. 'urgent', 'spam'). Score is 1.0 per correct step. Baseline overall success rate is reliably ~100% on the default batch.
- **Medium Task (`email-triage-medium`)**: Introduces action alignment. Baseline score averages ~0.90+ as deterministic routing is largely deduced.
- **Hard Task (`email-triage-hard`)**: Rejects blank or exceptionally short draft responses. The baseline LLM maintains high performance (~0.95+ average completion) by generating valid email bodies fulfilling the "auto-reply" condition.
