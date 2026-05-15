import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


STATE_FILE = Path(__file__).resolve().with_name("dev_state.json")


def load_state():
    if not STATE_FILE.exists():
        return {"users": {}, "predictions": []}
    try:
        with STATE_FILE.open("r", encoding="utf-8") as handle:
            state = json.load(handle)
        state.setdefault("users", {})
        state.setdefault("predictions", [])
        return state
    except Exception:
        return {"users": {}, "predictions": []}


def save_state(state):
    temp_file = STATE_FILE.with_suffix(".json.tmp")
    with temp_file.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
    temp_file.replace(STATE_FILE)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    state = load_state()

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        self.close_connection = True

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def _get_token(self):
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.removeprefix("Bearer ").strip()
        return ""

    def _get_current_user(self):
        token = self._get_token()
        if not token:
            return None
        for user in Handler.state["users"].values():
            if user.get("token") == token:
                return user
        return None

    def do_GET(self):
        parsed = urlparse(self.path)
        print(f"[dev_server] GET {self.path} from {self.client_address}", flush=True)

        if parsed.path == "/":
            self._send_json({"message": "Sanjeevani dev backend running (mock)"})
            return

        if parsed.path == "/predict":
            user = self._get_current_user()
            if user is None:
                self._send_json({"detail": "Could not validate credentials"}, status=401)
                return

            qs = parse_qs(parsed.query)
            try:
                temperature = float(qs.get("temperature", [25.0])[0])
                humidity = float(qs.get("humidity", [60.0])[0])
                aqi = float(qs.get("aqi", [50.0])[0])
                lat = float(qs.get("lat", [0])[0])
                lon = float(qs.get("lon", [0])[0])
            except Exception:
                self._send_json({"error": "invalid query parameters"}, status=400)
                return

            score = (humidity * 0.35) + (aqi * 0.45) + (temperature * 0.2)
            if score > 130:
                risk = "High"
            elif score > 100:
                risk = "Medium"
            else:
                risk = "Low"

            disease = "None"
            if risk == "High":
                disease = "Dengue" if humidity >= 75 and aqi >= 120 else "Malaria"

            response = {
                "risk": risk,
                "risk_level": risk,
                "disease": disease,
                "explanation": "Mocked heuristic response",
                "alert": "Mock alert",
                "confidence": 0.75,
                "recommendation": "Follow local guidance",
                "inputs": {"temperature": temperature, "humidity": humidity, "aqi": aqi},
                "feature_score": round((temperature * 0.2) + (humidity * 0.4) + (aqi * 0.4), 2),
            }

            prediction_record = {
                "id": f"pred-{len(Handler.state['predictions']) + 1}",
                "user_id": user["id"],
                "location": f"{lat:.4f}, {lon:.4f}",
                "temperature": temperature,
                "humidity": humidity,
                "aqi": aqi,
                "risk": risk,
                "risk_level": risk,
                "disease": disease,
                "confidence": 0.75,
                "recommendation": response["recommendation"],
                "explanation": response["explanation"],
                "alert": response["alert"],
                "feature_score": response["feature_score"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            Handler.state["predictions"].insert(0, prediction_record)
            save_state(Handler.state)
            self._send_json(response)
            return

        if parsed.path == "/history":
            user = self._get_current_user()
            if user is None:
                self._send_json({"detail": "Could not validate credentials"}, status=401)
                return
            history = [item for item in Handler.state["predictions"] if item.get("user_id") == user["id"]]
            self._send_json(history)
            return

        if parsed.path == "/weather":
            qs = parse_qs(parsed.query)
            lat = float(qs.get("lat", [0])[0])
            lon = float(qs.get("lon", [0])[0])
            data = {"location": {"lat": lat, "lon": lon}, "temperature": 26.3, "humidity": 64.2, "source": "mock"}
            self._send_json(data)
            return

        if parsed.path == "/aqi":
            qs = parse_qs(parsed.query)
            lat = float(qs.get("lat", [0])[0])
            lon = float(qs.get("lon", [0])[0])
            data = {"aqi": 78, "category": "Moderate", "location": {"lat": lat, "lon": lon}}
            self._send_json(data)
            return

        if parsed.path == "/iot-live":
            data = {
                "vitals": {"temperature": 36.8, "bp": "128/82", "spo2": 98, "heart_rate": 82, "ecg": "Normal Sinus Rhythm"},
                "prediction": {"risk": "Low", "disease": "None", "confidence": 0.75},
                "explanation": "Mock IoT stream",
                "alerts": [],
            }
            self._send_json(data)
            return

        if parsed.path == "/reports":
            self._send_json([])
            return

        if parsed.path == "/report":
            self._send_json({"detail": "report generation not implemented in mock server"}, status=404)
            return

        self._send_json({"error": "not found"}, status=404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
        self.close_connection = True

    def do_POST(self):
        parsed = urlparse(self.path)
        print(f"[dev_server] POST {self.path} from {self.client_address}", flush=True)

        if parsed.path == "/signup":
            body = self._read_json_body() or {}
            print(f"[dev_server] signup body: {body}", flush=True)
            name = body.get("name")
            email = body.get("email")
            password = body.get("password")
            if not (name and email and password):
                self._send_json({"detail": "Missing fields"}, status=400)
                return
            if email in Handler.state["users"]:
                self._send_json({"detail": "User already exists"}, status=400)
                return
            user_id = str(len(Handler.state["users"]) + 1)
            token = f"mock-token-{user_id}"
            Handler.state["users"][email] = {"id": user_id, "name": name, "email": email, "password": password, "token": token}
            save_state(Handler.state)
            self._send_json({"access_token": token, "user_id": user_id, "name": name, "email": email})
            return

        if parsed.path == "/login":
            body = self._read_json_body() or {}
            print(f"[dev_server] login body: {body}", flush=True)
            email = body.get("email")
            password = body.get("password")
            user = Handler.state["users"].get(email)
            if not user or user.get("password") != password:
                self._send_json({"detail": "Invalid credentials"}, status=401)
                return
            token = user.get("token") or f"mock-token-{user['id']}"
            user["token"] = token
            Handler.state["users"][email] = user
            save_state(Handler.state)
            self._send_json({"access_token": token, "user_id": user["id"], "name": user["name"], "email": user["email"]})
            return

        self._send_json({"error": "not found"}, status=404)


def run(host="0.0.0.0", port=8010):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Dev backend running on http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    run()
