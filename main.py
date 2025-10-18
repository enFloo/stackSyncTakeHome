from flask import Flask, request, jsonify
import tempfile, subprocess, os, json, shutil, pathlib

app = Flask(__name__)

@app.post("/execute")
def execute_script():
    data = request.get_json(force=True, silent=True) or {}
    script = data.get("script")
    if not isinstance(script, str) or "def main" not in script:
        return jsonify(error="Body must contain a Python script defining main()"), 400

    tmpdir = tempfile.mkdtemp(prefix="sandbox_", dir="/app")
    script_path = pathlib.Path(tmpdir) / "user_script.py"
    script_path.write_text(
        script
        + "\n\nimport json\nif __name__ == '__main__':\n"
          "    r = main()\n    print('<<<RESULT>>>')\n    print(json.dumps(r))\n"
    )

    cmd = [
        "/usr/sbin/nsjail",
        "--config", "/app/nsjail.config",
        "--",
        "/usr/local/bin/python3", str(script_path)
    ]

    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if "<<<RESULT>>>" not in p.stdout:
            return jsonify(error=p.stderr or p.stdout or "no output"), 400
        out, ret = p.stdout.split("<<<RESULT>>>", 1)
        return jsonify(result=json.loads(ret.strip()), stdout=out.strip())
    except subprocess.TimeoutExpired:
        return jsonify(error="timeout"), 408
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

@app.get("/health")
def health(): return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
