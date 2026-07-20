# Platform Infrastructure & Reliability

The platform runs a **multi-region architecture** (US, EU, APAC). Latency-sensitive traffic
is served from the nearest region. We track **P95 latency per region** as a core reliability
SLO and page the on-call engineer when a region exceeds target during peak hours. In 2024,
**APAC** was persistently the slowest region and generated the most alerts; a regional read
cache was rolled out to bring P95 back under target.
