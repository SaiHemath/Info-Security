import hashlib, string, random

# def hash_password(password):
#     password_bytes = password.encode('utf-8')
#     sha256 = hashlib.sha256()
#     sha256.update(password_bytes)
#     hash = sha256.hexdigest()
#     # print(f'hash of {password} is {hash}')
#     return hash

def hash_password(password, n=1):
    word = password
    for i in range(0,n):
        password_bytes = word.encode('utf-8')
        sha256 = hashlib.sha256()
        sha256.update(password_bytes)
        word = sha256.hexdigest()
    return word

def random_string(n):
    chars=string.ascii_letters + string.digits
    choices = random.choices(chars, k=n)
    result = ''.join(choices)
    return result

known_password = "hello"

#for i in range(0,10):
salt = random_string(20)
hash_known_password = hash_password(known_password + salt, n=10000000) + ":" + salt
print(hash_known_password)

known_password = None

submit_password = "hello"

hash_known_password, salt = hash_known_password.split(":")
if hash_known_password == hash_password(submit_password + salt, n=10000000):
    print("password correct")
else:
    print("bad password")

