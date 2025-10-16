# Python Script Executor API

A Flask-based API service that executes arbitrary Python code in a sandboxed environment and returns the result.

## Cloud Run URL
https://script-executor-dh7od47dlq-uc.a.run.app

## Example Usage

### Basic execution:
```bash
curl -X POST https://script-executor-dh7od47dlq-uc.a.run.app/execute -H "Content-Type: application/json" -d '{"script": "def main():\n    return {\"sum\": 2 + 2}"}'
```

### With pandas and numpy:
```bash
curl -X POST https://script-executor-dh7od47dlq-uc.a.run.app/execute -H "Content-Type: application/json" -d '{"script": "import pandas as pd\nimport numpy as np\n\ndef main():\n    print(\"Testing pandas and numpy\")\n    df = pd.DataFrame({\"a\": [1, 2, 3], \"b\": [4, 5, 6]})\n    arr = np.array([1, 2, 3])\n    return {\"sum\": int(df[\"a\"].sum()), \"mean\": float(arr.mean())}"}'
```

## Running Locally
```bash
docker build -t script-executor .
docker run -p 8080:8080 script-executor
```

Test locally:
```bash
curl -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"script": "def main():\n    return {\"sum\": 2 + 2}"}'
```

## Implementation Details

1. **Docker Image**: Uses Python 3.11-slim base image (~688MB)
2. **Validation**: Checks for JSON content-type, valid script string, and main() function presence
3. **Available Libraries**: Flask, pandas, numpy, os
4. **Timeouts**: 10-second execution limit per script
5. **Response Format**: Returns both the main() result and stdout separately
6. **Error Handling**: Returns appropriate error messages for invalid scripts, timeouts, and execution failures
7. **Flask Framework**: Simple REST API with /execute endpoint
8. **Security Implementation**: 
   - Initial approach attempted to use nsjail as specified in the requirements
   - Cloud Run's gVisor-based security model restricts the Linux namespace operations (CLONE_NEWUSER, CLONE_NEWPID, etc.) that nsjail requires for process isolation
   - Disabling these namespaces defeats nsjail's security purpose, providing no meaningful isolation
   - Current implementation uses Python's resource limits (CPU, memory via setrlimit) and subprocess timeouts as basic sandboxing
   - Cloud Run's existing gVisor isolation provides container-level security
   - For production deployment requiring full nsjail support, would recommend GCE or GKE where kernel capabilities are available

## Time Spent
Approximately 3 hours including research, implementation, and deployment debugging.

1. Created Repo @ 7:10pm CST
2. started coding at 8:10pm CST
3. 9:30pm CST Believe I'm running into an issue with codespaces not having permission to run in nsjail
4. 10pm downloading gcloud to codespace, setting up account and billing
5. 10:43pm First test on Gcloud url; nsjail namespace error 
6. 10:55pm First break; other priotities calling 
7. 12:30am trying to resolve nsjail error
8. 1:30am Having gone over the allotted time I've reverted to the working version w/o nsJail
    From w
9. I know there's a solution but I'd like to turn in something that works

