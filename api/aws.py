import ast
import json
import boto3
import openai
import requests

import numpy as np

from eidetic.settings import DEBUG

OPENAI = True

def fetch_embeddings(input_text):
    if OPENAI:
        response = openai.Embedding.create(
            input=input_text,
            model="text-embedding-ada-002"
        )

        embeddings = np.array(response['data'][0]['embedding'])[np.newaxis, ...]
        embeddings /= np.linalg.norm(embeddings)

        return embeddings, [[True]]

    if DEBUG:
        res = requests.post('http://localhost:5000/get-embedding', json={ 'text': input_text })
        body = res.json()
    else:
        client = boto3.client('sagemaker-runtime', region_name='us-east-2')
        endpoint = 'pytorch-inference-2023-02-06-16-53-37-195'

        print(f'contacting endpoint {endpoint}...')

        res = client.invoke_endpoint(EndpointName=endpoint,
                                     Body=json.dumps({ 'inputs': input_text }),
                                     ContentType='application/json')

        print(f"status: {res['ResponseMetadata']['HTTPStatusCode']}")

        body = res['Body'].read().decode()
        body = ast.literal_eval(body)
        print(body)

    embedding = np.array([np.array([float(i) for i in s]) for s in body['embedding']])
    mask = np.array([np.array([bool(s)]) for s in body['mask']])

    return embedding, mask
