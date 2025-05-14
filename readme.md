# To read before

Read the readme file in the `checkpoints` folder to know how to download the checkpoints.

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

Then, run the frontend:

```
npm run dev
```

# Usage

Open your browser and go to `http://localhost:5173` to access the web application (frontend). And the backend will be running on `http://localhost:8000` by default. You can change the port in the `backend/__main__.py` file if needed.
