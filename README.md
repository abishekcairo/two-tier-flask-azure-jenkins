Two-Tier Flask App: CI/CD with Docker and Jenkins on Azure
A Flask + MySQL "Notes Board" that is built, tested and deployed automatically.
Every push to main triggers a Jenkins pipeline on an Azure VM.

Architecture
```mermaid
flowchart LR
Dev[Developer] -->|git push| GH[GitHub repository]
GH -->|webhook| J[Jenkins on Azure VM]
subgraph VM[Azure Ubuntu VM]
J -->|docker compose up| W[Flask container]
W -->|SQL| D[(MySQL container and volume)]
end
U[Browser] -->|port 5000| W
```

Tech stack
Python 3.12, Flask, gunicorn, PyMySQL
MySQL 8.4
Docker and Docker Compose
Jenkins (declarative pipeline)
Microsoft Azure (virtual machine, network security group)
Pipeline stages
Checkout
Build image
Unit tests
Deploy with Docker Compose
Health check
Screenshots
<img width="1533" height="645" alt="Screenshot 2026-10-13 212030" src="https://github.com/user-attachments/assets/467010c5-6f89-441e-8a90-5ac61dd19662" />
<img width="1535" height="693" alt="Screenshot 2026-10-15 230852" src="https://github.com/user-attachments/assets/77aaa46c-ddc1-4849-b533-63bbd12a53c2" />
<img width="1535" height="777" alt="Screenshot 2026-10-15 203556" src="https://github.com/user-attachments/assets/a209620b-2f03-4885-8e11-89a46bfb9eea" />
<img width="1535" height="740" alt="Screenshot 2026-10-15 220726" src="https://github.com/user-attachments/assets/fa0024bc-987e-4fd8-87ae-8895eb2b2dc8" />
<img width="1535" height="817" alt="Screenshot 2026-10-15 222844" src="https://github.com/user-attachments/assets/7c5a7ab1-5ec7-47af-aa96-45a185709365" />
<img width="1527" height="692" alt="Screenshot 2026-10-15 223244" src="https://github.com/user-attachments/assets/cc194273-abfd-4be3-a911-a6cd5247d427" />
<img width="1535" height="692" alt="Screenshot 2026-10-15 223309" src="https://github.com/user-attachments/assets/c38b1b87-7ee8-4c09-8289-4196b634d799" />
<img width="1266" height="686" alt="Screenshot 2026-10-15 224741" src="https://github.com/user-attachments/assets/0688e348-cfb6-4f28-aba8-b0bc3162aa32" />
<img width="1535" height="776" alt="Screenshot 2026-10-15 230250" src="https://github.com/user-attachments/assets/3fcee538-3abb-4e02-bf14-f95d4ee18cfb" />
<img width="1535" height="685" alt="Screenshot 2026-10-15 230320" src="https://github.com/user-attachments/assets/22214248-997f-4d80-b2f3-2ccdfcd4cfa9" />
<img width="1237" height="777" alt="Screenshot 2026-10-16 202057" src="https://github.com/user-attachments/assets/3e236cea-c979-4ba4-84b4-1a6070665447" />


Run it yourself
```bash
git clone https://github.com/<your-username>/two-tier-flask-azure-jenkins.git
cd two-tier-flask-azure-jenkins
cp .env.example .env # then set DB_PASSWORD in .env
docker compose up -d --build
```

Open http://localhost:5000

Design decisions
The database port is not published, so only the web container can reach MySQL.
Notes live in a Docker volume and survive restarts and redeploys.
The database password is stored in Jenkins credentials, never in Git.
Docker health checks and a pipeline health stage confirm both tiers are working.
The web container runs as a non-root user.
What I learned
<write 3 or 4 points in your own words>
