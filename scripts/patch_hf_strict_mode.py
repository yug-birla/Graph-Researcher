from pathlib import Path

path = Path("app/generation/providers/huggingface_provider.py")
text = path.read_text(encoding="utf-8")

old = '''        if api_mode == "chat":
            answer = self.call_chat_completion_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            answer = self.call_hf_inference_model_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            return ""

        if api_mode == "inference":
            answer = self.call_hf_inference_model_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            answer = self.call_chat_completion_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            return ""
'''

new = '''        if api_mode == "chat":
            answer = self.call_chat_completion_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            return ""

        if api_mode == "inference":
            answer = self.call_hf_inference_model_api(prompt)

            if answer:
                return clean_hosted_output(answer)

            return ""
'''

if old not in text:
    print("Could not find old fallback block. No change made.")
else:
    text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print("Strict HF_API_MODE patch applied successfully.")
