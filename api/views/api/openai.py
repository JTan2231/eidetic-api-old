import pickle
import numpy as np

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from api.models import Embedding
from api.openai_api import get_command
from api.aws import fetch_embeddings
from api.engine.compute import rank

CMD_MAP = {
    '0': 'aggregate',
    '1': 'collect',
    '2': 'summarize',
}

TOKEN_LEVEL = True

def pad(m, l):
    return np.concatenate([m, np.zeros([max(l - m.shape[0], 0), m.shape[1]], np.float32)])

class OpenAIView(APIView,
                 UpdateModelMixin,
                 DestroyModelMixin):

    def collect(self, user_id, topic):
        topic_embedding, _ = fetch_embeddings(topic)

        try:
            if TOKEN_LEVEL:
                MAXLEN = 0
                embedding_queryset = Embedding.objects.filter(user_id=user_id).values('entry_id', 'embedding', 'mask')
                embed_by_entry = {}
                masks_by_entry = {}
                for e in embedding_queryset:
                    eid, embed, mask = (e['entry_id'], pickle.loads(e['embedding']), pickle.loads(e['mask']))
                    ebe = embed_by_entry.get(eid, None)
                    if ebe is None:
                        embed_by_entry[eid] = [embed]
                        masks_by_entry[eid] = [mask]
                    else:
                        embed_by_entry[eid].append(embed)
                        masks_by_entry[eid].append(mask)

                    MAXLEN = max(MAXLEN, len(embed_by_entry[eid]) + 1)

                id_list = []
                embedding_matrix = []
                mask_matrix = []
                for emat, mmat in zip(embed_by_entry.items(), masks_by_entry.items()):
                    embed = pad(np.array(emat[1]), MAXLEN)
                    mask = pad(np.array(mmat[1]), MAXLEN)

                    id_list.append(emat[0])
                    embedding_matrix.append(embed)
                    mask_matrix.append(mask)

                embedding_matrix = np.array(embedding_matrix)
                mask_matrix = np.array(mask_matrix)
            else:
                print("WARNING: TOKEN_LEVEL is False! This else clause is unimplemented!")
                return []

        except Embedding.DoesNotExist:
            return []

        print(embedding_matrix.shape)
        print(id_list)

        embedding_matrix = np.transpose(embedding_matrix, [0, 2, 1])
        mask_matrix = np.transpose(mask_matrix, [0, 2, 1])

        scores = rank(topic_embedding, embedding_matrix, mask_matrix, return_scores=True)

        relevant_entry_ids = []
        for i in range(len(scores)):
            if scores[i][0] > 0.80:
                relevant_entry_ids.append(id_list[scores[i][1]])


        return relevant_entry_ids

    def aggregate(self, user_id, topic):
        # TODO
        return
    
    def summarize(self, user_id, topic):
        # TODO
        return

    def post(self, request):
        prompt = request.data['prompt']

        #command = get_command(prompt)
        entry_ids = self.collect(request.session['user_id'], prompt)

        return Response(entry_ids, status=200)
