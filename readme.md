# To do before

The checkpoints should be downloaded from the following links below and placed in the `checkpoints` folder:

- `Best_EfficientNet_B0.pt` [[Download](https://drive.google.com/file/d/1oyJfknmaAk0TNeMetndZbKtsiMjSvcVr/view?usp=sharing)]: The checkpoint for the image classification model.
- `cubicasa5k-rfdetr-wall-window-door-v3.pt` [[Download](https://drive.google.com/file/d/1ZzSI1BGaTm5I09qQOur3rb-YB75tJunq/view?usp=sharing)]: The checkpoint for the object detection model.

# Run with Docker

If you want to run the application using Docker, you can use the provided `docker-compose.yml` file. This will set up both the backend and frontend services. To run the application with Docker, execute the following command in the root directory of the project:

```
docker-compose up -d --build
```

# Backend (One Terminal)

Version requirements:

- `python ≥ 3.11.11` (but 3.11.11 is recommended since the code is tested on it)

Create a virtual environment with conda:

```
conda create -n <env_name> python=3.11.11 ipykernel ipython
conda activate <env_name>
```

Install the required packages using pip:

```
pip install -r requirements.txt
```

**If you are on windows, we have to install GTK3 from this [link](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases). Download the `.exe` and execute it.**

run the server:

```
python backend/__main__.py
```

# Frontend (Another Terminal)

Version requirements:

- `node ≥ 18.0.0`

Enter the `frontend` folder and install the required packages:

```
cd frontend
npm install
```

Before running, create an `.env` file in the `frontend` directory and put this inside:

```
VITE_BACKEND_URL=http://localhost:8000
```

Finally, run the frontend:

```
npm run dev
```

# Usage

Open your browser and go to `http://localhost:5173` to access the web application (frontend). And the backend will be running on `http://localhost:8000` by default. You can change the port in the `backend/__main__.py` file if needed.
