import os
import hashlib
import shutil
import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

SALT_LEN = 16
NONCE_LEN = 12
TAG_LEN = 16


def derive_key(password, salt, iterations=200000):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)


def encrypt_backup(db_path, outpath, password):
    salt = get_random_bytes(SALT_LEN)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=get_random_bytes(NONCE_LEN))
    with open(db_path, "rb") as f:
        data = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(data)
    with open(outpath, "wb") as out:
        out.write(b"SLB2")
        out.write(salt)
        out.write(cipher.nonce)
        out.write(tag)
        out.write(ciphertext)
    return outpath


def decrypt_backup(inpath, outpath, password):
    with open(inpath, "rb") as f:
        header = f.read(4)
        if header != b"SLB2":
            salt = header + f.read(SALT_LEN - 4)
            nonce = f.read(NONCE_LEN)
            tag = f.read(TAG_LEN)
            ciphertext = f.read()
        else:
            salt = f.read(SALT_LEN)
            nonce = f.read(NONCE_LEN)
            tag = f.read(TAG_LEN)
            ciphertext = f.read()
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        data = cipher.decrypt_and_verify(ciphertext, tag)
    except Exception as e:
        raise ValueError("Λάθος κωδικός ή κατεστραμμένο αρχείο backup") from e
    with open(outpath, "wb") as out:
        out.write(data)
    return outpath


def make_plain_backup(db_path, outdir):
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"backup_{stamp}.db"
    path = os.path.join(outdir, name)
    shutil.copy2(db_path, path)
    return path


def auto_backup(db_path, outdir, keep=5, password=None):
    if not os.path.exists(db_path):
        return None
    os.makedirs(outdir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    done = []
    if password:
        target = os.path.join(outdir, f"backup_{stamp}.enc")
        encrypt_backup(db_path, target, password)
        done.append(target)
    else:
        for i in range(1, 4):
            target = os.path.join(outdir, f"backup_{stamp}_{i}.db")
            try:
                shutil.copy2(db_path, target)
                done.append(target)
                break
            except Exception:
                continue
    backups = sorted(
        f for f in os.listdir(outdir)
        if (f.startswith("backup_") and (f.endswith(".enc") or f.endswith(".db")))
    )
    for old in backups[:-keep]:
        try:
            os.remove(os.path.join(outdir, old))
        except OSError:
            pass
    return done