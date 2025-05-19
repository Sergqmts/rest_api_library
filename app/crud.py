@app.post("/readers/", response_model=schema.ReaderRead)
def create_reader(reader_in: schema.ReaderCreate, db: Session = Depends(get_db)):
    existing_reader = db.query(models.Reader).filter(models.Reader.email == reader_in.email).first()
    if existing_reader:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_reader = models.Reader(**reader_in.dict())
    db.add(new_reader)
    db.commit()
    db.refresh(new_reader)
    return new_reader



@app.get("/readers/", response_model=List[schema.ReaderRead])
def get_readers(db: Session = Depends(get_db)):
    return db.query(models.Reader).all()



@app.get("/readers/{reader_id}", response_model=schema.ReaderRead)
def get_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = db.query(models.Reader).filter(models.Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader



@app.put("/readers/{reader_id}", response_model=schema.ReaderRead)
def update_reader(reader_id: int, reader_in: schema.ReaderCreate, db: Session = Depends(get_db)):
    reader = db.query(models.Reader).filter(models.Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    for key, value in reader_in.dict().items():
        setattr(reader, key, value)
    db.commit()
    db.refresh(reader)
    return reader



@app.delete("/readers/{reader_id}")
def delete_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = db.query(models.Reader).filter(models.Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    db.delete(reader)
    db.commit()
    return {"detail": "Reader deleted"}