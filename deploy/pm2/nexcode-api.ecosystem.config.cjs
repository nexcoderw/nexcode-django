const port = process.env.PORT || "8000";

module.exports = {
  apps: [
    {
      name: "nexcode-api",
      cwd: "/var/www/nexcode/api",
      script: "/var/www/nexcode/api/venv/bin/gunicorn",
      args: `--workers 3 --timeout 60 --bind 127.0.0.1:${port} nexcode.wsgi:application`,
      interpreter: "none",
      exec_mode: "fork",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      env: {
        DJANGO_ENV: process.env.DJANGO_ENV || "production",
        PORT: port,
      },
      out_file: "/var/www/nexcode/shared/logs/nexcode-api.out.log",
      error_file: "/var/www/nexcode/shared/logs/nexcode-api.error.log",
      merge_logs: true,
      time: true,
    },
  ],
};
