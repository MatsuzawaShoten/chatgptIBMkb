import openai

openai.api_key = "sk-"
'''
    role
     ├─ system システムメッセージを設定chatgpt側 content その内容
     └─ user   プロンプトを設定 content その内容

'''
messages = [
    {"role": "system", "content": "あなたはIBMナレッジモール研究のメンバーです。"
     "一人称は「私」で、丁寧な言葉遣いで話します。IBMナレッジモール研究とは企業、業界、"
     "世代の枠を超えたワーキンググループ (WG) の仲間と、自主的に、研究活動をするプログラムです"},
    {"role": "user", "content": "こんにちは"}
]

'''
    openai.ChatCompletion.create
     ├─ model どのモデルを使用するか
     ├─ messages 上記で設定したdictの配列,話を繰り返すことによって会話履歴となる、これを元にレスポンスを返す。
     ├─ temperature  回答の文章のランダムさ0.0~2.0
     └─ max_tokens 入出力される文字をトークンという単位としている。レスポンスで最大何トークン返すか。

'''
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.7,
    max_tokens=300,
)
print(response.choices[0].message.content)
