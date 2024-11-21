# 🕵️‍♂️ SpearCopy

**SpearCopy** is an educational and auditing tool designed to clone websites locally and capture credentials entered into forms. It’s ideal for controlled environments such as internal network testing and does not require Internet access.

> **⚠️ Disclaimer:** This project is intended **only for educational purposes** and testing in controlled environments. **Misuse of this tool is strictly prohibited.** I am not responsible for any damage caused by improper use of this software.

---

## ✨ **Features**

- **📋 Website cloning:** Downloads the full content of a webpage, including HTML, CSS, JavaScript, images, and other resources, preserving the original structure.
- **🦝 Credential capture:** Modifies forms to capture and log entered data in JSON format.
- **💻 Local HTTP server:** Hosts the cloned site locally for testing.
- **💀 Customizable payload:** Includes an editable JavaScript payload to tailor phishing behavior.
- **📚 Download management:** Avoids duplicate downloads and organizes resources in folders based on the target URL.

---

## 🛠️ **Requirements**

- Python 3.9 or higher.
- Dependencies listed in `requirements.txt` (install them with `pip install -r requirements.txt`).

---

## 🚀 **Usage**

### **Main Commands**

1. **Clone a website and start the server:**

   ```bash
   python main.py start <url>
   ```

   - Downloads the specified website into `tmp/<hash>/public`.
   - Starts a local HTTP server at `http://localhost:8080` to serve the cloned site.

2. **Clean the temporary directory:**

   ```bash
   python main.py clean
   ```

   - Deletes all files and folders under the `tmp` directory.

---

## 📁 **File Structure**

### **Generated Files**

When running the `start` command, the cloned site is saved in the following structure:

```python
tmp/
└── <hash_md5>/
    ├── public/        # Contains the cloned website.
    │   ├── index.html # Main cloned page.
    │   ├── css/       # Local or remote CSS files.
    │   ├── js/        # Local or remote JavaScript files.
    │   └── ...        # Other resources (images, videos, etc.).
    └── logs/          # Folder for captured data logs.
        └── <log_id>.json
```

### **Captured Data Logs**

Each submitted form is logged as a JSON file in the `logs` folder. An example log looks like this:

```json
{
   "local_url": "http://evil.com/index.html",
   "remote_url": "http://realwebsite.com/index.html",
   "address": "192.168.0.10",
   "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.94 Safari/537.36",
   "data": {
      "username": "test_user",
      "password": "1234"
   }
}
```

---

## 📋 **Payload JavaScript**

The credential-capturing behavior is defined in the `capture.js` file. By default, it intercepts form submissions, prevents them from being sent, and logs the captured data via the `/capture` endpoint.

You can edit the `capture.js` file to customize the phishing behavior.

---

## 📢 **Example Usage**

1. Run the command to clone a website:

   ```bash
   python main.py start https://example.com
   ```

   This will download the site and serve it at `http://localhost:8080`. All files will be stored in `tmp/<hash_md5>/public`.

2. Open the cloned site in a browser.

3. Submit data into a form and check the console or the logs stored in `tmp/<hash_md5>/logs`.

4. To clean up temporary files:

   ```bash
   python main.py clean
   ```

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome! Feel free to check [issues page](https://github.com/sammwyy/spearcopy/issues).

---

## ❤️ Show your support

Give a ⭐️ if this project helped you! Or buy me a coffeelatte 🙌 on [Ko-fi](https://ko-fi.com/sammwy)

---

## 📝 License

Copyright © 2024 [Sammwy](https://github.com/sammwyy). This project is [MIT](LICENSE) licensed.
