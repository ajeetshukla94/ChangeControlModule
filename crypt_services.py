# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 16:22:11 2022

@author: Vivek
"""


import hashlib

def encrypt_sha256(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

def encrypt_md5(hash_string):
    sha_signature = \
        hashlib.md5(hash_string.encode()).hexdigest()
    return sha_signature
