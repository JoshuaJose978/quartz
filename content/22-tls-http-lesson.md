---
title: TLS HTTP Introduction
---

Scenario
![image-1](assets/pictures/tls-http-1.png)
The hacker can easily steal the credentials if the communication is not encrypted.
![image-2](assets/pictures/tls-http-2.png)

Symmetric Encryption

So we have to do the encryption with a key and the hacker does not know what the credentials are. But so is the server.
![image-3](assets/pictures/tls-http-3.png)

Send over the key? Maybe…
![image-4](assets/pictures/tls-http-4.png)

This is what we call Symmetric Encryption.

Asymmetric Encryption
![image-5](assets/pictures/tls-http-5.png)
Back to the scenario

The server gives the user its public key.

![image-6](assets/pictures/tls-http-6.png)

The user encrypts its key with the public key and sends it back to the server.
![image-7](assets/pictures/tls-http-7.png)
What should the hack do?
![image-8](assets/pictures/tls-http-8.png)

The key should be sent with a certificate to prove the site is [my-bank.com](http://my-bank.com). But the hacker can self-sign a certificate too.

![image-9](assets/pictures/tls-http-9.png)

This is where Certificate Authority (CA) comes in.
![imagefwefwe](assets/pictures/tls-http-final.png)
The certificate guarantees:

1. the communication is encrypted.
    
2. the server is who it says it is.
    

Naming convention

![image-fe](assets/pictures/tls-http-final-1.png)
