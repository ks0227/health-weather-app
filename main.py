from flask import Flask, render_template
from database import init_db
from routes.health import health_bp  
from routes.analysis import analysis_bp  
from routes.dashboard import dashboard_bp  

app = Flask(__name__)
app.secret_key = "health_weather_app"  
init_db(app) 
app.register_blueprint(health_bp)    
app.register_blueprint(analysis_bp)     
app.register_blueprint(dashboard_bp) 

@app.route('/')
def index():
    return render_template('index.html') 

if __name__ == '__main__':
    app.debug = True
    app.run()