import random
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

clients = {}
trainings = []


class TrainingRequest(BaseModel):
    name: str
    problem: str


class TrainingResponse(BaseModel):
    id: int
    name: str
    problem: str
    cost: int
    revenue: int
    completed: bool
    success: bool


class TotalRevenue(BaseModel):
    total_revenue: int


class ClientInfo(BaseModel):
    completed_trainings: int
    education_costs: int
    revenue: int
    trainings: List[TrainingResponse]


@app.get("/")
def root():
    return {"message": "Puss in Boots Consulting"}


@app.post("/trainings/", response_model=TrainingResponse)
def start_training(request: TrainingRequest):
    training_id = len(trainings)
    name = request.name
    problem = request.problem
    cost = random.randint(20, 30)
    revenue = random.randint(40, 50)
    training = {
        "id": training_id,
        "name": name,
        "problem": problem,
        "cost": cost,
        "revenue": revenue,
        "completed": False,
        "success": False
    }
    trainings.append(training)
    if name not in clients.keys():
        clients[name] = []
    clients[name].append(training)
    return training


@app.post("/trainings/{training_id}/", response_model=TrainingResponse)
def complete_training(training_id: int):
    try:
        training = trainings[training_id]
    except IndexError:
        raise HTTPException(status_code=404, detail="Training not found")
    if training["completed"]:
        raise HTTPException(status_code=400, detail="Training has already been completed")
    training["completed"] = True
    success = random.randint(1, 10) > 1
    if not success:
        training["revenue"] = 0
    training["success"] = success
    return training

    
@app.get("/trainings/", response_model=List[TrainingResponse])
def list_trainings():
    return trainings


@app.get("/revenue/", response_model=TotalRevenue)
def get_total_revenue():
    total_revenue = 0
    for training in trainings:
        if training["success"]:
            total_revenue += (training["revenue"] - training["cost"])
    return {"total_revenue": total_revenue}


@app.get("/clients/", response_model=ClientInfo)
def get_clients_info(name: str):
    completed_trainings = 0
    education_costs = 0
    revenue = 0
    if name not in clients.keys():
        raise HTTPException(status_code=404, detail="Client does not exist")
    clients_trainings = clients.get(name, [])
    for training in clients_trainings:
        education_costs += training["cost"]
        if training["completed"]:
            completed_trainings += 1
            if training["success"]:
                revenue += (training["revenue"] - training["cost"])
    client_info = {
        "completed_trainings": completed_trainings,
        "education_costs": education_costs,
        "revenue": revenue,
        "trainings": clients_trainings
    }
    return client_info


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
