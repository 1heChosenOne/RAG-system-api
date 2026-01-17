from utils import groq_client

def chat_response(chunks_text,question,system_prompt):
    context = "\n\n".join(chunks_text)
    full_prompt = f"CONTEXT:{context}\n\nQUESTION:{question}"
    response = groq_client.chat.completions.create(
		model="llama-3.3-70b-versatile",
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": full_prompt}
		],
		temperature=0.1
	)
    return response.choices[0].message.content