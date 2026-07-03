thon
from fastapi import FastAPI, Request
from pydantic import BaseModel
import psycopg2
from psycopg2 import errorcodes, extensions
from typing import List, Optional

app = FastAPI()

# Define a simple Pydantic model for demonstration purposes
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float


@app.post("/items/")
async def create_item(item: Item):
    return {"item_name": item.name}

# Connect to the PostgreSQL database
def connect_db():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="postgres",
        user="yourusername",
        password="yourpassword"
    )
    return conn

@app.get("/")
async def read_root(request: Request):
    db_conn = connect_db()
    cursor = db_conn.cursor()

    # Fetch data from the database
    cursor.execute("SELECT * FROM items")
    result = cursor.fetchall()

    response_items = []
    for row in result:
        item = {
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "tax": row[4]
        }
        response_items.append(item)

    return {"items": response_items}

@app.delete("/items/{item_id}")
async def delete_item(request: Request, item_id: int):
    db_conn = connect_db()
    cursor = db_conn.cursor()

    # Delete the item from the database
    try:
        cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
        db_conn.commit()
        return {"message": "Item deleted successfully"}
    except psycopg2.errors.ForwardOnlyTransactionNeeded:
        print(f"Transaction was already committed. Deleting again.")
        cursor.execute("ROLLBACK")
        db_conn.commit()

@app.put("/items/{item_id}")
async def update_item(request: Request, item_id: int):
    new_price = float(request.query_params.get('price'))
    tax = float(request.query_params.get('tax'))

    db_conn = connect_db()
    cursor = db_conn.cursor()

    # Update the price and tax of the item
    try:
        cursor.execute("UPDATE items SET price = %s, tax = %s WHERE id = %s", (new_price, tax, item_id))
        db_conn.commit()
        return {"message": "Item updated successfully"}
    except psycopg2.errors.ForwardOnlyTransactionNeeded:
        print(f"Transaction was already committed. Updating again.")
        cursor.execute("ROLLBACK")
        db_conn.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)