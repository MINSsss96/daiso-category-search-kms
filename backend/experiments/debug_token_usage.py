import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

# Load env
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash-exp") 

async def main():
    print("--- Debugging Token Usage ---")
    output_lines = []
    try:
        response = await asyncio.to_thread(model.generate_content, "Hello, are you working?")
        
        output_lines.append(f"Response Text: {response.text}")
        
        output_lines.append("\n[Attributes check]")
        if hasattr(response, "usage_metadata"):
            output_lines.append("found 'usage_metadata'")
            output_lines.append(str(response.usage_metadata))
            output_lines.append(f"Prompt: {response.usage_metadata.prompt_token_count}")
            output_lines.append(f"Candidates: {response.usage_metadata.candidates_token_count}")
            output_lines.append(f"Total: {response.usage_metadata.total_token_count}")
        else:
            output_lines.append("NO 'usage_metadata' found.")
            output_lines.append(str(dir(response)))

    except Exception as e:
        output_lines.append(f"Error: {e}")
    
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Done writing to debug_output.txt")

if __name__ == "__main__":
    asyncio.run(main())
