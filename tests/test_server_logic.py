import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Mock SimpleWebSocketServer before importing server
sys.modules['SimpleWebSocketServer'] = MagicMock()
# We need to mock the WebSocket class specifically so it can be inherited
class MockWebSocket:
    def __init__(self, server, sock, address):
        self.server = server
        self.client = sock
        self.address = address
    def handleMessage(self): pass
    def handleConnected(self): pass
    def handleClose(self): pass
    def sendMessage(self, msg): pass
    def close(self): pass

sys.modules['SimpleWebSocketServer'].WebSocket = MockWebSocket

# Also mock requests
sys.modules['requests'] = MagicMock()

# Import server
# Add the directory containing server.py to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../SuperClaude/ui')))

try:
    import server
except ImportError:
    # If import fails (e.g. because of path), try loading source
    import importlib.util
    spec = importlib.util.spec_from_file_location("server", os.path.join(os.path.dirname(__file__), "../SuperClaude/ui/server.py"))
    server = importlib.util.module_from_spec(spec)
    sys.modules["server"] = server
    spec.loader.exec_module(server)

class TestServerLogic(unittest.TestCase):
    def setUp(self):
        # Create a mock socket and server for WebSocket init
        self.mock_socket = MagicMock()
        self.mock_server = MagicMock()
        self.mock_address = ('127.0.0.1', 12345)

        self.ws = server.ChatWebSocket(self.mock_server, self.mock_socket, self.mock_address)
        # Mock sendMessage on the instance
        self.ws.sendMessage = MagicMock()

        # Reset chat_sessions
        server.chat_sessions = {}

        # Reset requests mock
        server.requests.post.reset_mock()

    def test_start_session(self):
        # Test start command
        self.ws.data = json.dumps({
            'command': 'start',
            'sessionId': 'test_session',
            'modelId': 'claude'
        })
        self.ws.handleMessage()

        # Verify session created
        self.assertIn('test_session', server.chat_sessions)
        self.assertEqual(server.chat_sessions['test_session'].model_id, 'claude')

        # Verify response sent
        self.ws.sendMessage.assert_called()
        args, _ = self.ws.sendMessage.call_args
        response = json.loads(args[0])
        self.assertEqual(response['type'], 'session_started')
        self.assertEqual(response['sessionId'], 'test_session')

    @patch('server.query_huggingface_model')
    def test_message_huggingface(self, mock_query):
        mock_query.return_value = "HuggingFace response"

        # Start session first
        server.chat_sessions['hf_session'] = server.ChatSession('hf_session', 'huggingface')

        # Send message
        self.ws.data = json.dumps({
            'command': 'message',
            'sessionId': 'hf_session',
            'content': 'Hello'
        })
        self.ws.handleMessage()

        # Verify query called
        mock_query.assert_called_with('Hello')

        # Verify response sent (user message and AI message)
        self.assertEqual(self.ws.sendMessage.call_count, 2)

        # Check last message (AI response)
        args, _ = self.ws.sendMessage.call_args
        response = json.loads(args[0])
        self.assertEqual(response['type'], 'message')
        self.assertEqual(response['message']['role'], 'assistant')
        self.assertEqual(response['message']['content'], 'HuggingFace response')

    def test_message_claude_simulated(self):
        # Start session first
        server.chat_sessions['claude_session'] = server.ChatSession('claude_session', 'claude')

        # Send message
        self.ws.data = json.dumps({
            'command': 'message',
            'sessionId': 'claude_session',
            'content': 'Hello'
        })
        self.ws.handleMessage()

        # Verify response sent
        self.assertEqual(self.ws.sendMessage.call_count, 2)

        # Check last message (AI response) - simulated reverses string
        args, _ = self.ws.sendMessage.call_args
        response = json.loads(args[0])
        self.assertEqual(response['type'], 'message')
        self.assertEqual(response['message']['role'], 'assistant')
        # "Response from Claude 2: olleH"
        self.assertIn("olleH", response['message']['content'])

    def test_message_localai(self):
        # Mock requests.post response for OpenAI compatible API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "LocalAI response"}}]
        }
        server.requests.post.return_value = mock_response

        # Start session
        server.chat_sessions['local_session'] = server.ChatSession('local_session', 'localai')

        # Send message
        self.ws.data = json.dumps({
            'command': 'message',
            'sessionId': 'local_session',
            'content': 'Hello LocalAI'
        })
        self.ws.handleMessage()

        # Verify query called correctly
        server.requests.post.assert_called()
        args, kwargs = server.requests.post.call_args
        self.assertIn('/chat/completions', args[0])
        self.assertEqual(kwargs['json']['messages'][0]['content'], 'Hello LocalAI')

        # Check response
        args, _ = self.ws.sendMessage.call_args
        response = json.loads(args[0])
        self.assertEqual(response['message']['content'], 'LocalAI response')

    def test_message_ollama(self):
        # Mock requests.post response for Ollama API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Ollama response"}
        }
        server.requests.post.return_value = mock_response

        # Start session
        server.chat_sessions['ollama_session'] = server.ChatSession('ollama_session', 'ollama')

        # Send message
        self.ws.data = json.dumps({
            'command': 'message',
            'sessionId': 'ollama_session',
            'content': 'Hello Ollama'
        })
        self.ws.handleMessage()

        # Verify query called correctly
        server.requests.post.assert_called()
        args, kwargs = server.requests.post.call_args
        self.assertIn('/chat', args[0])
        self.assertNotIn('/completions', args[0]) # Ollama uses /chat
        self.assertEqual(kwargs['json']['messages'][0]['content'], 'Hello Ollama')
        self.assertFalse(kwargs['json']['stream'])

        # Check response
        args, _ = self.ws.sendMessage.call_args
        response = json.loads(args[0])
        self.assertEqual(response['message']['content'], 'Ollama response')

    def test_message_ollama_cloud(self):
        # Set API KEY
        with patch.dict(os.environ, {'OLLAMA_CLOUD_API_KEY': 'test_key'}):
            # We need to reload the module or just manually set the variable because it's read at module level
            # But wait, in the function `query_ollama`, api_key is passed.
            # In handleMessage, OLLAMA_CLOUD_API_KEY is used.
            # But OLLAMA_CLOUD_API_KEY is a global variable in server.py initialized from os.getenv.
            # So updating os.environ now won't update the already imported server.OLLAMA_CLOUD_API_KEY.
            # I need to update server.OLLAMA_CLOUD_API_KEY directly.

            old_key = server.OLLAMA_CLOUD_API_KEY
            server.OLLAMA_CLOUD_API_KEY = 'test_key'

            try:
                # Mock requests.post response for Ollama Cloud API
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "message": {"content": "Ollama Cloud response"}
                }
                server.requests.post.return_value = mock_response

                # Start session
                server.chat_sessions['ollama_cloud_session'] = server.ChatSession('ollama_cloud_session', 'ollama_cloud')

                # Send message
                self.ws.data = json.dumps({
                    'command': 'message',
                    'sessionId': 'ollama_cloud_session',
                    'content': 'Hello Cloud'
                })
                self.ws.handleMessage()

                # Verify query called correctly
                server.requests.post.assert_called()
                args, kwargs = server.requests.post.call_args
                self.assertIn('https://ollama.com/api/chat', args[0])
                self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test_key')

                # Check response
                args, _ = self.ws.sendMessage.call_args
                response = json.loads(args[0])
                self.assertEqual(response['message']['content'], 'Ollama Cloud response')

            finally:
                server.OLLAMA_CLOUD_API_KEY = old_key

    def test_message_ollama_cloud_no_key(self):
        # Ensure no key
        old_key = server.OLLAMA_CLOUD_API_KEY
        server.OLLAMA_CLOUD_API_KEY = None

        try:
            # Start session
            server.chat_sessions['ollama_cloud_session_no_key'] = server.ChatSession('ollama_cloud_session_no_key', 'ollama_cloud')

            # Send message
            self.ws.data = json.dumps({
                'command': 'message',
                'sessionId': 'ollama_cloud_session_no_key',
                'content': 'Hello Cloud'
            })
            self.ws.handleMessage()

            # Verify response is error
            args, _ = self.ws.sendMessage.call_args
            response = json.loads(args[0])
            self.assertIn('Error: OLLAMA_CLOUD_API_KEY not set', response['message']['content'])

        finally:
            server.OLLAMA_CLOUD_API_KEY = old_key

if __name__ == '__main__':
    unittest.main()
