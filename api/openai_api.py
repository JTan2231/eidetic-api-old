import os
import openai

CMD_MAP = {
    '0': 'aggregate',
    '1': 'collect',
    '2': 'summarize',
}

def get_command(user_prompt):
    prompt = user_prompt + '\nCommand:'

    openai.api_key = os.getenv('OPENAI_API_KEY')
    completion = openai.Completion.create(
        model="curie:ft-personal-2023-05-16-20-27-21",
        prompt=prompt,
        max_tokens=1,
    )

    model_output = completion.choices[0].text

    return model_output.strip()
