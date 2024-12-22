## **Table of Contents**

1. Prerequisites
2. Step 1: Create a DigitalOcean Droplet
3. Step 2: Configure DNS A Records
4. Step 3: Connect to Your Droplet via SSH
5. Step 4: Update System Packages
6. Step 5: Install Docker
7. Step 6: Execute Docker Commands Without `sudo`
8. Step 7: Install Docker Compose
9. Step 8: Clone the Repository
10. Step 9: Configure Environment Variables
11. Step 10: Configure Docker Compose for Let's Encrypt
12. Step 11: Initialize Let's Encrypt Storage
13. Step 12: Deploy the Application with Docker Compose
14. Step 13: Verify the Deployment
15. Additional Recommendations

---

## **Prerequisites**

Before you begin, ensure you have the following:

- **DigitalOcean Account**: Sign up at [DigitalOcean](https://www.digitalocean.com/) if you don't have an account.
- **Domain Name**: You should own a domain name (e.g., `yourdomain.com`) and have access to its DNS settings.
- **SSH Key**: It's recommended to use SSH keys for authenticating with your Droplet. If you don't have one, you can generate it using `ssh-keygen`.
- **Basic Knowledge**: Familiarity with command-line operations and Docker concepts.

---

## **Step 1: Create a DigitalOcean Droplet**

1. **Log into DigitalOcean**:
   - Navigate to the [DigitalOcean Control Panel](https://cloud.digitalocean.com/login).
   - Enter your credentials to log in.

2. **Create a New Droplet**:
   - Click on the **"Create"** button in the top right corner and select **"Droplet"**.

3. **Choose an Image**:
   - Select the **Ubuntu** distribution (e.g., Ubuntu 22.04 LTS).

4. **Choose a Datacenter Region**:
   - Select a region closest to your target audience (e.g., New York, San Francisco).

5. **Choose a Plan**:
   - For optimal performance, especially for processing media files, consider selecting at least **$20/month** (4GB RAM, 2 vCPUs). Adjust based on your expected load.

6. **Authentication**:
   - **SSH Keys**: Add your public SSH key for secure access. If you don't have one, refer to [Generating an SSH Key](https://www.digitalocean.com/docs/ssh/create-ssh-keys/) and add it to your account.
   - **Password**: Alternatively, you can use a password, but **SSH keys** are recommended for enhanced security.

7. **Finalize and Create**:
   - Set a hostname (e.g., `nca-toolkit-droplet`).
   - Click **"Create Droplet"**.

---

## **Step 2: Configure DNS A Records**

1. **Access Domain DNS Settings**:
   - Log in to your domain registrar's website (e.g., GoDaddy, Namecheap).
   - Navigate to the DNS management section for your domain.

2. **Create an A Record**:
   - **Host**: `@` (represents the root domain, e.g., `yourdomain.com`)
   - **Points to**: Your Droplet's **IPv4** address (available in the DigitalOcean Control Panel under your Droplet's details)
   - **TTL**: Default or set to `3600` seconds

3. **Create a Subdomain (Optional)**:
   - If you prefer to use a subdomain (e.g., `api.yourdomain.com`), create another A record:
     - **Host**: `api`
     - **Points to**: Droplet's IPv4 address
     - **TTL**: `3600` seconds

4. **Save Changes**:
   - Ensure all records are saved. DNS propagation may take up to 24 hours, but typically completes within a few hours.

---
## **Step 3: Connect to Your Droplet**

You can connect to your DigitalOcean Droplet using one of the following methods:

### **Option 1: Using SSH**

1. **On Windows**:
   - Use **PowerShell** or **Command Prompt**.
   - Consider using [PuTTY](https://www.putty.org/) or the Windows Subsystem for Linux (WSL) for a better experience.

2. **Connect to Droplet**:
   - Use the following command, replacing `your_user` with your Droplet's username (typically `root` for initial access) and `your_droplet_ip` with the Droplet's IP address.

     ```bash
     ssh your_user@your_droplet_ip
     ```

   - **Example**:

     ```bash
     ssh root@192.0.2.1
     ```

3. **Accept the Host Key**:
   - The first time you connect, you'll be prompted to confirm the host key. Type `yes` and press **Enter**.

---

### **Option 2: Using the DigitalOcean Web Console**

If you encounter issues with SSH or prefer a web-based interface, the DigitalOcean Web Console provides direct access to your Droplet's terminal without the need for SSH.

1. **Log into DigitalOcean**:
   - Navigate to the [DigitalOcean Control Panel](https://cloud.digitalocean.com/login) and log in to your account.

2. **Navigate to Your Droplet**:
   - Click on **"Droplets"** in the top navigation bar.
   - Select the Droplet you wish to access from the list.

3. **Launch the Web Console**:
   - On your Droplet's overview page, click the **"Console"** button. This is usually located under the **"Access"** section or in the top-right corner.

4. **Access the Console**:
   - A new browser window or tab will open, displaying the Droplet's terminal interface.
   - Log in using your Droplet's username and password or your SSH key credentials.

5. **Perform Operations**:
   - You can now execute command-line instructions as needed, just as you would via SSH.
   - This is especially useful for troubleshooting SSH issues or performing administrative tasks without an SSH client.

6. **Close the Console**:
   - Once you are done, simply close the browser tab or window to exit the console.

---

## **Step 4: Update System Packages**

Once connected to your Droplet (via SSH or Web Console), update your system packages:

```bash
sudo apt update && sudo apt upgrade -y
```

- **Explanation**:
  - `sudo`: Executes the command with administrative privileges.
  - `apt update`: Updates the package index.
  - `apt upgrade -y`: Upgrades all installed packages to their latest versions without prompting.

---

## **Step 5: Install Docker**

1. **Install Necessary Packages**:

   ```bash
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
   ```

2. **Add Docker’s Official GPG Key**:

   ```bash
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   ```

3. **Set Up the Stable Repository**:

   ```bash
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

4. **Install Docker Engine**:

   ```bash
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io
   ```

5. **Verify Docker Installation**:

   ```bash
   sudo docker run hello-world
   ```

   - **Expected Output**: Displaying a "Hello from Docker!" message.

---

## **Step 6: Execute Docker Commands Without `sudo`**

By default, the `docker` command can only be run by the **root** user or by a user in the `docker` group, which is automatically created during Docker’s installation process. To execute `docker` commands without prefixing them with `sudo`, follow these steps:

1. **Add Your User to the `docker` Group**:

   ```bash
   sudo usermod -aG docker ${USER}
   ```

   - **Explanation**:
     - `sudo`: Executes the command with administrative privileges.
     - `usermod -aG docker ${USER}`: Adds your current user to the `docker` group.

2. **Apply the New Group Membership**:

   - **Option 1**: Log out of the server and back in.
   - **Option 2**: Refresh your group membership in the current session without logging out:

     ```bash
     su - ${USER}
     ```

     - **Note**: You will be prompted to enter your user’s password to continue.

3. **Verify Group Membership**:

   ```bash
   groups
   ```

   - **Expected Output**:

     ```
     your_username sudo docker
     ```

   - **Explanation**: This output indicates that your user is now part of the `docker` group.

4. **Confirm Docker Commands Execute Without `sudo`**:

   ```bash
   docker run hello-world
   ```

   - **Expected Output**: Similar to the earlier verification, displaying a "Hello from Docker!" message without needing `sudo`.

5. **Adding Another User to the `docker` Group (If Needed)**:

   If you need to add a user to the `docker` group that you’re not currently logged in as, specify the username explicitly:

   ```bash
   sudo usermod -aG docker username
   ```

   - **Replace** `username` with the actual username.

---

## **Step 7: Install Docker Compose**

1. **Download the Latest Version of Docker Compose**:

   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   ```

   - **Note**: Replace `2.20.2` with the latest version number if a newer version is available. You can check the latest version [here](https://github.com/docker/compose/releases).

2. **Apply Executable Permissions**:

   ```bash
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Create a Symbolic Link (Optional)**:

   ```bash
   sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
   ```

4. **Verify Docker Compose Installation**:

   ```bash
   docker-compose --version
   ```

   - **Expected Output**: `docker-compose version 2.32.1`

---

## **Step 8: Clone the Repository**

1. **Install Git (If Not Already Installed)**:

   ```bash
   sudo apt install -y git
   ```

2. **Navigate to the Home Directory**:

   ```bash
   cd ~
   ```

3. **Clone Your Repository**:

   ```bash
   git clone https://github.com/your-username/your-repository.git
   ```

   - **Replace** `your-username/your-repository.git` with your actual GitHub repository URL.

4. **Navigate to the Project Directory**:

   ```bash
   cd your-repository
   ```

---

## **Step 9: Configure Environment Variables**

1. **Create a `.env` File**:

   - Copy the provided [`.env.example`](.env.example ) to `.env`:

     ```bash
     cp .env.example .env
     ```

2. **Edit the `.env` File**:

   - Open the file using a text editor like `nano`:

     ```bash
     nano .env
     ```

   - **Populate the Variables**:
     - Replace placeholder values with your actual configuration.

     ```env
     # General Environment Variables
     API_KEY=your_secure_api_key

     # Google Cloud Platform (GCP) Environment Variables
     GCP_SA_CREDENTIALS='{"type":"service_account","project_id":"your_project_id",...}'
     GCP_BUCKET_NAME=your_gcp_bucket_name

     # S3-Compatible Storage Environment Variables (if applicable)
     S3_ENDPOINT_URL=https://s3.your-provider.com
     S3_ACCESS_KEY=your_s3_access_key
     S3_SECRET_KEY=your_s3_secret_key

     # Gunicorn Configuration
     GUNICORN_WORKERS=4
     GUNICORN_TIMEOUT=300

     # Whisper Configuration
     WHISPER_CACHE_DIR=/app/whisper_cache

     # Build Number (Optional)
     BUILD_NUMBER=1
     ```

   - **Save and Exit**:
     - In `nano`, press `CTRL + O` to write out (save) the file, then `CTRL + X` to exit.

   - **Secure Sensitive Variables**:
     - Ensure that `.env` is listed in your [`.gitignore`](.gitignore ) to prevent sensitive data from being pushed to version control.

---

## **Step 10: Configure Docker Compose for Let's Encrypt**

1. **Ensure Traefik Configuration is Updated**:

   - Your existing `docker-compose.yaml` should already include Traefik with Let's Encrypt configuration.
   - Confirm that the [`traefik/traefik.yml`](traefik/traefik.yml ) file is correctly set up (as per your previous configuration).

2. **Update `compose.yaml`**:

   Ensure that `compose.yaml` includes necessary services and configurations.

   - **Example `compose.yaml` Structure**:

     ```yaml
     version: '3.8'

     services:
       traefik:
         image: traefik:v3.1
         command:
           - "--providers.docker=true"
           - "--providers.docker.exposedbydefault=false"
           - "--entrypoints.web.address=:80"
           - "--entrypoints.websecure.address=:443"
           - "--certificatesresolvers.myresolver.httpchallenge=true"
           - "--certificatesresolvers.myresolver.httpchallenge.entrypoint=web"
           - "--certificatesresolvers.myresolver.acme.email=${CERT_EMAIL}"
           - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
           - "--log.level=INFO"
         ports:
           - "80:80"
           - "443:443"
         volumes:
           - "/var/run/docker.sock:/var/run/docker.sock:ro"
           - "./traefik/traefik.yml:/etc/traefik/traefik.yml"
           - "./traefik/acme.json:/letsencrypt/acme.json"
         restart: unless-stopped
         container_name: traefik
         networks:
           - traefik_network

       app:
         build:
           context: .
           dockerfile: Dockerfile
         labels:
           - "traefik.enable=true"
           - "traefik.http.routers.app.rule=Host(`${DOMAIN}`)"
           - "traefik.http.routers.app.entrypoints=websecure"
           - "traefik.http.routers.app.tls=true"
           - "traefik.http.routers.app.tls.certresolver=myresolver"
         env_file:
           - .env
         restart: unless-stopped
         container_name: no_code_architects_toolkit
         networks:
           - traefik_network

     networks:
       traefik_network:
         driver: bridge
     ```

   - **Replace Placeholders**:
     - `${CERT_EMAIL}`: Your email address for Let's Encrypt.
     - `${DOMAIN}`: Your domain name (e.g., `yourdomain.com`).

---

## **Step 11: Initialize Let's Encrypt Storage**

1. **Create `acme.json` File**:

   ```bash
   mkdir -p traefik
   touch traefik/acme.json
   ```

2. **Set Permissions**:

   ```bash
   chmod 600 traefik/acme.json
   ```

   - **Explanation**: This ensures that only Traefik can read/write to the certificate storage file, enhancing security.

---

## **Step 12: Deploy the Application with Docker Compose**

1. **Build and Launch Containers**:

   ```bash
   docker-compose up --build -d
   ```

   - **Flags**:
     - `--build`: Rebuilds the images before starting the containers.
     - `-d`: Runs the containers in detached mode (in the background).

2. **Monitor Logs (Optional)**:

   - **Traefik Logs**:

     ```bash
     docker logs -f traefik
     ```

   - **App Logs**:

     ```bash
     docker logs -f no_code_architects_toolkit
     ```

   - **Explanation**:
     - Monitoring logs helps in troubleshooting any issues during the deployment.

3. **Verify Services Are Running**:

   ```bash
   docker ps
   ```

   - **Expected Output**:

     ```
     CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS          PORTS                                      NAMES
     abcdef123456   traefik:v3.1    "/entrypoint.sh --p…"   10 seconds ago   Up 9 seconds    0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp   traefik
     123456abcdef   your-app-image   "/app/run_gunicorn/*"   8 seconds ago    Up 7 seconds    8080/tcp                                   no_code_architects_toolkit
     ```

---

## **Step 13: Verify the Deployment**

1. **Access Your Application**:

   - Open a web browser and navigate to `https://your-domain.com`.
   - **Expected Result**: Your application should be accessible over HTTPS with a valid SSL certificate.

2. **Check SSL Certificate**:

   - Click on the padlock icon in the browser's address bar to view SSL certificate details.
   - **Ensure**: The certificate is issued by Let's Encrypt and corresponds to your domain.

3. **API Verification (Optional)**:

   - Use tools like **Postman** or **cURL** to test your API endpoints.
   - **Example**:

     ```bash
     curl -X POST https://your-domain.com/v1/ffmpeg/compose \
       -H "x-api-key: your_api_key" \
       -H "Content-Type: application/json" \
       -d '{
             "inputs": [
               {"file_url": "https://example.com/video1.mp4"},
               {"file_url": "https://example.com/video2.mp4"}
             ],
             "filters": [...],
             "output_options": {...}
           }'
     ```

   - **Expected Response**: As per your API's functionality, you should receive a successful response indicating that the media composition task has been queued or completed.

4. **Monitor Traefik and App Logs**:

   - Ensure there are no errors in the logs.

     ```bash
     docker logs traefik
     docker logs no_code_architects_toolkit
     ```

---

## **Additional Recommendations**

1. **Secure Your Droplet**:

   - **Create a Non-Root User**:

     ```bash
     adduser your_username
     usermod -aG sudo your_username
     ```

   - **Configure SSH Access**:
     - Disable root SSH login for enhanced security.

       ```bash
       sudo nano /etc/ssh/sshd_config
       ```

       - Set `PermitRootLogin` to `no`.
       - Reload SSH:

         ```bash
         sudo systemctl reload sshd
         ```

2. **Set Up a Firewall**:

   - **Install UFW (Uncomplicated Firewall)**:

     ```bash
     sudo apt install -y ufw
     ```

   - **Allow SSH and Web Traffic**:

     ```bash
     sudo ufw allow OpenSSH
     sudo ufw allow 80/tcp
     sudo ufw allow 443/tcp
     ```

   - **Enable UFW**:

     ```bash
     sudo ufw enable
     ```

3. **Enable Automatic Updates**:

   - **Install Unattended Upgrades**:

     ```bash
     sudo apt install -y unattended-upgrades
     ```

   - **Configure Automatic Updates**:

     ```bash
     sudo dpkg-reconfigure --priority=low unattended-upgrades
     ```

4. **Regular Backups**:

   - Consider setting up regular backups of your Droplet and any persistent data to prevent data loss.

5. **Monitoring and Alerts**:

   - Implement monitoring tools (e.g., **Prometheus**, **Grafana**) to keep an eye on your application's performance and receive alerts for any anomalies.

6. **Scaling Considerations**:

   - If you anticipate high traffic or increased load, consider configuring Docker Compose services for scalability or exploring container orchestration platforms like **Kubernetes**.

7. **Optimize Dockerfile and Images**:

   - Regularly update your Docker images to incorporate security patches and performance improvements.

8. **Documentation**:

   - Keep your [`README.md`](README.md ) and other documentation up-to-date with any changes in the setup or deployment process.

---

## **Conclusion**

By following this updated guide, you will have a fully functional **No-Code Architects Toolkit** deployed on a **DigitalOcean Droplet** using **Docker Compose** with **Traefik** managing the reverse proxy and SSL via **Let's Encrypt**. Additionally, you've configured Docker to run commands without needing `sudo`, enhancing your workflow efficiency.

Ensure to customize the placeholders with your actual domain, API keys, and other configuration details to suit your specific needs. If you encounter any issues or have further questions, feel free to ask!
---

## **Step 4: Update System Packages**

Once connected to your Droplet:

```bash
sudo apt update && sudo apt upgrade -y
```

- **Explanation**:
  - `sudo`: Executes the command with administrative privileges.
  - `apt update`: Updates the package index.
  - `apt upgrade -y`: Upgrades all installed packages to their latest versions without prompting.

---

## **Step 5: Install Docker**

1. **Install Necessary Packages**:

   ```bash
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
   ```

2. **Add Docker’s Official GPG Key**:

   ```bash
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   ```

3. **Set Up the Stable Repository**:

   ```bash
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

4. **Install Docker Engine**:

   ```bash
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io
   ```

5. **Verify Docker Installation**:

   ```bash
   sudo docker run hello-world
   ```

   - If Docker is installed correctly, you'll see a "Hello from Docker!" message.

---

## **Step 6: Execute Docker Commands Without `sudo`**

By default, the `docker` command can only be run by the **root** user or by a user in the `docker` group, which is automatically created during Docker’s installation process. To execute `docker` commands without prefixing them with `sudo`, follow these steps:

1. **Add Your User to the `docker` Group**:

   ```bash
   sudo usermod -aG docker ${USER}
   ```

   - **Explanation**:
     - `sudo`: Executes the command with administrative privileges.
     - `usermod -aG docker ${USER}`: Adds your current user to the `docker` group.

2. **Apply the New Group Membership**:

   - **Option 1**: Log out of the server and back in.
   - **Option 2**: Refresh your group membership in the current session without logging out:

     ```bash
     su - ${USER}
     ```

     - **Note**: You will be prompted to enter your user’s password to continue.

3. **Verify Group Membership**:

   ```bash
   groups
   ```

   - **Expected Output**:

     ```
     your_username sudo docker
     ```

   - **Explanation**: This output indicates that your user is now part of the `docker` group.

4. **Confirm Docker Commands Execute Without `sudo`**:

   ```bash
   docker run hello-world
   ```

   - **Expected Output**: Similar to the earlier verification, displaying a "Hello from Docker!" message without needing `sudo`.

5. **Adding Another User to the `docker` Group (If Needed)**:

   If you need to add a user to the `docker` group that you’re not currently logged in as, specify the username explicitly:

   ```bash
   sudo usermod -aG docker username
   ```

   - **Replace** `username` with the actual username.

---

## **Step 7: Install Docker Compose**

1. **Download the Latest Version of Docker Compose**:

   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   ```

   - **Note**: Replace `2.20.2` with the latest version number if a newer version is available. You can check the latest version [here](https://github.com/docker/compose/releases).

2. **Apply Executable Permissions**:

   ```bash
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Create a Symbolic Link (Optional)**:

   ```bash
   sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
   ```

4. **Verify Docker Compose Installation**:

   ```bash
   docker-compose --version
   ```

   - **Expected Output**: `docker-compose version 2.20.2, build <commit>`

---

## **Step 8: Clone the Repository**

1. **Install Git (If Not Already Installed)**:

   ```bash
   sudo apt install -y git
   ```

2. **Navigate to the Home Directory**:

   ```bash
   cd ~
   ```

3. **Clone Your Repository**:

   ```bash
   git clone https://github.com/your-username/your-repository.git
   ```

   - **Replace** `your-username/your-repository.git` with your actual GitHub repository URL.

4. **Navigate to the Project Directory**:

   ```bash
   cd your-repository
   ```

---

## **Step 9: Configure Environment Variables**

1. **Create a `.env` File**:

   - Copy the provided [`.env.example`](.env.example ) to `.env`:

     ```bash
     cp .env.example .env
     ```

2. **Edit the `.env` File**:

   - Open the file using a text editor like `nano`:

     ```bash
     nano .env
     ```

   - **Populate the Variables**:
     - Replace placeholder values with your actual configuration.
     - **Example**:

       ```env
       # General Environment Variables
       API_KEY=your_secure_api_key

       # Google Cloud Platform (GCP) Environment Variables
       GCP_SA_CREDENTIALS='{"type":"service_account","project_id":"your_project_id",...}'
       GCP_BUCKET_NAME=your_gcp_bucket_name

       # S3-Compatible Storage Environment Variables (if applicable)
       S3_ENDPOINT_URL=https://s3.your-provider.com
       S3_ACCESS_KEY=your_s3_access_key
       S3_SECRET_KEY=your_s3_secret_key

       # Gunicorn Configuration
       GUNICORN_WORKERS=4
       GUNICORN_TIMEOUT=300

       # Whisper Configuration
       WHISPER_CACHE_DIR=/app/whisper_cache

       # Build Number (Optional)
       BUILD_NUMBER=1
       ```

   - **Save and Exit**:
     - In `nano`, press `CTRL + O` to write out (save) the file, then `CTRL + X` to exit.

   - **Secure Sensitive Variables**:
     - Ensure that `.env` is listed in your [`.gitignore`](.gitignore ) to prevent sensitive data from being pushed to version control.

---

## **Step 10: Configure Docker Compose for Let's Encrypt**

1. **Ensure Traefik Configuration is Updated**:

   - Your existing `docker-compose.yaml` should already include Traefik with Let's Encrypt configuration.
   - Confirm that the [`traefik/traefik.yml`](traefik/traefik.yml ) file is correctly set up (as per your previous configuration).

2. **Update `docker-compose.yaml`**:

   Ensure that `docker-compose.yaml` includes necessary services and configurations.

   - **Example `docker-compose.yaml` Structure**:

     ```yaml
     version: '3.8'

     services:
       traefik:
         image: traefik:v3.1
         command:
           - "--providers.docker=true"
           - "--providers.docker.exposedbydefault=false"
           - "--entrypoints.web.address=:80"
           - "--entrypoints.websecure.address=:443"
           - "--certificatesresolvers.myresolver.acme.httpchallenge=true"
           - "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
           - "--certificatesresolvers.myresolver.acme.email=${CERT_EMAIL}"
           - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
           - "--log.level=INFO"
         ports:
           - "80:80"
           - "443:443"
         volumes:
           - "/var/run/docker.sock:/var/run/docker.sock:ro"
           - "./traefik/traefik.yml:/etc/traefik/traefik.yml"
           - "./traefik/acme.json:/letsencrypt/acme.json"
         restart: unless-stopped
         container_name: traefik
         networks:
           - traefik_network

       app:
         build:
           context: .
           dockerfile: Dockerfile
         labels:
           - "traefik.enable=true"
           - "traefik.http.routers.app.rule=Host(\`${DOMAIN}\`)"
           - "traefik.http.routers.app.entrypoints=websecure"
           - "traefik.http.routers.app.tls=true"
           - "traefik.http.routers.app.tls.certresolver=myresolver"
         env_file:
           - .env
         restart: unless-stopped
         container_name: no_code_architects_toolkit
         networks:
           - traefik_network

     networks:
       traefik_network:
         driver: bridge
     ```

   - **Replace Placeholders**:
     - `${CERT_EMAIL}`: Your email address for Let's Encrypt.
     - `${DOMAIN}`: Your domain name (e.g., `yourdomain.com`).

---

## **Step 11: Initialize Let's Encrypt Storage**

1. **Create `acme.json` File**:

   ```bash
   mkdir -p traefik
   touch traefik/acme.json
   ```

2. **Set Permissions**:

   ```bash
   chmod 600 traefik/acme.json
   ```

   - **Explanation**: This ensures that only Traefik can read/write to the certificate storage file, enhancing security.

---

## **Step 12: Deploy the Application with Docker Compose**

1. **Build and Launch Containers**:

   ```bash
   docker-compose up --build -d
   ```

   - **Flags**:
     - `--build`: Rebuilds the images before starting the containers.
     - `-d`: Runs the containers in detached mode (in the background).

2. **Monitor Logs (Optional)**:

   - **Traefik Logs**:

     ```bash
     docker logs -f traefik
     ```

   - **App Logs**:

     ```bash
     docker logs -f no_code_architects_toolkit
     ```

   - **Explanation**:
     - Monitoring logs helps in troubleshooting any issues during the deployment.

3. **Verify Services Are Running**:

   ```bash
   docker ps
   ```

   - **Expected Output**:

     ```
     CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS          PORTS                                      NAMES
     abcdef123456   traefik:3.1    "/entrypoint.sh --p…"   10 seconds ago   Up 9 seconds    0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp   traefik
     123456abcdef   your-app-image   "/app/run_gunicorn/*"   8 seconds ago    Up 7 seconds    8080/tcp                                   no_code_architects_toolkit
     ```

---

## **Step 13: Verify the Deployment**

1. **Access Your Application**:

   - Open a web browser and navigate to `https://your-domain.com`.
   - **Expected Result**: Your application should be accessible over HTTPS with a valid SSL certificate.

2. **Check SSL Certificate**:

   - Click on the padlock icon in the browser's address bar to view SSL certificate details.
   - **Ensure**: The certificate is issued by Let's Encrypt and corresponds to your domain.

3. **API Verification (Optional)**:

   - Use tools like **Postman** or **cURL** to test your API endpoints.
   - **Example**:

     ```bash
        curl --location 'https://{your DNS Address}' \
        --header 'x-api-key: {your-key}'
     ```

   - **Expected Response**: As per your API's functionality, you should receive a successful response indicating that the media composition task has been queued or completed.

4. **Monitor Traefik and App Logs**:

   - Ensure there are no errors in the logs.

     ```bash
     docker logs traefik
     docker logs no_code_architects_toolkit
     ```

## **Conclusion**

By following this updated guide, you will have a fully functional **No-Code Architects Toolkit** deployed on a **DigitalOcean Droplet** using **Docker Compose** with **Traefik** managing the reverse proxy and SSL via **Let's Encrypt**. Additionally, you've configured Docker to run commands without needing `sudo`, enhancing your workflow efficiency.
