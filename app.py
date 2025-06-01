from flask import Flask, render_template_string, jsonify, request
import datetime
import random
import json

# Create Flask application instance
app = Flask(__name__)

# HTML template with embedded JavaScript (client-side code)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Server-Client Bridge Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        #dynamic-content { background: #f0f0f0; padding: 15px; margin: 10px 0; }
        .server-data { color: #0066cc; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Flask: Server-Side Python → Client-Side JavaScript Bridge</h1>
        
        <div class="section">
            <h2>1. Server-Generated Content (Python → HTML)</h2>
            <p>Current server time: <span class="server-data">{{ current_time }}</span></p>
            <p>Random number from Python: <span class="server-data">{{ random_number }}</span></p>
            <p>Server message: <span class="server-data">{{ server_message }}</span></p>
        </div>
        
        <div class="section">
            <h2>2. Dynamic Client-Server Communication</h2>
            <button onclick="fetchServerData()">Get Fresh Data from Server</button>
            <button onclick="sendDataToServer()">Send Data to Server</button>
            <div id="dynamic-content">Click buttons to see server-client interaction...</div>
        </div>
        
        <div class="section">
            <h2>3. Real-time Server Processing</h2>
            <input type="text" id="user-input" placeholder="Enter text to process on server">
            <button onclick="processOnServer()">Process on Server</button>
            <div id="processed-result"></div>
        </div>
    </div>

    <script>
        // CLIENT-SIDE JAVASCRIPT CODE
        // This runs in the browser and communicates with Python server
        
        async function fetchServerData() {
            try {
                // Make request to Python server endpoint
                const response = await fetch('/api/data');
                const data = await response.json();
                
                // Update DOM with server-generated data
                document.getElementById('dynamic-content').innerHTML = `
                    <h3>Fresh Data from Python Server:</h3>
                    <p><strong>Server Time:</strong> ${data.timestamp}</p>
                    <p><strong>Random Number:</strong> ${data.random_num}</p>
                    <p><strong>Request Count:</strong> ${data.request_count}</p>
                    <p><strong>Server Status:</strong> ${data.status}</p>
                `;
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        async function sendDataToServer() {
            const clientData = {
                browser: navigator.userAgent,
                timestamp: new Date().toISOString(),
                random_client_num: Math.floor(Math.random() * 1000)
            };
            
            try {
                const response = await fetch('/api/receive', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(clientData)
                });
                
                const result = await response.json();
                document.getElementById('dynamic-content').innerHTML = `
                    <h3>Server Processed Client Data:</h3>
                    <p><strong>Server Response:</strong> ${result.message}</p>
                    <p><strong>Data Received:</strong> ${JSON.stringify(result.received_data, null, 2)}</p>
                    <p><strong>Server Processing:</strong> ${result.server_processing}</p>
                `;
            } catch (error) {
                console.error('Error sending data:', error);
            }
        }
        
        async function processOnServer() {
            const userText = document.getElementById('user-input').value;
            
            if (!userText) {
                alert('Please enter some text');
                return;
            }
            
            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: userText})
                });
                
                const result = await response.json();
                document.getElementById('processed-result').innerHTML = `
                    <h3>Server Processing Results:</h3>
                    <p><strong>Original:</strong> ${result.original}</p>
                    <p><strong>Uppercase:</strong> ${result.uppercase}</p>
                    <p><strong>Word Count:</strong> ${result.word_count}</p>
                    <p><strong>Reversed:</strong> ${result.reversed}</p>
                    <p><strong>Python Analysis:</strong> ${result.analysis}</p>
                `;
            } catch (error) {
                console.error('Error processing text:', error);
            }
        }
    </script>
</body>
</html>
"""

# Global counter for demonstration
request_counter = 0

@app.route('/')
def home():
    """
    SERVER-SIDE PYTHON CODE
    This runs on the server and generates HTML sent to browser
    """
    global request_counter
    request_counter += 1
    
    # Python processes data server-side
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_number = random.randint(1, 1000)
    server_message = f"This message was generated by Python on the server! (Request #{request_counter})"
    
    # Python renders template and sends to browser
    return render_template_string(HTML_TEMPLATE, 
                                current_time=current_time,
                                random_number=random_number,
                                server_message=server_message)

@app.route('/api/data')
def api_data():
    """
    API endpoint - Python processes request and returns JSON
    Client-side JavaScript will consume this data
    """
    global request_counter
    request_counter += 1
    
    # Server-side Python logic
    server_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'random_num': random.randint(100, 999),
        'request_count': request_counter,
        'status': 'Python server is running smoothly!',
        'server_info': 'Generated by Flask/Python backend'
    }
    
    return jsonify(server_data)

@app.route('/api/receive', methods=['POST'])
def receive_data():
    """
    Receives data from client, processes it with Python, returns response
    """
    client_data = request.get_json()
    
    # Python processes the client data
    processed_response = {
        'message': 'Python server successfully received and processed your data!',
        'received_data': client_data,
        'server_processing': f"Server added this at {datetime.datetime.now()}",
        'data_analysis': {
            'client_random_doubled': client_data.get('random_client_num', 0) * 2,
            'browser_detected': 'Chrome' in client_data.get('browser', ''),
            'data_size': len(str(client_data))
        }
    }
    
    return jsonify(processed_response)

@app.route('/api/process', methods=['POST'])
def process_text():
    """
    Processes text using Python server-side logic
    """
    data = request.get_json()
    text = data.get('text', '')
    
    # Complex Python processing that can't be done client-side
    analysis_result = {
        'original': text,
        'uppercase': text.upper(),
        'word_count': len(text.split()),
        'reversed': text[::-1],
        'analysis': f"Python analyzed: {len(text)} chars, {text.count(' ')} spaces, vowels: {sum(1 for c in text.lower() if c in 'aeiou')}"
    }
    
    return jsonify(analysis_result)

if __name__ == '__main__':
    print("🚀 Starting Flask Server...")
    print("📍 Open your browser to: http://localhost:5000")
    print("🔄 This demonstrates Python server ↔ Browser client communication")
    print("⚡ Server-side Python code generates dynamic content for the browser")
    
    # Start the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)