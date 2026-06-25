"""
AI explainer module for CPU scheduling simulations.
Provides two capabilities:
  1. get_explanation()       — Generates a full academic performance report using Gemini.
  2. get_ai_recommendation() — Generates a targeted, data-driven algorithm recommendation
                               for the specific workload being simulated.

Uses the google-genai SDK (google.genai) which is the current supported package.
"""

from google import genai
from google.genai import types

# --- Gemini Model Configuration ---
GEMINI_MODEL = "gemini-2.0-flash"


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Create a configured Gemini client
# ─────────────────────────────────────────────────────────────────────────────

def _create_client(api_key: str) -> genai.Client:
    """
    Creates a Google Gemini client configured with the provided API key.

    Parameters:
        api_key (str): The Google Gemini API key.

    Returns:
        genai.Client: Configured Gemini client instance.
    """
    return genai.Client(api_key=api_key.strip())


def _friendly_error(e: Exception) -> str:
    """
    Converts raw API exceptions into clear, actionable user-facing messages.

    Parameters:
        e (Exception): The exception raised by the Gemini API call.

    Returns:
        str: A user-friendly error string in markdown format.
    """
    msg = str(e)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        return (
            "⏳ **Rate Limit Reached (429)**\n\n"
            "You have temporarily exceeded the Gemini free-tier quota. This is NOT a code bug.\n\n"
            "**How to fix:**\n"
            "- Wait **1–2 minutes** and click the button again\n"
            "- If this keeps happening, your **daily free quota** may be used up — "
            "try again tomorrow or enable billing at "
            "[Google AI Studio](https://aistudio.google.com/app/apikey)\n"
            "- Make sure you are using your **latest/new API key** (not the revoked one)"
        )
    elif "401" in msg or "API_KEY_INVALID" in msg or "invalid" in msg.lower():
        return (
            "🔑 **Invalid API Key (401)**\n\n"
            "The Gemini API key you entered is invalid or has been revoked.\n\n"
            "**How to fix:**\n"
            "- Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)\n"
            "- Generate a **brand new API key**\n"
            "- Paste it into the text box above and try again"
        )
    elif "404" in msg or "NOT_FOUND" in msg:
        return (
            "❌ **Model Not Found (404)**\n\n"
            "The AI model name is not recognised by the API.\n\n"
            f"Raw error: `{msg[:200]}`"
        )
    else:
        return (
            f"❌ **API Error**: {msg[:300]}\n\n"
            "Please check your API key and internet connection."
        )


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """
    Sends a minimal test request to Gemini to verify the API key works.

    Parameters:
        api_key (str): The API key to validate.

    Returns:
        tuple[bool, str]: (is_valid, message)
    """
    if not api_key or api_key.strip() == "":
        return False, "No API key provided."
    try:
        client = _create_client(api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents="Say 'OK' in one word only.",
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=5)
        )
        if response and response.text:
            return True, "✅ API key is valid and working!"
        return False, "API returned an empty response."
    except Exception as e:
        return False, _friendly_error(e)


# ─────────────────────────────────────────────────────────────────────────────
# Function 1: Full Academic Performance Report
# ─────────────────────────────────────────────────────────────────────────────

def get_explanation(
    metrics: dict[str, dict],
    recommendations: dict[str, dict],
    api_key: str
) -> str:
    """
    Constructs a detailed prompt from simulation metrics and recommendations,
    then calls the Gemini API to generate a full academic explanation report.

    Parameters:
        metrics (dict[str, dict]): Dictionary mapping algorithm names to their computed metrics.
        recommendations (dict[str, dict]): Rule-based recommendations for different scenarios.
        api_key (str): Google Gemini API Key.

    Returns:
        str: Generated explanation text in markdown format, or an error message string.
    """
    if not api_key or api_key.strip() == "":
        return (
            "⚠️ **API Key Missing**: Please provide a valid Gemini API key in the panel "
            "or configure it in Streamlit secrets to generate the explanation."
        )

    # 1. Format the metrics block
    formatted_metrics = ""
    for algo, data in metrics.items():
        formatted_metrics += f"**{algo}**\n"
        formatted_metrics += f"  - Avg Waiting Time: {data['avg_waiting_time']} time units\n"
        formatted_metrics += f"  - Avg Turnaround Time: {data['avg_turnaround_time']} time units\n"
        formatted_metrics += f"  - Avg Response Time: {data['avg_response_time']} time units\n"
        formatted_metrics += f"  - Throughput: {data['throughput']} processes/time unit\n"
        formatted_metrics += f"  - CPU Utilization: {data['cpu_utilization']}%\n\n"

    # 2. Format the recommendations block
    formatted_recs = ""
    for scenario, rec in recommendations.items():
        formatted_recs += f"- **{scenario}**: {rec['algorithm']} — {rec['reason']}\n"

    # 3. Construct the prompt
    prompt = (
        "You are an Operating Systems expert and computer science professor.\n\n"
        "Given these CPU scheduling simulation results:\n\n"
        f"{formatted_metrics}"
        "And these rule-based scenario recommendations:\n\n"
        f"{formatted_recs}\n\n"
        "Please write a structured academic report covering exactly these 5 points:\n"
        "1. **Overall Best Performer**: Which algorithm performed best overall and why, citing actual metric numbers.\n"
        "2. **Fairness**: Which algorithm ensures fairness and prevents starvation and why.\n"
        "3. **Real-Time / Embedded Systems**: Which algorithm suits time-critical systems and why.\n"
        "4. **Throughput Maximizer**: Which algorithm achieves highest throughput and what trade-offs it makes.\n"
        "5. **Student Guidance**: A brief practical guide for a student choosing between these algorithms.\n\n"
        "Important formatting rules:\n"
        "- Use markdown headings (## for each point), bold text, and bullet points.\n"
        "- Reference actual metric values from the data above.\n"
        "- Keep the tone clear and educational, suitable for an undergraduate OS course.\n"
        "- Do NOT use any HTML tags in the output."
    )

    # 4. Call the API
    try:
        client = _create_client(api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4)
        )

        if response and response.text:
            return response.text
        else:
            return "❌ **API Error**: No response was returned from the Gemini service."

    except Exception as e:
        return (
            f"❌ **API Error**: {str(e)}\n\n"
            "Please verify your API key is valid, active, and that you have internet connectivity."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Function 2: AI-Powered Smart Recommendation
# ─────────────────────────────────────────────────────────────────────────────

def get_ai_recommendation(
    metrics: dict[str, dict],
    process_list: list[dict],
    api_key: str
) -> dict:
    """
    Analyzes the specific workload characteristics and simulation metrics,
    then asks Gemini to recommend the single best algorithm for this workload.

    Parameters:
        metrics (dict[str, dict]): Map of algorithm name to computed metrics dict.
        process_list (list[dict]): The list of process dicts (pid, arrival, burst, priority).
        api_key (str): Google Gemini API Key.

    Returns:
        dict: A result dictionary with keys:
              - "success": bool
              - "algorithm": str  — the recommended algorithm name
              - "confidence": str — "High" | "Medium" | "Low"
              - "headline": str   — one-line summary
              - "reasoning": str  — detailed markdown reasoning
              - "error": str      — populated only when success=False
    """
    if not api_key or api_key.strip() == "":
        return {
            "success": False,
            "error": "⚠️ No API key provided. Please enter your Gemini API key first."
        }

    # --- Build workload characteristics summary ---
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
        f"- Arrival Spread: {arrival_spread:.2f} (0 = all arrive at once)\n"
        f"- Priority Range: {priority_range} (0 = all same priority)\n"
    )

    # --- Build metrics summary ---
    metrics_summary = ""
    for algo, data in metrics.items():
        metrics_summary += (
            f"- {algo}: AvgWT={data['avg_waiting_time']}, "
            f"AvgTAT={data['avg_turnaround_time']}, "
            f"AvgRT={data['avg_response_time']}, "
            f"Throughput={data['throughput']}, "
            f"CPU Util={data['cpu_utilization']}%\n"
        )

    # --- Construct the prompt ---
    prompt = (
        "You are an Operating Systems scheduling expert. Analyze this workload and simulation data.\n\n"
        "=== WORKLOAD CHARACTERISTICS ===\n"
        f"{workload_summary}\n"
        "=== SIMULATION RESULTS (4 algorithms) ===\n"
        f"{metrics_summary}\n"
        "=== YOUR TASK ===\n"
        "Based on this specific workload, recommend the SINGLE best CPU scheduling algorithm.\n\n"
        "You MUST respond in exactly this format (no extra text outside of it):\n\n"
        "RECOMMENDED: <algorithm name — one of: FCFS, SJF, Priority, Round Robin>\n"
        "CONFIDENCE: <High, Medium, or Low>\n"
        "HEADLINE: <one sentence summary of why this algorithm wins for this workload>\n"
        "REASONING:\n"
        "<3-5 bullet points explaining the recommendation based on the actual numbers above.\n"
        "Reference specific metric values. Use markdown bullet points starting with ->\n"
        "Do NOT use HTML tags.>\n"
    )

    # --- Call Gemini API ---
    try:
        client = _create_client(api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )

        if not response or not response.text:
            return {
                "success": False,
                "error": "❌ No response received from Gemini. Please try again."
            }

        raw = response.text.strip()
        return _parse_ai_recommendation(raw)

    except Exception as e:
        return {
            "success": False,
            "error": _friendly_error(e)
        }


def _parse_ai_recommendation(raw_text: str) -> dict:
    """
    Parses the structured Gemini response into a clean dict.

    Parameters:
        raw_text (str): The raw response text from Gemini.

    Returns:
        dict: Parsed recommendation with success=True, or error dict on parse failure.
    """
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

    # Validate we got the key fields
    if not result["algorithm"]:
        # Fallback: try to find a known algo name in the response
        for algo in ["SJF", "Round Robin", "Priority", "FCFS"]:
            if algo.lower() in raw_text.lower():
                result["algorithm"] = algo
                break

    if not result["algorithm"]:
        return {
            "success": False,
            "error": (
                "⚠️ Could not parse AI recommendation response. "
                "The model may have returned an unexpected format. Please try again.\n\n"
                f"**Raw response:**\n```\n{raw_text[:500]}\n```"
            )
        }

    return result
