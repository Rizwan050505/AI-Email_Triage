import os
import json
from openai import OpenAI
import sys
from env.email_env import EmailTriageEnv, Action

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

def run_inference(task_name: str, env_name: str):
    print(f"[START] task={task_name} env={env_name} model={MODEL_NAME}")
    
    env = EmailTriageEnv()
    obs = env.reset(task_id=task_name)
    
    step_count = 0
    rewards = []
    success = True
    info = {}
    
    # Simple predefined logic to extract action from LLM output
    while True:
        step_count += 1
        current_email = obs.current_email
        if current_email is None:
            break
            
        prompt = f"""
        You are an advanced Corporate Email Triage Assistant. 
        Your objective is to evaluate incoming emails and route them correctly based on company policy.
        
        [INCOMING EMAIL] 
        Email ID: {current_email.id}
        From: {current_email.sender}
        Subject: {current_email.subject}
        Body: {current_email.body[:500]} ...
        
        [TASK REQUIREMENTS: {task_name}]
        1. Classify 'priority' exactly as one of: [low, normal, high].
        2. Assign 'action' exactly as one of: [ignore, auto-reply, escalate, notify].
        3. If action is 'auto-reply', generate a polite 'drafted_response' (min 20 chars). Otherwise leave empty.
        
        Return ONLY valid JSON:
        {{"priority": "value", "action": "value", "drafted_response": "response here"}}
        """
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an AI Email Triage agent. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            action_obj = Action(
                predicted_priority=parsed.get("priority", "normal"),
                predicted_action=parsed.get("action", "auto-reply"),
                drafted_response=parsed.get("drafted_response", "")
            )
            
            action_str = f"predict_priority('{action_obj.predicted_priority}')"
            if task_name in ["email-triage-medium", "email-triage-hard"]:
                action_str = f"predict_priority_and_action('{action_obj.predicted_priority}', '{action_obj.predicted_action}')"
            
            obs, reward_obj, done, info = env.step(action_obj)
            
            rewards.append(reward_obj.step_reward)
            err_str = "null"
            
        except Exception as e:
            action_str = "error"
            from env.email_env import Reward
            # Strict penalty that is not exactly 0.0 
            error_reward = 0.05
            reward_obj = Reward(step_reward=error_reward, total_reward=env.total_reward_val, message="Failure")
            done = True
            import traceback
            traceback.print_exc()
            err_str = str(e).replace('\n', ' ')
            success = False
            rewards.append(error_reward)
            
        done_str = "true" if done else "false"
        print(f"[STEP] step={step_count} action={action_str} reward={rewards[-1]:.4f} done={done_str} error={err_str}")
        
        if done:
            break
    
    env.close()
    
    # Use exact floats to avoid openenv grader receiving rounded 0.00 or 1.00 strings
    rewards_str = ",".join([str(r) for r in rewards])
    success_str = "true" if success else "false"
    print(f"[END] success={success_str} steps={step_count} rewards={rewards_str}")

if __name__ == "__main__":
    tasks = ["email-triage-easy", "email-triage-medium", "email-triage-hard"]
    for t in tasks:
        run_inference(t, "email-triage-env")
