from dash_app import app, create_app
import sys

if __name__=='__main__':
    create_app(sys.argv[1])
    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)
