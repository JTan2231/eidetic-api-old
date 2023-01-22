import numpy as np

def score(query, embed, mask):
    """
    v.shape == (m, 128,)
    m.shape == (128, n,)

    Uses cosine distance
    """

    print("shapes", query.shape, embed.shape)
    print("mask", mask)
    embed = np.multiply(embed, mask)
    distances = np.dot(query, embed)
    print("distances", distances)
    distances = np.amax(distances, axis=1)
    print("distances", distances)
    print(distances.shape)

    distance = np.sum(distances)
    print("distances FINAL", distances)

    return distance

def rank(query, embeddings, masks, return_scores=False):
    scores = [score(query, embed, mask) for embed, mask in zip(embeddings, masks)]
    print([round(s, 4) for s in scores])
    ranks = sorted([(s, i) for i, s in enumerate(scores)], key=lambda p: p[0], reverse=True)

    if return_scores:
        return ranks
    else:
        return [r[1] for r in ranks]
