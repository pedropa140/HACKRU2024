import requests


API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/ce787f621d3df59e07bd0ff342723ae1/ai/run/"
headers = {"Authorization": "Bearer wkd748PVSeSQRk2iQSS-eb8rB25ihto-296YmYAD"}


def run(model, inputs):
    input = { "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()


inputs = [
    { "role": "system", "content": "You are a friendly assistan that helps write stories" },
    { "role": "user", "content": "Write a short story about a llama that goes on a journey to find an orange cloud "}
];
output = run("@cf/meta/llama-2-7b-chat-int8", inputs)
# print(output)