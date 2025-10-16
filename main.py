from flask import Flask, request, jsonify
import tempfile
import subprocess
import os
import json

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def handle_script():
   
    if not request.is_json:
        return jsonify({"error": "Invalid content type, expecting JSON"}), 400

    data = request.get_json()
    script = data.get("script")

    if not script or not isinstance(script, str):
        return jsonify({"error": "Missing or invalid 'script' field"}), 400

    if "def main" not in script:
        return jsonify({"error": "Script must have a main() function"}), 400

    # Create temp file for script
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    temp_file.write(script)
    temp_file.write('\n\n')
    temp_file.write('import json\n')
    temp_file.write('if __name__ == "__main__":\n')
    temp_file.write('    output = main()\n')
    temp_file.write('    print("<<<RESULT>>>")\n')
    temp_file.write('    print(json.dumps(output))\n')
    temp_file.close()

    script_path = temp_file.name

    try:
        process_result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        script_stdout = process_result.stdout
        script_stderr = process_result.stderr

        if "<<<RESULT>>>" not in script_stdout:
            error_message = script_stderr if script_stderr else "Script did not return a result"
            return jsonify({"error": error_message}), 400

        parts = script_stdout.split("<<<RESULT>>>")
        clean_output = parts[0].strip()
        result_string = parts[1].strip()

        # Try to parse the result as JSON
        try:
            result_data = json.loads(result_string)
        except Exception:
            return jsonify({"error": "main() must return valid JSON"}), 400

        # Return the result and stdout
        return jsonify({
            "result": result_data,
            "stdout": clean_output
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Script took too long to run"}), 408
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        # Delete temp file
        if os.path.exists(script_path):
            os.remove(script_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)