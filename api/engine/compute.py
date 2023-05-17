import numpy as np

def score(query, embed, mask):
    """
    Uses cosine distance
    """

    embed = np.multiply(embed, mask)
    distances = np.dot(query, embed)
    distances = np.amax(distances, axis=1)

    distance = np.sum(distances)

    return distance

# query.shape == (token_count, embed_dim)
# embeddings.shape == (entry_count, embed_dim, token_count)
def rank(query, embeddings, masks, return_scores=False):
    print(query.shape, embeddings.shape, masks.shape)
    scores = [score(query, embed, mask) for embed, mask in zip(embeddings, masks)]
    ranks = sorted([(s, i) for i, s in enumerate(scores)], key=lambda p: p[0], reverse=True)

    if return_scores:
        return ranks
    else:
        return [r[1] for r in ranks]
