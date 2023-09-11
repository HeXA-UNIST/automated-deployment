# automated-deployment

A simple flask server that deploies UNIST HeXA services automatically

# Usage

1. Implement your service on git remote

2. Enroll the project to https://deploy.hexa.pro/enroll (POST)
    - (header) Access-Token: request to President of HeXA
    - service: service name
    - repo: github repository url
    - port_info: <internal port(your service)>:<deploy port(apache httpd)> (e.g. 8080:7778 if your service use 8080, and apache httpd map the subdomain to 8080 of HeXA server)

3. Add workflow (see example_workflow.yml)

4. Push or Merge PR to main