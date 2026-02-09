#!/usr/bin/env python3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json
import cgi
import zipfile
import shutil
import urllib.request
import tempfile
from urllib.parse import urlparse, parse_qs
import subprocess
import threading
from datetime import datetime
import signal
import requests
try:
    from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
except ImportError:
    from simple_websocket_server import WebSocketServer as SimpleWebSocketServer, WebSocket

# Store active chat sessions
chat_sessions = {}
# Store available models
AI_MODELS = {
    'claude': {
        'name': 'Claude 2',
        'provider': 'Anthropic',
        'description': 'Advanced language model with strong coding capabilities'
    },
    'gpt4': {
        'name': 'GPT-4',
        'provider': 'OpenAI',
        'description': 'Latest GPT model with advanced reasoning'
    },
    'llama2': {
        'name': 'Llama 2',
        'provider': 'Meta',
        'description': 'Open source model with strong performance'
    },
    'palm2': {
        'name': 'PaLM 2',
        'provider': 'Google',
        'description': 'Google\'s advanced language model'
    },
    'huggingface': {
        'name': 'HuggingFace',
        'provider': 'HuggingFace',
        'description': 'HuggingFace hosted models'
    },
    'localai': {
        'name': 'LocalAI',
        'provider': 'LocalAI',
        'description': 'Local AI models via LocalAI'
    },
    'lmstudio': {
        'name': 'LM Studio',
        'provider': 'LM Studio',
        'description': 'Local models via LM Studio'
    },
    'ollama': {
        'name': 'Ollama',
        'provider': 'Ollama',
        'description': 'Local models via Ollama'
    },
    'ollama_cloud': {
        'name': 'Ollama Cloud',
        'provider': 'Ollama Cloud',
        'description': 'Cloud models via Ollama Cloud'
    }
}

# Configuration
LOCALAI_URL = os.getenv("LOCALAI_URL", "http://localhost:8080/v1")
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api")
OLLAMA_CLOUD_API_KEY = os.getenv("OLLAMA_CLOUD_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
LOCALAI_MODEL = os.getenv("LOCALAI_MODEL", "gpt-3.5-turbo")
LMSTUDIO_MODEL = os.getenv("LMSTUDIO_MODEL", "local-model")

def query_openai_compatible(prompt, base_url, model_name, api_key=None):
    """Query OpenAI compatible API"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        url = f"{base_url.rstrip('/')}/chat/completions"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return f"Error: Unexpected response format from {base_url}"
        else:
            return f"Error: API returned status code {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error connecting to {base_url}: {str(e)}"

def query_ollama(prompt, base_url, model_name, api_key=None):
    """Query Ollama API"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        url = f"{base_url.rstrip('/')}/chat"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if "message" in data and "content" in data["message"]:
                return data["message"]["content"]
            else:
                return f"Error: Unexpected response format from Ollama"
        else:
            return f"Error: Ollama returned status code {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

def query_huggingface_model(prompt, model="gpt2"):
    """Query HuggingFace Inference API for a text generation model"""
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    if not API_TOKEN:
        raise Exception("HUGGINGFACE_API_TOKEN environment variable not set")
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        else:
            return "Error: Unexpected response format from HuggingFace API"
    else:
        return f"Error: HuggingFace API returned status code {response.status_code}"

class ChatSession:
    def __init__(self, session_id, model_id):
        self.session_id = session_id
        self.model_id = model_id
        self.messages = []
        self.created_at = datetime.now()
        self.active = True

    def add_message(self, role, content):
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.messages.append(message)
        return message

class ChatWebSocket(WebSocket):
    def handleMessage(self):
        try:
            data = json.loads(self.data)
            command = data.get('command')
            print(f"Processing command: {command}")

            if command == 'start':
                # Start new chat session
                session_id = data.get('sessionId')
                model_id = data.get('modelId', 'claude')
                print(f"Starting new chat session: {session_id} with model: {model_id}")
                
                chat_sessions[session_id] = ChatSession(session_id, model_id)
                response = {
                    'type': 'session_started',
                    'sessionId': session_id,
                    'model': AI_MODELS.get(model_id, AI_MODELS['claude'])
                }
                print(f"Sending session start response: {response}")
                self.sendMessage(json.dumps(response))

            elif command == 'message':
                # Handle chat message
                session_id = data.get('sessionId')
                session = chat_sessions.get(session_id)
                if session and session.active:
                    content = data.get('content', '')
                    print(f"Processing message in session {session_id}: {content}")
                    
                    # Add user message
                    user_message = session.add_message('user', content)
                    self.sendMessage(json.dumps({
                        'type': 'message',
                        'message': user_message
                    }))

                    # Call AI model for response
                    if session.model_id == 'huggingface':
                        try:
                            ai_response_text = query_huggingface_model(content)
                        except Exception as e:
                            ai_response_text = f"Error querying HuggingFace model: {str(e)}"
                    elif session.model_id == 'localai':
                        ai_response_text = query_openai_compatible(content, LOCALAI_URL, LOCALAI_MODEL)
                    elif session.model_id == 'lmstudio':
                        ai_response_text = query_openai_compatible(content, LMSTUDIO_URL, LMSTUDIO_MODEL)
                    elif session.model_id == 'ollama':
                        ai_response_text = query_ollama(content, OLLAMA_URL, OLLAMA_MODEL)
                    elif session.model_id == 'ollama_cloud':
                        if not OLLAMA_CLOUD_API_KEY:
                            ai_response_text = "Error: OLLAMA_CLOUD_API_KEY not set"
                        else:
                            ai_response_text = query_ollama(content, "https://ollama.com/api", OLLAMA_MODEL, OLLAMA_CLOUD_API_KEY)
                    else:
                        # Simulate AI response for other models
                        ai_response_text = f"Response from {AI_MODELS[session.model_id]['name']}: " + content[::-1]

                    ai_message = session.add_message('assistant', ai_response_text)
                    print(f"Sending AI response: {ai_response_text}")
                    self.sendMessage(json.dumps({
                        'type': 'message',
                        'message': ai_message
                    }))

            elif command == 'end':
                # End chat session
                session_id = data.get('sessionId')
                if session_id in chat_sessions:
                    print(f"Ending chat session: {session_id}")
                    chat_sessions[session_id].active = False
                    self.sendMessage(json.dumps({
                        'type': 'session_ended',
                        'sessionId': session_id
                    }))

        except json.JSONDecodeError as e:
            print(f"Invalid JSON message received: {e}")
        except Exception as e:
            print(f"Error handling message: {str(e)}")

    def handleConnected(self):
        print(f"New client connected: {self.address}")

    def handleClose(self):
        print(f"Client disconnected: {self.address}")

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

class UploadHandler(CORSRequestHandler):
    def __init__(self, *args, **kwargs):
        self.uploads_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "uploads")
        os.makedirs(self.uploads_dir, exist_ok=True)
        super().__init__(*args, directory=os.path.dirname(os.path.realpath(__file__)), **kwargs)

    def do_GET(self):
        if self.path == '/projects':
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'projects': self.get_projects()
                }).encode())
                return
            except Exception as e:
                self.send_error(500, f'Internal Server Error: {str(e)}')
                return
        elif self.path == '/models':
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'models': AI_MODELS
                }).encode())
                return
            except Exception as e:
                self.send_error(500, f'Internal Server Error: {str(e)}')
                return
        # Serve static files for all other GET requests
        super().do_GET()

    def do_DELETE(self):
        if self.path.startswith('/project/'):
            try:
                project_name = os.path.basename(self.path)
                project_path = os.path.join(self.uploads_dir, project_name)
                
                if os.path.exists(project_path):
                    shutil.rmtree(project_path)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'status': 'success',
                        'message': f'Project deleted: {project_name}',
                        'projects': self.get_projects()
                    }).encode())
                else:
                    self.send_error(404, f'Project not found: {project_name}')
                return
            except Exception as e:
                self.send_error(500, f'Internal Server Error: {str(e)}')
                return

    def do_POST(self):
        if self.path == '/upload':
            try:
                content_type = self.headers.get('Content-Type')
                if content_type:
                    ctype, pdict = cgi.parse_header(content_type)
                    if ctype == 'multipart/form-data':
                        form = cgi.FieldStorage(
                            fp=self.rfile,
                            headers=self.headers,
                            environ={'REQUEST_METHOD': 'POST',
                                   'CONTENT_TYPE': self.headers['Content-Type']}
                        )
                        
                        if 'file' in form:
                            fileitem = form['file']
                            if fileitem.filename:
                                filename = os.path.basename(fileitem.filename)
                                project_name = os.path.splitext(filename)[0]
                                upload_dir = os.path.join(self.uploads_dir, project_name)
                                os.makedirs(upload_dir, exist_ok=True)
                                
                                filepath = os.path.join(upload_dir, filename)
                                with open(filepath, 'wb') as f:
                                    f.write(fileitem.file.read())
                                
                                if filename.lower().endswith('.zip'):
                                    try:
                                        with zipfile.ZipFile(filepath, 'r') as zip_ref:
                                            zip_ref.extractall(upload_dir)
                                        os.remove(filepath)
                                        message = f'ZIP file extracted: {filename}'
                                    except zipfile.BadZipFile:
                                        message = f'Error: Invalid ZIP file: {filename}'
                                        os.remove(filepath)
                                else:
                                    message = f'File uploaded: {filename}'
                                
                                self.send_response(200)
                                self.send_header('Content-Type', 'application/json')
                                self.end_headers()
                                self.wfile.write(json.dumps({
                                    'status': 'success',
                                    'message': message,
                                    'projects': self.get_projects()
                                }).encode())
                                return
                
                self.send_error(400, 'Bad Request: No file found')
                return
                        
            except Exception as e:
                self.send_error(500, f'Internal Server Error: {str(e)}')
                return
                
        elif self.path == '/clone':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())
                repo_url = data.get('url')
                
                if repo_url:
                    parsed_url = urlparse(repo_url)
                    repo_name = os.path.splitext(os.path.basename(parsed_url.path))[0]
                    clone_dir = os.path.join(self.uploads_dir, repo_name)
                    
                    try:
                        subprocess.run(['git', 'clone', repo_url, clone_dir], 
                                    check=True, capture_output=True)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'status': 'success',
                            'message': f'Repository cloned: {repo_url}',
                            'projects': self.get_projects()
                        }).encode())
                        return
                    except subprocess.CalledProcessError as e:
                        self.send_error(500, f'Failed to clone repository: {str(e)}')
                        return
                    
                self.send_error(400, 'Bad Request: No repository URL provided')
                return
                
            except Exception as e:
                self.send_error(500, f'Internal Server Error: {str(e)}')
                return

        self.send_error(404, 'Not Found')

    def get_projects(self):
        """Get list of projects in the uploads directory"""
        projects = []
        try:
            if os.path.exists(self.uploads_dir):
                for item in os.listdir(self.uploads_dir):
                    item_path = os.path.join(self.uploads_dir, item)
                    if os.path.isdir(item_path):
                        file_count = 0
                        for root, _, files in os.walk(item_path):
                            file_count += len(files)
                        
                        modified_time = os.path.getmtime(item_path)
                        
                        projects.append({
                            'name': item,
                            'files': file_count,
                            'path': item_path,
                            'modified': modified_time
                        })
                projects.sort(key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            print(f"Error listing projects: {str(e)}")
        return projects

def run_websocket_server():
    """Run the WebSocket server"""
    print("Starting WebSocket server on port 8001...")
    server = SimpleWebSocketServer('', 8001, ChatWebSocket)
    server.serveforever()

if __name__ == "__main__":
    # Install required package
    try:
        import pip
        pip.main(['install', 'simple-websocket-server'])
    except Exception as e:
        print(f"Error installing package: {str(e)}")

    # Start WebSocket server in a separate thread
    websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
    websocket_thread.start()

    # Start HTTP server
    port = 8000
    print(f"Starting SuperClaude UI server on port {port}...")
    print(f"Visit http://localhost:{port} to access the dashboard")
    httpd = HTTPServer(("", port), UploadHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()
