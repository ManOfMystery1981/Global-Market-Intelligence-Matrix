import os
from google import genai
from google.genai import types

class SeniorEconomistAgent:
    """
    Autonomous Macro Strategic Agent: Transforms raw multi-asset quantitative data 
    into professional macroeconomic insights and forward-looking predictions.
    """
    def __init__(self):
        # Grabs your API Key from the safe Environment Variable
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in environment.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    def synthesize_market_playbook(self, raw_playbook_data):
        print(" Invoking Senior Economist Agent for trend synthesis...")
        
        # Isolate anomalies to maximize analytical efficiency
        breakouts = [item for item in raw_playbook_data if item['trend'] == "BREAKOUT"]
        
        # Create a compressed data presentation
        data_string = "\n".join([
            f"Asset: {item['ticker']} ({item['category']}) | Price: ${item['price']:,} | Condition: {item['trend']}"
            for item in breakouts[:10]
        ])

        system_instruction = (
            "You are a Senior Fund Strategist and Macro Economist. Your tone is highly calculative, "
            "clinical, and factual. Do not use corporate marketing fluff. Focus on liquidity, market "
            "inefficiencies, and velocity of capital shifts."
        )

        prompt = f"""
        Analyze the following cross-asset market volume breakouts detected by our ingestion systems:
        
        {data_string}
        
        Generate an Institutional Strategy Review formatted using standard HTML containing exactly three parts:
        
        1. LIQUIDITY SHIFTS & CAPITAL VELOCITY: Interpret what these sudden asset volume anomalies reveal about larger macroeconomic rotations.
        2. ASSET CORRELATION ANALYSIS: Critique potential spillover risks between asset classes (e.g., Crypto/AI Stocks divergence).
        3. 30-DAY OPERATIONAL PREDICTIONS: Provide explicit forward-looking assessments for asset allocation over the next month.
        
        Format the response using clean HTML elements (<p>, <strong>, <ul>). Do not wrap the response in markdown code formatting.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                ),
            )
            return response.text

        except Exception as e:
            print(f" Gemini API Network Alert: {e}")
            return """
            <div>
                <p><strong>[NOTICE: PIPELINE AUTOMATED FALLBACK ENGAGED]</strong></p>
                <p><strong>1. LIQUIDITY SHIFTS & CAPITAL VELOCITY:</strong> Current multi-asset cross-referencing indicates structural liquidity expansion across specific breakout categories.</p>
                <p><strong>2. ASSET CORRELATION ANALYSIS:</strong> Cross-market correlation coefficients show relative decoupling between traditional commodity channels and high-beta technical assets.</p>
                <p><strong>3. 30-DAY OPERATIONAL PREDICTIONS:</strong> Risk exposure models recommend strict stop-loss protocols.</p>
            </div>
            """
