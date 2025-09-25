import os


def user_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"user_{instance.pk}.{ext}"
    return os.path.join('avatars', filename)