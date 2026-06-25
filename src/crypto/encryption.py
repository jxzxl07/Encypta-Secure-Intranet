import random, math
from typing import Tuple

def hash_password(password):
    ascii_values = []
    password = str(password)
    for char in password:
        ascii_values.append(ord(char))
    hash_value = len(password) * 7919
    position = 1
    previous_value = 0
    sum = 0
    for value in ascii_values:
        position_factor = position * 31
        hash_value = (hash_value * position_factor + value) % (2**32)
        if position > 1:
            hash_value = (hash_value + value * previous_value * 17) % (2**32)
        sum = sum + value
        position = position + 1
    mix_count = 3
    while mix_count > 0:
        hash_value = (hash_value * 7919) % (2**32)
        hash_value = (hash_value * 6007) % (2**32)
        hash_value = (hash_value + (hash_value ** 2 % 10000) * 31) % (2**32)
        mix_count = mix_count - 1
    result = ""
    while len(result) < 32:
        hash_value = (hash_value * 7919 + 123) % (2**32)
        hex_part = hex(hash_value)[2:]
        while len(hex_part) < 8:
            hex_part = "0" + hex_part
        result = result + hex_part
    return result[:32]


class AsymmetricEncryption:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        
    def generate_prime(self, min_val: int, max_val: int) -> int:
        # Generate a prime number within the given range
        def is_prime(n: int) -> bool:
            if n < 2:
                return False
            for i in range(2, int(math.sqrt(n)) + 1):
                if n % i == 0:
                    return False
            return True
        
        while True:
            num = random.randint(min_val, max_val)
            if is_prime(num):
                return num
    
    def generate_keypair(self) -> None:
        # Generate two prime numbers
        p = self.generate_prime(100, 1000)
        q = self.generate_prime(100, 1000)
        # Calculate n
        n = p * q
        # Calculate phi (Euler's totient function)
        phi = (p - 1) * (q - 1)
        # Generate public key (e)
        def find_coprime(phi: int) -> int:
            # Find a number coprime with phi
            def gcd(a: int, b: int) -> int:
                while b:
                    a, b = b, a % b
                return a
            e = random.randint(3, phi - 1)
            while gcd(e, phi) != 1:
                e = random.randint(3, phi - 1)
            return e
        
        e = find_coprime(phi)
        
        # Generate private key (d)
        def mod_inverse(e: int, phi: int) -> int:
            # Calculate modular multiplicative inverse
            def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
                if a == 0:
                    return b, 0, 1
                gcd, x1, y1 = extended_gcd(b % a, a)
                x = y1 - (b // a) * x1
                y = x1
                return gcd, x, y
            
            _, d, _ = extended_gcd(e, phi)
            return d % phi
        
        d = mod_inverse(e, phi)
        
        # Store the keys
        self.public_key = (e, n)
        self.private_key = (d, n)
    
    def encrypt(self, message: str, public_key: Tuple[int, int]) -> list:
        e, n = public_key
        # Convert each character to its ASCII value and encrypt
        encrypted = []
        for char in message:
            m = ord(char)
            # Encryption formula: c = (m^e) mod n
            c = pow(m, e, n)
            encrypted.append(c)
        return encrypted
    
    
    def decrypt(self, encrypted_msg: list, private_key: Tuple[int, int]) -> str:
        d, n = private_key
        # Decrypt each value and convert back to character
        decrypted = ""
        for c in encrypted_msg:
            # Decryption formula: m = (c^d) mod n
            m = pow(c, d, n)
            decrypted += chr(m)
        return decrypted
    

    def get_public_key(self) -> Tuple[int, int]:
        """Return the public key"""
        return self.public_key
    
    def get_private_key(self) -> Tuple[int, int]:
        """Return the private key"""
        return self.private_key
    
    # Methods for storing and retrieving keys
    def keys_to_string(self) -> Tuple[str, str]:
        """Convert keys to string format for storage"""
        if not self.public_key or not self.private_key:
            return None, None
        
        public_str = f"{self.public_key[0]},{self.public_key[1]}"
        private_str = f"{self.private_key[0]},{self.private_key[1]}"
        return public_str, private_str
    
    # Method to convert string format back to key tuples
    @staticmethod
    def keys_from_string(public_str: str, private_str: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Convert string format back to key tuples"""
        try:
            e, n1 = map(int, public_str.split(','))
            d, n2 = map(int, private_str.split(','))
            return (e, n1), (d, n2)
        except:
            return None, None
        

class SymmetricEncryption:
    # Class variable
    def __init__(self):
        self.block_size = 16
    
    # Static method to generate a random key of specified length
    @staticmethod
    def generate_key(length=16):
        """Generate a random encryption key of specified length"""
        import random
        return bytes([random.randint(0, 255) for _ in range(length)])
    
    # Encrypt/decrypt a single block using the key (XOR operation)
    def _transform_block(self, block, key, encrypt=True):
        """Transform a single block using the key"""
        if len(key) != self.block_size:
            raise ValueError(f"Key must be {self.block_size} bytes long")
            
        result = bytearray()
        for b, k in zip(block, key):
            if encrypt:
                val = (b + k) % 256
            else:
                val = (b - k) % 256
            result.append(val)
        return bytes(result)
    
    # Add PKCS7 padding to data to make it multiple of block size
    def pad_data(self, data):
        """Add PKCS7 padding"""
        pad_length = self.block_size - (len(data) % self.block_size)
        padding = bytes([pad_length] * pad_length)
        return data + padding
    
    # Remove PKCS7 padding from data (inverse of padding)
    def unpad_data(self, padded_data):
        """Remove PKCS7 padding"""
        pad_length = padded_data[-1]
        return padded_data[:-pad_length]
    
    # Encrypt data using the key (CBC mode) with PKCS7 padding
    def encrypt(self, key, plaintext):
        """
        Encrypt data using provided key
        
        Args:
            key (bytes): Encryption key
            plaintext (str/bytes): Data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        # Convert string to bytes if necessary
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        
        # Add padding
        padded_data = self.pad_data(plaintext)
        
        # Encrypt each block
        encrypted_blocks = []
        for i in range(0, len(padded_data), self.block_size):
            block = padded_data[i:i + self.block_size]
            encrypted_block = self._transform_block(block, key, encrypt=True)
            encrypted_blocks.append(encrypted_block)
        
        return b''.join(encrypted_blocks)
    
    # Decrypt data using the key (CBC mode) and remove padding 
    def decrypt(self, key, ciphertext):
        """
        Decrypt data using provided key
        
        Args:
            key (bytes): Encryption key
            ciphertext (bytes): Data to decrypt
            
        Returns:
            bytes: Decrypted data
        """
        # Decrypt each block
        decrypted_blocks = []
        for i in range(0, len(ciphertext), self.block_size):
            block = ciphertext[i:i + self.block_size]
            decrypted_block = self._transform_block(block, key, encrypt=False)
            decrypted_blocks.append(decrypted_block)
        
        # Join blocks and remove padding
        decrypted_data = b''.join(decrypted_blocks)
        return self.unpad_data(decrypted_data)