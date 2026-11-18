# Research Workstation & Execution Environment

## 1. Observed Host Analysis Environment

Exact software platform on which all static extractions, Merkle verifications, cryptographic proofs, and test runs were executed:

| Layer | Exact Observed Value |
|---|---|
| **Operating System** | `Linux-6.14.0-37-generic-x86_64-with-glibc2.39` |
| **Python Interpreter** | `Python 3.12.3` (`[GCC 13.3.0]`) |
| **Disassembly Framework** | `Capstone 5.0.7` (`ARM` + `Thumb` modes) |
| **OpenSSL Runtime (Host)** | `OpenSSL 3.0.13 30 Jan 2024` |
| **JavaScript Engine (Syntax Verification)** | `Node.js v18.19.1` |
| **Binary Inspection Utilities** | `GNU readelf (GNU Binutils for Ubuntu) 2.42` |
| **Version Control** | `git version 2.43.0` |
| **Absent Tools (Explicit Disclosure)** | No `qemu-arm` / `qemu-arm-static`, no external hardware NAND chip programmer, no `binwalk` in container |

---

## 2. OpenSSL 3.x vs. Legacy Key/Cipher Note

Host verification uses `OpenSSL 3.0.13` purely for offline container manipulation (`openssl pkeyutl -verifyrecover` and `openssl enc -aes-128-cbc -nopad`), whereas the analyzed firmware executes `OpenSSL 1.0.0d` inside target ARMv7 binaries (`libssl.so.1.0.0`).
