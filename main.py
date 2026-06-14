from fastapi import FastAPI , Path
import json
from pydantic import BaseModel, computed_field, Field, field_validator
from typing import Optional
from prometheus_fastapi_instrumentator import Instrumentator


app=FastAPI()

Instrumentator().instrument(app).expose(app)

class Patient(BaseModel):
    
    id: str
    name: str
    Gender: str
    age: int
    height: float = Field(description="in meters", example=1.67)
    weight: float

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v <= 0:
            raise ValueError('Age must be greater than 0')
        return v

    @field_validator('weight')
    @classmethod
    def validate_weight(cls, v):
        if v <= 0:
            raise ValueError('Weight must be greater than 0')
        return v

    @field_validator('height')
    @classmethod
    def validate_and_convert_height(cls, v):
        if v <= 0:
            raise ValueError('Height must be greater than 0')
        # cm ko meter mein convert kar dega, divide by 100 then roundof till 2 decimal places
        if v > 3.0:
            v = round(v / 100, 2)
        return v

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Fit"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    
    id:Optional[str]=None
    name:Optional[str]=None
    Gender:Optional[str]=None
    age:Optional[int]=None
    height:Optional[float]=Field(defaul=None,description="in meters",example=1.67)
    weight:Optional[float]=None        
    

def load_data():
    with open('patient.json' , 'r') as f:
        data=json.load(f)
        
    return data    
def save_data(data):
    with open('patient.json','w') as f:
        json.dump(data,f)

@app.get('/')
def Welcome():
    return {'message':'Welcome to patient managment API system'}

@app.get('/view')
def view_data():
    data_of_patients=load_data()
    
    return data_of_patients

@app.get('/patient/{patient_id}')
def View_patient(patient_id:str=Path(..., example='P001')):
    #laod all patient data
    data=load_data()
    
    if patient_id in data:
        return data[patient_id]
    return {"error":"patient not found"}

@app.post('/new_patient')
def new_patient(patient:Patient):
    # load data
    data=load_data()
    
    #if patient already exist?
    if patient.id in data:
        return "Patient already exist"
    
    #Add new patient
    data[patient.id]=patient.model_dump(exclude=['id'])
    
    #save data
    save_data(data)
    
    return "Patient Successfully added"

@app.put('/edit{patient_id}')
def edit_patient(patient_id:str , updated_patient:PatientUpdate):
    
    #load data
    data=load_data()
    
    if patient_id not in data:
        return "Patient not found"
    
    existing_patient_info=data[patient_id]
    
    updated_patient_info=updated_patient.model_dump(exclude_unset=True)
    
    for key,value in updated_patient_info.items():
        existing_patient_info[key]=value
        
    existing_patient_info['id']=patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')
    
    data[patient_id] = existing_patient_info
    
    save_data(data) 
    
    return "Patient data updated successfully"

@app.delete('/delet/{patient_id}')
def delet_patient_data(patient_id:str):
    
    data=load_data()
    
    if patient_id not in data:
        return "patient not found"
    del data[patient_id]
    
    save_data(data)
    
    return "patient data deleted"