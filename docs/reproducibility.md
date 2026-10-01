# Reproducibility

Record:
- commit SHA
- Python version
- operating system
- CPU and memory hardware
- provider and exact model version
- API configuration without secrets
- benchmark metadata revision
- input regime and generator seed
- warmups and repeats
- timeout and memory limit
- acceptance policy and temperature schedule
- experiment configuration
- number of completed and failed runs

LLM API calls are excluded from ordinary CI. Publication runs must preserve raw outputs and the exact configuration used.
