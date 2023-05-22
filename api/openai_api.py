import os
import openai

CMD_MAP = {
    '0': 'aggregate',
    '1': 'collect',
    '2': 'summarize',
}

def init_key():
    openai.api_key = os.getenv('OPENAI_API_KEY')

def get_command(user_prompt):
    init_key()

    prompt = user_prompt + '\nCommand:'

    completion = openai.Completion.create(
        model="curie:ft-personal-2023-05-16-20-27-21",
        prompt=prompt,
        max_tokens=1,
    )

    model_output = completion.choices[0].text

    return model_output.strip()

def get_topic(user_prompt):
    init_key()

    prompt = 'You are a topic-extraction AI. Your job is to state the topic of a given statement as concisely as possible.\n\n'
    prompt += f'"{user_prompt}"\n'
    prompt += 'Topic:'

    completion = openai.Completion.create(
        model='text-curie-001',
        prompt=prompt,
        max_tokens=64,
    )

    model_output = completion.choices[0].text

    return model_output.strip()

def get_summary(user_prompt):
    prompt = 'You are a summary-extraction AI. Your job is to summarize given text in a concise and information-dense manner.\n\n'
    prompt += f'"{user_prompt}"\n'
    prompt += 'Summary:'

    completion = openai.Completion.creat(
        model='text-curie-001',
        prompt=prompt,
        max_tokens=512,
    )

    model_output = completion.choices[0].text

    return model_output.strip()
