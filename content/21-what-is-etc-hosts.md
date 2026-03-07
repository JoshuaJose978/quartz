---
title: The `/etc/hosts` File A System-Level DNS Mechanism
---


## What is the hosts file?

The `/etc/hosts` file is a fundamental system file found on virtually all operating systems that maps hostnames to IP addresses. It's one of the oldest and simplest forms of name resolution in computer networking.

## Location by Operating System

- **Unix/Linux/macOS**: `/etc/hosts`
- **Windows**: `C:\Windows\System32\drivers\etc\hosts`

## Purpose and Function

The hosts file serves as a local, static lookup table for hostname resolution. When your computer needs to connect to a host by name (like "google.com"), it first checks the hosts file before consulting DNS servers.

## Format of the hosts file

The format is straightforward:
```
IP_address    hostname1    [hostname2] [hostname3] ...
```

Example:
```
127.0.0.1    localhost
192.168.1.10  myserver.local  myserver
10.0.0.5     database.internal
```

## How it works in the networking stack

```
Application wants to reach "example.com"
           |
           ▼
┌──────────────────────┐
│ Name Resolution Order│
├──────────────────────┤
│ 1. Check /etc/hosts  │
│ 2. Check DNS cache   │
│ 3. Query DNS servers │
└──────────┬───────────┘
           |
           ▼
   Connection established
```

## Common Use Cases

1. **Local development**:
   ```
   127.0.0.1    myproject.local dev.myapp.com
   ```

2. **Blocking websites**:
   ```
   127.0.0.1    adserver.example.net malware.example.com
   ```

3. **Network shortcuts**:
   ```
   192.168.1.55    printer database intranet
   ```

4. **Testing before DNS changes**:
   ```
   54.243.31.200    www.mycompany.com
   ```

5. **Overriding DNS for specific hosts**:
   ```
   10.0.0.5    api.thirdparty.com  # Point to internal version
   ```

## Advantages and Limitations

### Advantages
- Works without network connectivity
- Takes precedence over DNS
- Simple to modify
- No need for a DNS server
- Immediate changes (no cache clearing needed in most cases)

### Limitations
- Only applies to the local machine
- Requires administrative access to modify
- Not scalable for large networks
- No centralized management
- Can be forgotten when troubleshooting

## Relationship to DNS

The hosts file is essentially a precursor to DNS (Domain Name System). It performs a similar function but in a static, local manner:

```
┌───────────────┐     ┌────────────┐     ┌──────────────┐
│ Application   │     │ Resolver   │     │ DNS Server   │
│ looks up host │────►│ checks     │────►│ queried for  │
│ "example.com" │     │ /etc/hosts │     │ "example.com"│
└───────────────┘     │ FIRST      │     └──────────────┘
                      └────────────┘
```

## Administrative Aspects

- Requires root/administrator privileges to modify
- Changes take effect immediately on most systems
- Some applications may cache DNS independently
- Security software may monitor/protect this file

## Example of a typical hosts file

```
# This is an example hosts file

# Localhost entries
127.0.0.1       localhost
::1             localhost ip6-localhost

# Custom entries
192.168.1.100   fileserver
192.168.1.101   printserver
10.0.0.15       intranet.company.local

# Development entries
127.0.0.1       dev.myapp.com test.myapp.com

# Blocked sites
127.0.0.1       adserver.annoying.com
```

The hosts file is a simple yet powerful networking tool that has survived decades of technological evolution due to its simplicity and utility. Despite the widespread use of DNS, the hosts file remains relevant for local control over hostname resolution.
