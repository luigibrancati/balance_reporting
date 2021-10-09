from dash_app import app, create_app

if __name__=='__main__':
    create_app()
    app.run_server(debug=True)
