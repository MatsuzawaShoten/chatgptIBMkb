import openai

openai.api_key = "sk-****************"
messages = [
    {"role": "system", "content": "あなたはIBMナレッジモール研究のメンバーです。"
     "一人称は「私」で、丁寧な言葉遣いで話します。IBMナレッジモール研究とは企業、業界、"
     "世代の枠を超えたワーキンググループ (WG) の仲間と、自主的に、研究活動をするプログラムです"},
    {"role": "user", "content": "こんにちは"}
]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.7,
    max_tokens=300,
)
print(response.choices[0].message.content)
