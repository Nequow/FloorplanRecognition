<div align="center">

# 🏠 3D Floorplan Web App

**Transform architectural floorplans into interactive 3D environments**

*Easily launch with Docker or run manually with Python + Node.js*

[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)]()
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue?style=for-the-badge&logo=docker)]()
[![Node.js](https://img.shields.io/badge/node-%3E=18.0.0-brightgreen?style=for-the-badge&logo=javascript)]()
[![Python](https://img.shields.io/badge/python-%3E=3.11.11-blueviolet?style=for-the-badge&logo=python)]()

</div>

<hr style="height:2px;border-width:0;color:gray;background-color:gray">

## 📸 Demo

<div align="center">
  <img src="docs/screenshot.png" alt="Web App Screenshot" width="90%" style="border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.1);" />
</div>

> 📌 **_Replace `docs/screenshot.png` with your own screenshot or animated GIF to showcase your app in action!_**

<hr style="height:2px;border-width:0;color:gray;background-color:gray">

## 📦 Before You Begin

### Required Model Checkpoints

Download and place the following model files in the `checkpoints` folder:

<table align="center" style="width:90%">
  <thead>
    <tr>
      <th align="center" style="width:35%">Model</th>
      <th align="center" style="width:35%">Description</th>
      <th align="center" style="width:30%">Download</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><code>Best_EfficientNet_B0.pt</code></td>
      <td align="center">🖼️ Image classification model</td>
      <td align="center"><a href="https://drive.google.com/file/d/1oyJfknmaAk0TNeMetndZbKtsiMjSvcVr/view?usp=sharing"><img src="https://img.shields.io/badge/download-model-success?style=for-the-badge" alt="Download" /></a></td>
    </tr>
    <tr>
      <td align="center"><code>cubicasa5k-rfdetr-wall-window-door-v3.pt</code></td>
      <td align="center">🧱 Object detection model<br />(walls, windows, doors)</td>
      <td align="center"><a href="https://drive.google.com/file/d/1ZzSI1BGaTm5I09qQOur3rb-YB75tJunq/view?usp=sharing"><img src="https://img.shields.io/badge/download-model-success?style=for-the-badge" alt="Download" /></a></td>
    </tr>
  </tbody>
</table>

<hr style="height:2px;border-width:0;color:gray;background-color:gray">

## 🚀 Getting Started

<div align="center">
  <p>Choose your preferred installation method below</p>
  <div style="display:inline-block;margin:0 15px;">
    <a href="#docker-option"><img src="https://img.shields.io/badge/Option%201-Docker-blue?style=for-the-badge&logo=docker" alt="Docker Option" /></a>
  </div>
  <div style="display:inline-block;margin:0 15px;">
    <a href="#manual-option"><img src="https://img.shields.io/badge/Option%202-Manual%20Setup-green?style=for-the-badge&logo=terminal" alt="Manual Option" /></a>
  </div>
</div>

---

### <img src="https://img.icons8.com/color/48/000000/docker.png" width="30" style="vertical-align:middle;margin-right:10px;"/> Option 1: Run with Docker

The easiest way to get started is using Docker. This method automatically sets up both the backend and frontend services with a single command.



#### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)



```bash
# Run the application with Docker
docker-compose up -d --build
```

<details>
<summary><strong>Docker Command Explanation</strong></summary>
<ul>
<li><code>up</code>: Creates and starts the containers</li>
<li><code>-d</code>: Runs containers in detached mode (background)</li>
<li><code>--build</code>: Builds images before starting containers</li>
</ul>
</details>

---

### <img src="https://img.icons8.com/fluency/48/000000/code.png" width="30" style="vertical-align:middle;margin-right:10px;"/> Option 2: Manual Setup

If you prefer to run the services separately or need more control over the setup, follow these instructions:



#### <img src="https://img.icons8.com/color/48/000000/python.png" width="24" style="vertical-align:middle;margin-right:5px;"/> Backend Setup (Terminal 1)

**Requirements:**
- Python `>= 3.11.11` (⚠️ recommended version: `3.11.11`)

**Setup Instructions:**

```bash
# Create a virtual environment with conda
conda create -n <env_name> python=3.11.11 ipykernel ipython
conda activate <env_name>

# Install the required packages
pip install -r requirements.txt
```

**Platform-Specific Setup:**
- **Windows Users:** Install GTK3 from [this link](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)

**Run the backend:**

```bash
python backend/__main__.py
```

---

#### <img src="https://img.icons8.com/color/48/000000/javascript.png" width="24" style="vertical-align:middle;margin-right:5px;"/> Frontend Setup (Terminal 2)

**Requirements:**
- `node ≥ 18.0.0`

**Setup Instructions:**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_BACKEND_URL=http://localhost:8000" > .env

# Start the development server
npm run dev
```


<strong>💡 Tip:</strong> Keep both terminal windows open while using the application. The backend must be running for the frontend to function properly.


<hr style="height:2px;border-width:0;color:gray;background-color:gray">

## 🔍 Using the Application

<div align="center">
  <table style="width:90%; margin:20px auto; border-collapse: separate; border-spacing: 0 10px;">
    <tr>
      <td align="center" width="70px">
        <img src="https://img.icons8.com/fluency/48/000000/browser-window.png" width="36"/>
      </td>
      <td>
        <strong>Step 1: Access the Application</strong><br/>
        Open your browser and navigate to <a href="http://localhost:5173" style="background-color:#f0f8ff; padding:2px 5px; border-radius:3px;">http://localhost:5173</a>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="https://img.icons8.com/fluency/48/000000/upload-to-cloud.png" width="36"/>
      </td>
      <td>
        <strong>Step 2: Upload Your Floorplan</strong><br/>
        Click on the upload button and select a floorplan image file (.jpg, .png, or .pdf)
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="https://img.icons8.com/fluency/48/000000/process.png" width="36"/>
      </td>
      <td>
        <strong>Step 3: Wait for Processing</strong><br/>
        The backend will detect walls, windows, and doors in your floorplan
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="https://img.icons8.com/fluency/48/000000/3d-select.png" width="36"/>
      </td>
      <td>
        <strong>Step 4: Explore the 3D Model</strong><br/>
        Interact with your 3D environment: rotate, zoom, and navigate
      </td>
    </tr>
  </table>
</div>

### 🛠️ Troubleshooting

<details>
<summary><strong>Common Issues & Solutions</strong></summary>
<br/>

- **Backend Connection Error**: Ensure the backend is running on <a href="http://localhost:8000">http://localhost:8000</a>
- **Model Loading Errors**: Verify you've downloaded and placed the model files in the `checkpoints` folder
- **Slow Processing**: Large or complex floorplans may take longer to process

</details>

> 💡 **Pro Tip**: You can change the backend port in the `backend/__main__.py` file and update the `.env` file in the frontend directory accordingly.
