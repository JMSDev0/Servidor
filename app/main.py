from app.api.routes import create_app

app = create_app()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8080)