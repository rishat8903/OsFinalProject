"""
Groq AI explainer module for CPU scheduling simulations.
Uses the Groq API (free tier) with Llama 3.3 70B as an alternative to Gemini.

Groq Free Tier:
  - 14,400 requests/day
  - 30 requests/minute
  - No credit card required
  - Get a key at: https://console.groq.com/keys
"""

from groq import Groq

# --- Model Configuration ---
GROQ_MODEL = "llama-3.3-70b-versatile"


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Friendly error messages
# ─────────────────────────────────────────────────────────────────────────────

def _friendly_groq_error(e: Exception) -> str:
    """Converts Groq API exceptions into clear user-facing messages."""
    msg = str(e)
    if "401" in msg or "invalid_api_key" in msg.lower() or "authentication" in msg.lower():
        return (
            "🔑 **Invalid Groq API Key (401)**\n\n"
            "The key you entered is invalid or expired.\n\n"
            "**How to fix:**\n"
            "- Go to [https://console.groq.com/keys](https://console.groq.com/keys)\n"
            "- Generate a **new API key**\n"
            "- Paste it into the Groq key box and try again"
        )
    elif "429" in msg or "rate_limit" in msg.lower():
        return (
            "⏳ **Rate Limit Reached (429)**\n\n"
            "You've hit Groq's per-minute limit. Wait **30 seconds** and try again.\n"
            "Groq allows 14,400 requests/day so this resets quickly."
        )
    else:
        return f"❌ **Groq API Error**: {msg[:300]}"


def validate_groq_key(api_key: str) -> tuple[bool, str]:
    """
    Sends a minimal test request to Groq to verify the API key works.

    Parameters:
        api_key (str): The Groq API key to validate.

    Returns:
        tuple[bool, str]: (is_valid, message)
    """
    if not api_key or api_key.strip() == "":
        return False, "No Groq API key provided."
    try:
        client = Groq(api_key=api_key.strip())
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "Say 'OK' in one word only."}],
            max_tokens=5,
            temperature=0.0
        )
        if response and response.choices:
            return True, "✅ Groq API key is valid and working!"
        return False, "Groq returned an empty response."
    except Exception as e:
        return False, _friendly_groq_error(e)


# ─────────────────────────────────────────────────────────────────────────────
# Function 1: Full Academic Performance Report (Groq version)
# ─────────────────────────────────────────────────────────────────────────────

def get_groq_explanation(
    metrics: dict[str, dict],
    recommendations: dict[str, dict],
    api_key: str
) -> str:
    """
    Generates a full academic CPU scheduling performance report using Groq (Llama 3.3 70B).

    Parameters:
        metrics (dict[str, dict]): Algorithm name → computed metrics dict.
        recommendations (dict[str, dict]): Rule-based scenario recommendations.
        api_key (str): Groq API key.

    Returns:
        str: Markdown-formatted academic report, or an error message.
    """
    if not api_key or api_key.strip() == "":
        return (
            "⚠️ **Groq API Key Missing**: Please enter your Groq API key.\n"
            "Get a free key at https://console.groq.com/keys"
        )

    # Format metrics
    formatted_metrics = ""
    for algo, data in metrics.items():
        formatted_metrics += f"**{algo}**\n"
        formatted_metrics += f"  - Avg Waiting Time: {data['avg_waiting_time']} time units\n"
        formatted_metrics += f"  - Avg Turnaround Time: {data['avg_turnaround_time']} time units\n"
        formatted_metrics += f"  - Avg Response Time: {data['avg_response_time']} time units\n"
        formatted_metrics += f"  - Throughput: {data['throughput']} processes/time unit\n"
        formatted_metrics += f"  - CPU Utilization: {data['cpu_utilization']}%\n\n"

    # Format recommendations
    formatted_recs = ""
    for scenario, rec in recommendations.items():
        formatted_recs += f"- **{scenario}**: {rec['algorithm']} — {rec['reason']}\n"

    prompt = (
        "You are an Operating Systems expert and computer science professor.\n\n"
        "Given these CPU scheduling simulation results:\n\n"
        f"{formatted_metrics}"
        "And these rule-based scenario recommendations:\n\n"
        f"{formatted_recs}\n\n"
        "Write a structured academic report covering these 5 points:\n"
        "1. **Overall Best Performer**: Which algorithm performed best overall and why, with actual metric numbers.\n"
        "2. **Fairness**: Which ensures fairness and prevents starvation.\n"
        "3. **Real-Time / Embedded Systems**: Which suits time-critical systems.\n"
        "4. **Throughput Maximizer**: Which achieves highest throughput and trade-offs.\n"
        "5. **Student Guidance**: Brief practical guide for choosing between algorithms.\n\n"
        "Rules: Use markdown (## headings, bold, bullets). Reference actual metric values. "
        "Clear undergraduate-level language. No HTML tags."
    )

    try:
        client = Groq(api_key=api_key.strip())
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert Operating Systems professor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=2048
        )
        if response and response.choices:
            return response.choices[0].message.content
        return "❌ **Error**: No response returned from Groq."
    except Exception as e:
        return _friendly_groq_error(e)


# ─────────────────────────────────────────────────────────────────────────────
# Function 2: AI-Powered Smart Recommendation (Groq version)
# ─────────────────────────────────────────────────────────────────────────────

def get_groq_recommendation(
    metrics: dict[str, dict],
    process_list: list[dict],
    api_key: str
) -> dict:
    """
    Analyzes workload and simulation metrics, then asks Groq (Llama 3.3 70B)
    to recommend the single best CPU scheduling algorithm.

    Parameters:
        metrics (dict[str, dict]): Algorithm name → metrics dict.
        process_list (list[dict]): Process list with pid, arrival, burst, priority.
        api_key (str): Groq API key.

    Returns:
        dict: {"success": bool, "algorithm": str, "confidence": str,
               "headline": str, "reasoning": str, "error": str}
    """
    if not api_key or api_key.strip() == "":
        return {
            "success": False,
            "error": (
                "⚠️ No Groq API key provided.\n"
                "Get a free key at https://console.groq.com/keys"
            )
        }

    # Build workload characteristics
    bursts = [float(p["burst"]) for p in process_list]
    arrivals = [float(p["arrival"]) for p in process_list]
    priorities = [int(p["priority"]) for p in process_list]

    n = len(process_list)
    avg_burst = sum(bursts) / n
    burst_variance = sum((b - avg_burst) ** 2 for b in bursts) / n
    arrival_spread = max(arrivals) - min(arrivals)
    priority_range = max(priorities) - min(priorities)

    workload_summary = (
        f"- Total Processes: {n}\n"
        f"- Avg Burst Time: {avg_burst:.2f} units\n"
        f"- Burst Time Variance: {burst_variance:.2f} (higher = more unequal)\n"
        f"- Burst Times: {[round(b, 2) for b in bursts]}\n"
        f"- Arrival Spread: {arrival_spread:.2f}\n"
        f"- Priority Range: {priority_range}\n"
    )

    metrics_summary = ""
    for algo, data in metrics.items():
        metrics_summary += (
            f"- {algo}: AvgWT={data['avg_waiting_time']}, "
            f"AvgTAT={data['avg_turnaround_time']}, "
            f"AvgRT={data['avg_response_time']}, "
            f"Throughput={data['throughput']}, "
            f"CPU={data['cpu_utilization']}%\n"
        )

    prompt = (
        "You are an Operating Systems scheduling expert.\n\n"
        "=== WORKLOAD CHARACTERISTICS ===\n"
        f"{workload_summary}\n"
        "=== SIMULATION RESULTS ===\n"
        f"{metrics_summary}\n"
        "=== TASK ===\n"
        "Recommend the SINGLE best CPU scheduling algorithm for this specific workload.\n\n"
        "Respond in EXACTLY this format (nothing else outside it):\n\n"
        "RECOMMENDED: <one of: FCFS, SJF, Priority, Round Robin>\n"
        "CONFIDENCE: <High, Medium, or Low>\n"
        "HEADLINE: <one sentence why this algorithm wins for this workload>\n"
        "REASONING:\n"
        "-> <bullet 1 with specific metric values>\n"
        "-> <bullet 2 with specific metric values>\n"
        "-> <bullet 3 with specific metric values>\n"
        "-> <bullet 4 optional>\n"
        "-> <bullet 5 optional>\n"
    )

    try:
        client = Groq(api_key=api_key.strip())
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are an OS scheduling expert. Follow the response format exactly."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=512
        )

        if not response or not response.choices:
            return {"success": False, "error": "❌ No response from Groq. Try again."}

        raw = response.choices[0].message.content.strip()
        return _parse_groq_recommendation(raw)

    except Exception as e:
        return {"success": False, "error": _friendly_groq_error(e)}


def _parse_groq_recommendation(raw_text: str) -> dict:
    """Parses the structured Groq response into a clean result dict."""
    lines = raw_text.strip().splitlines()
    result = {
        "success": True,
        "algorithm": "",
        "confidence": "Medium",
        "headline": "",
        "reasoning": "",
        "error": ""
    }

    reasoning_lines = []
    in_reasoning = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("RECOMMENDED:"):
            result["algorithm"] = stripped.replace("RECOMMENDED:", "").strip()
        elif stripped.startswith("CONFIDENCE:"):
            result["confidence"] = stripped.replace("CONFIDENCE:", "").strip()
        elif stripped.startswith("HEADLINE:"):
            result["headline"] = stripped.replace("HEADLINE:", "").strip()
        elif stripped.startswith("REASONING:"):
            in_reasoning = True
        elif in_reasoning:
            reasoning_lines.append(line)

    result["reasoning"] = "\n".join(reasoning_lines).strip()

    # Fallback: search for algo name in raw text
    if not result["algorithm"]:
        for algo in ["SJF", "Round Robin", "Priority", "FCFS"]:
            if algo.lower() in raw_text.lower():
                result["algorithm"] = algo
                break

    if not result["algorithm"]:
        return {
            "success": False,
            "error": (
                "⚠️ Could not parse response. Please try again.\n\n"
                f"**Raw response:**\n```\n{raw_text[:400]}\n```"
            )
        }

    return result
