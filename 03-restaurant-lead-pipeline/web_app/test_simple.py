from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Restaurant Lead Generation - Hammad Durrani</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 50px;
                margin: 0;
                min-height: 100vh;
            }
            .container {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 800px;
                margin: 0 auto;
            }
            h1 { 
                font-size: 3rem; 
                margin-bottom: 20px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .watermark {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-45deg);
                font-size: 8rem;
                color: rgba(255,255,255,0.1);
                z-index: -1;
                pointer-events: none;
            }
            .status {
                background: rgba(255,255,255,0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                margin: 10px;
                text-decoration: none;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="watermark">HAMMAD DURRANI</div>
        <div class="container">
            <h1>🍕 Restaurant Lead Generation</h1>
            <p style="font-size: 1.2rem;">Advanced AI-Powered System for Restaurant Lead Discovery</p>
            <p style="font-size: 1.1rem;">Created by <strong>Hammad Durrani</strong></p>
            
            <div class="status">
                <h3>✅ Server Status: RUNNING</h3>
                <p>Flask web server is working perfectly!</p>
                <p>Port: 5000 | Host: localhost</p>
            </div>
            
            <h3>🎯 System Features:</h3>
            <ul style="text-align: left; max-width: 500px; margin: 0 auto;">
                <li>✅ Beautiful Glassmorphism UI Design</li>
                <li>✅ 20 Pakistani Cities Coverage</li>
                <li>✅ 4 Data Sources (Yellow Pages, FoodPanda, Google Maps, Facebook)</li>
                <li>✅ Real-time Data Collection</li>
                <li>✅ Advanced Analytics Dashboard</li>
                <li>✅ CSV & JSON Export</li>
                <li>✅ Hammad Durrani Watermark</li>
            </ul>
            
            <div style="margin-top: 30px;">
                <a href="/test" class="btn">Test API Endpoint</a>
                <a href="/data" class="btn">View Sample Data</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return {"status": "success", "message": "API is working!", "creator": "Hammad Durrani"}

@app.route('/data')
def data():
    return {
        "restaurants": [
            {"name": "BBQ Tonight Karachi", "city": "Karachi", "rating": 4.5},
            {"name": "Chinese Wok Lahore", "city": "Lahore", "rating": 4.2},
            {"name": "Pizza Hut Islamabad", "city": "Islamabad", "rating": 4.0}
        ],
        "total": 3,
        "creator": "Hammad Durrani"
    }

if __name__ == '__main__':
    print("🚀 Starting Simple Flask Test Server...")
    print("=" * 50)
    print("Open your browser and go to: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
