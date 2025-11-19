import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import Product as ProductSchema, Order as OrderSchema, ContactMessage as ContactSchema

app = FastAPI(title="Upcycled Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Upcycled Shop Backend Running"}

@app.get("/api/products", response_model=List[ProductSchema])
def list_products(featured: Optional[bool] = Query(default=None)):
    try:
        q = {}
        if featured is not None:
            q["featured"] = bool(featured)
        docs = get_documents("product", q)
        # convert ObjectId to string and ensure fields compliant
        items: List[ProductSchema] = []
        for d in docs:
            d.pop("_id", None)
            items.append(ProductSchema(**d))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{slug}", response_model=ProductSchema)
def get_product(slug: str):
    try:
        docs = get_documents("product", {"slug": slug}, limit=1)
        if not docs:
            raise HTTPException(status_code=404, detail="Product not found")
        d = docs[0]
        d.pop("_id", None)
        return ProductSchema(**d)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products", response_model=dict)
def create_product(product: ProductSchema):
    try:
        # ensure unique slug
        existing = get_documents("product", {"slug": product.slug}, limit=1)
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")
        inserted_id = create_document("product", product)
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders", response_model=dict)
def create_order(order: OrderSchema):
    try:
        inserted_id = create_document("order", order)
        return {"id": inserted_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contact", response_model=dict)
def contact(message: ContactSchema):
    try:
        inserted_id = create_document("contactmessage", message)
        return {"id": inserted_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
