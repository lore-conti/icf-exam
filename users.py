
import bcrypt

# Hashed passwords using bcrypt
users = {
    "jorge@leadershipboot.com": bcrypt.hashpw("jorge".encode('utf-8'), bcrypt.gensalt()),
    "lorenzo@leadershipboot.com": bcrypt.hashpw("lorenzo".encode('utf-8'), bcrypt.gensalt()),
    "1@1.com": bcrypt.hashpw("1".encode('utf-8'), bcrypt.gensalt()),
}