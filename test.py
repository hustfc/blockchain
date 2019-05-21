import hashlib
def validProof(lastProof, proof):
    """
    验证证明: 是否hash(last_proof, proof)以4个0开头?
    :param last_proof: <int> Previous Proof
    :param proof: <int> Current Proof
    :return: <bool> True if correct, False if not.
    """
    guess = f'{lastProof}{proof}'.encode()
    guessHash = hashlib.sha256(guess).hexdigest()
    return guessHash[:4] == '0000'
print(validProof(100, 68429))