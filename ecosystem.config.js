module.exports = {
  apps: [
    {
      name: "nexus-backend",
      script: "python3",
      args: "-m uvicorn main:app --host 0.0.0.0 --port 8000",
      cwd: "/root/nexus-ai/backend",
      interpreter: "none",
      env: {
        PYTHONPATH: "."
      }
    },
    {
      name: "nexus-frontend",
      script: "bun",
      args: "run dev --port 5008 --hostname 0.0.0.0",
      cwd: "/root/nexus-ai/frontend",
      interpreter: "none",
      env: {
        NEXT_TELEMETRY_DISABLED: "1",
        NODE_ENV: "development"
      }
    }
  ]
};
